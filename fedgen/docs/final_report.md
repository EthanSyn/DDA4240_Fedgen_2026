# FedGen: A Sovereign Dataspace for Decentralized AI Training Corpora

**Course:** CSC4240/CSC6203 Data Spaces  
**Author:** Yinuo Sheng (122090461)  
**Date:** May 2026  
**Repository:** https://github.com/EthanSyn/DDA4240_Fedgen_2026

---

## Abstract

This report presents FedGen, a decentralized dataspace ecosystem built upon the Eclipse Dataspace Components (EDC) framework. FedGen demonstrates secure, policy-enforced business-to-business data sharing for AI training corpora. The system implements a federated architecture with four logical participants, integrates real-world external data sources (OpenAlex, Hacker News, Wikidata), and showcases a federated learning pipeline where collaborative AI model training occurs without centralizing raw data. All data exchanges are governed by ODRL policies and authenticated via the Decentralized Claims Protocol (DCP) with verifiable credentials.

---

## Table of Contents

1. [Introduction and Motivation](#1-introduction-and-motivation)
2. [Related Work](#2-related-work)
3. [System Architecture](#3-system-architecture)
4. [Component Design](#4-component-design)
5. [Data Sources](#5-data-sources)
6. [Implementation Details](#6-implementation-details)
7. [Demonstration Scenarios](#7-demonstration-scenarios)
8. [Proof of Functionality](#8-proof-of-functionality)
9. [Discussion](#9-discussion)
10. [Conclusions and Future Work](#10-conclusions-and-future-work)
11. [References](#11-references)

---

## 1. Introduction and Motivation

The rapid advancement of Large Language Models (LLMs) has created a critical demand for high-quality, domain-specific training data. However, data sovereignty concerns, copyright regulations, and privacy laws (e.g., GDPR) prevent enterprises from freely sharing proprietary datasets in centralized data lakes. Organizations holding valuable training corpora — such as legal archives, news publishers, or medical record holders — need mechanisms to monetize and share their data while retaining full control over access, usage, and provenance.

**Data spaces** address this challenge by creating federated, decentralized ecosystems where data providers and consumers interact through standardized protocols, with policy-enforced contracts governing every data exchange. The Eclipse Dataspace Components (EDC) project provides an open-source reference implementation of the Dataspace Protocol, enabling sovereign data sharing with identity verification, policy evaluation, and automated contract negotiation.

FedGen extends the EDC Minimum Viable Dataspace (MVD) to demonstrate a realistic ecosystem where:

- **Data providers** (legal archives, news syndicates) register and govern access to their training corpora.
- **Data consumers** (AI labs) discover, negotiate, and acquire data through standardized contracts.
- **Federated catalogs** enable cross-provider discovery without centralized metadata stores.
- **Third-party databases** (e.g., Wikidata) are accessed through the same sovereign governance framework.
- **Federated learning** enables collaborative AI model training where raw data never leaves the provider's premises.

---

## 2. Related Work

### 2.1 Dataspace Initiatives

Several large-scale dataspace initiatives informed the design of FedGen:

- **Gaia-X** [1]: A European initiative to create a federated data infrastructure with self-sovereign identity and policy enforcement. Gaia-X defines trust frameworks and federated catalogs similar to FedGen's Node D.
- **International Data Spaces (IDS)** [2]: The IDS Reference Architecture Model defines data connectors, brokers, and identity providers — concepts that directly map to EDC's connector, catalog server, and identity hub.
- **Catena-X** [3]: An automotive industry dataspace built on EDC, demonstrating real-world B2B data sharing with ODRL policies. FedGen applies similar patterns to the AI training domain.

### 2.2 Eclipse Dataspace Components (EDC)

The EDC project [4] provides the core runtime for dataspace participants, including:

- **Management API**: RESTful API for asset, policy, and contract management.
- **Dataspace Protocol (DSP)**: Standard protocol for catalog queries, contract negotiation, and data transfer.
- **Decentralized Claims Protocol (DCP)**: Identity verification using DIDs and Verifiable Credentials.
- **ODRL Policy Engine**: Evaluation of Open Digital Rights Language policies for access and usage control.

The EDC Minimum Viable Dataspace (MVD) [5] provides a reference deployment with Kubernetes, Terraform, and Identity Hubs. FedGen extends MVD with custom data backends, additional scenarios, and a federated learning layer.

### 2.3 Federated Learning in Data Spaces

Federated learning [6] is a machine learning paradigm where models are trained across decentralized data holders without exchanging raw data. McMahan et al. proposed FedAvg (Federated Averaging), where each participant trains locally and only shares model weight updates. Combining federated learning with data spaces provides a natural architecture: the dataspace governs who participates and under what terms, while FL ensures raw data sovereignty during training.

---

## 3. System Architecture

### 3.1 High-Level Topology

FedGen consists of four logical participants deployed as a federated network within a Kubernetes cluster:

```
┌─────────────────────────────────────────────────────────────────┐
│                       FedGen Ecosystem                          │
│                                                                 │
│  ┌──────────────────┐         ┌──────────────────────────────┐  │
│  │     Node A        │         │          Node B               │  │
│  │  Legal Archives   │         │    News Syndicate             │  │
│  │  (Provider)       │         │  ┌──────────┐ ┌────────────┐ │  │
│  │  + Wikidata Proxy │         │  │ B-Prov   │ │ B-Cons     │ │  │
│  └────────┬─────────┘         │  │(Provider)│ │(Consumer)  │ │  │
│           │                    │  └────┬─────┘ └────────────┘ │  │
│           │                    └───────┼──────────────────────┘  │
│           │                            │                         │
│           ▼                            ▼                         │
│  ┌─────────────────────────────────────────────┐                │
│  │        Node D: Federated Catalog             │                │
│  │   (Crawls & aggregates all provider catalogs)│                │
│  └─────────────────────────────────────────────┘                │
│                       ▲                                          │
│                       │ query                                    │
│           ┌───────────┴───────────┐                              │
│           │       Node C          │                              │
│           │      AI Lab           │                              │
│           │   (Consumer +         │                              │
│           │    FL Coordinator)    │                              │
│           └───────────────────────┘                              │
│                                                                  │
│  ┌──────────────────────────────────────────────┐               │
│  │   FedGen Data Backend (Python HTTP server)   │               │
│  │   /legal/documents  /news/articles           │               │
│  │   /legal/live       /news/live               │               │
│  │   /thirdparty/wikidata                       │               │
│  └──────────────────────────────────────────────┘               │
└──────────────────────────────────────────────────────────────────┘
```

**Figure 1.** FedGen ecosystem topology with four logical nodes, a custom data backend, and external API integrations.

### 3.2 Node Roles

| Node | Role | Description | MVD Connector |
|------|------|-------------|---------------|
| **A** | Provider | Legal archives (Pile-of-Law), Wikidata gateway | `provider-manufacturing` |
| **B-Prov** | Provider | News corpus (CNN/DailyMail, Hacker News) | `provider-qna` |
| **B-Cons** | Consumer | News Syndicate consumer role (dual-role) | `consumer` (shared) |
| **C** | Consumer | AI Lab — acquires training data, FL coordinator | `consumer` |
| **D** | Catalog | Federated catalog — crawls all providers | `catalog-server` |

### 3.3 Dual-Role Participant Strategy

A key project requirement was the inclusion of entities acting as both data providers and consumers. While deploying a single EDC connector with dual identities involves significant IAM configuration overhead, FedGen adopts a pragmatic approach: **Node B** (the News Syndicate) is implemented as two distinct connector instances — one for providing (`B-Prov` on `provider-qna`) and one for consuming (`B-Cons` on the `consumer` connector). This is functionally equivalent to a single dual-role entity while avoiding complex identity management within a single connector.

---

## 4. Component Design

### 4.1 EDC Connector Infrastructure

Each connector instance comprises:

- **Control Plane**: Handles Management API, catalog queries, contract negotiations, and policy evaluation.
- **Data Plane**: Manages data transfer execution (HttpData-PULL) and Endpoint Data Reference (EDR) token generation.
- **Identity Hub**: Manages Decentralized Identifiers (DIDs) and Verifiable Credentials for DCP authentication.

All components are deployed in the `mvd` Kubernetes namespace via Terraform.

### 4.2 FedGen Data Backend

The custom data backend (`data-backend/server.py`) is a lightweight Python HTTP server deployed as a Kubernetes pod. It serves as the data source behind EDC assets:

| Route | Description | Source |
|-------|-------------|--------|
| `/legal/documents` | Static legal corpus sample | Local JSON file |
| `/news/articles` | Static news corpus sample | Local JSON file |
| `/legal/live` | Live academic papers on data privacy | OpenAlex API |
| `/news/live` | Live tech news stories | Hacker News Algolia API |
| `/thirdparty/wikidata` | Knowledge graph concepts (AI, privacy) | Wikidata SPARQL endpoint |

The backend implements:

- **API proxying with transformation**: External API responses are transformed into standardized FedGen data formats.
- **In-memory caching**: Responses are cached for 5 minutes to reduce external API load.
- **Fallback mechanisms**: If live APIs are unavailable, the backend falls back to local static JSON files.

### 4.3 Python Automation Layer

The EDC Management API client (`scripts/fedgen_client.py`) provides a Python interface for:

- **Asset management**: Register datasets with `HttpData` data addresses.
- **Policy creation**: Define ODRL permission and obligation policies.
- **Contract definitions**: Link policies to assets.
- **Catalog queries**: Discover assets via the Dataspace Protocol.
- **Contract negotiation**: Full DCP-authenticated negotiation flow.
- **Data transfer**: HttpData-PULL transfer initiation and EDR retrieval.

### 4.4 Federated Learning Module

The `fl/` module implements a complete federated learning pipeline in pure NumPy (no external ML frameworks):

- **`model.py`** — `LogisticRegression`: Binary classifier with mini-batch SGD, weight export/import for federated aggregation.
- **`data_utils.py`** — `SimpleTfidfVectorizer`: Custom TF-IDF vectorizer with tokenization, stop-word removal, IDF computation, and L2 normalization.
- **`fedavg.py`** — `run_fedavg()`: Federated Averaging algorithm with per-round local training, weighted aggregation proportional to sample counts, and global model evaluation.
- **`fl_demo.py`** — Standalone and integrated entry points for the FL demonstration.

### 4.5 Seed Script

The environment seed script (`scripts/seed_mvd.sh`) orchestrates the complete initialization of the dataspace:

1. Wait for all control planes to be ready (health checks).
2. Seed base asset/policy/contract data via Newman (Postman CLI).
3. Create Consumer and Provider participants in their respective Identity Hubs, with EC public keys matching the hard-coded `SecretsExtension` keys.
4. Store STS (Secure Token Service) client secrets in all connector vaults.
5. Activate participants to publish their DID documents.
6. Create and seed the Issuer participant for credential issuance.

---

## 5. Data Sources

### 5.1 Static Sample Data

- **Legal Domain** — Simulates the **Pile-of-Law** dataset [7]: A sample of 3 legal documents covering contract law, intellectual property law, and data protection regulations.
- **News Domain** — Simulates the **CNN/DailyMail** dataset [8]: A sample of 4 news articles covering AI infrastructure, EU AI regulation, data sovereignty, and open-source AI models.

### 5.2 Live API Data

- **OpenAlex API** (`api.openalex.org`): Returns academic papers related to data privacy and law, including titles, abstracts (reconstructed from inverted indices), publication years, citation counts, and DOIs.
- **Hacker News Algolia API** (`hn.algolia.com`): Returns top stories related to AI and technology, with titles, scores, URLs, and timestamps.

### 5.3 Third-Party Database

- **Wikidata Query Service** (`query.wikidata.org`): Queried via SPARQL for knowledge graph entities related to AI, machine learning, data privacy, data protection, GDPR, and cybersecurity. Returns structured records with entity IDs, labels, descriptions, and URIs under a CC0 license.

---

## 6. Implementation Details

### 6.1 Technology Stack

| Component | Technology |
|-----------|-----------|
| Dataspace Runtime | Eclipse Dataspace Components (EDC) |
| Container Orchestration | Kubernetes (k3d) |
| Infrastructure as Code | Terraform |
| Programming Languages | Python (automation, FL), Java (EDC), Bash (scripts) |
| Identity | DIDs (`did:web`), Verifiable Credentials, DCP |
| Policy Language | ODRL (Open Digital Rights Language) |
| API Testing | Newman (Postman CLI) |
| ML Framework | NumPy (pure implementation, no sklearn/PyTorch) |

### 6.2 DCP Authentication Flow

Every catalog query and contract negotiation involves the DCP authentication flow:

```
Consumer CP ──SI Token──▶ Provider CP ──PresentationQuery──▶ Consumer IH
                                      ◀──VP (credentials)──┘
                          [verify credentials + evaluate ODRL policy]
             ◀──FINALIZED──┘
```

**Figure 2.** DCP authentication sequence during contract negotiation.

The Consumer's Control Plane sends a Self-Issued (SI) Token to the Provider. The Provider sends a Presentation Query to the Consumer's Identity Hub, which returns a Verifiable Presentation containing the consumer's `MembershipCredential`. The Provider verifies this credential and evaluates the attached ODRL policy. If the policy is satisfied, the negotiation transitions to `FINALIZED`.

### 6.3 Policy Enforcement

FedGen demonstrates two types of ODRL policy constraints:

- **Permission-based — `MembershipCredential`**: Requires the consumer to hold an active membership credential, verified via DCP. Used for all asset access policies.
- **Obligation-based — `DataAccess.level`**: Specifies a usage obligation (e.g., `"processing"`) that the consumer must commit to when accepting the contract. Used for the news corpus contract policy.

### 6.4 Data Transfer: HttpData-PULL

After contract agreement, data transfer uses the `HttpData-PULL` pattern:

1. Consumer initiates a transfer process referencing the contract agreement.
2. Provider's data plane generates an **Endpoint Data Reference (EDR)** containing a time-limited authorization token and the data plane endpoint URL.
3. Consumer retrieves the EDR and uses the token to pull data via HTTP GET from the provider's data plane.
4. The data plane proxies the request to the underlying data backend (FedGen Data Backend).

### 6.5 Federated Learning: FedAvg Algorithm

The FedAvg implementation follows McMahan et al. [6]:

```
┌─────────────────────────────────────────────────────────┐
│              Federated Averaging (FedAvg)                │
│                                                          │
│  ┌─────────────────┐    ┌──────────────────────────┐    │
│  │  Coordinator     │    │  For each round r:       │    │
│  │  (Node C)        │───▶│                          │    │
│  │  Initialize w₀   │    │  1. Distribute wᵣ to     │    │
│  └─────────────────┘    │     all nodes             │    │
│                          │                          │    │
│  ┌─────────────────┐    │  2. Each node k trains    │    │
│  │  Node A (Legal)  │    │     locally for E epochs: │    │
│  │  Local SGD on    │    │     wₖ ← SGD(wᵣ, Dₖ)   │    │
│  │  legal texts     │    │                          │    │
│  └─────────────────┘    │  3. Aggregate:            │    │
│                          │     wᵣ₊₁ = Σ(nₖ/n)·wₖ  │    │
│  ┌─────────────────┐    │                          │    │
│  │  Node B (News)   │    │  4. Evaluate on test set │    │
│  │  Local SGD on    │    │                          │    │
│  │  news articles   │    └──────────────────────────┘    │
│  └─────────────────┘                                     │
└─────────────────────────────────────────────────────────┘
```

**Figure 3.** FedAvg training loop across Node A and Node B, coordinated by Node C.

Key implementation details:

- **Text vectorization**: Custom TF-IDF vectorizer with stop-word removal, document frequency filtering, and L2 normalization.
- **Non-IID partitioning**: Node A receives primarily legal documents; Node B receives primarily news articles — reflecting realistic data heterogeneity.
- **Model**: Binary logistic regression with binary cross-entropy loss and mini-batch SGD (batch size 32).
- **Aggregation**: Weighted average of model parameters proportional to each node's training sample count.

### 6.6 Project Structure

```
fedgen/
├── README.md                        # Project documentation
├── fedgen.md                        # Original project proposal
├── requirements.txt                 # Python dependencies (requests, numpy)
├── run_demo.sh                      # Main demo entry point
├── run_fl_demo.sh                   # FL-only demo
├── run_thirdparty_demo.sh           # Third-party DB demo
├── run_full_transfer.sh             # Postman-based transfer demo
├── configs/
│   └── endpoints.py                 # Node-to-connector endpoint mapping
├── data/
│   ├── legal_sample.json            # Static legal corpus (3 documents)
│   └── news_sample.json             # Static news corpus (4 articles)
├── data-backend/
│   ├── Dockerfile                   # Container image definition
│   └── server.py                    # HTTP server (static + live APIs + SPARQL)
├── deployment/
│   ├── provider.tf                  # Terraform provider config
│   └── data-backend.tf              # K8s deployment for data backend
├── docs/
│   ├── final_report.md              # This report
│   ├── presentation_script.md       # Presentation speaking notes
│   └── troubleshooting-403-unauthorized.md  # Debug guide
├── fl/
│   ├── __init__.py                  # FL module init
│   ├── model.py                     # Logistic regression (NumPy)
│   ├── data_utils.py                # TF-IDF vectorizer + data processing
│   ├── fedavg.py                    # FedAvg algorithm
│   └── fl_demo.py                   # Standalone FL demo
├── postman/
│   ├── FedGen.postman_collection.json
│   └── FedGen_FullTransfer.postman_collection.json
└── scripts/
    ├── fedgen_client.py             # EDC Management API client
    ├── fedgen_demo.py               # Comprehensive 6-scenario demo
    ├── demo_thirdparty_database.py  # Standalone: third-party DB demo
    ├── demo_federated_learning.py   # Standalone: FL demo
    ├── demo_c_to_a_transfer.py      # Single transfer demo
    ├── full_http_transfer.py        # Full HTTP transfer script
    ├── seed_mvd.sh                  # Environment seed script
    ├── seed_identityhub.sh          # Identity Hub seed helper
    └── setup_port_forward.sh        # K8s port-forward helper
```

---

## 7. Demonstration Scenarios

FedGen implements six demonstration scenarios, each exercising different aspects of the dataspace:

### Scenario 1: C → A (Legal Data Transfer)

Node C (AI Lab) acquires legal training data from Node A (Legal Archives). Demonstrates the full EDC lifecycle: asset registration → ODRL policy creation → contract definition → catalog query → DCP-authenticated contract negotiation → HttpData-PULL transfer → EDR-based data access.

### Scenario 2: C → B (News Data Transfer)

Node C acquires news corpus from Node B (News Syndicate). Extends Scenario 1 with separate access and contract policies, including a `DataAccess.level` obligation constraint.

### Scenario 3: Federated Catalog Discovery

Node C queries Node D's federated catalog to discover all datasets across the federation without querying individual providers. Demonstrates scalable cross-provider discovery.

### Scenario 4: B-Cons → A (Dual-Role Demonstration)

Node B switches to its consumer role (B-Cons) and acquires legal data from Node A. Proves that a single business entity can both provide and consume data within the same dataspace.

### Scenario 5: Federated Learning (FedAvg)

Node C coordinates federated model training with data from Node A (legal) and Node B (news). Runs 5 FedAvg rounds with local SGD training — raw data never leaves local nodes; only model weights are aggregated.

### Scenario 6: Third-Party Database Access (Wikidata)

Node A exposes Wikidata as an EDC-governed asset. Node C discovers, negotiates, transfers, and retrieves actual knowledge graph records from Wikidata via the full EDC contract flow. Demonstrates end-to-end data delivery from a real external database through the sovereign dataspace.

---

## 8. Proof of Functionality

### 8.1 Full Demo Run (All 6 Scenarios)

The complete demonstration (`bash run_demo.sh`) executes all six scenarios sequentially. Below is a representative summary output from a successful test run:

```
**********************************************************************
  FedGen - Sovereign Dataspace for Decentralized AI Training
**********************************************************************

======================================================================
  Scenario 1: C → A  |  AI Lab acquires Legal Training Data
======================================================================
  ✓ Asset 'fedgen-legal-corpus' registered (static sample)
  ✓ Asset 'fedgen-legal-live' registered (OpenAlex API)
  ✓ Policy 'fedgen-legal-policy' created (requires MembershipCredential)
  ✓ Contract 'fedgen-legal-contract' created (static)
  ✓ Contract 'fedgen-legal-live-contract' created (live API)
  ✓ Catalog returned 4 offer(s)
  ✓ Found target asset: fedgen-legal-corpus
  [negotiation] state: INITIAL → REQUESTING → AGREED → VERIFIED → FINALIZED
  ✓ Contract Agreement: <agreement-id>
  [transfer] state: INITIAL → PROVISIONING → REQUESTED → STARTED
  ✓ EDR endpoint: http://consumer-dataplane:11002/api/public/
  ✓ Authorization token obtained (488 chars)

======================================================================
  Scenario 2: C → B  |  AI Lab acquires News Corpus
======================================================================
  ✓ Asset 'fedgen-news-corpus' registered (static sample)
  ✓ Asset 'fedgen-news-live' registered (Hacker News API)
  ✓ Access policy created (MembershipCredential)
  ✓ Contract policy created (DataAccess.level)
  ✓ Catalog returned 4 offer(s)
  ✓ Found target asset: fedgen-news-corpus
  ✓ Contract Agreement: <agreement-id>
  ✓ EDR endpoint obtained with authorization token

======================================================================
  Scenario 3: Federated Catalog Discovery via Node D
======================================================================
  ✓ Discovered datasets across the federation

======================================================================
  Scenario 4: B-Cons → A  |  News Syndicate acquires Legal Data
======================================================================
  ✓ B-Cons queries Node A catalog successfully
  ✓ Contract negotiation FINALIZED
  ✓ EDR obtained — Node B can now consume legal data

======================================================================
  Scenario 5: Federated Learning across the Dataspace
======================================================================
  Dataset: 7 samples (3 legal + 4 news)
  Round 1/5: test_accuracy=0.5000
  Round 2/5: test_accuracy=0.5000
  Round 3/5: test_accuracy=1.0000
  Round 4/5: test_accuracy=1.0000
  Round 5/5: test_accuracy=1.0000
  ✓ Global model accuracy: 100.0%
  ✓ Training completed over 5 federation rounds

======================================================================
  Scenario 6: C → A (Wikidata)  |  Third-Party Database Access
======================================================================
  ✓ Asset 'fedgen-wikidata-kg' registered (Wikidata SPARQL)
  ✓ Contract negotiation FINALIZED
  ✓ Data retrieved successfully via EDR!
  ✓ Source: Wikidata Query Service (SPARQL)
  ✓ Records received: 5
    artificial intelligence (Q11660): branch of computer science
    machine learning (Q2539): study of algorithms improved through experience
    data privacy (Q3624078): ...
    General Data Protection Regulation (Q23894374): ...
    cybersecurity (Q3510521): ...

======================================================================
  Demo Summary
======================================================================
  ✓  Scenario 1: C → A (Legal data transfer)
  ✓  Scenario 2: C → B (News data transfer)
  ✓  Scenario 3: Federated catalog discovery
  ✓  Scenario 4: B-Cons → A (Dual-role demonstration)
  ✓  Scenario 5: Federated learning (FedAvg)
  ✓  Scenario 6: Third-party database access (Wikidata)

  🎉 All scenarios completed successfully!
```

### 8.2 Standalone Demo A: Third-Party Database (Wikidata)

Running `bash run_thirdparty_demo.sh`:

- Pre-check confirms the FedGen backend connects to real Wikidata and returns 5 knowledge graph records.
- Full EDC flow (asset registration → catalog query → contract negotiation → transfer → EDR) succeeds.
- End-to-end data delivery is verified: actual Wikidata records are fetched through the EDC data plane using the EDR authorization token from inside the Kubernetes cluster.

### 8.3 Standalone Demo B: Federated Learning

Running `bash run_fl_demo.sh`:

- Live data loaded from the FedGen backend: 30 legal documents (OpenAlex) + 20 news articles (Hacker News).
- FedAvg runs 5 federation rounds with 3 local SGD epochs per round.
- Accuracy progression: 60% → 60% → 70% → 80% → 80%.
- Per-node training losses decrease consistently across rounds.
- Final global model accuracy: **80%** with 50 live data samples.

### 8.4 Code Repository

The complete source code is available at: **https://github.com/EthanSyn/DDA4240_Fedgen_2026**

The repository includes all source files, configuration, deployment manifests, documentation, and sample data. No EDC source code is included — only the FedGen extension layer.

---

## 9. Discussion

### 9.1 Problems Overcome

#### 9.1.1 The 403 Unauthorized Bug (DCP Authentication Failure)

The most significant technical challenge was debugging persistent 403 errors during contract negotiation. Three interconnected root causes were identified:

1. **Private key overwritten by public key in InMemoryVault**: The EDC `SecretsExtension` stores both private and public keys by alias. All Terraform modules configured the same alias (`key-1`) for both, causing `ConcurrentHashMap.put()` to overwrite the private key with the public key. **Fix**: Changed `sts-public-key-id` to `key-1-pub` in all four Terraform variable files.

2. **DID Document key mismatch**: The original seed script used `keyGeneratorParams` to generate new EC keys, but the ControlPlane's `SecretsExtension` hard-codes a different EC key. This caused signature verification failures because the DID Document contained a different public key than the one corresponding to the signing private key. **Fix**: Used `publicKeyPem` in the seed script to provide the exact public key matching the hard-coded `SecretsExtension` key.

3. **Missing participant activation and STS client secrets**: Participants start in `CREATED` state (not `ACTIVATED`), so DID Documents are not published. Additionally, the Remote STS client requires client secrets stored in each connector's vault. **Fix**: Added explicit activation API calls and STS secret storage to the seed script.

A detailed troubleshooting guide is provided in `docs/troubleshooting-403-unauthorized.md`.

#### 9.1.2 Kubernetes Networking Complexity

EDC connectors communicate internally via Kubernetes service DNS names (e.g., `consumer-controlplane:8082`), while external access uses ingress paths (e.g., `http://127.0.0.1/consumer/cp/`). The `did:web` resolution mechanism must use the correct hostname matching the DID (e.g., `consumer-identityhub:7083`), which required careful alignment between DID definitions, service endpoints, and seed script parameters.

#### 9.1.3 InMemoryVault Non-Persistence

The MVD uses `InMemoryVault` for development, which loses all stored secrets on pod restart. After any Kubernetes cluster restart (e.g., k3d reboot), the entire seed script must be re-run to restore STS secrets, participant states, and DID Documents.

### 9.2 Design Decisions

- **Python over Java for automation**: The EDC runtime is Java-based, but the automation layer (asset registration, negotiation orchestration, FL) is implemented in Python for rapid development and readability.
- **Pure NumPy for FL**: The federated learning module avoids external ML frameworks (sklearn, PyTorch) to minimize dependencies and demonstrate the algorithm transparently.
- **API proxying for third-party data**: Rather than having consumers directly access external databases, the FedGen backend acts as a proxy, keeping the external API details hidden behind EDC's governance layer.

### 9.3 Limitations

- **InMemoryVault**: Not suitable for production; secrets are lost on restart. A persistent vault (e.g., HashiCorp Vault) would be needed for production deployments.
- **Shared consumer connector**: Node B-Cons and Node C share the same `consumer` connector instance, which means they share the same DID. In a production deployment, each entity would have its own connector and DID.
- **Small dataset FL**: The static sample data (7 documents) limits FL demonstration quality. Live API data (50+ samples) provides better results but requires the Kubernetes backend to be running.
- **Single-machine deployment**: All nodes run on a single k3d cluster. A real deployment would distribute nodes across organizations.

---

## 10. Conclusions and Future Work

### 10.1 Conclusions

FedGen successfully demonstrates a sovereign dataspace ecosystem for decentralized AI training corpora built on Eclipse Dataspace Components. The project achieves:

- **Sovereign data sharing**: Six end-to-end scenarios proving policy-enforced, DCP-authenticated data transfer between providers and consumers.
- **Dual-role participation**: A single business entity (News Syndicate) operating as both provider and consumer within the same dataspace.
- **Federated discovery**: Cross-provider dataset discovery through a federated catalog service.
- **Third-party database integration**: Real external database (Wikidata) accessed through the same EDC governance framework, with end-to-end verified data delivery.
- **Privacy-preserving AI training**: Federated learning with FedAvg, where raw data never leaves provider nodes and only model weights are exchanged.

The project also produced a comprehensive troubleshooting guide for DCP authentication issues, which may benefit future EDC developers.

### 10.2 Future Work

Several directions could extend FedGen:

- **Persistent storage**: Replace `InMemoryVault` with HashiCorp Vault and use PostgreSQL-backed stores for production-grade persistence.
- **True multi-organization deployment**: Deploy nodes across separate Kubernetes clusters or cloud regions to demonstrate real federation.
- **Advanced FL algorithms**: Implement FedProx, differential privacy, or secure aggregation for stronger privacy guarantees.
- **Richer policy framework**: Add time-based constraints (e.g., "access expires after 30 days"), purpose limitation, and data usage tracking/auditing.
- **Larger datasets**: Integrate the full Pile-of-Law (256 GB) and CNN/DailyMail corpora with distributed storage backends.
- **Web-based dashboard**: Build a React-based UI for real-time visualization of data flows, contract states, and FL training progress.
- **Billing and metering**: Implement data marketplace features with usage-based billing through EDC's contract agreement framework.

---

## 11. References

[1] Gaia-X European Association for Data and Cloud. "Gaia-X Architecture Document." https://gaia-x.eu/

[2] International Data Spaces Association. "IDS Reference Architecture Model 4.0." https://internationaldataspaces.org/

[3] Catena-X Automotive Network. "Eclipse Tractus-X." https://catena-x.net/

[4] Eclipse Dataspace Components (EDC) Project. https://projects.eclipse.org/projects/technology.edc

[5] Eclipse EDC Minimum Viable Dataspace (MVD). https://github.com/eclipse-edc/MinimumViableDataspace

[6] B. McMahan et al., "Communication-Efficient Learning of Deep Networks from Decentralized Data," AISTATS 2017. https://arxiv.org/abs/1602.05629

[7] P. Henderson et al., "Pile of Law: Learning Responsible Data Filtering from the Law and a 256GB Open-Source Legal Dataset," NeurIPS 2022. https://arxiv.org/abs/2207.00220

[8] A. See, P. J. Liu, and C. D. Manning, "Get To The Point: Summarization with Pointer-Generator Networks," ACL 2017. https://arxiv.org/abs/1704.04368

[9] ODRL Information Model 2.2. W3C Recommendation. https://www.w3.org/TR/odrl-model/

[10] Decentralized Identifiers (DIDs) v1.0. W3C Recommendation. https://www.w3.org/TR/did-core/

---

*End of Report*
