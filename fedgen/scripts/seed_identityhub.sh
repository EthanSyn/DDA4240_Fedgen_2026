#!/bin/bash
# Simplified seed script using port-forwarded endpoints

API_KEY="c3VwZXItdXNlcg==.c3VwZXItc2VjcmV0LWtleQo="

echo "=== Seeding Consumer IdentityHub ==="
# Consumer participant context
DATA_CONSUMER='{
  "roles":[],
  "serviceEndpoints":[
    {
      "type": "CredentialService",
      "serviceEndpoint": "http://consumer-identityhub:7082/api/credentials/v1/participants/ZGlkOndlYjpjb25zdW1lci1pZGVudGl0eWh1YiUzQTcwODM6Y29uc3VtZXI=",
      "id": "consumer-credentialservice-1"
    },
    {
      "type": "ProtocolEndpoint", 
      "serviceEndpoint": "http://consumer-controlplane:8082/api/dsp",
      "id": "consumer-dsp"
    }
  ],
  "active": true,
  "participantId": "did:web:consumer-identityhub%3A7083:consumer",
  "did": "did:web:consumer-identityhub%3A7083:consumer",
  "key":{
    "keyId": "did:web:consumer-identityhub%3A7083:consumer#key-1",
    "privateKeyAlias": "did:web:consumer-identityhub%3A7083:consumer#key-1",
    "keyGeneratorParams":{
      "algorithm": "EC"
    }
  }
}'

curl -s --location "http://127.0.0.1:7083/api/identity/v1alpha/participants/" \
  --header 'Content-Type: application/json' \
  --header "x-api-key: $API_KEY" \
  --data "$DATA_CONSUMER"
echo ""

echo "=== Seeding Provider IdentityHub ==="
# Provider participant context
DATA_PROVIDER='{
  "roles":[],
  "serviceEndpoints":[
    {
      "type": "CredentialService",
      "serviceEndpoint": "http://provider-identityhub:7082/api/credentials/v1/participants/ZGlkOndlYjpwcm92aWRlci1pZGVudGl0eWh1YiUzQTcwODM6cHJvdmlkZXI=",
      "id": "provider-credentialservice-1"
    },
    {
      "type": "ProtocolEndpoint",
      "serviceEndpoint": "http://provider-catalog-server-controlplane:8082/api/dsp", 
      "id": "provider-dsp"
    }
  ],
  "active": true,
  "participantId": "did:web:provider-identityhub%3A7083:provider",
  "did": "did:web:provider-identityhub%3A7083:provider",
  "key":{
    "keyId": "did:web:provider-identityhub%3A7083:provider#key-1",
    "privateKeyAlias": "did:web:provider-identityhub%3A7083:provider#key-1",
    "keyGeneratorParams":{
      "algorithm": "EC"
    }
  }
}'

curl -s --location "http://127.0.0.1:7093/api/identity/v1alpha/participants/" \
  --header 'Content-Type: application/json' \
  --header "x-api-key: $API_KEY" \
  --data "$DATA_PROVIDER"
echo ""

echo "=== Seed Complete ==="
