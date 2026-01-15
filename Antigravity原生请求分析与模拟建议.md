# Antigravity 原生请求分析与反代模拟建议报告

本报告记录了对 Antigravity 原生扩展（`extension.js`）请求机制的分析结果，旨在通过高度真实的请求模拟，解决反代过程中出现的 429（限流）及风控拦截问题。

---

## 1. 核心通信协议：Connect-RPC

Antigravity 并没有采用标准的 REST API，而是基于 **Connect-RPC**（原 `connect-web`）协议。这是模拟请求的首要前提。

*   **协议版本**：Connect v1。
*   **交互格式**：Protobuf (二进制) 为主，JSON 为辅。
*   **请求类型**：始终为 `POST`。
*   **Content-Type**：
    *   `application/connect+proto` (生产环境常用)
    *   `application/connect+json` (调试或特定接口)

---

## 2. 必须模拟的 HTTP 头部 (Headers)

上游服务器会根据以下特殊头部判定请求是否来自合法的 IDE 客户端：

| Header 键名 | 取值参考 | 角色与建议 |
| :--- | :--- | :--- |
| `Connect-Protocol-Version` | `1` | **核心协议标识**，必须携带。 |
| `x-antigravity-ide-name` | `Antigravity` | 客户端名称，必须对齐。 |
| `x-antigravity-ide-version`| `0.44.11` | 建议根据原生应用的最新版本动态更新。 |
| `x-antigravity-device-id` | `uuid-xxxx...` | **硬件指纹**。上游风控的主要依据。 |
| `x-antigravity-locale` | `zh-CN` | 语言环境标识。 |
| `User-Agent` | `Mozilla/5.0 ... (Electron)` | 必须模拟真机 Electron 渲染进程的 UA。 |
| `Accept-Encoding` | `gzip, deflate, br` | 开启压缩，减少流量特征差异。 |

---

## 3. 元数据 (Metadata) 结构分析

代码中的 `MetadataProvider` 会在每次发送 RPC 请求时构建一个 `Metadata` 消息体并附带在 Payload 或 Header 中：

```json
{
  "ideName": "Antigravity",
  "ideVersion": "0.44.11",
  "extensionName": "antigravity",
  "deviceFingerprint": "unique_hardware_id", // 关键：每台机器唯一
  "apiKey": "ya29.v...",                  // OAuth 令牌
  "triggerId": "random_uuid"              // 本次请求的唯一序列号
}
```

---

## 4. 针对 429 及风控的深度改进建议

目前本项目作为反代服务器，为了彻底解决限流和拦截，建议实施以下策略：

### 4.1 独立设备指纹池 (Fingerprint-per-Account)
*   **现状**：如果反代对所有请求使用同一个指纹，上游会将 100 个账号判定为“在同一台机器上频繁登录”，极易触发 429。
*   **改进**：为账号池中的每个账号生成的**唯一指纹 (device-id)**。在数据库中持久化账号与指纹的绑定关系。

### 4.2 智能 429 熔断与接力
*   **状态感知**：实时解析 `quotaResetDelay` 字段，精确锁定账号至解封时刻。
*   **热接力**：配合 `workbench.desktop.main.js` 的无感换号补丁，当反代层感知到 429 后，立即向前端返回指令或自动转发至下一个指纹完全不同的健康账号。

### 4.3 协议头一致性校验
*   **User-Agent 一致性**：确保反代请求的 `User-Agent` 与 headers 里的 `ideVersion` 版本逻辑闭环（例如：0.44.11 版本必须对应特定的 Electron 内核版本 UA）。

---

## 5. 总结

模拟原生请求的本质是**“降低统计学差异”**。通过从 Connect 协议层、Headers 特征层到设备指纹层全方位对齐原生应用，可以极大地提升多账号池的存活率及请求稳定性。
