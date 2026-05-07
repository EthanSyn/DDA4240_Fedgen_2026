# CSC4240/CSC6203 Data Spaces Project Proposal
# FedGen
A Sovereign Dataspace for Decentralized AI Training Corpora 
Submitted by: 
Yinuo Sheng 122090461 
# 1 EXECUTIVE SUMMARY
The rapid advancement of Large Language Models (LLMs) has created a critical demand for high-quality, domain-specific training data. However, data sovereignty concerns and copyright regulations often prevent enterprises from sharing proprietary datasets in centralized data lakes. This project proposes FedGen, a decentralized dataspace ecosystem built upon the Eclipse Dataspace Components (EDC). By implementing a federated architecture with strict usage control policies, FedGen demonstrates a secure B2B marketplace where data providers can monetize sensitive assets (e.g., legal archives, news corpora) for AI training without compromising sovereignty. 
# 2 PROPOSED ECOSYSTEM ARCHITECTURE
To simulate a realistic industrial environment, the proposed dataspace consists of a federated network comprising four distinct functional entities. 
# 2.1 Implementation Strategy for Dual-Role Entity
A key requirement of the project is the inclusion of entities that act as both data providers and consumers. While the standard EDC Minimum Viable Dataspace (MVD) configuration typically assigns single roles to connectors, implementing dual identities within a single MVD instance involves significant configuration overhead regarding Identity and Access Management (IAM). 
To address this challenge efficiently, we have adopted a technically equivalent but more streamlined strategy: the dual-role entity (Node B) will be deployed as two distinct connector instances (one for providing, one for consuming) operating within the same logical domain. 
1 
This approach simplifies the deployment process while fully satisfying the functional requirement for a bidirectional participant. 
The ecosystem comprises the following nodes: 
# 1. Node A: The Legal Archives (Data Provider)
Hosting sensitive legal texts. It enforces policies restricting access to certified AI developers only. 
# 2. Node B: The News Syndicate (Dual-Role Participant)
Functionally a single business entity, implemented via two coordinated connector instances to ensure stability: 
• Instance B-Prov: Publishes copyrighted news articles as assets. 
• Instance B-Cons: Subscribes to analytics services to improve editorial content. 
# 3. Node C: The AI Lab (Data Consumer)
Represents a technology firm that queries the network to acquire training data for model fine-tuning. 
# 4. Node D: Federated Catalog Service
A dedicated discovery node configured to periodically crawl the catalogs of Node A and Node B-Prov, providing a unified search interface for the entire federation. 
# 3 REAL-WORLD DATA STRATEGY
To ensure the demonstration reflects real-world ”Big Data” challenges, we will utilize subsets of established open datasets hosted on local HTTP backends. 
• Legal Domain Data: The Pile-of-Law Dataset [3]. A large-scale corpus of legal and administrative texts, simulating high-value intellectual property. 
• Media Domain Data: CNN/Daily Mail Dataset [4]. A collection of news articles and summaries, representing copyrighted media assets. 
# 4 IMPLEMENTATION METHODOLOGY
The project will be implemented by extending the official Eclipse EDC MVD [2]. The development plan focuses on orchestration and policy enforcement rather than core protocol modification. 
1. Orchestration: We will utilize Docker Compose to orchestrate the multi-connector environment, ensuring network isolation and reproducible deployments. 
2. Automation Layer: While the core infrastructure runs on Java (EDC), we will develop a Python-based control layer. Python scripts will interact with the EDC Management API to automate complex workflows, including asset registration, contract negotiation, and transfer initiation. 
3. Policy Enforcement: We will implement ODRL (Open Digital Rights Language) policies to demonstrate sovereignty, such as time-constrained access (e.g., ”Access allowed until 2026-02-01”). 
4. Federated Discovery: The Federated Catalog node will be configured to dynamically discover assets from new participants, demonstrating the scalability of the dataspace. 
2 
# References


[1] Eclipse Dataspace Components (EDC) Project. https://projects.eclipse. org/projects/technology.edc. 




[2] Eclipse EDC Minimum Viable Dataspace (MVD). https://github.com/ eclipse-edc/MinimumViableDataspace. 




[3] Peter Henderson et al. ”Pile of Law: Learning Responsible Data Filtering from the Law and a 256GB Open-Source Legal Dataset”. NeurIPS 2022. https://arxiv.org/ abs/2207.00220. 




[4] Abigail See, Peter J. Liu, and Christopher D. Manning. ”Get To The Point: Summarization with Pointer-Generator Networks”. ACL 2017. https://arxiv.org/abs/1704. 04368. 


3 