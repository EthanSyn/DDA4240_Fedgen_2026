"""
FedGen - EDC Connector Endpoints Configuration
Maps FedGen logical nodes to MVD connector endpoints in k8s.

Architecture mapping:
  Node A (Legal Archives)  →  provider-manufacturing connector
  Node B (News Syndicate)  →  provider-qna connector (provider) + consumer connector (consumer role)
  Node C (AI Lab)          →  consumer connector
  Node D (Federated Catalog) →  provider-catalog-server

Note: Node B and Node C share the consumer connector for consuming.
      In a full deployment, Node B would have its own consumer connector.
      Here, Node C is the primary consumer for the demo.
"""

# DIDs for DCP protocol
CONSUMER_DID = "did:web:consumer-identityhub%3A7083:consumer"
PROVIDER_DID = "did:web:provider-identityhub%3A7083:provider"

# Management API key
API_KEY = "password"

# Node A: Legal Archives (Data Provider) → provider-manufacturing
NODE_A = {
    "name": "Node A: Legal Archives",
    "role": "provider",
    "did": PROVIDER_DID,
    "management_url": "http://127.0.0.1/provider-manufacturing/cp/api/management",
    "protocol_url": "http://provider-manufacturing-controlplane:8082/api/dsp",  # k8s internal
}

# Node B-Prov: News Syndicate (Data Provider) → provider-qna
NODE_B_PROV = {
    "name": "Node B-Prov: News Syndicate (Provider)",
    "role": "provider",
    "did": PROVIDER_DID,
    "management_url": "http://127.0.0.1/provider-qna/cp/api/management",
    "protocol_url": "http://provider-qna-controlplane:8082/api/dsp",  # k8s internal
}

# Node B-Cons: News Syndicate (Consumer role) → reuses consumer connector
NODE_B_CONS = {
    "name": "Node B-Cons: News Syndicate (Consumer)",
    "role": "consumer",
    "did": CONSUMER_DID,
    "management_url": "http://127.0.0.1/consumer/cp/api/management",
    "protocol_url": "http://consumer-controlplane:8082/api/dsp",  # k8s internal
}

# Node C: AI Lab (Data Consumer) → consumer
NODE_C = {
    "name": "Node C: AI Lab",
    "role": "consumer",
    "did": CONSUMER_DID,
    "management_url": "http://127.0.0.1/consumer/cp/api/management",
    "protocol_url": "http://consumer-controlplane:8082/api/dsp",  # k8s internal
}

# Node D: Federated Catalog → catalog-server
NODE_D = {
    "name": "Node D: Federated Catalog",
    "role": "catalog",
    "did": PROVIDER_DID,
    "management_url": "http://127.0.0.1/provider-catalog-server/cp/api/management",
    "catalog_url": "http://127.0.0.1/provider-catalog-server/cp/api/management",
}

# Data backend (inside k8s)
DATA_BACKEND = {
    "legal_url": "http://fedgen-data-backend:8080/legal/documents",
    "news_url": "http://fedgen-data-backend:8080/news/articles",
    "legal_live_url": "http://fedgen-data-backend:8080/legal/live",
    "news_live_url": "http://fedgen-data-backend:8080/news/live",
    "wikidata_url": "http://fedgen-data-backend:8080/thirdparty/wikidata",
}
