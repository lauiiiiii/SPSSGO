import numpy as np
import pandas as pd

from .common import coerce_scalar, sort_mixed_values

METHOD_KEY = "encode"


def handle(df, variables, params):
    mode = params.get('mode', 'new')
    new_var = params.get('new_var', True)
    new_var_name = params.get('new_var_name', '')
    code_map = params.get('code_map', {})
    range_map = params.get('range_map', [])
    auto_strategy = params.get('auto_strategy', 'mean_2')
    bins = max(2, int(params.get('bins', 5)))

    for col in variables:
        if col not in df.columns:
            continue
        if mode == 'new':
            if code_map:
                val_map = {coerce_scalar(k): coerce_scalar(v) for k, v in code_map.items()}
            else:
                unique_vals = sort_mixed_values(df[col].dropna().unique().tolist())
                val_map = {v: i + 1 for i, v in enumerate(unique_vals)}
            encoded = df[col].map(val_map)
        elif mode == 'range':
            numeric = pd.to_numeric(df[col], errors='coerce')
            if range_map:
                encoded = pd.Series(np.nan, index=df.index, dtype='object')
                for item in range_map:
                    try:
                        start = float(item.get('min'))
                        end = float(item.get('max'))
                    except (TypeError, ValueError):
                        continue
                    code = coerce_scalar(item.get('code'))
                    mask = numeric.ge(start) & numeric.le(end)
                    encoded.loc[mask] = code
            else:
                encoded = pd.cut(numeric, bins=5, labels=False) + 1
        elif mode == 'auto':
            numeric = pd.to_numeric(df[col], errors='coerce')
            valid = numeric.dropna()
            encoded = pd.Series(np.nan, index=df.index, dtype='float')
            if valid.empty:
                pass
            elif auto_strategy == 'mean_2':
                mean_val = valid.mean()
                encoded.loc[numeric < mean_val] = 1
                encoded.loc[numeric >= mean_val] = 2
            elif auto_strategy == 'median_2':
                median_val = valid.quantile(0.5)
                encoded.loc[numeric <= median_val] = 1
                encoded.loc[numeric > median_val] = 2
            elif auto_strategy == 'quantile_27_73':
                q27 = valid.quantile(0.27)
                q73 = valid.quantile(0.73)
                encoded.loc[numeric <= q27] = 1
                encoded.loc[(numeric > q27) & (numeric <= q73)] = 2
                encoded.loc[numeric > q73] = 3
            elif auto_strategy == 'quartile_4':
                q1 = valid.quantile(0.25)
                q2 = valid.quantile(0.5)
                q3 = valid.quantile(0.75)
                encoded.loc[numeric <= q1] = 1
                encoded.loc[(numeric > q1) & (numeric <= q2)] = 2
                encoded.loc[(numeric > q2) & (numeric <= q3)] = 3
                encoded.loc[numeric > q3] = 4
            else:
                try:
                    encoded = pd.qcut(numeric, q=bins, labels=False, duplicates='drop') + 1
                except Exception:
                    encoded = pd.cut(numeric, bins=bins, labels=False) + 1
        else:
            encoded = df[col]

        target_col = new_var_name if (new_var and new_var_name) else col + '_encoded'
        if new_var:
            df[target_col] = encoded
        else:
            df[col] = encoded

    return df, f'数据编码完成（{mode}）'


async def persist_metadata(session_id: str, params: dict):
    from backend.database import upsert_variable_metadata

    variables = params.get("variables", []) or []
    if not variables:
        return

    mode = params.get("mode", "new")
    new_var = bool(params.get("new_var", True))
    new_var_name = params.get("new_var_name", "")
    code_map = params.get("code_map", {}) or {}
    code_labels = params.get("code_labels", {}) or {}
    range_map = params.get("range_map", []) or []
    auto_strategy = params.get("auto_strategy", "mean_2")

    for col in variables:
        target_col = new_var_name if (new_var and new_var_name) else (f"{col}_encoded" if new_var else col)
        value_labels = {}
        if mode == "new":
            for _, code in code_map.items():
                if code in ("", None):
                    continue
                label = code_labels.get(str(code)) or code_labels.get(code)
                if label:
                    value_labels[str(code)] = label
        elif mode == "range":
            for item in range_map:
                code = item.get("code")
                label = item.get("label")
                if code not in ("", None) and label:
                    value_labels[str(code)] = label
        elif mode == "auto":
            if auto_strategy == "mean_2":
                value_labels = {"1": "低于均值", "2": "高于或等于均值"}
            elif auto_strategy == "median_2":
                value_labels = {"1": "低分组", "2": "高分组"}
            elif auto_strategy == "quantile_27_73":
                value_labels = {"1": "低分组", "2": "中间组", "3": "高分组"}
            elif auto_strategy == "quartile_4":
                value_labels = {"1": "第一四分位组", "2": "第二四分位组", "3": "第三四分位组", "4": "第四四分位组"}

        code_rules = {
            "mode": mode,
            "source_variable": col,
            "new_var": new_var,
            "new_var_name": new_var_name,
            "code_map": code_map,
            "range_map": range_map,
            "auto_strategy": auto_strategy,
            "bins": params.get("bins", 5),
        }
        await upsert_variable_metadata(
            session_id,
            target_col,
            var_type="categorical",
            value_labels=value_labels if value_labels else None,
            code_rules=code_rules,
        )

