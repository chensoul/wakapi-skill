# Wakapi 接口说明（与本 skill 相关）

[Wakapi](https://github.com/muety/wakapi) 是自托管的编码时间统计服务，提供 **原生 REST API** 与 **WakaTime 兼容** 路由。本仓库 CLI 只使用 **只读、与 WakaTime 形状一致的 GET** 接口。

## 官方资源

- 项目：<https://github.com/muety/wakapi>
- 公开实例（示例）：<https://wakapi.dev>

## 认证

与本 skill 脚本一致：请求头使用 **HTTP Basic**，值为 **API Key 的 Base64**（与 WakaTime 文档写法相同）：

```http
Authorization: Basic <base64(api_key)>
Accept: application/json
```

服务端对 `Authorization` 的解析见 Wakapi 源码中的 `ExtractBearerAuth`（支持 `Basic` / `Bearer` + Base64 载荷）。

## 路径前缀（读 stats 时）

设实例根为 `WAKAPI_BASE_URL`（无尾部 `/`），例如 `https://wakapi.dev`。

| 用途 | 前缀 | 说明 |
|------|------|------|
| 多数「WakaTime 形状」只读接口 | `{origin}/api/compat/wakatime/v1` | `projects`、`stats`、`summaries`、`all-time-since`、以及 `health` 探测用的 projects 等 |
| 今日状态条 | `{origin}/api/v1` | **仅** `…/users/current/statusbar/today` 固定走 `/api/v1`（Wakapi 在 `/api` 路由器上同时挂了 `/v1/...` 与 compat 路由） |

> 与 `scripts/wakatime_query.py` 一致：**非 `wakatime.com` 主机**用 compat 前缀；**`status-bar` 子命令**始终请求 `{origin}/api/v1/users/current/statusbar/today`。

## 本 CLI 使用的端点（GET）

| 子命令 | 路径（接在上表对应前缀后，status-bar 例外见上） |
|--------|--------------------------------------------------|
| `health` / `projects` | `/users/current/projects` |
| `all-time-since` | `/users/current/all_time_since_today` |
| `stats <range>` | `/users/current/stats/{range}`，可选 query：`timeout`、`writes_only` |
| `summaries` | `/users/current/summaries`，query：`start`+`end` 或 `range`，以及 `project`、`branches`、`timezone`、`timeout`、`writes_only` 等 |
| `status-bar` | **完整路径** `{origin}/api/v1/users/current/statusbar/today`（无前缀拼接规则上的例外） |

`{range}` 需 URL 编码（如 `last_7_days`、`all_time`）。

## CLI 与 HTTP 超时（本仓库脚本）

| 子命令 | HTTP 客户端超时 |
|--------|-----------------|
| `health` / `projects` / `status-bar` / `all-time-since` | 可通过子命令 **`--timeout`** 设置；默认分别为 **15** s（仅 `health`）与 **60** s |
| `stats` / `summaries` | 固定 **60** s；子命令上的 **`--timeout`**（若有）表示 **API query**（按键/keystroke 超时），勿与 HTTP 混淆 |

## 其他 API（本 skill 未封装）

- **心跳写入**、用户设置等走 Wakapi **原生** `/api/...` 路由，与上表 compat 前缀不同；需查 Wakapi 文档或源码中的 `routes/api`。
- 若部署在子路径（`base_path`），实际 URL 需加上配置中的前缀；本脚本默认按「根路径部署」拼接。

## curl 示例（请替换密钥与主机）

```bash
API_KEY='你的密钥'
B64=$(printf '%s' "$API_KEY" | base64 | tr -d '\n')
ORIGIN='https://wakapi.dev'

curl -sS -H "Authorization: Basic $B64" -H 'Accept: application/json' \
  "$ORIGIN/api/compat/wakatime/v1/users/current/projects"

curl -sS -H "Authorization: Basic $B64" -H 'Accept: application/json' \
  "$ORIGIN/api/v1/users/current/statusbar/today"
```
