# -*- coding: utf-8 -*-
"""OpenAPI 文档增强层，只补接口说明和鉴权标记，别写业务逻辑。"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

OPENAPI_DESCRIPTION = """
SPSSGO 前后端分离 API 文档。

对接规则：

- 前端通过 `spssgo-config.js` 的 `apiBaseUrl` 指向后端服务，例如 `https://api.example.com`。
- 需要登录的接口统一使用 `Authorization: Bearer <access_token>` 请求头。
- 文件上传使用 `multipart/form-data`；下载接口返回二进制流。
- 异步任务接口先返回 `job_id`，前端再通过 `/api/jobs/{job_id}` 轮询或 `/api/jobs/{job_id}/events` 监听 SSE。
- 分离部署时，后端必须配置 `CORS_ALLOW_ORIGINS` 放行前端域名。
""".strip()

OPENAPI_TAGS = [
    {"name": "Auth", "description": "登录、刷新令牌、当前用户和账号资料接口。"},
    {"name": "Session", "description": "分析会话管理。会话是数据、变量、分析结果的业务容器。"},
    {"name": "Datasets", "description": "我的数据集、数据集文件夹和版本归档接口。"},
    {"name": "Files", "description": "数据文件上传、预览、变量读取和文件下载。"},
    {"name": "Processing", "description": "数据处理、变量重命名、变量类型和数据集版本管理。"},
    {"name": "Analysis", "description": "AI 分析计划、统计方法执行、结果管理和 Word 报告生成。"},
    {"name": "Jobs", "description": "异步任务状态、SSE 事件、任务产物下载、取消和重试。"},
    {"name": "Share", "description": "分析报告公开分享和访问。"},
    {"name": "Admin", "description": "管理员后台接口，只允许管理员角色访问。"},
    {"name": "Health", "description": "健康检查和就绪检查。"},
]

COMPONENT_SCHEMAS = {
    "ApiError": {
        "type": "object",
        "properties": {
            "detail": {
                "oneOf": [
                    {"type": "string"},
                    {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "description": "机器可读错误码"},
                            "message": {"type": "string", "description": "给用户看的错误信息"},
                        },
                    },
                    {
                        "type": "array",
                        "items": {"type": "object"},
                    },
                ],
                "description": "错误详情。FastAPI 参数校验错误会返回数组，业务错误通常返回字符串或对象。",
            }
        },
        "required": ["detail"],
    },
    "LoginRequest": {
        "type": "object",
        "properties": {
            "username": {"type": "string", "description": "登录用户名", "example": "admin"},
            "password": {"type": "string", "description": "登录密码", "example": "spssgo2024"},
        },
        "required": ["username", "password"],
    },
    "TokenResponse": {
        "type": "object",
        "properties": {
            "token": {"type": "string", "description": "访问令牌，兼容旧前端字段"},
            "access_token": {"type": "string", "description": "访问令牌，推荐使用该字段"},
            "refresh_token": {"type": "string", "description": "刷新令牌"},
            "username": {"type": "string", "description": "用户名"},
            "role": {"type": "string", "description": "角色，常见值：user/admin"},
            "user_id": {"type": "integer", "description": "用户 ID"},
        },
        "required": ["access_token", "refresh_token", "username", "role", "user_id"],
    },
    "RefreshRequest": {
        "type": "object",
        "properties": {
            "refresh_token": {"type": "string", "description": "登录或刷新接口返回的刷新令牌"},
        },
        "required": ["refresh_token"],
    },
    "CurrentUser": {
        "type": "object",
        "properties": {
            "user_id": {"type": "integer", "description": "用户 ID"},
            "username": {"type": "string", "description": "用户名"},
            "role": {"type": "string", "description": "角色"},
            "created_at": {"type": "string", "nullable": True, "description": "创建时间"},
            "last_login_at": {"type": "string", "nullable": True, "description": "最后登录时间"},
        },
    },
    "SuccessResponse": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean", "description": "是否成功"},
        },
    },
    "ChangeUsernameRequest": {
        "type": "object",
        "properties": {
            "new_username": {"type": "string", "description": "新用户名"},
        },
        "required": ["new_username"],
    },
    "ChangePasswordRequest": {
        "type": "object",
        "properties": {
            "old_password": {"type": "string", "description": "当前密码"},
            "new_password": {"type": "string", "description": "新密码，至少 6 位"},
        },
        "required": ["old_password", "new_password"],
    },
    "JobAccepted": {
        "type": "object",
        "properties": {
            "accepted": {"type": "boolean", "description": "任务是否已受理"},
            "job_id": {"type": "string", "description": "异步任务 ID"},
            "status": {"type": "string", "description": "任务初始状态，通常为 queued"},
        },
        "required": ["job_id"],
    },
    "JobDetail": {
        "type": "object",
        "properties": {
            "id": {"type": "string", "description": "任务 ID"},
            "job_id": {"type": "string", "description": "任务 ID，兼容字段"},
            "type": {"type": "string", "description": "任务类型"},
            "status": {"type": "string", "description": "queued/running/succeeded/failed/canceled"},
            "progress": {"type": "integer", "description": "进度百分比，0-100"},
            "result": {"type": "object", "nullable": True, "description": "任务成功后的结构化结果"},
            "error_message": {"type": "string", "description": "失败原因"},
            "created_at": {"type": "string", "nullable": True, "description": "创建时间"},
            "updated_at": {"type": "string", "nullable": True, "description": "更新时间"},
        },
    },
    "SessionInfo": {
        "type": "object",
        "properties": {
            "session_id": {"type": "string", "description": "会话 ID"},
            "title": {"type": "string", "description": "会话标题"},
            "created_at": {"type": "string", "nullable": True, "description": "创建时间"},
            "updated_at": {"type": "string", "nullable": True, "description": "更新时间"},
            "current_dataset_version_id": {"type": "integer", "nullable": True, "description": "当前激活数据集版本 ID"},
        },
    },
    "SessionList": {
        "type": "object",
        "properties": {
            "sessions": {
                "type": "array",
                "items": {"$ref": "#/components/schemas/SessionInfo"},
            }
        },
    },
    "DataPreview": {
        "type": "object",
        "properties": {
            "headers": {"type": "array", "items": {"type": "string"}, "description": "列名"},
            "rows": {"type": "array", "items": {"type": "array", "items": {}}, "description": "预览行"},
            "total_rows": {"type": "integer", "description": "总行数"},
        },
    },
    "VariableMeta": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "变量名"},
            "label": {"type": "string", "description": "变量标签"},
            "type": {"type": "string", "description": "变量类型"},
            "missing_count": {"type": "integer", "description": "缺失值数量"},
            "unique_count": {"type": "integer", "description": "唯一值数量"},
        },
    },
    "VariableList": {
        "type": "object",
        "properties": {
            "variables": {"type": "array", "items": {"$ref": "#/components/schemas/VariableMeta"}},
        },
    },
    "VariableValues": {
        "type": "object",
        "properties": {
            "values": {"type": "array", "items": {}, "description": "变量取值列表"},
        },
    },
    "ProcessRequest": {
        "type": "object",
        "properties": {
            "method": {"type": "string", "description": "数据处理方法 ID"},
            "params": {"type": "object", "description": "方法参数，不同 method 结构不同"},
        },
        "required": ["method"],
    },
    "ExecuteMethodRequest": {
        "type": "object",
        "properties": {
            "method": {"type": "string", "description": "分析方法 ID，例如 frequency/descriptive/chi_square"},
            "params": {"type": "object", "description": "分析方法参数，不同 method 结构不同"},
        },
        "required": ["method"],
    },
    "MethodSlot": {
        "type": "object",
        "properties": {
            "key": {"type": "string", "description": "参数 key"},
            "label": {"type": "string", "description": "前端显示名称"},
            "type": {"type": "string", "description": "single/multiple"},
            "accept": {"type": "string", "description": "any/numeric/categorical"},
            "min": {"type": "integer", "nullable": True, "description": "多选时最少变量数"},
            "hint": {"type": "string", "description": "槽位说明"},
        },
    },
    "MethodOption": {
        "type": "object",
        "properties": {
            "key": {"type": "string", "description": "选项 key"},
            "label": {"type": "string", "description": "前端显示名称"},
            "default": {"description": "默认值"},
            "choices": {"type": "array", "items": {}, "description": "可选值"},
            "hint": {"type": "string", "description": "选项说明"},
        },
    },
    "AnalysisMethodMeta": {
        "type": "object",
        "properties": {
            "label": {"type": "string", "description": "方法名称"},
            "category": {"type": "string", "description": "方法分类"},
            "description": {"type": "string", "description": "方法说明"},
            "order": {"type": "integer", "description": "排序值"},
            "slots": {"type": "array", "items": {"$ref": "#/components/schemas/MethodSlot"}},
            "options": {"type": "array", "items": {"$ref": "#/components/schemas/MethodOption"}},
            "param_builder": {"type": "string", "description": "后端参数构建器"},
        },
    },
    "MethodCategory": {
        "type": "object",
        "properties": {
            "key": {"type": "string", "description": "分类 key"},
            "label": {"type": "string", "description": "分类名称"},
            "hot": {"type": "boolean", "description": "是否热门分类"},
        },
    },
    "MethodsResponse": {
        "type": "object",
        "properties": {
            "methods": {
                "type": "object",
                "additionalProperties": {"$ref": "#/components/schemas/AnalysisMethodMeta"},
                "description": "key 为 method ID，value 为方法元数据",
            },
            "categories": {
                "type": "array",
                "items": {"$ref": "#/components/schemas/MethodCategory"},
            },
        },
    },
    "MethodDetailResponse": {
        "type": "object",
        "properties": {
            "method": {"type": "string", "description": "分析方法 ID"},
            "meta": {"$ref": "#/components/schemas/AnalysisMethodMeta"},
            "slot_params_example": {
                "type": "object",
                "description": "按 `/api/methods` 槽位直接填写的参数示例",
            },
            "execute_params_example": {
                "type": "object",
                "description": "后端实际执行时读取的最终 params 示例",
            },
        },
        "required": ["method", "meta", "slot_params_example", "execute_params_example"],
    },
    "AnalysisResult": {
        "type": "object",
        "properties": {
            "id": {"type": "integer", "description": "结果 ID"},
            "analysis_name": {"type": "string", "description": "分析名称"},
            "table_headers": {"type": "array", "items": {"type": "string"}, "description": "表头"},
            "table_rows": {"type": "array", "items": {"type": "array", "items": {}}, "description": "表格行"},
            "sections": {"type": "array", "items": {"type": "object"}, "nullable": True, "description": "结构化报告章节"},
            "job_id": {"type": "string", "nullable": True, "description": "产生该结果的任务 ID"},
            "dataset_version_id": {"type": "integer", "nullable": True, "description": "结果对应的数据集版本"},
        },
    },
    "AnalysisResults": {
        "type": "object",
        "properties": {
            "results": {"type": "array", "items": {"$ref": "#/components/schemas/AnalysisResult"}},
        },
    },
    "DatasetVersion": {
        "type": "object",
        "properties": {
            "id": {"type": "integer", "description": "版本 ID"},
            "version_no": {"type": "integer", "description": "版本号"},
            "label": {"type": "string", "description": "版本说明"},
            "is_current": {"type": "boolean", "description": "是否当前激活版本"},
            "created_at": {"type": "string", "nullable": True, "description": "创建时间"},
            "source_job_id": {"type": "string", "nullable": True, "description": "生成该版本的任务 ID"},
            "source_method": {"type": "string", "nullable": True, "description": "生成该版本的数据处理方法 ID"},
            "source_job_status": {"type": "string", "nullable": True, "description": "来源任务状态"},
            "source_job_type": {"type": "string", "nullable": True, "description": "来源任务类型"},
        },
    },
    "DatasetItem": {
        "type": "object",
        "properties": {
            "id": {"type": "integer", "description": "数据集 ID"},
            "session_id": {"type": "string", "description": "关联会话 ID"},
            "name": {"type": "string", "description": "数据集显示名称"},
            "original_filename": {"type": "string", "description": "原始文件名"},
            "created_at": {"type": "number", "nullable": True, "description": "创建时间戳"},
            "last_used_at": {"type": "number", "nullable": True, "description": "最近使用时间戳"},
            "current_version_id": {"type": "integer", "nullable": True, "description": "当前版本 ID"},
            "current_version_no": {"type": "integer", "nullable": True, "description": "当前版本号"},
            "version_count": {"type": "integer", "description": "版本数量"},
            "result_count": {"type": "integer", "description": "分析结果数量"},
            "row_count": {"type": "integer", "description": "行数"},
            "column_count": {"type": "integer", "description": "列数"},
        },
    },
    "DatasetList": {
        "type": "object",
        "properties": {
            "datasets": {"type": "array", "items": {"$ref": "#/components/schemas/DatasetItem"}},
            "total": {"type": "integer", "description": "匹配条件下的数据集总数"},
            "page": {"type": "integer", "description": "当前页码"},
            "page_size": {"type": "integer", "description": "每页数量"},
            "sort": {"type": "string", "description": "当前排序字段"},
            "q": {"type": "string", "description": "当前搜索关键词"},
        },
    },
    "RenameDatasetRequest": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "新的数据集名称，最多 120 个字符"},
        },
        "required": ["name"],
    },
    "DatasetFolder": {
        "type": "object",
        "properties": {
            "id": {"type": "integer", "description": "文件夹 ID"},
            "name": {"type": "string", "description": "文件夹名称"},
            "created_at": {"type": "number", "nullable": True, "description": "创建时间戳"},
            "sessionIds": {"type": "array", "items": {"type": "string"}, "description": "文件夹内数据集对应的 session_id"},
        },
    },
    "DatasetFolderList": {
        "type": "object",
        "properties": {
            "folders": {"type": "array", "items": {"$ref": "#/components/schemas/DatasetFolder"}},
        },
    },
    "DatasetFolderRequest": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "文件夹名称，最多 80 个字符"},
        },
        "required": ["name"],
    },
    "MoveDatasetFolderRequest": {
        "type": "object",
        "properties": {
            "session_id": {"type": "string", "description": "要移动的数据集会话 ID"},
            "folder_id": {"type": "integer", "nullable": True, "description": "目标文件夹 ID，空值表示移出文件夹"},
        },
        "required": ["session_id"],
    },
    "DatasetVersions": {
        "type": "object",
        "properties": {
            "versions": {"type": "array", "items": {"$ref": "#/components/schemas/DatasetVersion"}},
            "current_dataset_version_id": {"type": "integer", "nullable": True},
        },
    },
    "ActivateDatasetVersionRequest": {
        "type": "object",
        "properties": {
            "version_id": {"type": "integer", "description": "要激活的数据集版本 ID"},
        },
        "required": ["version_id"],
    },
    "RenameVariableRequest": {
        "type": "object",
        "properties": {
            "new_name": {"type": "string", "description": "新变量名"},
        },
        "required": ["new_name"],
    },
    "ChangeVariableTypeRequest": {
        "type": "object",
        "properties": {
            "target_type": {"type": "string", "description": "目标变量类型"},
        },
        "required": ["target_type"],
    },
    "RenameResultRequest": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "新结果名称"},
        },
        "required": ["name"],
    },
    "ShareReportRequest": {
        "type": "object",
        "properties": {
            "session_id": {"type": "string", "description": "会话 ID"},
            "title": {"type": "string", "description": "分享标题"},
            "password": {"type": "string", "description": "可选分享密码，空字符串表示不设密码"},
        },
        "required": ["session_id"],
    },
    "ShareReport": {
        "type": "object",
        "properties": {
            "share_token": {"type": "string", "description": "分享 token"},
            "url": {"type": "string", "description": "前端分享 URL"},
            "requires_password": {"type": "boolean", "description": "是否需要密码访问"},
            "report": {"type": "object", "nullable": True, "description": "报告快照内容"},
        },
    },
    "HealthStatus": {
        "type": "object",
        "properties": {
            "status": {"type": "string", "description": "ok/degraded/error"},
            "checks": {"type": "object", "description": "依赖检查明细"},
        },
    },
}

PUBLIC_OPERATIONS = {
    ("post", "/api/login"),
    ("post", "/api/refresh"),
    ("get", "/api/health"),
    ("get", "/api/health/ready"),
    ("get", "/api/shared-reports/{share_token}"),
    ("post", "/api/shared-reports/{share_token}/access"),
}

OPERATION_DOCS: dict[tuple[str, str], dict[str, str]] = {
    ("post", "/api/login"): {
        "tag": "Auth",
        "summary": "账号登录",
        "description": "使用用户名和密码登录。成功后返回 `access_token`、`refresh_token`、用户名、角色和用户 ID。前端保存 token 后，后续受保护接口带 `Authorization: Bearer <token>`。",
    },
    ("post", "/api/refresh"): {
        "tag": "Auth",
        "summary": "刷新访问令牌",
        "description": "使用 `refresh_token` 换取新的访问令牌和刷新令牌。旧刷新令牌会被消费，前端需要用响应里的新值覆盖本地存储。",
    },
    ("get", "/api/me"): {
        "tag": "Auth",
        "summary": "获取当前用户",
        "description": "校验当前 Bearer Token，并返回当前登录用户的基础资料。前端启动时可用它判断登录态是否仍有效。",
    },
    ("post", "/api/change-username"): {
        "tag": "Auth",
        "summary": "修改用户名",
        "description": "修改当前登录用户的用户名。请求体字段：`new_username`。",
    },
    ("post", "/api/change-password"): {
        "tag": "Auth",
        "summary": "修改密码",
        "description": "修改当前登录用户密码。请求体字段：`old_password`、`new_password`，新密码至少 6 位。",
    },
    ("post", "/api/session"): {
        "tag": "Session",
        "summary": "创建分析会话",
        "description": "为当前用户创建一个新的分析会话。前端上传文件、执行分析、查看结果都要围绕 `session_id` 进行。",
    },
    ("get", "/api/session/{session_id}"): {
        "tag": "Session",
        "summary": "获取会话详情",
        "description": "读取指定会话的基础信息。只能访问当前用户自己的会话，管理员后台接口另走 `/api/admin/*`。",
    },
    ("get", "/api/sessions"): {
        "tag": "Session",
        "summary": "获取我的会话列表",
        "description": "返回当前用户的历史分析会话列表，用于前端工作台左侧历史记录或数据列表。",
    },
    ("patch", "/api/session/{session_id}/title"): {
        "tag": "Session",
        "summary": "重命名会话",
        "description": "用表单字段 `title` 修改会话标题。",
    },
    ("delete", "/api/session/{session_id}"): {
        "tag": "Session",
        "summary": "删除会话",
        "description": "删除当前用户自己的指定会话及相关业务数据。前端删除前应二次确认。",
    },
    ("get", "/api/datasets"): {
        "tag": "Datasets",
        "summary": "获取我的数据集列表",
        "description": "返回当前用户可访问的数据集、当前版本、版本数量、分析数量和行列摘要。支持查询参数：`q` 搜索名称/文件名/session_id，`sort` 可选 recent/created/name/versions/results，`page` 和 `page_size` 控制分页。管理员可查看全量数据集。",
    },
    ("patch", "/api/datasets/{dataset_id}"): {
        "tag": "Datasets",
        "summary": "重命名数据集",
        "description": "修改数据集显示名称。只能修改自己的数据集，管理员可修改任意数据集。",
    },
    ("post", "/api/datasets/{dataset_id}/touch"): {
        "tag": "Datasets",
        "summary": "更新数据集最近使用时间",
        "description": "前端切换到某个数据集后可调用该接口记录最近使用时间。",
    },
    ("delete", "/api/datasets/{dataset_id}"): {
        "tag": "Datasets",
        "summary": "删除数据集",
        "description": "删除数据集关联会话、版本、分析结果和存储文件。删除前必须由前端二次确认。",
    },
    ("get", "/api/dataset-folders"): {
        "tag": "Datasets",
        "summary": "获取数据集文件夹",
        "description": "返回当前用户的数据集文件夹，以及每个文件夹内的数据集 session_id 列表。",
    },
    ("post", "/api/dataset-folders"): {
        "tag": "Datasets",
        "summary": "创建数据集文件夹",
        "description": "为当前用户创建一个数据集文件夹。文件夹只保存归类关系，不移动实际文件。",
    },
    ("patch", "/api/dataset-folders/{folder_id}"): {
        "tag": "Datasets",
        "summary": "重命名数据集文件夹",
        "description": "修改当前用户自己的数据集文件夹名称。",
    },
    ("delete", "/api/dataset-folders/{folder_id}"): {
        "tag": "Datasets",
        "summary": "删除数据集文件夹",
        "description": "删除文件夹及归类关系，不删除文件夹内的数据集。",
    },
    ("put", "/api/dataset-folder-items"): {
        "tag": "Datasets",
        "summary": "移动数据集到文件夹",
        "description": "把数据集移动到指定文件夹；`folder_id` 为空时表示移出文件夹。",
    },
    ("post", "/api/upload/{session_id}"): {
        "tag": "Files",
        "summary": "上传数据文件",
        "description": "上传 Excel、CSV、SPSS、Stata 等数据文件。请求类型为 `multipart/form-data`，字段名为 `file`。接口返回异步任务 `job_id`，解析完成后再读取变量和预览。",
    },
    ("get", "/api/files/{session_id}"): {
        "tag": "Files",
        "summary": "获取会话文件列表",
        "description": "返回会话内已上传的数据文件和问卷文件信息。",
    },
    ("get", "/api/questionnaire/{session_id}/{filename}"): {
        "tag": "Files",
        "summary": "读取问卷文档内容",
        "description": "读取指定问卷文件的文本内容，用于 AI 规划分析时辅助理解变量和题项。",
    },
    ("get", "/api/data-preview/{session_id}"): {
        "tag": "Files",
        "summary": "获取数据预览",
        "description": "返回当前数据集的前若干行预览。可用查询参数 `limit` 控制返回行数，默认 100。",
    },
    ("get", "/api/variable-values/{session_id}/{column_name}"): {
        "tag": "Files",
        "summary": "获取变量取值",
        "description": "读取指定变量的常见取值，用于分类变量配置、筛选和前端下拉候选项。可用 `limit` 控制返回数量。",
    },
    ("get", "/api/data-file/{session_id}"): {
        "tag": "Files",
        "summary": "下载原始数据文件",
        "description": "下载会话当前数据文件，响应为二进制流。前端跨域部署时也要走后端 API 地址，不要拼本机文件路径。",
    },
    ("get", "/api/data-file/{session_id}/export"): {
        "tag": "Files",
        "summary": "导出数据文件",
        "description": "按查询参数 `format` 导出当前数据集，例如 `xlsx`、`csv`。响应为二进制流。",
    },
    ("get", "/api/variables/{session_id}"): {
        "tag": "Files",
        "summary": "获取变量列表",
        "description": "返回当前数据集的变量名、类型、标签等元数据，是分析配置面板的核心数据源。",
    },
    ("post", "/api/process/{session_id}"): {
        "tag": "Processing",
        "summary": "提交数据处理任务",
        "description": "提交缺失值、异常值、标准化、编码、生成变量等数据处理任务。请求体字段：`method`、`params`。返回 `job_id`。",
    },
    ("patch", "/api/variables/{session_id}/{column_name}/rename"): {
        "tag": "Processing",
        "summary": "重命名变量",
        "description": "修改变量名。请求体字段：`new_name`。变量改名会影响后续分析参数，前端需要刷新变量列表。",
    },
    ("patch", "/api/variables/{session_id}/{column_name}/type"): {
        "tag": "Processing",
        "summary": "修改变量类型",
        "description": "修改变量识别类型。请求体字段：`target_type`，常用于数值型、分类型等前端配置修正。",
    },
    ("delete", "/api/variables/{session_id}/{column_name}"): {
        "tag": "Processing",
        "summary": "删除变量",
        "description": "从当前数据集删除指定变量，并生成新的数据集版本。",
    },
    ("get", "/api/dataset-versions/{session_id}"): {
        "tag": "Processing",
        "summary": "获取数据集版本",
        "description": "返回数据处理产生的数据集版本列表，以及当前激活版本。",
    },
    ("post", "/api/dataset-versions/{session_id}/activate"): {
        "tag": "Processing",
        "summary": "切换数据集版本",
        "description": "请求体字段：`version_id`。切换后分析、变量、预览都基于该版本。",
    },
    ("post", "/api/plan/{session_id}"): {
        "tag": "Analysis",
        "summary": "提交 AI 分析计划任务",
        "description": "根据研究主题、变量说明、研究假设、分析需求生成分析计划。请求为表单字段：`research_topic`、`variable_desc`、`hypotheses`、`analysis_request`。返回 `job_id`。",
    },
    ("post", "/api/execute/{session_id}"): {
        "tag": "Analysis",
        "summary": "提交整套分析执行任务",
        "description": "根据用户确认后的分析计划执行整套分析。表单字段 `plan_edit` 为最终计划文本。返回 `job_id`。",
    },
    ("post", "/api/execute-stream/{session_id}"): {
        "tag": "Analysis",
        "summary": "流式执行分析计划",
        "description": "通过 SSE 返回分析执行过程事件。前端可用于实时展示步骤进度；分离部署时确保代理和网关不要缓冲 SSE。",
    },
    ("get", "/api/results/{session_id}"): {
        "tag": "Analysis",
        "summary": "获取分析结果",
        "description": "返回会话下保存的分析结果列表，包括表格、章节、图表元数据、任务 ID 和数据集版本信息。",
    },
    ("patch", "/api/results/{session_id}/{result_id}"): {
        "tag": "Analysis",
        "summary": "重命名分析结果",
        "description": "修改单个分析结果名称。请求体字段：`name`。",
    },
    ("delete", "/api/results/{session_id}/{result_id}"): {
        "tag": "Analysis",
        "summary": "删除分析结果",
        "description": "删除会话中的指定分析结果。",
    },
    ("get", "/api/download/{session_id}"): {
        "tag": "Analysis",
        "summary": "同步下载 Word 报告",
        "description": "直接生成并下载 Word 报告。新前端优先使用 POST 异步生成，再通过任务产物下载。",
    },
    ("post", "/api/download/{session_id}"): {
        "tag": "Analysis",
        "summary": "提交 Word 报告生成任务",
        "description": "异步生成 Word 报告。返回 `job_id`，任务成功后通过 `/api/jobs/{job_id}/output` 下载报告。",
    },
    ("get", "/api/methods"): {
        "tag": "Analysis",
        "summary": "获取分析方法元数据",
        "description": "返回平台支持的统计分析方法、分类和前端配置元数据。每个方法的完整 params 示例见 `docs/ANALYSIS_METHOD_PARAMS.md`。",
    },
    ("get", "/api/methods/{method_key}"): {
        "tag": "Analysis",
        "summary": "获取单个分析方法参数详情",
        "description": "按 method key 返回单个统计分析方法的元数据、前端槽位参数示例和最终执行 params 示例。用于前端分离时查看某个方法该怎么组装 `POST /api/execute-method/{session_id}` 的请求体。",
    },
    ("post", "/api/execute-method/{session_id}"): {
        "tag": "Analysis",
        "summary": "提交单个统计方法任务",
        "description": "执行单个统计分析方法。请求体字段：`method`、`params`。返回 `job_id`。",
    },
    ("post", "/api/ai-interpret"): {
        "tag": "Analysis",
        "summary": "提交 AI 结果解读任务",
        "description": "对分析结果章节进行 AI 解读。请求体包含 `method`、`sections`，可选 `session_id`、`dataset_version_id`。返回 `job_id`。",
    },
    ("get", "/api/jobs/{job_id}"): {
        "tag": "Jobs",
        "summary": "获取任务详情",
        "description": "查询异步任务状态、进度、结果和错误信息。终态包括 `succeeded`、`failed`、`canceled`。",
    },
    ("get", "/api/jobs/{job_id}/events"): {
        "tag": "Jobs",
        "summary": "监听任务 SSE 事件",
        "description": "以 `text/event-stream` 返回任务进度事件。前端推荐优先使用 SSE，失败后再降级轮询 `/api/jobs/{job_id}`。",
    },
    ("get", "/api/jobs/{job_id}/sandbox-runs"): {
        "tag": "Jobs",
        "summary": "获取任务沙箱运行记录",
        "description": "返回任务关联的沙箱执行记录，用于管理员或调试页面查看执行细节。",
    },
    ("get", "/api/jobs/{job_id}/output"): {
        "tag": "Jobs",
        "summary": "下载任务产物",
        "description": "下载任务输出文件，例如 Word 报告或导出数据。响应为二进制流。",
    },
    ("post", "/api/jobs/{job_id}/cancel"): {
        "tag": "Jobs",
        "summary": "取消任务",
        "description": "请求取消当前用户可访问的任务。已经完成的任务不会被回滚。",
    },
    ("post", "/api/jobs/{job_id}/retry"): {
        "tag": "Jobs",
        "summary": "重试任务",
        "description": "重新提交失败或可重试的任务。返回新的或更新后的任务状态。",
    },
    ("post", "/api/shared-reports"): {
        "tag": "Share",
        "summary": "创建报告分享",
        "description": "把当前分析结果生成可公开访问的分享快照。需要登录，请求体包含会话、结果范围和可选密码等分享配置。",
    },
    ("get", "/api/shared-reports/{share_token}"): {
        "tag": "Share",
        "summary": "读取公开分享报告",
        "description": "通过分享 token 读取公开报告。无密码分享可直接返回内容；有密码分享会返回需要访问校验的状态。",
    },
    ("post", "/api/shared-reports/{share_token}/access"): {
        "tag": "Share",
        "summary": "访问带密码分享报告",
        "description": "提交分享密码并读取报告内容。请求体字段：`password`。",
    },
    ("get", "/api/health"): {
        "tag": "Health",
        "summary": "存活检查",
        "description": "用于负载均衡或容器平台判断 API 进程是否存活。",
    },
    ("get", "/api/health/ready"): {
        "tag": "Health",
        "summary": "就绪检查",
        "description": "检查数据库、存储等后端依赖是否可用。部署平台应优先使用这个接口做 readiness probe。",
    },
}

ADMIN_OPERATION_DOCS: dict[tuple[str, str], str] = {
    ("get", "/api/admin/dashboard"): "管理员仪表盘汇总",
    ("get", "/api/admin/users"): "管理员分页查询用户",
    ("post", "/api/admin/users"): "管理员创建用户",
    ("put", "/api/admin/users/{user_id}"): "管理员更新用户",
    ("post", "/api/admin/users/{user_id}/reset-password"): "管理员重置用户密码",
    ("post", "/api/admin/users/{user_id}/toggle-active"): "管理员启用或停用用户",
    ("get", "/api/admin/sessions"): "管理员分页查询会话",
    ("get", "/api/admin/operations"): "管理员查看运营指标",
    ("get", "/api/admin/jobs"): "管理员分页查询任务",
    ("get", "/api/admin/sandbox-executions"): "管理员分页查询沙箱执行记录",
    ("delete", "/api/admin/sessions/{session_id}"): "管理员删除会话",
    ("post", "/api/admin/cleanup"): "管理员清理过期或异常会话",
    ("get", "/api/admin/system"): "管理员查看系统运行信息",
    ("get", "/api/admin/ai-config"): "管理员读取 AI 配置",
    ("put", "/api/admin/ai-config"): "管理员保存 AI 配置",
}

STANDARD_ERROR_RESPONSES = {
    "400": {"description": "请求参数不合法或业务校验失败"},
    "403": {"description": "权限不足，普通用户不能访问管理员接口或其他用户资源"},
    "404": {"description": "资源不存在，或当前用户无权访问该资源"},
    "409": {"description": "资源状态冲突，例如会话正在被其他任务写入"},
    "429": {"description": "触发限流，请稍后重试"},
    "500": {"description": "服务端异常"},
}

REQUEST_EXAMPLES: dict[tuple[str, str], dict] = {
    ("post", "/api/login"): {
        "用户名密码": {
            "summary": "用户名密码登录",
            "value": {"username": "admin", "password": "spssgo2024"},
        },
    },
    ("post", "/api/refresh"): {
        "刷新令牌": {
            "summary": "刷新 access token",
            "value": {"refresh_token": "refresh-token-from-login"},
        },
    },
    ("post", "/api/change-username"): {
        "新用户名": {
            "summary": "修改当前用户用户名",
            "value": {"new_username": "researcher01"},
        },
    },
    ("post", "/api/change-password"): {
        "新旧密码": {
            "summary": "修改当前用户密码",
            "value": {"old_password": "oldpass123", "new_password": "newpass123"},
        },
    },
    ("post", "/api/process/{session_id}"): {
        "标准化": {
            "summary": "提交标准化处理任务",
            "value": {"method": "standardize", "params": {"columns": ["score"], "method": "zscore"}},
        },
    },
    ("patch", "/api/variables/{session_id}/{column_name}/rename"): {
        "变量改名": {
            "summary": "把变量改成业务可读名称",
            "value": {"new_name": "满意度得分"},
        },
    },
    ("patch", "/api/variables/{session_id}/{column_name}/type"): {
        "变量类型": {
            "summary": "修正变量类型",
            "value": {"target_type": "categorical"},
        },
    },
    ("post", "/api/dataset-versions/{session_id}/activate"): {
        "切换版本": {
            "summary": "激活指定数据集版本",
            "value": {"version_id": 12},
        },
    },
    ("patch", "/api/datasets/{dataset_id}"): {
        "重命名数据集": {
            "summary": "修改数据集显示名称",
            "value": {"name": "用户满意度调研"},
        },
    },
    ("post", "/api/dataset-folders"): {
        "新建文件夹": {
            "summary": "创建数据集归类文件夹",
            "value": {"name": "问卷项目"},
        },
    },
    ("patch", "/api/dataset-folders/{folder_id}"): {
        "重命名文件夹": {
            "summary": "修改文件夹名称",
            "value": {"name": "2026 问卷项目"},
        },
    },
    ("put", "/api/dataset-folder-items"): {
        "移动数据集": {
            "summary": "把数据集移动到文件夹",
            "value": {"session_id": "sess_xxx", "folder_id": 3},
        },
        "移出文件夹": {
            "summary": "把数据集移出文件夹",
            "value": {"session_id": "sess_xxx", "folder_id": None},
        },
    },
    ("post", "/api/execute-method/{session_id}"): {
        "频数分析": {
            "summary": "提交单个分析方法任务",
            "value": {"method": "frequency", "params": {"variables": ["gender", "grade"]}},
        },
    },
    ("post", "/api/ai-interpret"): {
        "结果解读": {
            "summary": "提交 AI 解读任务",
            "value": {
                "method": "frequency",
                "sections": [{"title": "频数分析", "tables": []}],
                "session_id": "sess_xxx",
                "dataset_version_id": 12,
            },
        },
    },
    ("post", "/api/shared-reports"): {
        "创建分享": {
            "summary": "创建报告分享快照",
            "value": {"session_id": "sess_xxx", "title": "问卷分析报告", "password": ""},
        },
    },
    ("post", "/api/shared-reports/{share_token}/access"): {
        "分享密码": {
            "summary": "访问带密码分享",
            "value": {"password": "123456"},
        },
    },
}

RESPONSE_EXAMPLES: dict[tuple[str, str], dict] = {
    ("post", "/api/login"): {
        "登录成功": {
            "summary": "登录成功",
            "value": {
                "token": "access-token",
                "access_token": "access-token",
                "refresh_token": "refresh-token",
                "username": "admin",
                "role": "admin",
                "user_id": 1,
            },
        },
    },
    ("get", "/api/me"): {
        "当前用户": {
            "summary": "当前用户",
            "value": {
                "user_id": 1,
                "username": "admin",
                "role": "admin",
                "created_at": "2026-04-28T10:00:00",
                "last_login_at": "2026-04-28T11:00:00",
            },
        },
    },
    ("post", "/api/session"): {
        "会话": {
            "summary": "新建会话",
            "value": {"session_id": "sess_abc123", "title": "新分析", "created_at": "2026-04-28T10:00:00"},
        },
    },
    ("post", "/api/upload/{session_id}"): {
        "上传已受理": {
            "summary": "上传解析任务已创建",
            "value": {"accepted": True, "job_id": "job_abc123", "status": "queued"},
        },
    },
    ("get", "/api/jobs/{job_id}"): {
        "任务详情": {
            "summary": "任务执行中",
            "value": {
                "id": "job_abc123",
                "status": "running",
                "progress": 60,
                "result": None,
                "error_message": "",
            },
        },
    },
    ("get", "/api/results/{session_id}"): {
        "分析结果": {
            "summary": "结果列表",
            "value": {
                "results": [
                    {
                        "id": 101,
                        "analysis_name": "频数分析",
                        "table_headers": ["变量", "频数", "百分比"],
                        "table_rows": [["男", 42, "42%"]],
                        "job_id": "job_abc123",
                        "dataset_version_id": 12,
                    }
                ]
            },
        },
    },
    ("get", "/api/data-preview/{session_id}"): {
        "数据预览": {
            "summary": "数据预览",
            "value": {"headers": ["gender", "score"], "rows": [["男", 90], ["女", 86]], "total_rows": 2},
        },
    },
    ("get", "/api/datasets"): {
        "数据集列表": {
            "summary": "我的数据集",
            "value": {
                "datasets": [
                    {
                        "id": 8,
                        "session_id": "sess_xxx",
                        "name": "用户满意度调研",
                        "original_filename": "survey.xlsx",
                        "current_version_id": 12,
                        "current_version_no": 3,
                        "version_count": 3,
                        "result_count": 5,
                        "row_count": 300,
                        "column_count": 24,
                    }
                ],
                "total": 1,
                "page": 1,
                "page_size": 200,
                "sort": "recent",
                "q": "",
            },
        },
    },
    ("get", "/api/dataset-folders"): {
        "文件夹列表": {
            "summary": "我的数据集文件夹",
            "value": {"folders": [{"id": 3, "name": "问卷项目", "sessionIds": ["sess_xxx"]}]},
        },
    },
    ("get", "/api/variables/{session_id}"): {
        "变量列表": {
            "summary": "变量元数据",
            "value": {"variables": [{"name": "score", "type": "numeric", "label": "成绩"}]},
        },
    },
}

REQUEST_SCHEMA_MAP = {
    ("post", "/api/login"): "LoginRequest",
    ("post", "/api/refresh"): "RefreshRequest",
    ("post", "/api/change-username"): "ChangeUsernameRequest",
    ("post", "/api/change-password"): "ChangePasswordRequest",
    ("post", "/api/process/{session_id}"): "ProcessRequest",
    ("patch", "/api/variables/{session_id}/{column_name}/rename"): "RenameVariableRequest",
    ("patch", "/api/variables/{session_id}/{column_name}/type"): "ChangeVariableTypeRequest",
    ("patch", "/api/datasets/{dataset_id}"): "RenameDatasetRequest",
    ("post", "/api/dataset-folders"): "DatasetFolderRequest",
    ("patch", "/api/dataset-folders/{folder_id}"): "DatasetFolderRequest",
    ("put", "/api/dataset-folder-items"): "MoveDatasetFolderRequest",
    ("post", "/api/dataset-versions/{session_id}/activate"): "ActivateDatasetVersionRequest",
    ("post", "/api/execute-method/{session_id}"): "ExecuteMethodRequest",
    ("patch", "/api/results/{session_id}/{result_id}"): "RenameResultRequest",
    ("post", "/api/shared-reports"): "ShareReportRequest",
}

RESPONSE_SCHEMA_MAP = {
    ("post", "/api/login"): "TokenResponse",
    ("post", "/api/refresh"): "TokenResponse",
    ("get", "/api/me"): "CurrentUser",
    ("post", "/api/change-password"): "SuccessResponse",
    ("post", "/api/session"): "SessionInfo",
    ("get", "/api/session/{session_id}"): "SessionInfo",
    ("get", "/api/sessions"): "SessionList",
    ("get", "/api/datasets"): "DatasetList",
    ("get", "/api/dataset-folders"): "DatasetFolderList",
    ("post", "/api/upload/{session_id}"): "JobAccepted",
    ("get", "/api/data-preview/{session_id}"): "DataPreview",
    ("get", "/api/variable-values/{session_id}/{column_name}"): "VariableValues",
    ("get", "/api/variables/{session_id}"): "VariableList",
    ("post", "/api/process/{session_id}"): "JobAccepted",
    ("get", "/api/dataset-versions/{session_id}"): "DatasetVersions",
    ("post", "/api/plan/{session_id}"): "JobAccepted",
    ("post", "/api/execute/{session_id}"): "JobAccepted",
    ("post", "/api/download/{session_id}"): "JobAccepted",
    ("post", "/api/execute-method/{session_id}"): "JobAccepted",
    ("post", "/api/ai-interpret"): "JobAccepted",
    ("get", "/api/results/{session_id}"): "AnalysisResults",
    ("get", "/api/methods"): "MethodsResponse",
    ("get", "/api/methods/{method_key}"): "MethodDetailResponse",
    ("get", "/api/jobs/{job_id}"): "JobDetail",
    ("get", "/api/shared-reports/{share_token}"): "ShareReport",
    ("post", "/api/shared-reports/{share_token}/access"): "ShareReport",
    ("get", "/api/health"): "HealthStatus",
    ("get", "/api/health/ready"): "HealthStatus",
}


def _operation_doc(method: str, path: str) -> dict[str, str] | None:
    doc = OPERATION_DOCS.get((method, path))
    if doc:
        return doc
    admin_summary = ADMIN_OPERATION_DOCS.get((method, path))
    if admin_summary:
        return {
            "tag": "Admin",
            "summary": admin_summary,
            "description": f"{admin_summary}。该接口需要管理员角色，普通用户访问会被拒绝。",
        }
    return None


def _requires_auth(method: str, path: str) -> bool:
    if (method, path) in PUBLIC_OPERATIONS:
        return False
    return path.startswith("/api/")


def _set_request_examples(operation: dict, method: str, path: str) -> None:
    examples = REQUEST_EXAMPLES.get((method, path))
    if not examples:
        return
    request_body = operation.get("requestBody")
    if not request_body:
        return
    content = request_body.get("content", {})
    media = content.get("application/json") or content.get("multipart/form-data") or content.get("application/x-www-form-urlencoded")
    if media is not None:
        media["examples"] = examples


def _set_request_schema(operation: dict, method: str, path: str) -> None:
    schema_name = REQUEST_SCHEMA_MAP.get((method, path))
    if not schema_name:
        return
    request_body = operation.get("requestBody")
    if not request_body:
        return
    content = request_body.get("content", {})
    media = content.get("application/json")
    if media is not None:
        media["schema"] = {"$ref": f"#/components/schemas/{schema_name}"}


def _set_response_examples(operation: dict, method: str, path: str) -> None:
    examples = RESPONSE_EXAMPLES.get((method, path))
    if not examples:
        return
    response = operation.setdefault("responses", {}).setdefault("200", {"description": "请求成功"})
    content = response.setdefault("content", {}).setdefault("application/json", {})
    content["examples"] = examples


def _set_response_schema(operation: dict, method: str, path: str) -> None:
    schema_name = RESPONSE_SCHEMA_MAP.get((method, path))
    if not schema_name:
        return
    response = operation.setdefault("responses", {}).setdefault("200", {"description": "请求成功"})
    content = response.setdefault("content", {}).setdefault("application/json", {})
    content["schema"] = {"$ref": f"#/components/schemas/{schema_name}"}


def _set_binary_response(operation: dict, media_type: str, description: str) -> None:
    response = operation.setdefault("responses", {}).setdefault("200", {"description": description})
    response["description"] = description
    response["content"] = {
        media_type: {
            "schema": {"type": "string", "format": "binary"},
        }
    }


def _set_stream_response(operation: dict) -> None:
    response = operation.setdefault("responses", {}).setdefault("200", {"description": "SSE 事件流"})
    response["description"] = "SSE 事件流，Content-Type 为 text/event-stream"
    response["content"] = {
        "text/event-stream": {
            "schema": {
                "type": "string",
                "description": "事件格式：event: job\\ndata: {\"status\":\"running\",\"progress\":60}\\n\\n",
            },
            "examples": {
                "job": {
                    "summary": "任务进度事件",
                    "value": "event: job\ndata: {\"id\":\"job_abc123\",\"status\":\"running\",\"progress\":60}\n\n",
                },
                "done": {
                    "summary": "任务完成事件",
                    "value": "event: done\ndata: {\"id\":\"job_abc123\",\"status\":\"succeeded\",\"progress\":100}\n\n",
                },
            },
        }
    }


def _set_standard_errors(operation: dict, method: str, path: str) -> None:
    responses = operation.setdefault("responses", {})
    if _requires_auth(method, path):
        responses.setdefault("401", {"description": "未登录、Token 缺失或 Token 已失效"})
    for code, payload in STANDARD_ERROR_RESPONSES.items():
        response = responses.setdefault(code, dict(payload))
        response.setdefault("content", {}).setdefault(
            "application/json",
            {"schema": {"$ref": "#/components/schemas/ApiError"}},
        )


def _set_special_response(operation: dict, method: str, path: str) -> None:
    if (method, path) in {
        ("get", "/api/data-file/{session_id}"),
        ("get", "/api/data-file/{session_id}/export"),
        ("get", "/api/jobs/{job_id}/output"),
    }:
        _set_binary_response(operation, "application/octet-stream", "二进制文件流")
    if (method, path) == ("get", "/api/download/{session_id}"):
        _set_binary_response(
            operation,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "Word 报告文件流",
        )
    if (method, path) in {
        ("get", "/api/jobs/{job_id}/events"),
        ("post", "/api/execute-stream/{session_id}"),
    }:
        _set_stream_response(operation)


def install_openapi_docs(app: FastAPI) -> None:
    """安装自定义 OpenAPI 生成器，集中补齐前后端对接文档。"""

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        schema = get_openapi(
            title=app.title,
            version=app.version,
            description=OPENAPI_DESCRIPTION,
            routes=app.routes,
            tags=OPENAPI_TAGS,
        )
        schema.setdefault("components", {}).setdefault("securitySchemes", {})["BearerAuth"] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "登录接口返回的 access_token，前端请求头格式：Authorization: Bearer <token>",
        }
        schema["components"].setdefault("schemas", {}).update(COMPONENT_SCHEMAS)

        for path, path_item in schema.get("paths", {}).items():
            for method, operation in path_item.items():
                if method not in {"get", "post", "put", "patch", "delete"}:
                    continue

                doc = _operation_doc(method, path)
                if doc:
                    operation["tags"] = [doc["tag"]]
                    operation["summary"] = doc["summary"]
                    operation["description"] = doc["description"]

                if _requires_auth(method, path):
                    operation["security"] = [{"BearerAuth": []}]
                _set_standard_errors(operation, method, path)
                _set_request_schema(operation, method, path)
                _set_request_examples(operation, method, path)
                _set_response_schema(operation, method, path)
                _set_response_examples(operation, method, path)
                _set_special_response(operation, method, path)

        app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = custom_openapi
