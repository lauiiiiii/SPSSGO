# SPSSGO Frontend

SPSSGO 前端基于 Vue 3 与 Vite 构建，负责数据管理、数据处理、数据分析与结果展示等交互界面。

## API 地址配置

前端默认同源请求后端接口，适合本地 Vite proxy 或后端托管 `dist` 的单机部署。

分离部署时，修改 `frontend/.env` 文件，重新构建：

```env
VITE_API_BASE_URL=https://api.example.com
```

后端也要同步配置 `CORS_ALLOW_ORIGINS` 放行前端域名，例如：

```env
CORS_ALLOW_ORIGINS=https://www.example.com
```
