#!/bin/bash
#
# FedGen Complete HTTP Transfer Demo
# Node C (AI Lab) negotiates and transfers data from Node A (Legal Archives)
#

set -e

COLLECTION="./postman/FedGen_FullTransfer.postman_collection.json"

echo "============================================================"
echo "  FedGen: Complete HTTP Data Transfer Demo"
echo "============================================================"
echo ""
echo "Node A: Legal Archives (Data Provider)"
echo "Node C: AI Lab (Data Consumer)"
echo ""

# Step 1: Setup
echo "============================================================"
echo "  Step 1: Node A - Setup Legal Archives"
echo "============================================================"
newman run --folder "1-Setup" "$COLLECTION" || true

# Step 2: Catalog Discovery
echo ""
echo "============================================================"
echo "  Step 2: Node C - Query Catalog"
echo "============================================================"
newman run --folder "2-Catalog" "$COLLECTION" --export-collection "$COLLECTION"

# Step 3: Contract Negotiation
echo ""
echo "============================================================"
echo "  Step 3: Node C - Initiate Contract Negotiation"
echo "============================================================"
newman run --folder "3-Negotiate" --iteration-count 1 "$COLLECTION" --export-collection "$COLLECTION"

# Wait for negotiation to complete
echo ""
echo "Waiting for contract negotiation to finalize..."
sleep 5

# Check negotiation status again
newman run --folder "3-Negotiate" --iteration-count 1 "$COLLECTION" --export-collection "$COLLECTION"

# Step 4: Transfer Process
echo ""
echo "============================================================"
echo "  Step 4: Node C - Initiate Data Transfer"
echo "============================================================"
newman run --folder "4-Transfer" --iteration-count 1 "$COLLECTION" --export-collection "$COLLECTION"

# Wait for transfer to start
echo ""
echo "Waiting for transfer to start..."
sleep 3

# Check transfer status
newman run --folder "4-Transfer" --iteration-count 1 "$COLLECTION" --export-collection "$COLLECTION"

# Step 5: Get Data
echo ""
echo "============================================================"
echo "  Step 5: Node C - Get EDR and Pull Data"
echo "============================================================"
newman run --folder "5-GetData" "$COLLECTION" --export-collection "$COLLECTION"

echo ""
echo "============================================================"
echo "  HTTP Transfer Demo Complete!"
echo "============================================================"
echo ""
echo "Flow completed:"
echo "  1. Node A registered legal dataset asset"
echo "  2. Node C discovered asset in catalog"
echo "  3. Node C negotiated contract with Node A"
echo "  4. Node C initiated HTTP data transfer"
echo "  5. Node C retrieved EDR and pulled data via HTTP"
echo ""
