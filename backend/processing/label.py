from fastapi import HTTPException


METHOD_KEY = "label"


def handle(df, variables, params):
    from backend.services.variable_metadata_service import infer_variable_type

    if not variables:
        return df, '处理完成'

    col = variables[0]
    if col not in df.columns:
        raise ValueError(f'变量 {col} 不存在')

    var_type = infer_variable_type(df[col], col)
    if var_type != 'categorical':
        raise ValueError('数据标签仅支持定类变量')

    label_map = {
        str(k): v for k, v in (params.get('label_map', {}) or {}).items()
        if v not in ('', None)
    }
    if not label_map:
        return df, '未设置标签，原数据保持不变'

    # 数据标签只更新展示层元数据，不修改底层原始数据。
    return df, f'已为变量 {col} 保存数据标签'


async def validate_request(session_id: str, filepath: str, params: dict):
    from backend.database import get_variable_metadata_map
    from backend.services.file_service import load_dataframe
    from backend.services.variable_metadata_service import infer_variable_type

    variables = (params or {}).get("variables", []) or []
    if not variables:
        raise HTTPException(400, "请先选择一个定类变量")

    target = variables[0]
    df = load_dataframe(filepath)
    if target not in df.columns:
        raise HTTPException(404, f"变量 {target} 不存在")

    metadata_map = await get_variable_metadata_map(session_id)
    var_type = metadata_map.get(target, {}).get("var_type") or infer_variable_type(df[target], target)
    if var_type != "categorical":
        raise HTTPException(400, "数据标签仅支持定类变量")


async def persist_metadata(session_id: str, params: dict):
    from backend.database import upsert_variable_metadata

    variables = params.get("variables", []) or []
    if not variables:
        return

    value_labels = {str(k): v for k, v in (params.get("label_map", {}) or {}).items() if v}
    if not value_labels:
        return

    await upsert_variable_metadata(
        session_id,
        variables[0],
        var_type="categorical",
        value_labels=value_labels,
    )

