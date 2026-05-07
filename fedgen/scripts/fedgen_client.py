"""
FedGen - EDC Management API Client
Provides methods to interact with EDC connectors for asset management,
contract negotiation, and data transfer using DCP (Decentralized Claims Protocol).
"""

import requests
import json
import time
from typing import Optional, Dict, Any, List

MGMT_CONTEXT = ["https://w3id.org/edc/connector/management/v0.0.1"]


class EDCClient:
    """Client for EDC Management API v3 with DCP support."""

    def __init__(self, management_url: str, api_key: str = "password"):
        self.management_url = management_url.rstrip('/')
        self.headers = {
            "Content-Type": "application/json",
            "X-Api-Key": api_key
        }

    # ── Asset Management ────────────────────────────────────────

    def create_asset(self, asset_id: str, description: str,
                     base_url: str, content_type: str = "application/json",
                     properties: dict = None) -> Dict[str, Any]:
        """Register a new asset with an HttpData data address."""
        props = {"description": description}
        if properties:
            props.update(properties)
        payload = {
            "@context": MGMT_CONTEXT,
            "@id": asset_id,
            "@type": "Asset",
            "properties": props,
            "dataAddress": {
                "@type": "DataAddress",
                "type": "HttpData",
                "baseUrl": base_url,
                "contentType": content_type,
            }
        }
        return self._post("/v3/assets", payload)

    # ── Policy Management ───────────────────────────────────────

    def create_policy(self, policy_id: str,
                      permissions: list = None,
                      obligations: list = None) -> Dict[str, Any]:
        """Create a policy definition with ODRL permissions/obligations."""
        policy = {"@type": "Set"}
        if permissions:
            policy["permission"] = permissions
        if obligations:
            policy["obligation"] = obligations
        if not permissions and not obligations:
            policy["permission"] = [{
                "action": "use",
                "constraint": {
                    "leftOperand": "MembershipCredential",
                    "operator": "eq",
                    "rightOperand": "active"
                }
            }]
        payload = {
            "@context": MGMT_CONTEXT,
            "@type": "PolicyDefinition",
            "@id": policy_id,
            "policy": policy
        }
        return self._post("/v3/policydefinitions", payload)

    # ── Contract Definitions ────────────────────────────────────

    def create_contract_definition(self, contract_id: str, policy_id: str,
                                   asset_id: str) -> Dict[str, Any]:
        """Create a contract definition linking policy to asset."""
        payload = {
            "@context": MGMT_CONTEXT,
            "@id": contract_id,
            "accessPolicyId": policy_id,
            "contractPolicyId": policy_id,
            "assetsSelector": {
                "operandLeft": "https://w3id.org/edc/v0.0.1/ns/id",
                "operator": "=",
                "operandRight": asset_id
            }
        }
        return self._post("/v3/contractdefinitions", payload)

    # ── Catalog ─────────────────────────────────────────────────

    def query_catalog(self, provider_protocol_url: str,
                      counter_party_id: str) -> Dict[str, Any]:
        """Query a provider's catalog using DCP protocol."""
        payload = {
            "@context": MGMT_CONTEXT,
            "counterPartyAddress": provider_protocol_url,
            "counterPartyId": counter_party_id,
            "protocol": "dataspace-protocol-http"
        }
        return self._post("/v3/catalog/request", payload)

    @staticmethod
    def parse_catalog(catalog_json: dict) -> List[Dict]:
        """Parse catalog response into a list of {asset_id, offer_id, policy}."""
        datasets = catalog_json.get("dcat:dataset", [])
        if isinstance(datasets, dict):
            datasets = [datasets]
        results = []
        for ds in datasets:
            offers = ds.get("odrl:hasPolicy", [])
            if isinstance(offers, dict):
                offers = [offers]
            for offer in offers:
                results.append({
                    "asset_id": ds["@id"],
                    "offer_id": offer["@id"],
                    "policy": offer,
                })
        return results

    # ── Contract Negotiation ────────────────────────────────────

    def initiate_negotiation(self, provider_protocol_url: str,
                             counter_party_id: str,
                             offer_id: str, asset_id: str,
                             policy: dict) -> Dict[str, Any]:
        """Initiate contract negotiation with a provider using DCP."""
        offer = {
            "@id": offer_id,
            "@type": "odrl:Offer",
            "odrl:target": {"@id": asset_id},
            "odrl:assigner": {"@id": counter_party_id},
        }
        for key in ["odrl:permission", "odrl:prohibition", "odrl:obligation"]:
            if key in policy:
                offer[key] = policy[key]

        payload = {
            "@context": MGMT_CONTEXT,
            "@type": "ContractRequest",
            "counterPartyAddress": provider_protocol_url,
            "counterPartyId": counter_party_id,
            "protocol": "dataspace-protocol-http",
            "policy": offer,
        }
        return self._post("/v3/contractnegotiations", payload)

    def get_negotiation(self, negotiation_id: str) -> Dict[str, Any]:
        """Get the status of a contract negotiation."""
        return self._get(f"/v3/contractnegotiations/{negotiation_id}")

    # ── Transfer ────────────────────────────────────────────────

    def initiate_transfer(self, contract_id: str, asset_id: str,
                          provider_protocol_url: str,
                          counter_party_id: str,
                          transfer_type: str = "HttpData-PULL") -> Dict[str, Any]:
        """Initiate data transfer after contract agreement."""
        payload = {
            "@context": MGMT_CONTEXT,
            "@type": "TransferRequest",
            "connectorId": counter_party_id,
            "counterPartyAddress": provider_protocol_url,
            "contractId": contract_id,
            "assetId": asset_id,
            "protocol": "dataspace-protocol-http",
            "transferType": transfer_type,
        }
        return self._post("/v3/transferprocesses", payload)

    def get_transfer(self, transfer_id: str) -> Dict[str, Any]:
        """Get the status of a transfer process."""
        return self._get(f"/v3/transferprocesses/{transfer_id}")

    def get_edr(self, transfer_id: str) -> Dict[str, Any]:
        """Get Endpoint Data Reference for accessing transferred data."""
        return self._get(f"/v3/edrs/{transfer_id}/dataaddress")

    def fetch_data(self, transfer_id: str) -> Dict[str, Any]:
        """Fetch actual data using the EDR token from a completed transfer."""
        edr_result = self.get_edr(transfer_id)
        if edr_result["status"] != 200:
            return edr_result
        edr = json.loads(edr_result["body"])
        endpoint = edr.get("endpoint", "")
        token = edr.get("authorization", "")
        if not endpoint or not token:
            return {"status": 400, "body": "Missing endpoint or token in EDR"}
        r = requests.get(endpoint, headers={"Authorization": token})
        return {"status": r.status_code, "body": r.text}

    # ── Helpers ─────────────────────────────────────────────────

    def _post(self, path: str, payload: dict) -> Dict[str, Any]:
        r = requests.post(f"{self.management_url}{path}",
                          headers=self.headers, json=payload)
        return {"status": r.status_code, "body": r.text}

    def _get(self, path: str) -> Dict[str, Any]:
        r = requests.get(f"{self.management_url}{path}", headers=self.headers)
        return {"status": r.status_code, "body": r.text}


# ── Utility Functions ─────────────────────────────────────────────

def wait_for_state(check_fn, target_states: list, timeout: int = 60,
                   interval: int = 2, label: str = "") -> Optional[Dict]:
    """Poll until desired state is reached or error occurs."""
    start = time.time()
    last_state = ""
    while time.time() - start < timeout:
        result = check_fn()
        if result["status"] == 200:
            data = json.loads(result["body"])
            state = data.get("state", "")
            if state != last_state:
                if label:
                    print(f"  [{label}] state: {state}")
                last_state = state
            if state in target_states:
                return data
            if state in ["TERMINATED", "ERROR", "TERMINATING"]:
                print(f"  ✗ Process ended: {state}")
                return None
        time.sleep(interval)
    print(f"  ✗ Timeout after {timeout}s (last state: {last_state})")
    return None


def negotiate_and_transfer(consumer: EDCClient, provider_node: dict,
                           asset_id: str, offer_id: str, policy: dict,
                           timeout: int = 60) -> Optional[Dict]:
    """Execute complete negotiation→transfer→EDR flow. Returns EDR dict or None."""
    # Step 1: Negotiate
    r = consumer.initiate_negotiation(
        provider_protocol_url=provider_node["protocol_url"],
        counter_party_id=provider_node["did"],
        offer_id=offer_id, asset_id=asset_id, policy=policy,
    )
    if r["status"] not in [200, 201]:
        print(f"  ✗ Negotiation failed: {r['body'][:200]}")
        return None
    neg_id = json.loads(r["body"]).get("@id")
    print(f"  Negotiation ID: {neg_id}")

    # Step 2: Wait for FINALIZED
    final = wait_for_state(
        lambda: consumer.get_negotiation(neg_id),
        ["FINALIZED"], timeout=timeout, label="negotiation"
    )
    if not final:
        return None
    contract_id = final.get("contractAgreementId")
    print(f"  ✓ Contract Agreement: {contract_id}")

    # Step 3: Transfer
    r = consumer.initiate_transfer(
        contract_id=contract_id, asset_id=asset_id,
        provider_protocol_url=provider_node["protocol_url"],
        counter_party_id=provider_node["did"],
    )
    if r["status"] not in [200, 201]:
        print(f"  ✗ Transfer failed: {r['body'][:200]}")
        return None
    tp_id = json.loads(r["body"]).get("@id")
    print(f"  Transfer ID: {tp_id}")

    # Step 4: Wait for STARTED
    wait_for_state(
        lambda: consumer.get_transfer(tp_id),
        ["STARTED", "COMPLETED"], timeout=timeout, label="transfer"
    )

    # Step 5: Get EDR
    time.sleep(2)
    edr_r = consumer.get_edr(tp_id)
    if edr_r["status"] == 200:
        edr = json.loads(edr_r["body"])
        print(f"  ✓ Data endpoint: {edr.get('endpoint', 'N/A')}")
        return {"contract_id": contract_id, "transfer_id": tp_id, "edr": edr}
    print(f"  ✗ EDR not available: {edr_r['body'][:200]}")
    return None
