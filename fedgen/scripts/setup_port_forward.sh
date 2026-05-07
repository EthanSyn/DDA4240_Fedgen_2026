#!/bin/bash
# FedGen - Setup port forwarding for EDC connector access
# Run this script before executing the demo

echo "Setting up port forwarding for FedGen demo..."

# Kill any existing port-forward processes
pkill -f "kubectl port-forward" 2>/dev/null

# Wait for cleanup
sleep 2

echo "Port forwarding is handled by Ingress Controller."
echo "Endpoints available at http://localhost:"
echo "  - Provider Manufacturing: /provider/manufacturing/*"
echo "  - Consumer: /consumer/*"
echo "  - Catalog Server: /provider/catalog/*"
echo ""
echo "Ready to run the demo!"
