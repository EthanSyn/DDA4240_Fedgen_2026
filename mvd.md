C 
香港中文大學 (深圳)
The Chinese Universityof Hong Kong,Shenzhen 
数据科学学院
School of Data Science 
# CSC4240 (Spring 2026)
# Getting Started with MVD
TA: Shuwen Liu (shuwenliu@link.cuhk.edu.cn) 
Instructor: Prof. Polyzos 
# EDC - Eclipse Dataspace Components
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/d3bcceaa024e8a34c50f6c46abc7addee933e0f6d92de8feb9266a11a5f66899.jpg)

![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/6eb92b2edb2a120ada297b13bc5c9727640e783daff07306b64233bb7d9b4a97.jpg)

Backed by Leading Companies 
https://projects.eclipse.org/projects/technology.edc 
https://github.com/eclipse-edc 
aMaDEUS 
Google 
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/71856afba50b5b8a646f8f6610042a7a29b25c082fde53a7938a86485ec835fb.jpg)

![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/5caf5e3a1b88562873b735751e94a6efcbfed325cc3fba7b393267216d5f66a2.jpg)

![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/eb49764e910c8a7e4b823e753134204250b7a1f8cb3c678dd4cbc55777ae23cc.jpg)

![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/e8dc72d33a60c99e3e9b2db23a6187910248c14e9c29692b6947a7376ddba5eb.jpg)

![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/b34acdde74123b7f6f8034e985acff48bd6cda19c2ff5c52ef72ea968dcb602d.jpg)

Fraunhofer 
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/ca173cef1d8717ecbc19995423af04c5544440aecfdc1568954ce029fd93b543.jpg)

2 
# Repo
‣ https://github.com/eclipse-edc/MinimumViableDataspace 
‣ All demonstrations in this tutorial are based on this repository, which is also the MinimumViableDataspace (MVD) provided by EDC, helping us quickly implement a data space. 
‣ For more details and a better understanding of EDC connectors, please see: 
‣ https://github.com/eclipse-edc/Samples 
‣ By following the guide step-by-step from the basic module, you can gain a deeper understanding of the connector. 
3 
# MVD (Minimum Viable Dataspace) Scenario: Data Sharing
» Consumer Corp: Wants to access data. 
» Provider Corp: Has two independent departments (Q&A and Manufacturing) sharing a single Federated Catalog. 
# Goal: Securely exchange data between Consumer and Provider.
» Identity: Participants are identified by DIDs (Decentralized Identifiers). 
» Access Control: Data is NOT public. To access it, the Consumer must present their valid Verifiable Credentials (VCs): 
– MembershipCredential: "I am a trusted member." 
– DataProcessorCredential: "I am authorized to process sensitive/non-sensitive data." 
» We will simulate the flow of Discovery (Catalog) -> Negotiation (Contract) -> Transfer (Data). 
4 
# Outline
‣ Prerequisites 
‣ Setting Up the Toolchain (Inside Container) 
‣ Running MVD 
‣ Extension: Using Real datasets 
‣ Postman Verification (Demonstration) 
‣ Learning Roadmap (suggestions) 
‣ Preliminary plan of final project 
5 
# Why Dev Containers?
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/a1c42fbf30f5e646840442f8b038908e25d27041fb102ad2db06ae844fce0b26.jpg)

» Everyone gets the same OS, Java version, and tools. 
» Isolates the project from your local machine. 
» Solves compatibility issues between Mac (ARM) and Windows (x86). 
-> So you can focus on development instead of the os environment. 
# Setup Steps:
» Install VS Code + "Dev Containers" Extension. 
» Open the project folder (MinimumViableDataspace). 
» Press Ctrl+Shift+P -> Type: "Dev Containers: Reopen in Container". 
» Wait for the build to finish. 
» Success Indicator: Bottom-left corner shows green "Dev Container". 
https://code.visualstudio.com/docs/devcontainers/tutorial 
6 
https://code.visualstudio.com/docs/devcontainers/containers 
# For 2 operating systems:
‣ Way 1: if you’re using windows os 
‣ Install WSL2, vscode and docker 
‣ Using vscode dev container 

‣ Way 2: if you’re using macos 
‣ Install vscode and docker 
‣ Using vscode dev container 

7 
# Way 1: if you’re using windows os
» Critical Step: Enable WSL2 & Docker 
» Do NOT run MVD directly in CMD or PowerShell. It is not supported! 
» Step 1: Install Docker Desktop. 
https://docs.docker.com/desktop/setup/install/windows-install/ 
» Step 2: Install WSL2 (Windows Subsystem for Linux). 
https://learn.microsoft.com/en-us/windows/wsl/install 
» Restart your computer. 
» WSL2 Intsall/enabled Tutorial: 
https://www.youtube.com/watch?v=zZf4YH4WiZo 
– https://docs.docker.com/desktop/features/wsl/ 
https://learn.microsoft.com/zh-cn/windows/wsl/install 
https://marketplace.visualstudio.com/items?itemName=msvscode-remote.remote-wsl 
8 
# Install vscode
https://code.visualstudio.com/download 
# Download Visual Studio Code
Free and built on open source.Integrated Git,debugging and extensions. 
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/778959b151b314560eaa8e3574dd13f3e91c8ff1ea8698e62f8347119c8babc1.jpg)

![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/e75c69c91a5df154fe654ab7872afa7bacad5d0d52a775d4846c691bb8c02baa.jpg)

Windows 
Windows10,1 
User Installer 
x64Arm64 
System 
Installer 
x64Arm64 
x64Arm64 
CLI 
x64Arm64 
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/7144f9df8b41b1befe0ff634781b1ddf0d94cf2440e19635a043a1d6b9ff8038.jpg)

![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/6537e4eefa71a93b155ec57a7024a93b2b4e1c35dd11b20e5100e618269993e9.jpg)

.deb 
Debian,Ubunt 
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/44856fd28045e78f166ee19a2ae77d051aec4eea4379cd94fdbe8d5e9335a190.jpg)

.rpm 
Red Hat,edora, 
.deb 
x64Arm32 
Arm64 
.rpm 
x64Arm32 
Arm64 
.tar.gz 
x64Arm32 
Arm64 
Snap 
Snap Store 
x64 
Arm32 
Arm64 
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/839bd6f9726411bc16923755b5e046beac99683ff430d7c31d4e7fade840d6b4.jpg)

![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/1a16ff3babc69b62bd59f2a292c5ad3435ccf77afec498f9ed110cd1fd97d956.jpg)

Mac 
macos 11.0+ 
.zip 
Intel chip 
Apple silicon 
Universal 
CLI 
Intel chip 
Apple silicon 
# Install vscode dev containers
https://code.visualstudio.com/docs/devcontainers/tutorial 
# Input “dev containers”
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/178fa178b04b97747300aa95cc3db87b865df689b054decb6355f2db08791304.jpg)

10 
# Get Started with dev container
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/1a96487dd0a0965f47be2023ec4878113c84e9453f401507bc877bca3c1dd9b8.jpg)

Ctrl + Shift + P: input ‘container’, then choose ‘reopen in containers’ 
Now everything is ready for dev containers! 
开发容器:EDC MVD Project Environment @ desk..
11 
# Outline
‣ Prerequisites 
‣ Setting Up the Toolchain (Inside Container) 
‣ Running MVD 
‣ Extension: Using Real datasets 
‣ Postman Verification (Demonstration) 
‣ Learning Roadmap (suggestions) 
‣ Preliminary plan of final project 
12 
# Setting Up the Toolchain (Inside Container)
Simply follow the instructions below step by step. 
1. Update System: 
>> sudo apt-get update 
2. Install Kubectl (K8s CLI) 
>> curl -LO "https://dl.k8s.io/release/stable.txt" 
>> curl -LO "https://dl.k8s.io/release/$(cat stable.txt)/bin/linux/arm64/kubectl" 
>> sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl (for mac) 
>> curl -LO "https://dl.k8s.io/release/stable.txt" 
>> curl -LO "https://dl.k8s.io/release/$(cat stable.txt)/bin/linux/amd64/kubectl" 
>> sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl (windows) 
13 
# Setting Up the Toolchain (Inside Container)
Simply follow the instructions below step by step. 
3. Install Kind (Kubernetes in Docker): (Optional, we can also use k3d) 
>> curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-arm64 
>> chmod +x ./kind 
>> sudo mv ./kind /usr/local/bin/kind 
(for mac) 
>> curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64 
>> chmod +x ./kind 
>> sudo mv ./kind /usr/local/bin/kind 
(for windows) 
14 
# Setting Up the Toolchain (Inside Container)
Simply follow the instructions below step by step. 
4. Install Helm: 
>> curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | 
5. Install Terraform: 
# Add HashiCorp Key 
>> wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor --yes -o /usr/s 
# Add Repo 
>> echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt. 
# Install 
>> sudo apt-get update && sudo apt-get install terraform 
15 
# Setting Up the Toolchain (Inside Container)
Simply follow the instructions below step by step. 
6. Install jq (Better display of JSON): 
>> sudo apt-get install -y jq 
$\bullet$ vscode $\rightarrow$ /workspaces/MinimumViableDataspace (main) $ sudo apt-get update Hit:1 http://deb.debian.org/debian bookworm InRelease Hit:2 https://download.docker.com/linux/debian bookworm InRelease Get:3 https://dl.yarnpkg.com/debian stable InRelease Get:4 http://deb.debian.org/debian bookworm-updates InRelease [55.4 kB] Get:5 https://apt/releases hashicorp.com bookworm InRelease [12.9 kB] Get:6 http://deb.debian.org/debian-security bookworm-security InRelease [48.0 kB] Get:7 http://deb.debian.org/debian-security bookworm-security/main arm64 Packages [286 kB] Fetched 419 kB in 1s (526 kB/s) Reading package lists... Done $\bullet$ vscode $\rightarrow$ /workspaces/MinimumViableDataspace (main) $ curl -L0 "https://dl.k8s.io/release/stable.txt" curl -L0 "https://dl.k8s.io/release/$(cat stable.txt)/bin/linux/arm64/kubectl" sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl % Total % Received % Xferd Average Speed Time Time Current Dload Upload Total Spent Left Speed 100 138 100 138 0 0 250 0 -------- ------ ------ 251 100 7 100 7 0 0 7 0 0:00:01 -------- 0:00:01 21 % Total % Received % Xferd Average Speed Time Time Current Dload Upload Total Spent Left Speed 100 138 100 138 0 0 375 0 -------- ------ ------ 376 100 52.6M 100 52.6M 0 0 11.4M 0 0:00:04 0:00:04 -------- 13.1M $\bullet$ vscode $\rightarrow$ /workspaces/MinimumViableDataspace (main) $ curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-arm64 chmod +x ./kind sudo mv ./kind /usr/local/bin/kind % Total % Received % Xferd Average Speed Time Time Current Dload Upload Total Spent Left Speed 100 98 0 98 0 0 99 0 -------- ------ ------ ------ 99 0 0 0 0 0 0 0:00:01 -------- 0 100 6107k 100 6107k 0 0 2544k 0 0:00:02 0:00:02 -------- 15.4M % Total % Received % Xferd Average Speed Time Time Current Dload Upload Total Spent Left Speed 100 11929 100 11929 0 0 28137 0 -------- ------ ------ ------ 28134 Helm v3.19.4 is already latest 
# Setting Up the Toolchain (Inside Container)
Simply follow the instructions below step by step. 
7. Install Node.js (which would include npm): 
>> sudo apt-get update 
>> sudo apt-get install -y nodejs 
# Verify 
# node -v npm -v 
8. Install newman (postman in CLI): 
>> sudo npm install -g newman 
If you encounter an error while running this step, you can try configuring the NodeSource repository first: 
>> sudo apt-get install -y cacertificates curl gnupg 
>> curl -fsSL https://deb.nodesource.com/setup_20. x | sudo -E bash - 
Then try to install nodejs again. 
- vscode $\rightarrow$ /workspaces/MinimumViableDataspace (main) \$ newman -version 6.2.1 
# Setting Up the Toolchain (Inside Container)
Simply follow the instructions below step by step. 
# 9. Install k3d:
>> curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash 
# Why K3d?
1.Kubernetes (K8s): The industry standard for container orchestration, but the full version is heavy on resources. 
2. K3s: A lightweight Kubernetes distribution, perfect for edge & IoT. 
3. K3d (K3s in Docker): A utility that runs K3s clusters inside Docker containers. 
So it’s: 
Lightweight: Starts in seconds, uses minimal RAM. 
Docker-in-Docker Compatible: Runs perfectly inside our VS Code Dev Container. 
No VM needed: Unlike Minikube, it doesn't require a heavy Virtual Machine. 
18 
# Outline
‣ Prerequisites 
‣ Setting Up the Toolchain (Inside Container) 
‣ Running MVD 
‣ Extension: Using Real datasets 
‣ Postman Verification (Demonstration) 
‣ Learning Roadmap (suggestions) 
‣ Preliminary plan of final project 
19 
# Runing MVD
Simply follow the instructions below step by step. 
# 1. Open and run docker, adjust settings, for example:
Settings 
General 
回
resources 
Advanced 
Network 
Docker Engine 
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/9e2fda4f7683bcdb70bda40b250fc3eb45eb37e662215a3022712feee0d16053.jpg)

Builders 
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/8f01b4cca83b30b2a5e276462950ae01bcf218d32497efa2a6685e9f9a6d8ed0.jpg)

Kubernetes 
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/96dbd778378af20fa598279a1142b88c13b86efe96de5093ff5a0ee418c2e73b.jpg)

Softwareupdates 
Resources Advanced 
Resource Allocation 
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/c0f0abdad6cd6592d696c224da58d5d3d40fbf29e2bcd74835eca4dde978c414.jpg)

Memory limit:12GB 
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/7a27a133ed74e70d28511fccf6123f35aa250977922028f674275f7937b61068.jpg)

Swap:1.5GB 
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/aeb01197c2c3f1e09299356c9462946f8e517a14e32779edc95837e64e44c54d.jpg)

The larger the better! 
Cancel 
# Runing MVD
Simply follow the instructions below step by step. 
1. Build the Project: (Compiles Java code and downloads Gradle dependencies.) 
>> ./gradlew build or ./gradlew clean build 
2. Package Docker Images (Creates local Docker images (e.g. controlplane, dataplane, identityhub) needed for the Kubernetes cluster.) 
>> ./gradlew -Ppersistence=true dockerize 
BUILD SUCCESSFUL in 8m 8s 
90 actionable tasks: 82 executed, 8 up-to-date 
Successfully built c1047f82888c 
Successfully tagged issuerservice:0.15.0-SNAPSH0T 
Successfully tagged issuerservice:latest 
Created image with ID 'c1047f82888c'. 
BUILD SUCCESSFUL in 1m 46s 
26 actionable tasks: 10 executed, 16 up-to-date 
21 
# Runing MVD
Simply follow the instructions below step by step. 
3. Create cluster named “mvd /edc-cluster”: 
>> kind create cluster -n mvd --config deployment/kind.config.yaml 
/ >> k3d cluster create edc-cluster --agents 1 -p "80:80@loadbalancer" -p "81 
4. Load Images into edc-cluster nodes: 
>> kind load docker-image controlplane:latest dataplane:latest identity-hub:la 
or >> k3d image import catalog-server:latest controlplane:latest dataplane:lat 
22 
# Runing MVD
Simply follow the instructions below step by step. 
5. Install Ingress Controller (Nginx): 
# delete Traefik first 
>> kubectl -n kube-system delete service traefik 
>> kubectl -n kube-system scale deployment traefik --replicas=0 
# install Nginx 
>> helm upgrade --install ingress-nginx ingress-nginx \ 
--repo https://kubernetes.github.io/ingress-nginx \ 
--namespace ingress-nginx --create-namespace \ 
--set controller.service.type=LoadBalancer \ 
--set controller.watchIngressWithoutClass=true \ 
--set controller.ingressClassResource.default=true 
# Runing MVD
Simply follow the instructions below step by step. 
6. Deploy MVD with Terraform: 
>> cd deployment 
>> terraform init 
# For Mac (ARM64) Users inside Dev Container: 
>> terraform apply -var="useSVE=true" 
# For Windows (x86) Users: 
>>terraform apply -auto-approve 
Type ‘yes’ if prompted 
Apply complete! Resources: 66 added, 0 changed, 0 destroyed.   
Outputs:   
consumer-jdbcurl $\equiv$ "jdbc:postgres://consumer-postgres-service:5432/consumer"   
provider-jdbcurl $=$ { "catalog-server" $\equiv$ "jdbc:postgres://provider-postgres-service:5432/catalog_server" "provider-manufacturing" $\equiv$ "jdbc:postgres://provider-postgres-service:5432/provider_manufacturing" "provider-qna" $\equiv$ "jdbc:postgres://provider-postgres-service:5432/provider_qna"   
} $\text{口}$ vscode $\rightarrow$ /workspaces/MinimumViableDataspace/deployment (main) $ 
Do you want to perform these actions? Terraform will_perform the actions described above. Only'yes'will beaccepted toapprove. 
Enter a value: yes 
24 
# Runing MVD
Simply follow the instructions below step by step. 
# 7. Verify Deployment:
>> cd .. 
>> kubectl get pods -n mvd 
<table><tr><td colspan="5">● vscode → /workspaces/MinimumViableDataspace (main) $ kubectl get pods -n mvd</td></tr><tr><td>NAME</td><td>READY</td><td>STATUS</td><td>RESTARTS</td><td>AGE</td></tr><tr><td>consumer-controlplane-68c4696c57-4pgkp</td><td>1/1</td><td>Running</td><td>0</td><td>7m53s</td></tr><tr><td>consumer-dataplane-75d79bfd56-kh6dw</td><td>1/1</td><td>Running</td><td>0</td><td>7m45s</td></tr><tr><td>consumer-identityhub-77c77dc44d-ggpzn</td><td>1/1</td><td>Running</td><td>0</td><td>8m19s</td></tr><tr><td>consumer-postgres-687484545b-pp5dx</td><td>1/1</td><td>Running</td><td>0</td><td>8m54s</td></tr><tr><td>consumer-vault-0</td><td>1/1</td><td>Running</td><td>0</td><td>8m53s</td></tr><tr><td>dataspace-issuer-server-7ff68bd8b4-wspwj</td><td>1/1</td><td>Running</td><td>0</td><td>8m54s</td></tr><tr><td>dataspace-issuer-service-75b499cb57-t8h6v</td><td>1/1</td><td>Running</td><td>0</td><td>8m19s</td></tr><tr><td>issuer-postgres-5c87fdc69b-8plll</td><td>1/1</td><td>Running</td><td>0</td><td>8m54s</td></tr><tr><td>provider-catalog-server-58b67bdd89-7k6p9</td><td>1/1</td><td>Running</td><td>0</td><td>7m53s</td></tr><tr><td>provider-identityhub-7464c46699-rzczj</td><td>1/1</td><td>Running</td><td>0</td><td>8m19s</td></tr><tr><td>provider-manufacturing-controlplane-86bdd7c967-w67nc</td><td>1/1</td><td>Running</td><td>0</td><td>7m53s</td></tr><tr><td>provider-manufacturing-dataplane-7d66445bf8-7qnmv</td><td>1/1</td><td>Running</td><td>0</td><td>7m45s</td></tr><tr><td>provider-postgres-7fd78d95b8-8z7fh</td><td>1/1</td><td>Running</td><td>0</td><td>8m54s</td></tr><tr><td>provider-qna-controlplane-dc894c5ff-dw6nt</td><td>1/1</td><td>Running</td><td>0</td><td>7m53s</td></tr><tr><td>provider-qna-dataplane-8574c764fd-c8gqm</td><td>1/1</td><td>Running</td><td>0</td><td>7m45s</td></tr><tr><td>provider-vault-0</td><td>1/1</td><td>Running</td><td>0</td><td>8m53s</td></tr></table>
# Runing MVD
Simply follow the instructions below step by step. 
# 8. (Optional) Verify Ingress:
>> kubectl get ingress -n mvd 
>> curl -v http://127.0.0.1/provider-qna/health/api/check/readiness 
<table><tr><td colspan="6">● vscode → /workspaces/MinimumViableDataspace (main) $ kubectl get ingress -n mvd</td></tr><tr><td>NAME</td><td>CLASS</td><td>HOSTS</td><td>ADDRESS</td><td>PORTS</td><td>AGE</td></tr><tr><td>consumer-did-ingress</td><td>nginx</td><td>*</td><td>172.19.0.2, 172.19.0.3</td><td>80</td><td>179m</td></tr><tr><td>consumer-identityhub-ingress</td><td>nginx</td><td>*</td><td>172.19.0.2, 172.19.0.3</td><td>80</td><td>179m</td></tr><tr><td>consumer-ingress</td><td>nginx</td><td>*</td><td>172.19.0.2, 172.19.0.3</td><td>80</td><td>179m</td></tr><tr><td>dataspace-issuer-service-did-ingress</td><td>nginx</td><td>*</td><td>172.19.0.2, 172.19.0.3</td><td>80</td><td>179m</td></tr><tr><td>dataspace-issuer-service-ingress</td><td>nginx</td><td>*</td><td>172.19.0.2, 172.19.0.3</td><td>80</td><td>179m</td></tr><tr><td>provider-catalog-server-ingress</td><td>nginx</td><td>*</td><td>172.19.0.2, 172.19.0.3</td><td>80</td><td>179m</td></tr><tr><td>provider-did-ingress</td><td>nginx</td><td>*</td><td>172.19.0.2, 172.19.0.3</td><td>80</td><td>179m</td></tr><tr><td>provider-identityhub-ingress</td><td>nginx</td><td>*</td><td>172.19.0.2, 172.19.0.3</td><td>80</td><td>179m</td></tr><tr><td>provider-manufacturing-ingress</td><td>nginx</td><td>*</td><td>172.19.0.2, 172.19.0.3</td><td>80</td><td>179m</td></tr><tr><td>provider-qna-ingress</td><td>nginx</td><td>*</td><td>172.19.0.2, 172.19.0.3</td><td>80</td><td>179m</td></tr></table>
vscode → /workspaces/MinimumViableDataspace (main) $\$ 1$ curl -v http://127.0.0.1/provider-qna/health/api/check/readiness 
*Trying 127.0.0.1:80... 
$^ *$ Connected to 127.0.0.1 (127.0.0.1） port 80 （#0） 
>GET/provider-qna/health/api/check/readinessHTTP/1.1 
>Host:127.0.0.1 
$>$ User-Agent:curl/7.81.0 
>Accept:*/* 
> 
* Mark bundle as not suprrting multiuse 
HTTP/1.12000K 
<Date:Wed，07Jan 202615:32:23GMT 
$<$ Content-Type:application/json 
<Content-Length:310 
<Connection:keep-alive 
< 
$^ *$ Connection #0 to host 127.0.0.1 left intact 
{"componntRest：iureullponnt:sicpVltlth,seathtrue},fre"l"ct 
"CrawerSeterepeteete，fre 
ponent":"Observability_API","isHealthy":true}],"isSystemHealthy":true} 
# Runing MVD
Simply follow the instructions below step by step. 
# 9. Execute script:
>>chmod +x seed-k8s.sh 
>> ./seed-k8s.sh 
vscode → /workspaces/MinimumViableDataspace (main) $ ./seed-k8s.sh Step0:Waiting for Control Planes to be ready.. Waiting forhttp://127.0.0.1/provider-manufacturing/health UP! Waiting for http://127.0.0.1/provider-qna/healthUP！ 
√ All Control Planes are running. Starting seeding... 
Step 1:Running Base Postman Collection (Policies & Definitions)... ->Seeded base policies for provider-manufacturing ->Seeded base policies for provider-qna 
Step2:Replacing Dummy Assets with our DATASETS... Updated asset-1 for provider-manufacturing Updated asset-2 for provider-manufacturing asset-1 already exists (might be the real one) Updatedasset-2 for provider-qna 
Step 3:Seeding Catalog Server... $\gg$ Catalog seeded. Step 4:Registering Participants... ->Consumer Registered ->Provider Registered $\gg$ Issuer Registered Step 5:Seeding Issuer Data... $\gg$ Issuer participants seeded. 
SUCCESS: All systems seeded and ready! 
# Extension: Using Datasets
» From Static to Dynamic Data 
– Original MVD: Returns static text generated by Postman scripts. 
– Our Extension: The Provider acts as a Proxy to fetch live data from the internet (https://jsonplaceholder.typicode.com/). 
» Data Source: https://jsonplaceholder.typicode.com/photos (albums) (A public JSON API,here is for demonstration; you can use other open datasets instead). 
» How it works? -- little changes in seed-k8s.sh 
– Wait for EDC Control Planes to come online. 
– Delete the default asset-1 (original dummy data). 
– Create new asset-1and asset-2 pointing to the API URL. 
– When Consumer requests data, Provider fetches it live from JSONPlaceholder. 
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/9941b30d48d1060be3be063d545049832f6e61059480299567546d4023717140.jpg)

Our extended datasets 
# Outline
‣ Prerequisites 
‣ Setting Up the Toolchain (Inside Container) 
‣ Running MVD 
‣ Extension: Using Real datasets 
‣ Postman Verification (Demonstration) 
‣ Learning Roadmap (suggestions) 
‣ Preliminary plan of final project 
29 
# Using Postman to test
Simply follow the instructions below step by step. 
1. Run the Seed Script 
>> chmod +x seed-k8s.sh 
>> ./seed-k8s.sh 
This script initializes the participants (Consumer/Provider) and registers them with the IdentityHub. 
>> sudo npm install -g newman # Install newman 
2. Check the port in vscode 
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/0510dbf3d8d0209d0346027748e3c5749ac320bd1f2558f670a4a26c2950620c.jpg)

# Using Postman to test
Simply follow the instructions below step by step. 
# 3. Verify in postman
Import the `deployment/postman` folder of our project and modify the values in the environment settings, as shown in the image below: 
Crutial: replace localhost with localhost:58261 (the port you have seen in the last slide!) 
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/aceaa99c46dc2921f20f54448b1c28fb3bc07011d3b3103a5dcbf21581bd3920.jpg)

You should modify it according to your specific port information! 
# Using Postman to test
Simply follow the instructions below step by step. 
# 3. Verify in postman
Choose right environments and collections! 
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/31f2ee613783db4ffd19c67fb906b5284ddbeb191ee46a4a267f4f0e5d88e747.jpg)

![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/83f393ca8e48cf2111292d3993b88b1fbbcf60a839b593b660742def968a1535.jpg)

# Using Postman to test
Simply follow the instructions below step by step. 
# 3. Verify in postman
# Basic Workflow:
Step A: Initiate Negotiation -> Get contractAgreementId. 
Step B: Initiate Transfer -> Get transferProcessId. 
Step C: Download Data -> You will see a JSON List of Photos 
According to the official tutorial, we focus on the ControlPlane 
Management section： 
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/ba976e81aa542318a818614bd5dc8438d9ed3d59ea5e8ee732fe7aec96048631.jpg)

# Using Postman to test
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/da1080ddd6521074689c9c8f32e29d1569fde8f55c9192baa09707b153134a95.jpg)

34 
# Using Postman to test
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/ad230386ea6b9b1db5a8c5c9751ee3492af65ae2de25e5167ab8df5464c96028.jpg)

# Using Postman to test
# Paste the content copied in the previous step here!
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/35012a7c6f16b00c469bfbbf7598e81641ae43ec26f6158bd50f434d036593bc.jpg)

# Using Postman to test
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/1c32026405d83e9076f8d5d670642c301381782d10d05476c5495f3f3a704ed7.jpg)

Use Ctrl+F to search for the copied ID, check its status; if it shows "FINALIZED", it was successful. Then copy the contractagreementid. 
37 
# Using Postman to test
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/7f5d05f2d1d3f0719339a98ca8555635fcf05b43e6815f1b9d726274dea36ec1.jpg)

![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/5e5ded6d66717719b42c07d79a89f2552bc79d67e641a138fa56ad420f557cd6.jpg)

Obtain and copy the transfer ID here, which represents the ID of the current transfer process. 
# Using Postman to test
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/b601d624c1ee5b230d79a7a606f360977923f16ee74b7779993709cd5469aa9a.jpg)

Similarly, use Ctrl+F to search for the transfer ID you just copied. If the status is STARTED, it means the transfer process has started and everything is fine. 
39 
# Using Postman to test
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/cefbd8648a37eb88f4253bc6d046f67efdd4edac00f0038763373ca264f5ba39.jpg)


Click "send," then copy the transferProcessID from this page. We will use this ID to retrieve the address of the actual data.

# Using Postman to test
The transferProcessID here will automatically change to the value we obtained in the previous step, but you can double-check that it's correct before clicking send. 
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/854c1c45a40b82fa07571b299ecfb9bebcbf434c7736681ced7efab81a66344e.jpg)

Then you will get this long string of characters. Please copy it; it will be our proof of obtaining the final data!! 
41 
# Using Postman to test
Similarly, the previous string of characters will be updated here. You can click send after confirming that it is correct! 
![image](https://cdn-mineru.openxlab.org.cn/result/2026-03-17/8c5588e1-ad29-4149-b351-745e583d5c81/934a9f4dc4bc9d5bc3b9e4df2d2ba27333396ac6a0391c1601b08bedaeabd7f7.jpg)

# Possible solutions to the error (for reference only)
1. Delete the old cluster (clean up the environment): 
>> kubectl delete pods -n mvd --all 
>> kubectl get pods -n mvd -w 
>> k3d cluster delete edc-cluster # Delete the specified cluster mvd 
2. Error message: Client version 1.43 is too old: 
Upgrade K3d: 
>> curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash 
>> k3d --version # Make sure the version is newer than v5.6.0. 
3. Kill the process on a specific port (if a port conflict occurs): 
>> fuser -k 80/tcp 
# Possible solutions to the error (for reference only)
4. Clean up Docker remnants: 
>> docker rm -f $(docker ps -aq) 2>/dev/null || true 
>> docker network prune -f 
5. node(s) didn't have free ports... : Delete Traefik 
>> kubectl -n kube-system delete helmchart traefik 
>> kubectl -n kube-system delete helmchart traefik-crd 
You can also record the problems you encounter and your solutions! We would greatly appreciate your contributions! 
44 
# Possible solutions to the error (for reference only)
6. If you encounter “404 Not Found”: 
Install Nginx Ingress Controller: 
* Mark bundle as not supporting multiuse 
< HTTP/1.1 404 Not Found 
>> kubectl -n kube-system delete service traefik 
>> kubectl -n kube-system scale deployment traefik --replicas=0 
>> helm upgrade --install ingress-nginx ingress-nginx \ 
--repo https://kubernetes.github.io/ingress-nginx 
--namespace ingress-nginx --create-namespace 
--set controller.service.type=LoadBalancer 
--set controller.watchIngressWithoutClass=true 
--set controller.ingressClassResource.default=true 
45 
# Outline
‣ Prerequisites 
‣ Setting Up the Toolchain (Inside Container) 
‣ Running MVD 
‣ Extension: Using Real datasets 
‣ Postman Verification (Demonstration) 
Learning Roadmap (suggestions) 
‣ Preliminary plan of final project 
46 
# Learning Roadmap (suggestions)
» START FROM: 
» https://github.com/eclipse-edc/MinimumViableDataspace 
– Follow this PPT and official tutorial to deploy MVD locally (or Dev Containers/virtualbox), Kubernetes is recommended. 
» THEN read the official MVD Documentation (readme) to understand the "Consumer-Provider" flow. (Specifically, 8.4 Policy evaluation functions, because real-world dataspaces rely on strict access control (e.g., "Only EU companies can read this". You may need to explre and customize this later in your own project.) 
» Test the flow using Postman. 
» Try replacing the default dummy data with your own datasets (start with dummy data provided by official MVD, then try APIs like my jsonplaceholder demo, then it’d better to find some other real open datasets). 
47 
# Learning Roadmap (suggestions)
» After completing the above: 
» if you want to learn more about EDC connectors, or if you are not familiar with a particular function (such as Policy or Federated Catalog), you can learn EDC/samples for more details: 
» https://github.com/eclipse-edc/Samples 
Step-by-step reports will be uploaded to Blackboard (For reference only, please refer to the official tutorial for detailed steps). 
Always read the README.md in each sub-folder first! 
» Some tips: 
» How to Study eclipse-edc/Samples 
Start Here: basic/ folder. 
• Learn how to build a simple connector JAR. 
» Next Step: transfer/ folder. 
– Understand the Consumer vs Provider (contract) negotiation flow. 
» Access control -- Policy Evaluation Functions: policy/ folder 
48 
# Outline
Prerequisites 
‣ Setting Up the Toolchain (Inside Container) 
‣ Running MVD 
‣ Extension: Using Real datasets 
‣ Postman Verification (Demonstration) 
‣ Learning Roadmap (suggestions) 
‣ Preliminary plan of final project 
49 
# Preliminary plan of final project
» Format: Group (maximum three people) 
» (Required) Teams must establish a functional Minimum Viable Dataspace (MVD) locally. This serves as the foundation for your ecosystem. Specifically, you need to: 
Clone and deploy the official repository: git clone https://github.com/eclipse-edc/MinimumViableDataspace.git 
– Run it successfully! which means 2 providers and 1 consumer 
must include Negotiation (A successful contract negotiation process between the connectors) and Transfer (Execution of both a Provider Push and a Consumer Pull data transfer) 
» (Extensions) You can then choose to evolve the system into a Federated Ecosystem by implementing the following extensions: 
Real Datasets Integration: replace the default "dummy" data with structured, real-world datasets. (TIPS: Since the MVD uses the HttpData data address type, you should point your Asset's baseUrl to a public REST API (Open Data). You can use the provided jsonplaceholder examples (see bb later) or integrate external open APIs configure the EDC Asset to proxy an existing public URL.) (e.g., OpenWeather, Public Transport APIs...). You do not need to host a database; simply 5 
# Preliminary plan of final project
# – Advanced Policy Enforcement, for example:
Design and enforce specific access control policies (e.g., purpose $=$ research or region $=$ eu). 
• Modify the policy evaluation function. Maybe demonstrate scenarios where: 
Authorized Request: A consumer meeting the policy requirements successfully negotiates and transfers data. 
Unauthorized Request: A consumer failing the policy check is denied during the negotiation phase. 
# » Deliverables
– Format: Group submission (Max 3 members per team). 
– Required Artifacts: 
code.zip: Your project source code. 
Report: need to contain: 
– Essential screenshots and explanations of your process. 
– Insights and observations derived from the experiments. 
51– Explicitly state the specific contributions of each member. 
# Preliminary plan of final project
Demonstration: Offline presentation or Online demonstration video/meeting (subject to professor's update, please keep an eye of bb anouncement) showing the flow: Discovery (Catalog) -> Negotiation (Contract) -> Transfer (Data). 
» Grading: Final scores will be weighted based on individual contributions. 
» Good luck and enjoy building your Dataspace! 
C 
香港中文大學 (深圳)
The Chinese Universityof Hong Kong,Shenzhen 
数据科学学院
School of Data Science 
# CSC4240 (Spring 2026)
# Getting Started with MVD
If you have any questions, please feel free to contact me: shuwenliu@link.cuhk.edu.cn 