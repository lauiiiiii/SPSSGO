import re

import numpy as np
import pandas as pd
from fastapi import HTTPException
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.feature_selection import RFE, chi2, mutual_info_classif, mutual_info_regression
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import LabelEncoder
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant

from backend.database import get_variable_metadata_map, upsert_variable_metadata
from .common import existing_columns

try:
    from xgboost import XGBClassifier, XGBRegressor
except Exception:  # pragma: no cover
    XGBClassifier = None
    XGBRegressor = None


METHOD_KEY = "feature_select"
_MARK_SUFFIX_RE = re.compile(r"\s*[（(](应保留|应剔除)[）)]\s*$")


def _is_categorical_target(series: pd.Series) -> bool:
    if not pd.api.types.is_numeric_dtype(series):
        return True
    if pd.api.types.is_integer_dtype(series) and int(series.nunique(dropna=True)) <= 10:
        return True
    return False


def _normalize_keep_count(keep_count, feature_count: int) -> int:
    keep_count = int(keep_count or 0)
    if keep_count <= 0:
        raise ValueError("目标维度必须大于 0")
    if keep_count > feature_count:
        raise ValueError("目标维度不能超过待筛选特征数量")
    return keep_count


def _target_series(df: pd.DataFrame, target: str) -> pd.Series:
    if not target or target not in df.columns:
        raise ValueError("请选择目标变量")
    return df[target]


def _sorted_keep_drop(score_map: dict[str, float], keep_count: int):
    ordered = sorted(score_map.items(), key=lambda item: item[1], reverse=True)
    keep_cols = [name for name, _ in ordered[:keep_count]]
    drop_cols = [name for name, _ in ordered[keep_count:]]
    return ordered, keep_cols, drop_cols


def _variance_selection(df: pd.DataFrame, feature_cols: list[str], threshold: float):
    variances = df[feature_cols].var()
    keep_cols = variances[variances >= threshold].index.tolist()
    drop_cols = [col for col in feature_cols if col not in keep_cols]
    ordered = sorted(variances.items(), key=lambda item: item[1], reverse=True)
    return {
        "ordered_scores": ordered,
        "keep_cols": keep_cols,
        "drop_cols": drop_cols,
        "score_name": "方差",
    }


def _vif_selection(df: pd.DataFrame, feature_cols: list[str], threshold: float):
    keep_cols = list(feature_cols)
    vif_map = {col: 1.0 for col in keep_cols}
    drop_cols = []

    while len(keep_cols) > 1:
        vif_input = add_constant(df[keep_cols], has_constant="add")
        current_vif_map = {
            col: float(variance_inflation_factor(vif_input.values, index + 1))
            for index, col in enumerate(keep_cols)
        }
        vif_map.update(current_vif_map)
        worst_col, worst_vif = max(current_vif_map.items(), key=lambda item: item[1])
        if worst_vif <= threshold:
            break
        keep_cols.remove(worst_col)
        drop_cols.append(worst_col)

    ordered = sorted(vif_map.items(), key=lambda item: item[1])
    return {
        "ordered_scores": ordered,
        "keep_cols": keep_cols,
        "drop_cols": [col for col in feature_cols if col not in keep_cols],
        "score_name": "VIF",
    }


def _random_forest_selection(df: pd.DataFrame, feature_cols: list[str], target: str, keep_count: int):
    X = df[feature_cols]
    y = _target_series(df, target)
    if _is_categorical_target(y):
        encoded_y = LabelEncoder().fit_transform(y.astype(str))
        model = RandomForestClassifier(n_estimators=300, random_state=42)
        model.fit(X, encoded_y)
    else:
        model = RandomForestRegressor(n_estimators=300, random_state=42)
        model.fit(X, pd.to_numeric(y, errors="coerce"))
    score_map = dict(zip(feature_cols, map(float, model.feature_importances_)))
    ordered, keep_cols, drop_cols = _sorted_keep_drop(score_map, keep_count)
    return {
        "ordered_scores": ordered,
        "keep_cols": keep_cols,
        "drop_cols": drop_cols,
        "score_name": "特征重要性",
    }


def _xgboost_selection(df: pd.DataFrame, feature_cols: list[str], target: str, keep_count: int):
    if XGBClassifier is None or XGBRegressor is None:
        raise ValueError("当前环境未安装 xgboost，请先安装后再使用 XGBoost 特征筛选")

    X = df[feature_cols]
    y = _target_series(df, target)
    if _is_categorical_target(y):
        encoded_y = LabelEncoder().fit_transform(y.astype(str))
        model = XGBClassifier(
            n_estimators=300,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=42,
            eval_metric="mlogloss",
        )
        model.fit(X, encoded_y)
    else:
        model = XGBRegressor(
            n_estimators=300,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=42,
        )
        model.fit(X, pd.to_numeric(y, errors="coerce"))
    score_map = dict(zip(feature_cols, map(float, model.feature_importances_)))
    ordered, keep_cols, drop_cols = _sorted_keep_drop(score_map, keep_count)
    return {
        "ordered_scores": ordered,
        "keep_cols": keep_cols,
        "drop_cols": drop_cols,
        "score_name": "特征重要性",
    }


def _pearson_selection(df: pd.DataFrame, feature_cols: list[str], target: str, keep_count: int):
    y = pd.to_numeric(_target_series(df, target), errors="coerce")
    score_map = {}
    for col in feature_cols:
        score = abs(float(df[col].corr(y, method="pearson")))
        score_map[col] = 0.0 if np.isnan(score) else score
    ordered, keep_cols, drop_cols = _sorted_keep_drop(score_map, keep_count)
    return {
        "ordered_scores": ordered,
        "keep_cols": keep_cols,
        "drop_cols": drop_cols,
        "score_name": "Pearson系数绝对值",
    }


def _mutual_info_selection(df: pd.DataFrame, feature_cols: list[str], target: str, keep_count: int):
    X = df[feature_cols]
    y = _target_series(df, target)
    if _is_categorical_target(y):
        encoded_y = LabelEncoder().fit_transform(y.astype(str))
        scores = mutual_info_classif(X, encoded_y, random_state=42)
    else:
        scores = mutual_info_regression(X, pd.to_numeric(y, errors="coerce"), random_state=42)
    score_map = dict(zip(feature_cols, map(float, scores)))
    ordered, keep_cols, drop_cols = _sorted_keep_drop(score_map, keep_count)
    return {
        "ordered_scores": ordered,
        "keep_cols": keep_cols,
        "drop_cols": drop_cols,
        "score_name": "互信息",
    }


def _chi2_selection(df: pd.DataFrame, feature_cols: list[str], target: str, keep_count: int):
    y = _target_series(df, target)
    encoded_y = LabelEncoder().fit_transform(y.astype(str))
    X = df[feature_cols]
    if float(X.min().min()) < 0:
        raise ValueError("卡方检验法要求所有待筛选特征均为非负数")
    scores, _ = chi2(X, encoded_y)
    score_map = dict(zip(feature_cols, map(float, scores)))
    ordered, keep_cols, drop_cols = _sorted_keep_drop(score_map, keep_count)
    return {
        "ordered_scores": ordered,
        "keep_cols": keep_cols,
        "drop_cols": drop_cols,
        "score_name": "卡方值",
    }


def _rfe_selection(df: pd.DataFrame, feature_cols: list[str], target: str, keep_count: int):
    X = df[feature_cols]
    y = _target_series(df, target)
    if _is_categorical_target(y):
        estimator = LogisticRegression(max_iter=1000, solver="liblinear", random_state=42)
        encoded_y = LabelEncoder().fit_transform(y.astype(str))
        selector = RFE(estimator=estimator, n_features_to_select=keep_count)
        selector.fit(X, encoded_y)
        importance = np.abs(selector.estimator_.coef_)
        feature_importance = np.max(importance, axis=0) if importance.ndim > 1 else importance
        keep_cols = list(np.array(feature_cols)[selector.support_])
        score_map = {col: float(feature_importance[idx]) for idx, col in enumerate(keep_cols)}
    else:
        estimator = LinearRegression()
        selector = RFE(estimator=estimator, n_features_to_select=keep_count)
        selector.fit(X, pd.to_numeric(y, errors="coerce"))
        importance = np.abs(selector.estimator_.coef_)
        keep_cols = list(np.array(feature_cols)[selector.support_])
        score_map = {col: float(importance[idx]) for idx, col in enumerate(keep_cols)}

    for col in feature_cols:
        score_map.setdefault(col, 0.0)
    ordered, keep_cols, drop_cols = _sorted_keep_drop(score_map, keep_count)
    return {
        "ordered_scores": ordered,
        "keep_cols": keep_cols,
        "drop_cols": drop_cols,
        "score_name": "模型贡献度",
    }


def _compute_feature_selection(df: pd.DataFrame, params: dict):
    feature_cols = existing_columns(df, (params or {}).get("variables", []) or [])
    method = (params or {}).get("method", "random_forest")
    target = (params or {}).get("target", "")
    keep_count = int((params or {}).get("keep_count", 5) or 5)
    variance_threshold = float((params or {}).get("variance_threshold", 0.01) or 0.01)
    vif_threshold = float((params or {}).get("vif_threshold", 5) or 5)

    if len(feature_cols) < 2:
        raise ValueError("请至少选择 2 个待筛选定量变量")

    if method == "variance":
        result = _variance_selection(df, feature_cols, variance_threshold)
        if not result["keep_cols"]:
            raise ValueError("当前方差阈值过高，未保留任何特征，请降低阈值后重试")
        return result

    if method == "vif":
        return _vif_selection(df, feature_cols, vif_threshold)

    keep_count = _normalize_keep_count(keep_count, len(feature_cols))

    if method == "random_forest":
        return _random_forest_selection(df, feature_cols, target, keep_count)
    if method == "xgboost":
        return _xgboost_selection(df, feature_cols, target, keep_count)
    if method == "pearson":
        return _pearson_selection(df, feature_cols, target, keep_count)
    if method == "mutual_info":
        return _mutual_info_selection(df, feature_cols, target, keep_count)
    if method == "chi2":
        return _chi2_selection(df, feature_cols, target, keep_count)
    if method == "rfe":
        return _rfe_selection(df, feature_cols, target, keep_count)

    raise ValueError("未知特征筛选方法")


def _build_message(method: str, result: dict):
    keep_cols = result["keep_cols"]
    drop_cols = result["drop_cols"]
    keep_text = "、".join(keep_cols[:8]) if keep_cols else "无"
    drop_text = "、".join(drop_cols[:8]) if drop_cols else "无"
    return (
        f"特征筛选完成（{method}），应保留 {len(keep_cols)} 个变量，应剔除 {len(drop_cols)} 个变量。"
        f" 保留：{keep_text}。剔除：{drop_text}。"
    )


def handle(df, variables, params):
    result = _compute_feature_selection(df, {**(params or {}), "variables": variables})
    method = (params or {}).get("method", "random_forest")
    return df, _build_message(method, result)


async def validate_request(session_id: str, filepath: str, params: dict):
    from backend.services.file_service import load_dataframe
    from backend.services.variable_metadata_service import infer_variable_type

    params = params or {}
    feature_cols = params.get("variables", []) or []
    target = params.get("target", "")
    method = params.get("method", "random_forest")
    df = load_dataframe(filepath)

    if len(feature_cols) < 2:
        raise HTTPException(400, "请至少选择 2 个定量变量")

    for col in feature_cols:
        if col not in df.columns:
            raise HTTPException(404, f"变量 {col} 不存在")
        if infer_variable_type(df[col], col) != "numeric":
            raise HTTPException(400, f"变量 {col} 不是定量变量，特征筛选仅支持定量变量")
        if int(df[col].isna().sum()) > 0:
            raise HTTPException(400, f"变量 {col} 含有空值，请先进行缺失值处理")

    if method not in {"variance", "random_forest", "xgboost", "pearson", "mutual_info", "chi2", "vif", "rfe"}:
        raise HTTPException(400, "特征筛选方法不合法")

    if method in {"random_forest", "xgboost", "pearson", "mutual_info", "chi2", "rfe"}:
        if not target:
            raise HTTPException(400, "请选择目标变量")
        if target not in df.columns:
            raise HTTPException(404, f"目标变量 {target} 不存在")
        if target in feature_cols:
            raise HTTPException(400, "目标变量不能与待筛选特征重复")
        if int(df[target].isna().sum()) > 0:
            raise HTTPException(400, f"目标变量 {target} 含有空值，请先进行缺失值处理")
        if method == "pearson" and infer_variable_type(df[target], target) != "numeric":
            raise HTTPException(400, "相关系数法要求目标变量为定量变量")
        if method == "chi2" and infer_variable_type(df[target], target) != "categorical":
            raise HTTPException(400, "卡方检验法要求目标变量为定类变量")

    try:
        if method == "variance":
            threshold = float(params.get("variance_threshold", 0.01))
            if threshold < 0:
                raise HTTPException(400, "方差阈值不能小于 0")
        elif method == "vif":
            threshold = float(params.get("vif_threshold", 5))
            if threshold <= 1:
                raise HTTPException(400, "VIF 阈值必须大于 1")
        else:
            keep_count = int(params.get("keep_count", 5))
            if keep_count <= 0:
                raise HTTPException(400, "目标维度必须大于 0")
            if keep_count > len(feature_cols):
                raise HTTPException(400, "目标维度不能超过待筛选特征数量")
    except HTTPException:
        raise
    except (TypeError, ValueError):
        raise HTTPException(400, "特征筛选参数不合法")

    if method == "xgboost" and (XGBClassifier is None or XGBRegressor is None):
        raise HTTPException(400, "当前环境未安装 xgboost，请先安装后再使用 XGBoost 特征筛选")

    if method == "chi2":
        feature_frame = df[feature_cols]
        if float(feature_frame.min().min()) < 0:
            raise HTTPException(400, "卡方检验法要求待筛选定量变量均为非负数")


def _base_display_name(metadata: dict, variable_name: str) -> str:
    source = metadata.get("display_name") or str(variable_name)
    cleaned = _MARK_SUFFIX_RE.sub("", source).strip()
    return cleaned or str(variable_name)


async def persist_metadata(session_id: str, params: dict):
    from backend.services.file_service import find_data_file_name, load_dataframe, materialized_upload

    filename = find_data_file_name(session_id)
    if not filename:
        return

    with materialized_upload(session_id, filename) as filepath:
        df = load_dataframe(filepath)
        result = _compute_feature_selection(df, params or {})

    metadata_map = await get_variable_metadata_map(session_id)
    feature_cols = (params or {}).get("variables", []) or []
    target = (params or {}).get("target", "")
    keep_set = set(result["keep_cols"])

    for variable_name in feature_cols:
        existing = metadata_map.get(variable_name, {})
        base_name = _base_display_name(existing, variable_name)
        suffix = "（应保留）" if variable_name in keep_set else "（应剔除）"
        await upsert_variable_metadata(
            session_id,
            variable_name,
            display_name=f"{base_name}{suffix}",
        )

    if target:
        existing = metadata_map.get(target, {})
        await upsert_variable_metadata(
            session_id,
            target,
            display_name=_base_display_name(existing, target),
        )
