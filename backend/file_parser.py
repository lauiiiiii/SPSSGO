# -*- coding: utf-8 -*-
import asyncio
import pandas as pd
import os
import json


def _read_csv_auto(filepath, sep=","):
    for enc in ["utf-8", "gbk", "gb2312", "latin1"]:
        try:
            return pd.read_csv(filepath, encoding=enc, sep=sep)
        except (UnicodeDecodeError, Exception):
            continue
    return pd.read_csv(filepath, encoding="utf-8", errors="replace", sep=sep)


def parse_data_file(filepath):
    """读取多种格式的数据文件，返回 DataFrame 和数据摘要"""
    ext = os.path.splitext(filepath)[1].lower()

    if ext in (".xlsx", ".xls"):
        df = pd.read_excel(filepath)

    elif ext == ".csv":
        df = _read_csv_auto(filepath, sep=",")

    elif ext == ".tsv":
        df = _read_csv_auto(filepath, sep="\t")

    elif ext == ".txt":
        with open(filepath, "r", errors="replace") as f:
            first = f.readline()
        sep = "\t" if "\t" in first else ","
        df = _read_csv_auto(filepath, sep=sep)

    elif ext in (".sav", ".zsav"):
        import pyreadstat
        df, _ = pyreadstat.read_sav(filepath)

    elif ext == ".dta":
        import pyreadstat
        df, _ = pyreadstat.read_dta(filepath)

    elif ext == ".sas7bdat":
        import pyreadstat
        df, _ = pyreadstat.read_sas7bdat(filepath)

    elif ext == ".xpt":
        import pyreadstat
        df, _ = pyreadstat.read_xport(filepath)

    elif ext == ".parquet":
        df = pd.read_parquet(filepath)

    elif ext == ".json":
        df = pd.read_json(filepath, encoding="utf-8")

    else:
        raise ValueError(f"不支持的文件格式: {ext}")

    return df, summarize_dataframe(df)


def summarize_dataframe(df):
    summary = {
        "total_rows": len(df),
        "total_cols": len(df.columns),
        "columns": [],
        "preview_rows": json.loads(df.head(20).to_json(orient="records", force_ascii=False)),
    }

    for col in df.columns:
        col_info = {
            "name": str(col),
            "dtype": str(df[col].dtype),
            "missing": int(df[col].isna().sum()),
            "unique": int(df[col].nunique()),
        }
        if pd.api.types.is_numeric_dtype(df[col]):
            col_info["min"] = float(df[col].min()) if not df[col].isna().all() else None
            col_info["max"] = float(df[col].max()) if not df[col].isna().all() else None
            col_info["mean"] = round(float(df[col].mean()), 3) if not df[col].isna().all() else None
        else:
            top_vals = df[col].value_counts().head(5).to_dict()
            col_info["top_values"] = {str(k): int(v) for k, v in top_vals.items()}
        summary["columns"].append(col_info)

    return summary


def parse_questionnaire(filepath):
    """从 Word 文件中提取问卷文本"""
    ext = os.path.splitext(filepath)[1].lower()
    if ext in (".docx", ".doc"):
        from docx import Document
        doc = Document(filepath)
        lines = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                lines.append(text)
        return "\n".join(lines)
    else:
        return ""


async def parse_data_file_async(filepath):
    return await asyncio.to_thread(parse_data_file, filepath)


async def parse_questionnaire_async(filepath):
    return await asyncio.to_thread(parse_questionnaire, filepath)


def build_data_context(summary, questionnaire_text=""):
    """构建发给 AI 的数据上下文描述"""
    ctx = f"数据集共 {summary['total_rows']} 行、{summary['total_cols']} 列。\n\n"
    ctx += "各列信息：\n"
    for col in summary["columns"]:
        line = f"- {col['name']}（类型: {col['dtype']}，缺失: {col['missing']}，唯一值: {col['unique']}"
        if "mean" in col and col["mean"] is not None:
            line += f"，均值: {col['mean']}，范围: {col['min']}-{col['max']}"
        if "top_values" in col:
            top = ", ".join(f"{k}={v}" for k, v in list(col["top_values"].items())[:3])
            line += f"，常见值: {top}"
        line += "）"
        ctx += line + "\n"

    ctx += f"\n前5行数据预览：\n"
    for i, row in enumerate(summary["preview_rows"][:5]):
        ctx += f"  行{i+1}: {json.dumps(row, ensure_ascii=False)}\n"

    if questionnaire_text:
        ctx += f"\n问卷内容：\n{questionnaire_text}\n"

    return ctx

