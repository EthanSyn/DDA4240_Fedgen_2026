#!/usr/bin/env python3
"""
FedGen Demo: Node C (AI Lab) requests data from Node A (Legal Archives)

This script demonstrates the complete data transfer workflow:
1. Node A registers legal dataset as an asset
2. Node A creates access policy and contract definition
3. Node C queries the catalog to discover available assets
4. Node C negotiates a contract with Node A
5. Node C initiates data transfer
6. Node C retrieves the data using EDR (Endpoint Data Reference)
"""

import json
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.fedgen_client import EDCClient, wait_for_state

# Endpoint configurations (using MVD k8s ingress paths)
NODE_A_MANAGEMENT = "http://localhost/provider-manufacturing/cp/api/management"
NODE_A_PROTOCOL = "http://provider-manufacturing-controlplane:8082/api/dsp"  # Internal k8s URL
NODE_C_MANAGEMENT = "http://localhost/consumer/cp/api/management"

# Asset configuration
ASSET_ID = "legal-archives-dataset-001"
POLICY_ID = "legal-data-policy-001"
CONTRACT_DEF_ID = "legal-contract-def-001"

def print_section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_result(name: str, result: dict):
    status = "✓" if result["status"] in [200, 201, 204] else "✗"
    print(f"{status} {name}: Status {result['status']}")
    if result["status"] not in [200, 201, 204]:
        print(f"  Response: {result['body'][:200]}...")

def main():
    print_section("FedGen Demo: C → A Data Transfer")
    print("Node A: Legal Archives (Data Provider)")
    print("Node C: AI Lab (Data Consumer)")
    print(f"Asset: {ASSET_ID}")
    
    # Initialize clients
    node_a = EDCClient(NODE_A_MANAGEMENT)
    node_c = EDCClient(NODE_C_MANAGEMENT)
    
    # ========================================
    # STEP 1: Node A registers the legal dataset as an asset
    # ========================================
    print_section("Step 1: Node A - Register Legal Dataset Asset")
    
    result = node_a.create_asset(
        asset_id=ASSET_ID,
        name="Legal Archives Training Dataset",
        description="High-quality legal texts for AI model training. Includes contract law, IP law, and data privacy regulations.",
        base_url="http://dataspace-issuer:80",
        data_path="/.well-known/did.json"  # Using existing endpoint as demo data source
    )
    print_result("Create Asset", result)
    
    # ========================================
    # STEP 2: Node A creates access policy
    # ========================================
    print_section("Step 2: Node A - Create Access Policy")
    
    # Policy: Allow use for AI training purposes
    permissions = [{
        "action": "use",
        "constraint": [{
            "leftOperand": "purpose",
            "operator": "eq",
            "rightOperand": "ai-training"
        }]
    }]
    
    result = node_a.create_policy(POLICY_ID, permissions)
    print_result("Create Policy", result)
    
    # ========================================
    # STEP 3: Node A creates contract definition
    # ========================================
    print_section("Step 3: Node A - Create Contract Definition")
    
    result = node_a.create_contract_definition(CONTRACT_DEF_ID, POLICY_ID, ASSET_ID)
    print_result("Create Contract Definition", result)
    
    # ========================================
    # STEP 4: Node C queries the catalog
    # ========================================
    print_section("Step 4: Node C - Query Catalog from Node A")
    
    result = node_c.get_catalog(NODE_A_PROTOCOL)
    print_result("Query Catalog", result)
    
    offer_id = None
    policy = None
    if result["status"] == 200:
        catalog = json.loads(result["body"])
        datasets = catalog.get("dcat:dataset", [])
        if isinstance(datasets, dict):
            datasets = [datasets]
        print(f"\n  Found {len(datasets)} dataset(s) in catalog")
        
        # Find our legal dataset
        offer_id = None
        policy = None
        for ds in datasets:
            if ds.get("@id") == ASSET_ID or ds.get("edc:id") == ASSET_ID:
                print(f"  ✓ Found target asset: {ASSET_ID}")
                offers = ds.get("odrl:hasPolicy", [])
                if isinstance(offers, dict):
                    offers = [offers]
                if offers:
                    offer_id = offers[0].get("@id")
                    policy = {
                        "permission": offers[0].get("odrl:permission", []),
                        "prohibition": offers[0].get("odrl:prohibition", []),
                        "obligation": offers[0].get("odrl:obligation", [])
                    }
                    print(f"  ✓ Found offer: {offer_id}")
                break
    
    if not offer_id:
        print("\n⚠ No matching offer found in catalog. Using default negotiation.")
        offer_id = f"{CONTRACT_DEF_ID}:{ASSET_ID}:default"
        policy = {"permission": [{"action": "use"}]}
    
    # ========================================
    # STEP 5: Node C initiates contract negotiation
    # ========================================
    print_section("Step 5: Node C - Initiate Contract Negotiation")
    
    result = node_c.initiate_negotiation(
        provider_url=NODE_A_PROTOCOL,
        offer_id=offer_id,
        asset_id=ASSET_ID,
        policy=policy
    )
    print_result("Initiate Negotiation", result)
    
    negotiation_id = None
    if result["status"] in [200, 201]:
        data = json.loads(result["body"])
        negotiation_id = data.get("@id", data.get("edc:id"))
        print(f"  Negotiation ID: {negotiation_id}")
    
    # ========================================
    # STEP 6: Wait for negotiation to complete
    # ========================================
    print_section("Step 6: Wait for Contract Agreement")
    
    contract_id = None
    if negotiation_id:
        print("  Waiting for negotiation to complete...")
        final_state = wait_for_state(
            lambda: node_c.get_negotiation_status(negotiation_id),
            target_states=["FINALIZED", "VERIFIED"],
            timeout=60
        )
        
        if final_state:
            contract_id = final_state.get("contractAgreementId", 
                                          final_state.get("edc:contractAgreementId"))
            print(f"  ✓ Contract Agreement ID: {contract_id}")
        else:
            print("  ✗ Negotiation did not complete successfully")
    
    # ========================================
    # STEP 7: Node C initiates data transfer
    # ========================================
    print_section("Step 7: Node C - Initiate Data Transfer")
    
    transfer_id = None
    if contract_id:
        result = node_c.initiate_transfer(
            contract_id=contract_id,
            asset_id=ASSET_ID,
            provider_url=NODE_A_PROTOCOL,
            destination={"type": "HttpProxy"}
        )
        print_result("Initiate Transfer", result)
        
        if result["status"] in [200, 201]:
            data = json.loads(result["body"])
            transfer_id = data.get("@id", data.get("edc:id"))
            print(f"  Transfer ID: {transfer_id}")
    
    # ========================================
    # STEP 8: Wait for transfer and get EDR
    # ========================================
    print_section("Step 8: Wait for Transfer & Get Data Access")
    
    if transfer_id:
        print("  Waiting for transfer to start...")
        final_state = wait_for_state(
            lambda: node_c.get_transfer_status(transfer_id),
            target_states=["STARTED", "COMPLETED"],
            timeout=60
        )
        
        if final_state:
            print(f"  ✓ Transfer state: {final_state.get('state', 'STARTED')}")
            
            # Get EDR for data access
            time.sleep(2)  # Wait for EDR to be available
            edr_result = node_c.get_edr(transfer_id)
            print_result("Get EDR", edr_result)
            
            if edr_result["status"] == 200:
                edr = json.loads(edr_result["body"])
                endpoint = edr.get("endpoint", edr.get("edc:endpoint", "N/A"))
                print(f"\n  ✓ Data Endpoint: {endpoint}")
                print("  ✓ Node C can now access the legal dataset from Node A!")
    
    # ========================================
    # Summary
    # ========================================
    print_section("Demo Summary")
    print("The FedGen data transfer demo has completed.")
    print("\nWorkflow executed:")
    print("  1. Node A (Legal Archives) registered legal dataset as asset")
    print("  2. Node A created access policy for AI training")
    print("  3. Node A created contract definition")
    print("  4. Node C (AI Lab) discovered asset via catalog query")
    print("  5. Node C negotiated contract with Node A")
    print("  6. Node C initiated data transfer")
    print("  7. Node C received EDR for secure data access")
    print("\nThis demonstrates sovereign data sharing in the FedGen ecosystem!")

if __name__ == "__main__":
    main()
