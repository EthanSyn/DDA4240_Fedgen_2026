# FedGen/MVD 合同谈判 403 Unauthorized 故障排查文档

## 问题概述

在基于 Eclipse Dataspace Components (EDC) Minimum Viable Dataspace (MVD) 构建的 FedGen 去中心化数据空间中，Consumer 向 Provider 发起合同谈判（Contract Negotiation）时，持续返回 **403 Unauthorized** 或 **401 Unauthorized** 错误，Catalog 查询也会失败。

**错误表现**：

```
Unable to obtain credentials: Failed to fetch client secret from the vault
```

```
Invalid query: requested Credentials outside of scope.
```

```
Cannot publish DID '...' because the ParticipantContext state is not 'ACTIVATED', but 'CREATED'.
```

## 系统架构背景

MVD 的 DCP (Decentralized Claims Protocol) 认证流程如下：

```
Consumer CP                Provider CP                Consumer IH
    |                          |                          |
    |--- ContractRequest ----->|                          |
    |   (附带 SI Token +       |                          |
    |    access_token)         |                          |
    |                          |--- PresentationQuery --->|
    |                          |   (请求 credentials)     |
    |                          |<-- VP (credentials) -----|
    |                          |                          |
    |                          | [验证 credentials,       |
    |                          |  评估 policy]            |
    |<--- FINALIZED -----------|                          |
```

每个环节都有严格的密钥、DID、credential 匹配要求。本次故障涉及**三个互相关联的根本问题**，任一问题都会导致整个流程失败。

---

## 根因 1：InMemoryVault 中私钥被公钥覆盖

### 现象

所有组件（IdentityHub、ControlPlane、DataPlane、CatalogServer）在尝试签名时失败，因为 vault 中存储的"私钥"实际上是公钥。

### 原因分析

`SecretsExtension.java` 在 `InMemoryVault` 模式下硬编码了一对 EC 密钥，分别存储到两个 alias：

```java
vault.storeSecret(context.getConfig().getString(STS_PRIVATE_KEY_ALIAS), privateKey);
vault.storeSecret(context.getConfig().getString(STS_PUBLIC_KEY_ID), publicKey);
```

**问题在于**：所有 Terraform 模块的 `variables.tf` 中，这两个 alias 配置为相同的值：

```hcl
# deployment/modules/identity-hub/variables.tf (以及 connector、catalog-server、vault)
default = {
  sts-private-key   = "key-1"
  sts-public-key-id = "key-1"   # <-- 与 private key 相同!
}
```

`InMemoryVault.storeSecret()` 内部使用 `ConcurrentHashMap.put()`，第二次写入会**覆盖**第一次：

```java
// InMemoryVault.java
public Result<Void> storeSecret(String key, String value) {
    secrets.put(key, value);  // Map.put() 覆盖已有值
    return Result.success();
}
```

**结果**：vault 中 alias `key-1` 存储的是**公钥 PEM**，私钥丢失。

对于 ControlPlane，alias 格式为 `{participantId}#key-1`，同样存在覆盖：

| 配置项 | 值 |
|---|---|
| `EDC_IAM_STS_PRIVATEKEY_ALIAS` | `did:web:consumer-identityhub%3A7083:consumer#key-1` |
| `EDC_IAM_STS_PUBLICKEY_ID` | `did:web:consumer-identityhub%3A7083:consumer#key-1` |

### 修复

将所有模块的 `sts-public-key-id` 改为不同的 alias：

```hcl
# 4 个文件需要修改:
# - deployment/modules/identity-hub/variables.tf
# - deployment/modules/connector/variables.tf
# - deployment/modules/catalog-server/variables.tf
# - deployment/modules/vault/variables.tf

default = {
  sts-private-key   = "key-1"
  sts-public-key-id = "key-1-pub"   # <-- 不同 alias，避免覆盖
}
```

---

## 根因 2：DID Document 中的公钥与签名密钥不匹配

### 现象

Provider 验证 Consumer 的 SI Token 时签名验证失败。DID Document 中发布的公钥与实际用于签名的私钥不对应。

### 原因分析

原始 seed 脚本使用 `keyGeneratorParams` 创建 participant：

```json
{
  "key": {
    "keyId": "did:web:consumer-identityhub%3A7083:consumer#key-1",
    "privateKeyAlias": "did:web:consumer-identityhub%3A7083:consumer#key-1",
    "keyGeneratorParams": { "algorithm": "EC" }
  }
}
```

IdentityHub 收到此请求后会**生成一对全新的 EC 密钥**，将生成的公钥写入 DID Document，生成的私钥存入 IH 的 InMemoryVault。

**但是**，ControlPlane 的 `SecretsExtension` **硬编码了另一把 EC 密钥**到 ControlPlane 的 InMemoryVault。两者是不同的密钥对：

| 组件 | 密钥来源 | 存储位置 |
|---|---|---|
| IdentityHub | `keyGeneratorParams` 生成 | IH 的 InMemoryVault |
| ControlPlane | `SecretsExtension` 硬编码 | CP 的 InMemoryVault |
| DID Document | 来自 IH 生成的公钥 | DidResourceStore |

当 ControlPlane 使用硬编码私钥签名 token 时，Provider 用 DID Document 中（来自 IH 生成的）公钥验证——**签名验证必然失败**。

### 修复

seed 脚本改用 `publicKeyPem`，直接提供与 `SecretsExtension` 硬编码密钥匹配的公钥：

```json
{
  "key": {
    "keyId": "did:web:consumer-identityhub%3A7083:consumer#key-1",
    "privateKeyAlias": "key-1",
    "publicKeyPem": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE1l0Lof0a1yBc8KXhesAnoBvxZw5r\noYnkAXuqCYfNK3ex+hMWFuiXGUxHlzShAehR6wvwzV23bbC0tcFcVgW//A==\n-----END PUBLIC KEY-----"
  }
}
```

关键变化：
- **`publicKeyPem`** 替代 `keyGeneratorParams`：DID Document 直接使用提供的公钥，与 `SecretsExtension` 匹配
- **`privateKeyAlias: "key-1"`** 而非 `did:web:...:consumer#key-1`：与 `SecretsExtension` 在 IH vault 中存储私钥的 alias 一致

### 密钥一致性对照表（修复后）

| 组件 | Alias | 内容 | 来源 |
|---|---|---|---|
| IH Vault | `key-1` | EC 私钥 PEM | SecretsExtension |
| IH Vault | `key-1-pub` | EC 公钥 PEM | SecretsExtension |
| CP Vault | `{did}#key-1` | EC 私钥 PEM | SecretsExtension |
| CP Vault | `{did}#key-1-pub` | EC 公钥 PEM | SecretsExtension |
| DID Document | `{did}#key-1` | EC 公钥 JWK | seed 脚本 publicKeyPem |

三处公钥**完全一致**，私钥来自同一份硬编码源。

---

## 根因 3：Participant 未激活 + STS Client Secret 缺失

### 现象 A：DID Document 返回 204 No Content

其他组件通过 `did:web` 解析请求 DID Document 时，IdentityHub 返回 HTTP 204（空响应）。

### 原因分析 A

`DidWebController` 查询 `DidResourceStore` 时仅返回 **state = PUBLISHED** 的 DID 资源：

```java
// DidWebController.getDidDocument() 伪代码
QuerySpec query = QuerySpec.Builder.newInstance()
    .filter(new Criterion("state", "=", DidState.PUBLISHED.code()))
    .filter(new Criterion("did", "=", parsedDid))
    .build();
```

Participant 创建后处于 `CREATED` 状态（ordinal=0），DID Resource 处于 `GENERATED` 状态，不会被返回。

`ParticipantContextState` 枚举值：

| 枚举 | Ordinal（API 返回值） |
|---|---|
| `CREATED` | 0 |
| `ACTIVATED` | 1 |
| `DEACTIVATED` | 2 |

> **注意**：创建参数中的 `"active": true` 并不会自动激活 participant。需要调用独立的激活 API。

### 修复 A

seed 脚本中显式调用激活 API：

```bash
CONSUMER_B64=$(echo -n "did:web:consumer-identityhub%3A7083:consumer" | base64 -w0)
curl -X POST "${IH_URL}/api/identity/v1alpha/participants/${CONSUMER_B64}/state?isActive=true" \
  -H "x-api-key: ${API_KEY}"
```

### 现象 B：Catalog 查询返回 "Failed to fetch client secret"

```
Unable to obtain credentials: Failed to fetch client secret from the vault
with alias: did:web:consumer-identityhub%3A7083:consumer-sts-client-secret
```

### 原因分析 B

ControlPlane 的 base BOM (`libs.edc.bom.controlplane`) 包含 **Remote STS Client**（不仅在 SQL BOM 中）。它通过 OAuth 2.0 Client Credentials 从 IdentityHub 的 STS 端点获取 token，需要 `client_secret`。

创建 Participant 时 API 返回 `clientSecret`，必须存储到 ControlPlane 的 vault 中：

```
EDC_IAM_STS_OAUTH_CLIENT_SECRET_ALIAS = "{participantId}-sts-client-secret"
```

### 修复 B

通过 Secrets Management API 将 client secret 写入各 ControlPlane：

```bash
curl -X POST "${CP_URL}/api/management/v3/secrets" \
  -H "x-api-key: password" -H "Content-Type: application/json" \
  -d '{
    "@context": {"edc": "https://w3id.org/edc/v0.0.1/ns/"},
    "@type": "https://w3id.org/edc/v0.0.1/ns/Secret",
    "@id": "did:web:consumer-identityhub%3A7083:consumer-sts-client-secret",
    "https://w3id.org/edc/v0.0.1/ns/value": "<client-secret-from-participant-creation>"
  }'
```

---

## 修改的文件清单

| 文件 | 修改内容 |
|---|---|
| `deployment/modules/identity-hub/variables.tf` | `sts-public-key-id: "key-1"` → `"key-1-pub"` |
| `deployment/modules/connector/variables.tf` | `sts-public-key-id: "key-1"` → `"key-1-pub"` |
| `deployment/modules/catalog-server/variables.tf` | `sts-public-key-id: "key-1"` → `"key-1-pub"` |
| `deployment/modules/vault/variables.tf` | `sts-public-key-id: "key-1"` → `"key-1-pub"` |
| `fedgen/scripts/seed_mvd.sh` | 使用 `publicKeyPem`；添加激活步骤；添加 STS secret 存储 |

## 完整 Seed 流程（修复后）

```
1. 等待 ControlPlane 就绪（健康检查）
2. 通过 Newman 种子化 Asset/Policy/Contract 数据
3. 创建 Consumer Participant（publicKeyPem + privateKeyAlias=key-1）
4. 创建 Provider Participant（同上）
5. 将 STS Client Secret 写入各 ControlPlane vault
6. 激活 Consumer 和 Provider Participant（POST .../state?isActive=true）
7. 等待 DID Document 发布
8. 创建 Issuer Participant
9. 种子化 Issuer 数据
```

## 验证方法

```bash
# 1. 验证 DID Document 可解析
kubectl exec -n mvd deployment/consumer-identityhub -- \
  curl -s http://consumer-identityhub:7083/consumer/did.json | jq .id
# 期望: "did:web:consumer-identityhub%3A7083:consumer"

# 2. 验证 Catalog 查询
curl -X POST http://127.0.0.1/consumer/cp/api/management/v3/catalog/request \
  -H "Content-Type: application/json" -H "X-Api-Key: password" \
  -d '{"@context":["https://w3id.org/edc/connector/management/v0.0.1"],
       "counterPartyAddress":"http://provider-manufacturing-controlplane:8082/api/dsp",
       "counterPartyId":"did:web:provider-identityhub%3A7083:provider",
       "protocol":"dataspace-protocol-http"}'
# 期望: 返回 asset-1, asset-2

# 3. 验证合同谈判
# 发起 ContractRequest 后轮询状态
curl http://127.0.0.1/consumer/cp/api/management/v3/contractnegotiations/{id} \
  -H "X-Api-Key: password" | jq .state
# 期望: "FINALIZED"
```

## 调试技巧

- **查看 IH 日志**：`kubectl logs -n mvd deployment/consumer-identityhub | grep -i "WARN\|ERROR\|publish\|activ"`
- **检查 Participant 状态**：state=0 表示 CREATED，state=1 表示 ACTIVATED
- **DID web 解析**：`did:web:host%3Aport:path` 解析为 `http://host:port/path/did.json`，**注意 hostname 必须匹配**
- **解码 JWT**：`echo "<jwt>" | cut -d. -f2 | base64 -d 2>/dev/null | jq .` 查看 token 中的 claims
- **InMemoryVault 是非持久化的**：每次 pod 重启后所有 vault 数据丢失，需要重新 seed
