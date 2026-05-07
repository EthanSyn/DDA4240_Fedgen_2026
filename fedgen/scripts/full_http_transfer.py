#!/usr/bin/env python3
"""
FedGen: Complete HTTP Data Transfer Demo
Node C (AI Lab) negotiates contract and pulls data from Node A (Legal Archives)
"""

import requests
import json
import time
import sys

# Configuration - using port-forwarded endpoints
NODE_A_MGMT = "http://127.0.0.1:8181/api/management"
NODE_C_MGMT = "http://127.0.0.1:8081/api/management"
NODE_A_DSP = "http://provider-manufacturing-controlplane:8082/api/dsp"
PROVIDER_ID = "did:web:provider-identityhub%3A7083:provider"
ASSET_ID = "legal-http-transfer-001"

HEADERS = {"Content-Type": "application/json", "X-Api-Key": "password"}

def log(step, msg):
    print(f"[{step}] {msg}")

def api_call(method, url, data=None):
    if method == "POST":
        r = requests.post(url, headers=HEADERS, json=data)
    else:
        r = requests.get(url, headers=HEADERS)
    return r.status_code, r.text

def main():
    print("=" * 60)
    print("  FedGen: Complete HTTP Data Transfer")
    print("=" * 60)
    print(f"\nNode A (Provider): provider-manufacturing")
    print(f"Node C (Consumer): consumer")
    print(f"Asset: {ASSET_ID}\n")

    # Step 1: Create Asset on Node A
    print("=" * 60)
    print("  Step 1: Node A - Register Asset")
    print("=" * 60)
    
    asset_payload = {
        "@context": ["https://w3id.org/edc/connector/management/v0.0.1"],
        "@id": ASSET_ID,
        "@type": "Asset",
        "properties": {"description": "FedGen Legal Archives for AI Training"},
        "dataAddress": {
            "@type": "DataAddress",
            "type": "HttpData",
            "baseUrl": "https://jsonplaceholder.typicode.com/posts",
            "proxyPath": "true",
            "proxyQueryParams": "true"
        }
    }
    status, body = api_call("POST", f"{NODE_A_MGMT}/v3/assets", asset_payload)
    log("Asset", f"Status: {status}")
    
    # Step 2: Create Policy
    policy_payload = {
        "@context": ["https://w3id.org/edc/connector/management/v0.0.1"],
        "@type": "PolicyDefinition",
        "@id": "fedgen-http-policy",
        "policy": {
            "@type": "Set",
            "permission": [{"action": "use", "constraint": {"leftOperand": "MembershipCredential", "operator": "eq", "rightOperand": "active"}}]
        }
    }
    status, body = api_call("POST", f"{NODE_A_MGMT}/v3/policydefinitions", policy_payload)
    log("Policy", f"Status: {status}")
    
    # Step 3: Create Contract Definition
    contract_def = {
        "@context": ["https://w3id.org/edc/connector/management/v0.0.1"],
        "@type": "ContractDefinition",
        "@id": "fedgen-http-contract",
        "accessPolicyId": "fedgen-http-policy",
        "contractPolicyId": "fedgen-http-policy",
        "assetsSelector": {"operandLeft": "https://w3id.org/edc/v0.0.1/ns/id", "operator": "=", "operandRight": ASSET_ID}
    }
    status, body = api_call("POST", f"{NODE_A_MGMT}/v3/contractdefinitions", contract_def)
    log("Contract Def", f"Status: {status}")

    # Step 4: Query Catalog from Node C
    print("\n" + "=" * 60)
    print("  Step 2: Node C - Query Catalog")
    print("=" * 60)
    
    catalog_req = {
        "@context": ["https://w3id.org/edc/connector/management/v0.0.1"],
        "counterPartyAddress": NODE_A_DSP,
        "counterPartyId": PROVIDER_ID,
        "protocol": "dataspace-protocol-http"
    }
    status, body = api_call("POST", f"{NODE_C_MGMT}/v3/catalog/request", catalog_req)
    log("Catalog", f"Status: {status}")
    
    if status != 200:
        print(f"Catalog query failed: {body[:200]}")
        return
    
    catalog = json.loads(body)
    datasets = catalog.get("dcat:dataset", [])
    if isinstance(datasets, dict):
        datasets = [datasets]
    
    offer_id = None
    for ds in datasets:
        if ds.get("@id") == ASSET_ID:
            policy = ds.get("odrl:hasPolicy")
            if policy:
                offer_id = policy.get("@id")
                log("Found", f"Asset: {ASSET_ID}, Offer: {offer_id[:50]}...")
                break
    
    if not offer_id:
        print("No offer found for asset")
        return

    # Step 5: Initiate Contract Negotiation
    print("\n" + "=" * 60)
    print("  Step 3: Node C - Contract Negotiation")
    print("=" * 60)
    
    negotiation_req = {
        "@context": ["https://w3id.org/edc/connector/management/v0.0.1"],
        "@type": "ContractRequest",
        "counterPartyAddress": NODE_A_DSP,
        "protocol": "dataspace-protocol-http",
        "policy": {
            "@context": "http://www.w3.org/ns/odrl.jsonld",
            "@type": "Offer",
            "@id": offer_id,
            "assigner": PROVIDER_ID,
            "target": ASSET_ID,
            "permission": [{"action": "use", "constraint": {"leftOperand": "MembershipCredential", "operator": "eq", "rightOperand": "active"}}]
        }
    }
    status, body = api_call("POST", f"{NODE_C_MGMT}/v3/contractnegotiations", negotiation_req)
    log("Negotiation", f"Status: {status}")
    
    if status not in [200, 201]:
        print(f"Negotiation failed: {body[:300]}")
        return
    
    neg_data = json.loads(body)
    negotiation_id = neg_data.get("@id")
    log("Negotiation ID", negotiation_id)
    
    # Wait for negotiation to complete
    print("\nWaiting for negotiation to finalize...")
    contract_agreement_id = None
    for i in range(30):
        time.sleep(2)
        status, body = api_call("GET", f"{NODE_C_MGMT}/v3/contractnegotiations/{negotiation_id}")
        if status == 200:
            data = json.loads(body)
            state = data.get("state", "")
            log("State", state)
            if state == "FINALIZED":
                contract_agreement_id = data.get("contractAgreementId")
                log("Contract Agreement", contract_agreement_id)
                break
            elif state in ["TERMINATED", "ERROR"]:
                print(f"Negotiation ended with state: {state}")
                return
    
    if not contract_agreement_id:
        print("Negotiation did not complete in time")
        return

    # Step 6: Initiate Transfer
    print("\n" + "=" * 60)
    print("  Step 4: Node C - Initiate HTTP Transfer")
    print("=" * 60)
    
    transfer_req = {
        "@context": ["https://w3id.org/edc/connector/management/v0.0.1"],
        "@type": "TransferRequest",
        "connectorId": PROVIDER_ID,
        "counterPartyAddress": NODE_A_DSP,
        "contractId": contract_agreement_id,
        "assetId": ASSET_ID,
        "protocol": "dataspace-protocol-http",
        "transferType": "HttpData-PULL"
    }
    status, body = api_call("POST", f"{NODE_C_MGMT}/v3/transferprocesses", transfer_req)
    log("Transfer", f"Status: {status}")
    
    if status not in [200, 201]:
        print(f"Transfer initiation failed: {body[:300]}")
        return
    
    transfer_data = json.loads(body)
    transfer_id = transfer_data.get("@id")
    log("Transfer ID", transfer_id)
    
    # Wait for transfer to start
    print("\nWaiting for transfer to start...")
    for i in range(20):
        time.sleep(2)
        status, body = api_call("GET", f"{NODE_C_MGMT}/v3/transferprocesses/{transfer_id}")
        if status == 200:
            data = json.loads(body)
            state = data.get("state", "")
            log("State", state)
            if state == "STARTED":
                break

    # Step 7: Get EDR and Pull Data
    print("\n" + "=" * 60)
    print("  Step 5: Node C - Get EDR and Pull Data via HTTP")
    print("=" * 60)
    
    time.sleep(2)
    status, body = api_call("GET", f"{NODE_C_MGMT}/v3/edrs/{transfer_id}/dataaddress")
    log("EDR", f"Status: {status}")
    
    if status != 200:
        print(f"EDR retrieval failed: {body[:200]}")
        return
    
    edr = json.loads(body)
    endpoint = edr.get("endpoint")
    auth_token = edr.get("authorization")
    
    log("Endpoint", endpoint)
    log("Auth", "Token received" if auth_token else "No token")
    
    # Pull actual data via HTTP
    # Replace k8s internal DNS with localhost (requires port-forward)
    endpoint = endpoint.replace("provider-manufacturing-dataplane:11002", "localhost:11002")
    endpoint = endpoint.replace("consumer-dataplane:11002", "localhost:11003")
    
    print(f"\nPulling data via HTTP from: {endpoint}")
    data_headers = {"Authorization": auth_token} if auth_token else {}
    r = requests.get(endpoint, headers=data_headers)
    
    print("\n" + "=" * 60)
    print("  HTTP DATA RECEIVED!")
    print("=" * 60)
    print(f"Status: {r.status_code}")
    print(f"Content-Length: {len(r.text)} bytes")
    print(f"\nFirst 500 chars of data:\n{r.text[:500]}...")
    
    print("\n" + "=" * 60)
    print("  ✓ Complete HTTP Transfer Success!")
    print("=" * 60)
    print("\nSummary:")
    print("  1. Node A registered legal dataset")
    print("  2. Node C discovered asset via catalog")
    print("  3. Node C negotiated contract with Node A")
    print("  4. Node C initiated HTTP-PULL transfer")
    print("  5. Node C got EDR (Endpoint Data Reference)")
    print("  6. Node C pulled data via HTTP using EDR token")

if __name__ == "__main__":
    main()
