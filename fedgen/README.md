# FedGen - Sovereign Dataspace for Decentralized AI Training Corpora

A decentralized dataspace ecosystem built on [Eclipse Dataspace Components (EDC)](https://projects.eclipse.org/projects/technology.edc) that demonstrates secure B2B data sharing for AI training. Data providers can monetize sensitive assets (legal archives, news corpora) without compromising sovereignty.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FedGen Ecosystem                      │
│                                                         │
│  ┌──────────────┐     ┌──────────────────────────────┐  │
│  │   Node A     │     │        Node B                │  │
│  │  Legal       │     │   News Syndicate             │  │
│  │  Archives    │     │  ┌────────┐  ┌────────────┐  │  │
│  │  (Provider)  │     │  │B-Prov  │  │B-Cons      │  │  │
│  └──────┬───────┘     │  │(Prov)  │  │(Consumer)  │  │  │
│         │             │  └───┬────┘  └────────────┘  │  │
│         │             └──────┼───────────────────────┘  │
│         │                    │                          │
│         ▼                    ▼                          │
│  ┌──────────────────────────────────────────┐           │
│  │          Node D: Federated Catalog       │           │
│  │     (Crawls & aggregates all catalogs)   │           │
│  └──────────────────────────────────────────┘           │
│                    ▲                                    │
│                    │ query                              │
│         ┌─────────┴────────┐                            │
│         │     Node C       │                            │
│         │    AI Lab        │                            │
│         │   (Consumer)     │                            │
│         └──────────────────┘                            │
└─────────────────────────────────────────────────────────┘
```

| Node | Role | Description | MVD Connector |
|------|------|-------------|---------------|
| **A** | Provider | Legal archives (Pile-of-Law) | provider-manufacturing |
| **B-Prov** | Provider | News corpus (CNN/DailyMail) | provider-qna |
| **C** | Consumer | AI Lab - acquires training data | consumer |
| **D** | Catalog | Federated discovery service | catalog-server |

## Demo Scenarios

The demo runs three scenarios end-to-end:

1. **C → A**: AI Lab negotiates and transfers legal training data from Legal Archives
2. **C → B**: AI Lab negotiates and transfers news corpus from News Syndicate
3. **Federated Catalog**: Discovery of all datasets across the federation via Node D

Each scenario demonstrates:
- Asset registration with `HttpData` data addresses
- ODRL policy creation (MembershipCredential, DataAccess constraints)
- DCP-based contract negotiation with verifiable credentials
- `HttpData-PULL` transfer with EDR-based data access

## Quick Start

### Prerequisites

- Kubernetes cluster with `kubectl` configured
- Terraform
- Python 3.12+ with `requests`
- `newman` (Postman CLI)
- MVD jars built (see `MinimumViableDataspace/`)

### 1. Deploy Infrastructure

```bash
# Deploy MVD (connectors, identity hubs, etc.)
cd MinimumViableDataspace/deployment
terraform init && terraform apply -auto-approve

# Deploy FedGen data backend
cd ../../fedgen/deployment
terraform init && terraform apply -auto-approve
```

### 2. Seed the Environment

```bash
bash fedgen/scripts/seed_mvd.sh
```

This creates participants, stores STS secrets, activates DID documents, and seeds connector data.

### 3. Run the Demo

```bash
# Run all three scenarios
bash fedgen/run_demo.sh

# Or with seed included
bash fedgen/run_demo.sh --seed
```

## Project Structure

```
fedgen/
├── README.md
├── run_demo.sh                  # Main entry point
├── configs/
│   └── endpoints.py             # Node-to-connector mapping
├── data/
│   ├── legal_sample.json        # Pile-of-Law sample (3 documents)
│   └── news_sample.json         # CNN/DailyMail sample (4 articles)
├── data-backend/
│   ├── Dockerfile
│   └── server.py                # HTTP server for datasets
├── deployment/
│   ├── provider.tf              # Terraform provider config
│   └── data-backend.tf          # K8s deployment for data server
├── docs/
│   └── troubleshooting-403-unauthorized.md
├── scripts/
│   ├── fedgen_client.py         # EDC Management API client (DCP)
│   ├── fedgen_demo.py           # Comprehensive 3-scenario demo
│   └── seed_mvd.sh              # Environment seed script
└── requirements.txt
```

## Key Technical Details

### DCP Authentication Flow

```
Consumer CP ──SI Token──► Provider CP ──PresentationQuery──► Consumer IH
                                     ◄──VP (credentials)──┘
                           [verify + evaluate policy]
                ◄──FINALIZED──┘
```

### Policy Enforcement

- **MembershipCredential**: Required for catalog access (active membership)
- **DataAccess.level**: Obligation-based constraint for data processing rights
- Both enforced via ODRL using EDC's policy evaluation engine

### Datasets

- **Legal**: Simulates [Pile-of-Law](https://arxiv.org/abs/2207.00220) - contract law, IP law, data privacy
- **News**: Simulates [CNN/DailyMail](https://arxiv.org/abs/1704.04368) - tech news, policy, AI regulation

## Troubleshooting

See [troubleshooting-403-unauthorized.md](docs/troubleshooting-403-unauthorized.md) for detailed debug guide covering:
- InMemoryVault key alias conflicts
- DID document publishing issues
- Participant activation state machine
- STS client secret configuration
