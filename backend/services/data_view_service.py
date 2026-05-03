# -*- coding: utf-8 -*-
"""数据浏览服务，只管预览、变量查看和导出，别把上传落库塞进来。"""
import os
import tempfile
from io import BytesIO

import pandas as pd
from fastapi import HTTPException

from backend.app_runtime import download_response
from backend.file_parser import parse_data_file
from backend.services.file_service import load_dataframe
from backend.services.session_data_service import materialized_session_data, resolve_session_data_source
from backend.services.variable_metadata_service import infer_variable_type, recommended_auto_group_count, sort_label_values

EXPORT_FORMATS = {
    "xlsx": {"ext": ".xlsx", "media_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
    "csv": {"ext": ".csv", "media_type": "text/csv; charset=utf-8"},
    "sav": {"ext": ".sav", "media_type": "application/octet-stream"},
    "dta": {"ext": ".dta", "media_type": "application/octet-stream"},
    "xpt": {"ext": ".xpt", "media_type": "application/octet-stream"},
    "tsv": {"ext": ".tsv", "media_type": "text/tab-separated-values; charset=utf-8"},
    "txt": {"ext": ".txt", "media_type": "text/plain; charset=utf-8"},
    "json": {"ext": ".json", "media_type": "application/json; charset=utf-8"},
    "parquet": {"ext": ".parquet", "media_type": "application/octet-stream"},
}


async def build_data_preview(session_id: str, limit: int = 100, *, allow_legacy_fallback: bool = False):
    data_source = await resolve_session_data_source(
        session_id,
        allow_legacy_fallback=allow_legacy_fallback,
    )
    with materialized_session_data(data_source) as data_file:
        df, _ = parse_data_file(data_file)
        sample = df.head(min(limit, 200))
        headers = [str(c) for c in sample.columns]
        rows = []
        for _, row in sample.iterrows():
            rows.append([
                "" if pd.isna(v) else (str(int(v)) if isinstance(v, float) and v == int(v) else str(v))
                for v in row
            ])
        return {
            "filename": data_source["filename"],
            "total_rows": len(df),
            "total_cols": len(df.columns),
            "headers": headers,
            "rows": rows,
            "source": data_source["source"],
            "dataset_version_id": data_source["dataset_version_id"],
            "dataset_version_no": data_source["dataset_version_no"],
        }


async def get_variable_values(session_id: str, column_name: str, metadata_map: dict[str, dict], limit: int = 200, *, allow_legacy_fallback: bool = False):
    data_source = await resolve_session_data_source(
        session_id,
        allow_legacy_fallback=allow_legacy_fallback,
    )
    with materialized_session_data(data_source) as data_file:
        df = load_dataframe(data_file)
        if column_name not in df.columns:
            raise HTTPException(404, "变量不存在")
        series = df[column_name]
        inferred_type = infer_variable_type(series, column_name)
        metadata = metadata_map.get(column_name, {})
        values = sort_label_values(series.dropna().unique().tolist())
        final_type = metadata.get("var_type") or inferred_type
        return {
            "column": column_name,
            "type": final_type,
            "values": values[:limit],
            "total_unique": len(values),
            "truncated": len(values) > limit,
            "sample_size": int(series.dropna().shape[0]),
            "recommended_groups": recommended_auto_group_count(int(series.dropna().shape[0])),
            "supports_labels": final_type == "categorical",
            "value_labels": metadata.get("value_labels", {}),
            "code_rules": metadata.get("code_rules", {}),
            "source": data_source["source"],
            "dataset_version_id": data_source["dataset_version_id"],
            "dataset_version_no": data_source["dataset_version_no"],
        }


async def export_data_file(session_id: str, export_format: str, *, allow_legacy_fallback: bool = False):
    data_source = await resolve_session_data_source(
        session_id,
        allow_legacy_fallback=allow_legacy_fallback,
    )
    filename = data_source["filename"]
    with materialized_session_data(data_source) as data_file:
        df, _ = parse_data_file(data_file)
        content, media_type = _export_dataframe_content(df, export_format)
        export_name = _build_export_filename(filename, export_format)
        return download_response(content, export_name, media_type)


async def get_variables(session_id: str, metadata_map: dict[str, dict], *, allow_legacy_fallback: bool = False):
    data_source = await resolve_session_data_source(
        session_id,
        allow_legacy_fallback=allow_legacy_fallback,
    )
    with materialized_session_data(data_source) as data_file:
        df = load_dataframe(data_file)
        variables = []
        for col in df.columns:
            metadata = metadata_map.get(str(col), {})
            variables.append({
                "name": str(col),
                "display_name": metadata.get("display_name") or str(col),
                "dtype": str(df[col].dtype),
                "type": metadata.get("var_type") or infer_variable_type(df[col], col),
                "nunique": int(df[col].nunique(dropna=True)),
                "missing": int(df[col].isna().sum()),
                "value_labels": metadata.get("value_labels", {}),
                "code_rules": metadata.get("code_rules", {}),
            })
        return {
            "variables": variables,
            "total_rows": len(df),
            "source": data_source["source"],
            "dataset_version_id": data_source["dataset_version_id"],
            "dataset_version_no": data_source["dataset_version_no"],
        }


def _build_export_filename(filename: str, export_format: str) -> str:
    base_name = os.path.splitext(filename)[0]
    return f"{base_name}{EXPORT_FORMATS[export_format]['ext']}"


def _export_dataframe_content(df: pd.DataFrame, export_format: str):
    if export_format not in EXPORT_FORMATS:
        raise HTTPException(400, "不支持的导出格式")

    if export_format == "xlsx":
        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        return buffer.getvalue(), EXPORT_FORMATS[export_format]["media_type"]
    if export_format == "csv":
        return df.to_csv(index=False).encode("utf-8-sig"), EXPORT_FORMATS[export_format]["media_type"]
    if export_format in {"tsv", "txt"}:
        return df.to_csv(index=False, sep="\t").encode("utf-8-sig"), EXPORT_FORMATS[export_format]["media_type"]
    if export_format == "json":
        return df.to_json(orient="records", force_ascii=False, indent=2).encode("utf-8"), EXPORT_FORMATS[export_format]["media_type"]
    if export_format == "parquet":
        buffer = BytesIO()
        df.to_parquet(buffer, index=False)
        return buffer.getvalue(), EXPORT_FORMATS[export_format]["media_type"]

    try:
        import pyreadstat
    except Exception as exc:
        raise HTTPException(500, f"缺少导出依赖: {str(exc)}")

    suffix = EXPORT_FORMATS[export_format]["ext"]
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            temp_path = temp.name
        if export_format == "sav":
            pyreadstat.write_sav(df, temp_path)
        elif export_format == "dta":
            pyreadstat.write_dta(df, temp_path)
        elif export_format == "xpt":
            pyreadstat.write_xport(df, temp_path)
        else:
            raise HTTPException(400, "不支持的导出格式")
        with open(temp_path, "rb") as handle:
            return handle.read(), EXPORT_FORMATS[export_format]["media_type"]
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
