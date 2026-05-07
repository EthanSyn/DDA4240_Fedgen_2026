#!/bin/bash
# MVD Seed Script - Creates participant contexts and adds STS client secrets to connectors
# Adapted for k8s ingress access (http://127.0.0.1/...)

set -e

API_KEY="c3VwZXItdXNlcg==.c3VwZXItc2VjcmV0LWtleQo="

# k8s ingress base URLs
CONSUMER_IH="http://127.0.0.1/consumer/cs"
PROVIDER_IH="http://127.0.0.1/provider/cs"
ISSUER_IH="http://127.0.0.1/issuer/cs"
CONSUMER_CP="http://127.0.0.1/consumer/cp"
PROVIDER_MF_CP="http://127.0.0.1/provider-manufacturing/cp"
PROVIDER_QNA_CP="http://127.0.0.1/provider-qna/cp"
PROVIDER_CATALOG_CP="http://127.0.0.1/provider-catalog-server/cp"
ISSUER_ADMIN="http://127.0.0.1/issuer/ad"

echo "============================================"
echo "  MVD Seed Script (k8s ingress)"
echo "============================================"

###############################################
# Step 0: Wait for control planes to be ready
###############################################
echo ""
echo "=== Waiting for Control Planes ==="
for url in "http://127.0.0.1/provider-manufacturing/health/api/check/readiness" "http://127.0.0.1/provider-qna/health/api/check/readiness" "http://127.0.0.1/consumer/health/api/check/readiness"; do
  printf "Waiting for %s ... " "$url"
  until curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null | grep -q "200"; do
    sleep 2
  done
  echo "UP!"
done

###############################################
# Step 1: Seed base data via Newman
###############################################
echo ""
echo "=== Seeding Asset/Policy/Contract Data ==="
cd /home/workplace/MinimumViableDataspace

for url in "$PROVIDER_MF_CP" "$PROVIDER_QNA_CP"; do
  echo "Seeding to connector $url ..."
  newman run \
    --folder "Seed" \
    --env-var "HOST=$url" \
    ./deployment/postman/MVD.postman_collection.json 2>/dev/null || echo "Newman seed failed for $url"
done

echo ""
echo "=== Seeding Catalog Server ==="
newman run \
  --folder "Seed Catalog Server" \
  --env-var "HOST=$PROVIDER_CATALOG_CP" \
  --env-var "PROVIDER_QNA_DSP_URL=http://provider-qna-controlplane:8082" \
  --env-var "PROVIDER_MF_DSP_URL=http://provider-manufacturing-controlplane:8082" \
  ./deployment/postman/MVD.postman_collection.json 2>/dev/null || echo "Newman catalog seed failed"

###############################################
# Step 2: Create Consumer Participant
# Uses publicKeyPem matching the hard-coded EC key from
# SecretsExtension so DID document matches signing key.
# privateKeyAlias=key-1 matches SecretsExtension vault alias.
###############################################
echo ""
echo "=== Creating Consumer Participant ==="

# Hard-coded EC public key from SecretsExtension (must match exactly)
EC_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE1l0Lof0a1yBc8KXhesAnoBvxZw5r\noYnkAXuqCYfNK3ex+hMWFuiXGUxHlzShAehR6wvwzV23bbC0tcFcVgW//A==\n-----END PUBLIC KEY-----"

DATA_CONSUMER=$(jq -n --arg pem "$EC_PUBLIC_KEY" '{
  "roles":[],
  "serviceEndpoints":[
    {"type": "CredentialService", "serviceEndpoint": "http://consumer-identityhub:7082/api/credentials/v1/participants/ZGlkOndlYjpjb25zdW1lci1pZGVudGl0eWh1YiUzQTcwODM6Y29uc3VtZXI=", "id": "consumer-credentialservice-1"},
    {"type": "ProtocolEndpoint", "serviceEndpoint": "http://consumer-controlplane:8082/api/dsp", "id": "consumer-dsp"}
  ],
  "active": true,
  "participantId": "did:web:consumer-identityhub%3A7083:consumer",
  "did": "did:web:consumer-identityhub%3A7083:consumer",
  "key":{"keyId": "did:web:consumer-identityhub%3A7083:consumer#key-1", "privateKeyAlias": "key-1", "publicKeyPem": $pem}
}')

CONSUMER_RESULT=$(curl -s --location "$CONSUMER_IH/api/identity/v1alpha/participants/" \
  --header 'Content-Type: application/json' \
  --header "x-api-key: $API_KEY" \
  --data "$DATA_CONSUMER")

echo "Consumer result: $CONSUMER_RESULT"
CONSUMER_SECRET=$(echo "$CONSUMER_RESULT" | jq -r '.clientSecret // empty')
if [ -z "$CONSUMER_SECRET" ]; then
  echo "ERROR: Failed to get consumer client secret"
  exit 1
fi
echo "Consumer secret: ${CONSUMER_SECRET:0:10}..."

###############################################
# Step 3: Create Provider Participant
###############################################
echo ""
echo "=== Creating Provider Participant ==="

DATA_PROVIDER=$(jq -n --arg pem "$EC_PUBLIC_KEY" '{
  "roles":[],
  "serviceEndpoints":[
    {"type": "CredentialService", "serviceEndpoint": "http://provider-identityhub:7082/api/credentials/v1/participants/ZGlkOndlYjpwcm92aWRlci1pZGVudGl0eWh1YiUzQTcwODM6cHJvdmlkZXI=", "id": "provider-credentialservice-1"},
    {"type": "ProtocolEndpoint", "serviceEndpoint": "http://provider-catalog-server-controlplane:8082/api/dsp", "id": "provider-dsp"}
  ],
  "active": true,
  "participantId": "did:web:provider-identityhub%3A7083:provider",
  "did": "did:web:provider-identityhub%3A7083:provider",
  "key":{"keyId": "did:web:provider-identityhub%3A7083:provider#key-1", "privateKeyAlias": "key-1", "publicKeyPem": $pem}
}')

PROVIDER_RESULT=$(curl -s --location "$PROVIDER_IH/api/identity/v1alpha/participants/" \
  --header 'Content-Type: application/json' \
  --header "x-api-key: $API_KEY" \
  --data "$DATA_PROVIDER")

echo "Provider result: $PROVIDER_RESULT"
PROVIDER_SECRET=$(echo "$PROVIDER_RESULT" | jq -r '.clientSecret // empty')
if [ -z "$PROVIDER_SECRET" ]; then
  echo "ERROR: Failed to get provider client secret"
  exit 1
fi
echo "Provider secret: ${PROVIDER_SECRET:0:10}..."

###############################################
# Step 3b: Store STS Client Secrets in Connector Vaults
# Remote STS client needs these to authenticate with IH STS
###############################################
echo ""
echo "=== Storing STS Client Secrets ==="

store_secret() {
  local CP_URL=$1
  local SECRET_ID=$2
  local SECRET_VALUE=$3
  local LABEL=$4
  SECRETS_DATA=$(jq -n --arg v "$SECRET_VALUE" '{
    "@context": {"edc": "https://w3id.org/edc/v0.0.1/ns/"},
    "@type": "https://w3id.org/edc/v0.0.1/ns/Secret",
    "@id": $ARGS.named.id,
    "https://w3id.org/edc/v0.0.1/ns/value": $v
  }' --arg id "$SECRET_ID")
  R=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$CP_URL/api/management/v3/secrets" \
    -H "x-api-key: password" -H "Content-Type: application/json" -d "$SECRETS_DATA")
  echo "  $LABEL: HTTP $R"
}

store_secret "$CONSUMER_CP" "did:web:consumer-identityhub%3A7083:consumer-sts-client-secret" "$CONSUMER_SECRET" "consumer-cp"
for cp_url in "$PROVIDER_CATALOG_CP" "$PROVIDER_MF_CP" "$PROVIDER_QNA_CP"; do
  store_secret "$cp_url" "did:web:provider-identityhub%3A7083:provider-sts-client-secret" "$PROVIDER_SECRET" "$cp_url"
done

###############################################
# Step 4: Activate Participants
# Participants start in CREATED state; must be
# activated so DID documents are published.
###############################################
echo ""
echo "=== Activating Participants ==="

CONSUMER_B64=$(echo -n "did:web:consumer-identityhub%3A7083:consumer" | base64 -w0)
PROVIDER_B64=$(echo -n "did:web:provider-identityhub%3A7083:provider" | base64 -w0)

echo -n "Activating consumer... "
R=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$CONSUMER_IH/api/identity/v1alpha/participants/${CONSUMER_B64}/state?isActive=true" -H "x-api-key: $API_KEY")
echo "HTTP $R"

echo -n "Activating provider... "
R=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$PROVIDER_IH/api/identity/v1alpha/participants/${PROVIDER_B64}/state?isActive=true" -H "x-api-key: $API_KEY")
echo "HTTP $R"

# Wait for DID documents to be published
sleep 2

# Verify DID documents are resolvable
echo -n "Consumer DID: "
kubectl exec -n mvd deployment/consumer-identityhub -- curl -s -o /dev/null -w "%{http_code}" http://localhost:7083/consumer/did.json 2>/dev/null
echo ""
echo -n "Provider DID: "
kubectl exec -n mvd deployment/provider-identityhub -- curl -s -o /dev/null -w "%{http_code}" http://localhost:7083/provider/did.json 2>/dev/null
echo ""

###############################################
# Step 5: Create Issuer Participant
###############################################
echo ""
echo "=== Creating Issuer Participant ==="
DATA_ISSUER='{
  "roles":["admin"],
  "serviceEndpoints":[
    {"type": "IssuerService", "serviceEndpoint": "http://dataspace-issuer-service:10012/api/issuance/v1alpha/participants/ZGlkOndlYjpkYXRhc3BhY2UtaXNzdWVyLXNlcnZpY2UlM0ExMDAxNjppc3N1ZXI=", "id": "issuer-service-1"}
  ],
  "active": true,
  "participantId": "did:web:dataspace-issuer-service%3A10016:issuer",
  "did": "did:web:dataspace-issuer-service%3A10016:issuer",
  "key":{"keyId": "did:web:dataspace-issuer-service%3A10016:issuer#key-1", "privateKeyAlias": "key-1", "keyGeneratorParams":{"algorithm": "EdDSA"}}
}'

curl -s --location "$ISSUER_IH/api/identity/v1alpha/participants/" \
  --header 'Content-Type: application/json' \
  --data "$DATA_ISSUER"
echo ""

###############################################
# Step 6: Seed Issuer data
###############################################
echo ""
echo "=== Seeding Issuer ==="
cd /home/workplace/MinimumViableDataspace
newman run \
  --folder "Seed Issuer SQL" \
  --env-var "ISSUER_ADMIN_URL=$ISSUER_ADMIN" \
  --env-var "CONSUMER_ID=did:web:consumer-identityhub%3A7083:consumer" \
  --env-var "CONSUMER_NAME=MVD Consumer Participant" \
  --env-var "PROVIDER_ID=did:web:provider-identityhub%3A7083:provider" \
  --env-var "PROVIDER_NAME=MVD Provider Participant" \
  ./deployment/postman/MVD.postman_collection.json 2>/dev/null || echo "Newman issuer seed failed"

echo ""
echo "============================================"
echo "  Seed Complete!"
echo "============================================"
