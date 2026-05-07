# FedGen — Final Project Presentation Script

**Course:** CSC4240/CSC6203 Data Spaces
**Presenter:** Yinuo Sheng (122090461)
**Duration:** 12–15 minutes

---

## Slide 1: Title + Recap (30 seconds)

Good afternoon, everyone. My name is Yinuo Sheng. Today I will present the final implementation of FedGen — a Sovereign Dataspace for Decentralized AI Training Corpora. As you may recall from the proposal presentation, the core problem is: how can organizations share and trade training data for AI, while each party retains full control over access and usage? I will skip the background and focus on what was built and what was improved.

---

## Slide 2: Project Evolution (45 seconds)

The initial proposal covered a four-node dataspace with sample datasets and basic contract negotiation. Over the semester, I expanded the scope in two directions.

First, I integrated a **real third-party database** — Wikidata — to show that the dataspace can govern access not only to local files, but to live external data sources through API proxying.

Second, I implemented a **federated learning demonstration** using FedAvg, to show that once data is governed by the dataspace, it can be used for collaborative AI training without the raw data ever leaving the provider's premises.

---

## Slide 3: Architecture Overview (45 seconds)

Briefly recapping the architecture. Four logical nodes: **Node A** provides legal data and serves as the gateway for the Wikidata third-party database. **Node B** is dual-role — it provides news data and can also consume from others, implemented as two connector instances under the same domain. **Node C** is the AI Lab consumer. **Node D** is the Federated Catalog, crawling all providers to offer unified discovery.

On top of the standard MVD infrastructure, I added a custom **FedGen data backend** — a Python HTTP server deployed in Kubernetes that serves sample data, proxies live APIs, and handles the Wikidata SPARQL integration.

---

## Slide 4: Core Demo — Data Sharing Scenarios (2 minutes)

Let me walk through the core demonstration. The project implements six scenarios in total. I will walk through the most important ones in detail.

**Scenario 1: Node C acquires legal data from Node A.** This is the most complete scenario and illustrates the full EDC data sharing lifecycle.

First, Node A registers its legal corpus as an EDC asset. The asset's data address points to the FedGen data backend. Node A then creates an ODRL policy requiring a MembershipCredential — meaning the consumer must be a verified member of the dataspace. A contract definition links this policy to the asset.

Node C queries Node A's catalog using the Dataspace Protocol, discovers the legal corpus, and initiates a contract negotiation. During negotiation, the DCP authentication flow kicks in: the provider sends a presentation query to the consumer's Identity Hub, which returns a Verifiable Presentation containing the MembershipCredential. The provider verifies this credential and evaluates the policy. If everything checks out, the negotiation reaches the FINALIZED state.

Node C then initiates an HttpData-PULL transfer. Once the transfer starts, Node C obtains an Endpoint Data Reference — an EDR — containing a time-limited authorization token and the data plane endpoint. Using this token, Node C can pull the actual data through the provider's data plane.

**Scenario 2** follows the same pattern between Node C and Node B for news data, but with a richer policy setup. Here we use separate access and contract policies — the access policy still requires MembershipCredential, while the contract policy adds a DataAccess.level obligation set to "processing," which represents the consumer's commitment to use the data only for model training.

**Scenario 3** demonstrates federated discovery. Node D crawls the catalogs of all providers and gives Node C a unified view of available datasets, without needing to know individual provider endpoints. This is critical for scalability — in a large federation, consumers should not have to query each provider separately.

**Scenario 4** demonstrates the dual-role capability. Node B switches to its consumer role and acquires legal data from Node A. It goes through the same catalog query and negotiation process, proving that a single business entity can both provide and consume within the same dataspace.

---

## Slide 5: Third-Party Database Integration (1.5 minutes)

Now let me talk about the first extension: integrating a real third-party database.

Data spaces should not only govern access to local files. They should also be able to mediate access to external databases through API proxying, while still enforcing the same sovereignty policies.

I chose **Wikidata** as the external database because it provides a public SPARQL endpoint, returns structured knowledge graph data, and requires no API key — making it reliable for live demonstration.

Here is how it works. The FedGen data backend has a route at `/thirdparty/wikidata`. When this route is hit, the backend constructs a SPARQL query targeting AI and privacy-related concepts, sends it to `query.wikidata.org`, transforms the JSON response into a standardized format, caches the result, and returns it.

Node A registers this backend route as an EDC asset — just like any other dataset. The key insight is that from the consumer's perspective, acquiring data from a third-party database goes through exactly the same EDC flow: catalog query, contract negotiation, transfer, and EDR-based data access. The consumer never directly touches the external database. All access is policy-controlled.

In the demo output, after contract negotiation, Node C obtains an EDR token, and when we use that token to fetch data from inside the Kubernetes cluster, we receive actual Wikidata records — entities like "General Data Protection Regulation," "cybersecurity," and "data protection" — proving end-to-end data delivery from a real external database through the sovereign dataspace.

---

## Slide 6: Federated Learning Demonstration (2 minutes)

The second extension is federated learning.

Once the dataspace governs who can access what data, the next question is: can we train AI models collaboratively **without centralizing the raw data**? This is where federated learning comes in.

I implemented the FedAvg algorithm from scratch using NumPy — no external ML frameworks. Node A holds legal text data. Node B holds news article data. Node C acts as the federation coordinator. The task is binary text classification: legal document versus news article.

The entire FL pipeline is implemented from scratch in NumPy — the model, the gradient computation, the TF-IDF vectorizer, and the aggregation logic are all custom code, not library calls.

The training process works as follows. The coordinator initializes a global logistic regression model. In each round, the global weights are distributed to Node A and Node B. Each node trains locally using mini-batch SGD with binary cross-entropy loss for several epochs. Then, each node sends back only the updated model weights — not the raw data. The coordinator performs a weighted average proportional to each node's sample count. This is the FedAvg aggregation step. The updated global model is then evaluated on a shared test set.

In the demo, we load 50 live samples — 30 from OpenAlex and 20 from Hacker News — and run five federation rounds. The accuracy improves from 60% to 80%, with node-local losses decreasing consistently. This confirms the model is actually learning.

The key point for the data spaces context: the raw text never leaves each node. Only model parameters — a vector of floating-point numbers — are exchanged. This preserves data sovereignty while enabling collaborative AI training.

---

## Slide 7: Key Improvements over Base MVD (1 minute)

Let me highlight the specific improvements I made beyond the standard MVD.

1. **Custom seed script** — The original MVD seed did not properly handle STS client secrets and participant activation in Kubernetes. I rewrote the entire seed flow, including cryptographic key alignment between the Identity Hub and the connector vault.

2. **Live API integration** — The data backend proxies real-world APIs — OpenAlex, Hacker News, Wikidata — with caching and fallback mechanisms, instead of only serving static files.

3. **Third-party database gateway** — The Wikidata SPARQL proxy lets the dataspace govern access to external databases through the same EDC contract flow.

4. **Federated learning pipeline** — A complete FedAvg implementation with TF-IDF feature extraction, non-IID data partitioning, and per-round evaluation.

5. **ODRL policy diversity** — Both permission-based policies using MembershipCredential and obligation-based policies using DataAccess.level constraints.

---

## Slide 8: Demo Walkthrough (1.5 minutes)

Now let me show you the actual demo output.

*[Refer to screenshot or video of `run_thirdparty_demo.sh` output]*

In Demo A, the pre-check confirms the backend is connected to real Wikidata — it returns five actual knowledge graph records. Then the full EDC flow proceeds: asset registration, policy creation, contract definition, catalog query returning three offers, negotiation transitioning from INITIAL to VERIFIED to FINALIZED, transfer starting, and the EDR being obtained with a 488-character authorization token. In the final step — Step 10 — we use that token from inside the Kubernetes cluster to actually fetch the data through the EDC data plane. Five Wikidata records arrive successfully, proving genuine end-to-end data delivery from a real external database, governed entirely by the dataspace.

*[Refer to screenshot or video of `run_fl_demo.sh` output]*

In Demo B, the system first loads live training data: 30 legal documents from OpenAlex and 20 news articles from Hacker News. This data is fetched from the FedGen data backend inside the cluster — these are real API responses, not static files. The FedAvg training then runs for five rounds. You can see the test accuracy increasing round by round: 60%, 60%, 70%, 80%, 80%. The per-node training losses also decrease consistently, which confirms the model weights are converging through the federated aggregation process. The final global model accuracy of 80% demonstrates that the federated learning pipeline is working correctly.

---

## Slide 9: Summary (45 seconds)

To summarize, FedGen demonstrates:

- **Sovereign data sharing** with ODRL policy enforcement and DCP-based identity verification.
- **Multi-role participation** — a single entity can both provide and consume data.
- **Federated discovery** through a catalog server that aggregates offerings across providers.
- **Third-party database access** governed by the same EDC contract negotiation flow.
- **Federated learning** that enables collaborative AI training without centralizing raw data.

The system is fully automated through Terraform and Python, and uses real-world data from OpenAlex, Hacker News, and Wikidata.

Thank you. I am happy to take any questions.

---

## Timing Summary

| Section | Duration |
|---|---|
| Title + Recap | 0:30 |
| Project Evolution | 0:45 |
| Architecture Overview | 0:45 |
| Core Demo Scenarios | 2:00 |
| Third-Party DB | 1:30 |
| Federated Learning | 2:00 |
| Key Improvements | 1:00 |
| Demo Walkthrough | 1:30 |
| Summary | 0:45 |
| **Total** | **~10:45** |

*Note: Timing above is speaking time only. With slide transitions, pausing for audience, and Q&A buffer, total presentation time should reach 12–14 minutes.*

---

## Suggested Slide Visuals

- **Slide 3**: Architecture diagram from README (Node A/B/C/D topology)
- **Slide 4**: Sequence diagram: Asset Registration → Policy → Contract Def → Catalog Query → Negotiation → Transfer → EDR
- **Slide 5**: Data flow diagram: Consumer → EDC Data Plane → FedGen Backend → Wikidata SPARQL
- **Slide 6**: FedAvg round diagram: Coordinator distributes weights → Nodes train locally → Nodes return weights → Coordinator aggregates
- **Slide 7**: Bullet list of improvements (could overlay on project directory tree)
- **Slide 8**: Screenshots of terminal output from both demos
- **Slide 9**: Summary bullet points + "Questions?"
