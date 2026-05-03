# SPSSGO API 对接说明

这里是前后端分离部署时给前端和集成方看的接口说明。在线调试仍以 FastAPI 自动文档为准：

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## 部署对接

前端通过 `frontend/public/spssgo-config.js` 配置后端 API 地址：

```js
window.__SPSSGO_CONFIG__ = {
  apiBaseUrl: 'https://api.example.com',
}
```

后端通过 `.env` 放行前端域名：

```env
CORS_ALLOW_ORIGINS=https://www.example.com
```

如果前端和后端同源部署，`apiBaseUrl` 留空即可。

## 鉴权

除登录、刷新令牌、健康检查和公开分享访问外，业务接口都需要 Bearer Token：

```http
Authorization: Bearer <access_token>
```

登录：

```http
POST /api/login
Content-Type: application/json
```

```json
{
  "username": "admin",
  "password": "spssgo2024"
}
```

成功后前端保存：

- `access_token`：用于请求头鉴权
- `refresh_token`：用于刷新访问令牌
- `username` / `role` / `user_id`：用于前端展示和权限判断

## 推荐前端主流程

1. 登录：`POST /api/login`
2. 创建会话：`POST /api/session`
3. 上传数据：`POST /api/upload/{session_id}`
4. 等待上传解析任务完成：优先 `GET /api/jobs/{job_id}/events`，失败后轮询 `GET /api/jobs/{job_id}`
5. 获取变量和预览：`GET /api/variables/{session_id}`、`GET /api/data-preview/{session_id}`
6. 执行数据处理或分析：
   - 数据处理：`POST /api/process/{session_id}`
   - 单个分析方法：`POST /api/execute-method/{session_id}`
   - AI 分析计划：`POST /api/plan/{session_id}`
   - 执行整套计划：`POST /api/execute/{session_id}`
7. 获取结果：`GET /api/results/{session_id}`
8. 生成报告：`POST /api/download/{session_id}`
9. 下载任务产物：`GET /api/jobs/{job_id}/output`

## 异步任务

耗时接口通常返回 `job_id`，前端不要一直等 HTTP 请求阻塞完成。

典型响应：

```json
{
  "accepted": true,
  "job_id": "job_abc123",
  "status": "queued"
}
```

任务状态：

```http
GET /api/jobs/{job_id}
```

常见状态：

- `queued`：已排队
- `running`：执行中
- `succeeded`：成功
- `failed`：失败
- `canceled`：已取消

SSE 事件流：

```http
GET /api/jobs/{job_id}/events
Accept: text/event-stream
```

网关或反向代理要关闭 SSE 缓冲，否则前端会收不到实时进度。

SSE 消息格式：

```text
event: job
data: {"id":"job_abc123","status":"running","progress":60}

event: done
data: {"id":"job_abc123","status":"succeeded","progress":100}
```

前端处理建议：

- 优先建立 SSE 连接，实时刷新任务状态。
- SSE 报错或浏览器不支持时，降级轮询 `GET /api/jobs/{job_id}`。
- 收到 `succeeded`、`failed`、`canceled` 后停止监听或轮询。
- `succeeded` 后按任务类型读取结果或下载产物。

## 文件上传和下载

上传数据：

```http
POST /api/upload/{session_id}
Content-Type: multipart/form-data
```

字段：

- `file`：上传文件，支持 Excel、CSV、SPSS、Stata、SAS、JSON、Parquet 等格式。

下载文件：

- `GET /api/data-file/{session_id}`：下载当前数据文件
- `GET /api/data-file/{session_id}/export?format=xlsx`：按格式导出数据文件
- `GET /api/jobs/{job_id}/output`：下载任务产物，例如 Word 报告

下载接口返回二进制流，前端不要按 JSON 解析。文件名优先读取响应头 `Content-Disposition`。

## 核心接口分组

### Auth

- `POST /api/login`：登录
- `POST /api/refresh`：刷新 token
- `GET /api/me`：获取当前用户
- `POST /api/change-username`：修改用户名
- `POST /api/change-password`：修改密码

### Session

- `POST /api/session`：创建分析会话
- `GET /api/sessions`：获取我的会话列表
- `GET /api/session/{session_id}`：获取会话详情
- `PATCH /api/session/{session_id}/title`：重命名会话
- `DELETE /api/session/{session_id}`：删除会话

### Files

- `POST /api/upload/{session_id}`：上传数据文件
- `GET /api/files/{session_id}`：获取会话文件列表
- `GET /api/questionnaire/{session_id}/{filename}`：读取问卷内容
- `GET /api/data-preview/{session_id}`：获取数据预览
- `GET /api/variables/{session_id}`：获取变量列表
- `GET /api/variable-values/{session_id}/{column_name}`：获取变量取值
- `GET /api/data-file/{session_id}`：下载原始数据文件
- `GET /api/data-file/{session_id}/export?format=xlsx`：导出数据文件

### Processing

- `POST /api/process/{session_id}`：提交数据处理任务
- `PATCH /api/variables/{session_id}/{column_name}/rename`：重命名变量
- `PATCH /api/variables/{session_id}/{column_name}/type`：修改变量类型
- `DELETE /api/variables/{session_id}/{column_name}`：删除变量
- `GET /api/dataset-versions/{session_id}`：获取数据集版本
- `POST /api/dataset-versions/{session_id}/activate`：切换数据集版本

### Analysis

- `GET /api/methods`：获取分析方法元数据
- `GET /api/methods/{method_key}`：获取单个分析方法参数详情
- `POST /api/plan/{session_id}`：提交 AI 分析计划任务
- `POST /api/execute/{session_id}`：提交整套分析执行任务
- `POST /api/execute-stream/{session_id}`：流式执行分析计划
- `POST /api/execute-method/{session_id}`：提交单个统计方法任务
- `POST /api/ai-interpret`：提交 AI 结果解读任务
- `GET /api/results/{session_id}`：获取分析结果
- `PATCH /api/results/{session_id}/{result_id}`：重命名分析结果
- `DELETE /api/results/{session_id}/{result_id}`：删除分析结果
- `POST /api/download/{session_id}`：提交 Word 报告生成任务

统计分析方法的 `method` 与 `params` 详见 [ANALYSIS_METHOD_PARAMS.md](./ANALYSIS_METHOD_PARAMS.md)。该文档由后端 `METHOD_META` 自动生成，当前覆盖 `/api/methods` 返回的全部统计分析方法。

如果只想查某一个方法，可调用：

```http
GET /api/methods/frequency
```

返回里重点看：

- `meta`：方法名称、分类、变量槽位、额外选项
- `slot_params_example`：按前端槽位填写的示例
- `execute_params_example`：后端最终执行时读取的 `params` 示例

### Jobs

- `GET /api/jobs/{job_id}`：获取任务详情
- `GET /api/jobs/{job_id}/events`：监听任务 SSE 事件
- `GET /api/jobs/{job_id}/output`：下载任务产物
- `POST /api/jobs/{job_id}/cancel`：取消任务
- `POST /api/jobs/{job_id}/retry`：重试任务

### Share

- `POST /api/shared-reports`：创建报告分享
- `GET /api/shared-reports/{share_token}`：读取公开分享报告
- `POST /api/shared-reports/{share_token}/access`：访问带密码分享报告

### Admin

管理员接口统一在 `/api/admin/*` 下，需要管理员角色。普通用户请求会被拒绝。

## 常见错误

- `400`：请求参数不合法或业务校验失败
- `401`：未登录、Token 缺失或 Token 失效
- `403`：权限不足
- `404`：资源不存在，或当前用户无权访问
- `409`：资源状态冲突，例如会话正在被任务写入
- `429`：触发限流
- `500`：服务端异常

错误响应通常是：

```json
{
  "detail": "用户名或密码错误"
}
```

参数校验错误可能是 FastAPI 默认结构：

```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

前端建议统一封装错误解析：

- `detail` 是字符串：直接展示。
- `detail` 是对象：优先展示 `detail.message`。
- `detail` 是数组：展示“请求参数不完整或格式错误”，详细内容写入调试日志。

## Schema 完整度

`/docs` 目前已经补充核心链路的请求体、响应体、示例、错误模型、文件流和 SSE 说明。分析方法的 `params` 属于动态结构，完整清单见 [ANALYSIS_METHOD_PARAMS.md](./ANALYSIS_METHOD_PARAMS.md)。

后续如果要做 SDK 级文档，建议继续从 `METHOD_META` 自动生成类型定义，不要手写一份容易和代码跑偏的清单。

## 文档形态说明

Swagger UI 是开发调试台，适合在线试接口和导出 OpenAPI。真正对外的开发者文档通常会再做一层产品化页面，例如 Stripe、GitHub、OpenAI、阿里云、腾讯云这类文档站：左侧导航、场景教程、接口参考、错误码、示例代码分开写。

本项目当前采用“双轨”：

- `/docs`：自动接口参考和在线调试
- `docs/API.md`：前后端分离部署和主流程对接说明
- `docs/ANALYSIS_METHOD_PARAMS.md`：统计分析方法 `method + params` 自动生成文档
