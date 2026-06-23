# SPSSGO 开发文档

## 1. 项目概述

SPSSGO 是一个 AI 驱动的数据分析工作台，当前项目由前后端两部分组成：

- 后端：FastAPI + MySQL
- 前端：Vue 3 + Vite + Vue Router
- 统计执行：模板引擎优先，AI 代码生成兜底
- 文件存储：已重构为统一存储抽象，支持 `local` / `s3` 两种后端

当前代码目标是同时支持：

- 本地独立部署
- 后续切换对象存储的生产部署


## 2. 当前技术架构

### 2.1 前端

- 单入口 SPA
- 路由模式：Vue Router `history`
- 当前主要路由：
  - `/`
  - `/login`
  - `/workspace`
  - `/admin`
  - `/help`
  - `/legal`

### 2.2 后端

- FastAPI 提供 REST API
- MySQL 保存业务数据
- `authx` 做登录鉴权
- `Celery + Redis` 承载异步任务
- 兼容本地回退执行，仅用于开发或缺少 Celery 运行时的场景

### 2.3 数据层

MySQL 当前主要承载：

- `users`
- `refresh_tokens`
- `sessions`
- `datasets`
- `dataset_versions`
- `jobs`
- `sandbox_executions`
- `results`

数据库保存的是业务元数据，不直接保存上传的大文件本体。

### 2.4 存储层

已经完成统一存储抽象，业务层不再直接依赖 `uploads/` / `outputs/` 目录。

存储模块：

- [storage/base.py](/c:/Users/Administrator.DESKTOP-854VSP0/Desktop/API自助模式/data-analysis-web/storage/base.py)
- [storage/local.py](/c:/Users/Administrator.DESKTOP-854VSP0/Desktop/API自助模式/data-analysis-web/storage/local.py)
- [storage/s3.py](/c:/Users/Administrator.DESKTOP-854VSP0/Desktop/API自助模式/data-analysis-web/storage/s3.py)
- [storage/service.py](/c:/Users/Administrator.DESKTOP-854VSP0/Desktop/API自助模式/data-analysis-web/storage/service.py)

支持后端：

- `local`
- `s3`

说明：

- `local` 模式用于当前开发和独立部署场景
- `s3` 模式面向 MinIO / AWS S3 / 阿里云 OSS S3 兼容接口 / 腾讯 COS S3 兼容接口


## 技术亮点

### 分析方法自动注册机制

新增分析方法只需在 `backend/analysis/methods/` 下放一个 `.py` 文件，定义 `METHOD_KEY`、`METHOD_META` 和 `run()`，无需改任何注册中心代码。通过 `pkgutil.iter_modules()` 自动发现、`importlib` 动态加载，上线新方法零配置。

### 三引擎降级策略

分析执行走三级降级：
1. **模板引擎优先**——AI 生成 JSON 任务配置，模板引擎直接调度 `METHOD_REGISTRY` 的内置函数执行
2. **R 增强**——信度、EFA、CFA、SEM 等高级方法走独立 R 引擎（`backend/r_runner.py`）
3. **AI 代码兜底**——模板走不通时，AI 生成可执行 Python 代码，失败后带错误反馈重试，最多 3 次

### 统一图表协议

所有分析方法输出标准化图表协议，三种通用类型覆盖全场景：

| chartType | 用途 | 关键字段 |
|---|---|---|
| `category_distribution` | 分类/选项分布 | `labels` / `counts` / `percents` / `variable` |
| `crosstab_distribution` | 交叉列联 | `groupVariable` / `xVariable` / `matrix` |
| `metric_comparison` | 指标对比 | `metric` / `labels` / `values` |

前端公共组件 `AnalysisChartItem` 统一渲染，支持柱状图、条形图、饼图、环形图、折线图、雷达图、悬浮提示、保存导出。新方法只需吐协议数据，不重复造图表轮子。

### Celery 六队列分派

异步任务按类型路由到独立队列，互不阻塞：

| 队列 | 职责 |
|---|---|
| `ingest` | 文件上传与解析 |
| `process` | 数据处理 |
| `analysis` | 分析方法执行 |
| `ai` | AI 规划与解读 |
| `report` | 报告生成 |
| `sandbox` | 自定义代码沙箱执行 |

`ingest` / `process` / `analysis` 共用 `worker-analysis`，`ai` / `report` / `sandbox` 各有独立 worker，通过 `--queues` 参数隔离，可独立扩缩容。


## 3. 已上线功能清单

### 3.1 账号与权限

- 用户登录
- 当前用户信息获取
- 修改用户名
- 修改密码
- 接口鉴权校验

### 3.2 会话管理

- 创建分析会话
- 获取单个会话信息
- 获取会话列表
- 重命名会话
- 删除会话
- 过期会话自动清理
- 管理后台手动清理过期会话

### 3.3 文件上传与解析

- 上传数据文件
- 上传问卷文件
- 数据文件格式校验
- 上传大小限制
- 数据摘要提取
- 问卷文本提取
- 问卷预览元数据保存

当前支持的数据格式：

- Excel：`.xlsx` `.xls`
- CSV：`.csv`
- SPSS：`.sav` `.zsav`
- Stata：`.dta`
- SAS：`.sas7bdat` `.xpt`
- TSV / TXT：`.tsv` `.txt`
- JSON：`.json`
- Parquet：`.parquet`
- 问卷文档：`.docx` `.doc`

### 3.4 AI 规划与执行

- 基于数据摘要和问卷内容生成分析计划
- 模板任务 JSON 生成
- 模板分析执行
- 自定义分析代码生成
- AI 代码执行兜底
- SSE 流式执行反馈
- AI 智能解读结果

### 3.5 数据分析工作台

- 方法列表加载
- 变量列表读取
- 历史分析结果查看
- 单方法直接执行
- AI 助手侧栏
- 结果导出 Word

### 3.6 数据处理

当前已实现的数据处理能力包括：

- 标签处理
- 编码
- 异常值处理
- 无效样本处理
- 新变量生成
- 标准化
- 虚拟变量
- 缺失值处理
- 滑窗转换
- 缩尾 / 截尾
- 降采样
- 加权
- 数学变换
- 样本均衡
- 特征筛选
- PCA 降维

### 3.7 文件访问接口

- 文件列表
- 问卷内容预览
- 原始数据文件下载
- 数据预览
- Word 报告下载

### 3.8 管理后台

- 仪表盘概览
- 会话管理
- 系统设置查看
- 存储用量统计


## Docker 一键部署

项目已完整容器化，支持 `docker compose up -d` 一行命令拉起全套服务：

```powershell
docker compose up -d
```

Compose 编排包含以下服务：

| 服务 | 职责 |
|---|---|
| `app` | FastAPI 后端 + 前端静态文件 |
| `db` | MySQL 8.4 |
| `redis` | Celery 消息队列 + 缓存 |
| `worker-analysis` | ingest / process / analysis 队列消费 |
| `worker-report` | report 队列消费 |
| `worker-ai` | ai 队列消费 |
| `worker-sandbox` | sandbox 队列消费 |

Docker 镜像内置 `Rscript`、`jsonlite`、`lavaan`，无需宿主机额外安装 R。部署后浏览器打开 `http://localhost:8000` 即可使用，是可运行原型的直接证据。


## 4. 当前配置项

配置文件见：

- [config.py](/c:/Users/Administrator.DESKTOP-854VSP0/Desktop/API自助模式/spssgo/backend/config.py)

### 4.1 AI 配置

- `DEEPSEEK_API_KEY`
- `DEEPSEEK_BASE_URL`
- `DEEPSEEK_MODEL`

### 4.2 存储配置

- `STORAGE_BACKEND`
- `LOCAL_STORAGE_ROOT`
- `S3_ENDPOINT_URL`
- `S3_REGION`
- `S3_BUCKET`
- `S3_ACCESS_KEY`
- `S3_SECRET_KEY`
- `S3_KEY_PREFIX`

### 4.3 数据库配置

- `MYSQL_HOST`
- `MYSQL_PORT`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_DATABASE`

### 4.4 系统配置

- `APP_ENV`
- `ALLOW_INSECURE_DEV_DEFAULTS`
- `DB_AUTO_CREATE`
- `MAX_UPLOAD_SIZE_MB`
- `MAX_EXECUTION_SECONDS`
- `MAX_MEMORY_MB`
- `MAX_CONCURRENT_TASKS`
- `SESSION_EXPIRE_HOURS`

### 4.5 管理员配置

- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`
- `ADMIN_SECRET_KEY`


## 5. 当前存储策略

### 5.1 开发环境默认行为

默认：

- `APP_ENV=development`
- `ALLOW_INSECURE_DEV_DEFAULTS=1`
- `DB_AUTO_CREATE=1`
- `STORAGE_BACKEND=local`
- `LOCAL_STORAGE_ROOT=.data/`

因此当前开发环境依然默认走本地存储，但业务主链路已经优先读取 `dataset_versions` 中的标准化数据版本。

### 5.2 local 模式

逻辑分类：

- `uploads/{session_id}/...`
- `datasets/{session_id}/...`
- `outputs/{session_id}/...`

### 5.3 s3 模式

对象 key 逻辑保持一致：

- `uploads/{session_id}/...`
- `datasets/{session_id}/...`
- `outputs/{session_id}/...`

这样业务层不需要关心存储介质差异。

### 5.4 当前实现方式

- 业务代码通过 `storage_service` 统一访问文件
- 分析执行时会先把对象存储文件临时 materialize 到本地
- 分析结束后释放临时文件


## 6. 已完成的重要重构

### 6.1 前端路由重构

- 多 HTML 入口改为单入口 Vue Router
- 地址从 `.html` 形式切换为语义化路由
- 工作台主路由统一为 `/workspace`

### 6.2 存储层重构

- 抽离统一存储接口
- 完成 `local` 实现
- 完成 `s3` 兼容实现骨架
- 后端文件读写从业务代码中收口


## 7. 当前已知限制

### 7.1 存储层

- 已支持 `s3` 实现，但还未做真实 MinIO / OSS / COS 联调验证
- `LOCAL_STORAGE_ROOT` 默认指向项目根目录 `.data/`，容器环境会覆盖到 `/var/lib/spssgo/storage`
- 历史上遗留的 `uploads` 兼容读路径仍保留在开发/管理员兜底场景，不作为正式验收主路径

### 7.2 鉴权与用户系统

- 已支持用户表、角色字段、JWT Access Token、Refresh Token 和 `owner_id` 资源隔离
- 目前仍建议把旧历史数据统一归到初始管理员账号下管理

### 7.3 任务执行

- 当前主路径已拆分为 `ingest / process / analysis / ai / report / sandbox` 队列
- 自定义代码默认应走独立 `sandbox` 执行链路，并记录审计信息
- 本地任务回退模式仅作为开发兼容手段，不作为生产验收依据

### 7.4 报告与结果资产

- 报告文件已能生成和下载
- 结果已支持 `job_id` 与 `dataset_version_id` 追溯，但正式压测报告、故障演练记录和上线回滚材料仍需补齐


## 8. 后续建议优先级

### P0：尽快完成

- 做一次本机异步主链路 smoke 验证并记录结果
- 完成 Compose 准生产环境 smoke、压测和故障演练
- 沉淀压测报告、故障演练记录、上线回滚方案
- 明确旧 `uploads` 兼容路径的保留范围和禁用策略

### P1：建议下一阶段完成

- 做一次 MinIO / S3 兼容服务联调验证
- 补齐对象存储下载缓存策略优化
- 补齐更细的生产部署说明和环境变量清单

### P2：中期演进

- 增加报告版本管理
- 增加结果文件统一归档
- 增加审计日志

### P3：产品化增强

- 多用户体系
- 团队空间 / 项目空间
- 细粒度角色权限
- 更完整的帮助中心
- 付费能力 / 授权能力
- 配额控制
- 存储生命周期管理


## 9. 推荐的下一步开发顺序

建议按照下面顺序继续推进：

1. 收尾 `dataset_versions` 主路径和旧兼容路径策略
2. 本机跑通异步主链路 smoke 和 k6 冒烟
3. Compose 准生产环境跑 smoke、正式压测和故障演练
   建议直接使用 `scripts/run-compose-validation.ps1` 与 `scripts/run-compose-failure-drills.py`
4. 产出第 6 阶段交付材料
5. 再补 MinIO / S3 联调和更完整的生产部署文档


## 10. 说明

本文件用于记录当前代码状态和后续开发方向，重点是：

- 让“现在已经做了什么”可快速对齐
- 让“下一步应该做什么”可直接排期
- 为本地独立部署和对象存储切换提供统一认知
## 监控本地联调

如果你想在本地一起拉起 Prometheus 和 Grafana，可以在复制 `.env.example` 为 `.env` 后执行：

```powershell
docker compose --profile monitoring up -d
```

相关配置文件位于：

- [monitoring/prometheus.yml](/c:/Users/Administrator.DESKTOP-854VSP0/Desktop/API自助模式/spssgo/monitoring/prometheus.yml)
- [monitoring/alerts.yml](/c:/Users/Administrator.DESKTOP-854VSP0/Desktop/API自助模式/spssgo/monitoring/alerts.yml)
- [monitoring/grafana/dashboards/spssgo-overview.json](/c:/Users/Administrator.DESKTOP-854VSP0/Desktop/API自助模式/spssgo/monitoring/grafana/dashboards/spssgo-overview.json)

本仓库当前环境里没有预装 `docker` / `docker compose`，因此如果你在别的机器验证这套监控栈，记得先安装对应工具。

## 备份与恢复联调

逻辑备份：

```powershell
python scripts/backup_mysql.py --output-dir backups/mysql --gzip --retention-days 7
python scripts/restore_mysql.py backups/mysql/your-backup.sql.gz --dry-run
```

生命周期规则 dry-run：

```powershell
python scripts/apply_s3_lifecycle.py --config ops/s3-lifecycle.example.json --bucket your-bucket --dry-run
```

当前仓库已经把 `backups/` 加入忽略规则，便于本地定时任务直接输出到仓库旁路目录。
