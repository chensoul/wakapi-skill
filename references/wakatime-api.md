# WakaTime 云端接口说明（与本 skill 相关）

[WakaTime](https://wakatime.com) 官方提供 HTTP API，本仓库 CLI 仅使用 **v1 下与统计相关的只读 GET**（与插件上报心跳无关）。

## 官方文档

- 开发者文档：<https://wakatime.com/developers>
- API 概览：<https://wakatime.com/api/>

## Base URL

默认（`WAKAPI_URL` 未设置或指向 WakaTime）：

```text
https://wakatime.com/api/v1
```

所有下列路径均接在该前缀之后（无前导 `/` 重复问题：前缀已含 `/api/v1`）。

## 认证

官方说明：使用 **HTTP Basic**，将 **API Key 经 Base64 编码** 放入 `Authorization`（与 Wakapi 本 skill 用法一致）：

```http
Authorization: Basic <base64(api_key)>
Accept: application/json
```

也可使用文档中描述的 OAuth / `api_key` query 等方式；**本脚本仅实现 Basic**。

## 本 CLI 使用的端点（GET）

| 子命令 | 路径 | 备注 |
|--------|------|------|
| `health` / `projects` | `/users/current/projects` | `health` 以 HTTP 200 为健康 |
| `status-bar` | 脚本实际请求：`https://wakatime.com/api/v1/users/current/statusbar/today` | 与 WakaTime 路径一致（`statusbar` 无下划线） |
| `all-time-since` | `/users/current/all_time_since_today` | |
| `stats <range>` | `/users/current/stats/{range}` | `range` 示例：`last_7_days`、`last_30_days`、`2025`、`2025-03`、`all_time` 等；可选 query：`timeout`、`writes_only` |
| `summaries` | `/users/current/summaries` | `start`+`end`（`YYYY-MM-DD`）或 `range`（预设文案如 `Last 7 Days`）；可选：`project`、`branches`、`timezone`、`timeout`（按键超时，非 HTTP）、`writes_only` |

具体 query 与响应字段以官方文档为准。

## CLI 与 HTTP 超时（本仓库脚本）

| 子命令 | HTTP 客户端超时 |
|--------|-----------------|
| `health` / `projects` / `status-bar` / `all-time-since` | 子命令 **`--timeout`** = HTTP socket；默认 **15** s（`health`）或 **60** s |
| `stats` / `summaries` | HTTP **固定 60** s；**`stats --timeout`** / **`summaries --timeout`** = **API** 查询参数（keystroke timeout），不是 HTTP 超时 |

## curl 示例（请替换 API Key）

```bash
API_KEY='你的密钥'
B64=$(printf '%s' "$API_KEY" | base64 | tr -d '\n')

curl -sS -H "Authorization: Basic $B64" -H 'Accept: application/json' \
  'https://wakatime.com/api/v1/users/current/projects'

curl -sS -H "Authorization: Basic $B64" -H 'Accept: application/json' \
  'https://wakatime.com/api/v1/users/current/statusbar/today'
```

## 说明

- 部分能力（团队、排行榜、OAuth 等）不在本 skill 范围内。
- 若使用自建兼容服务（如 Wakapi），路径前缀可能与纯 WakaTime 不同，见 [wakapi-api.md](wakapi-api.md)。
