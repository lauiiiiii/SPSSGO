import numpy as np
import pandas as pd
from fastapi import HTTPException
from sklearn.decomposition import KernelPCA, PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.manifold import Isomap, LocallyLinearEmbedding, TSNE
from sklearn.preprocessing import LabelEncoder, StandardScaler

from .common import existing_columns


METHOD_KEY = "reduce"


def _output_prefix(method: str) -> str:
    return {
        "pca": "PC",
        "lda": "LD",
        "isomap": "ISO",
        "lle": "LLE",
        "kpca": "KPC",
        "tsne": "TSNE",
    }.get(method, "DIM")


def _validated_numeric_frame(df: pd.DataFrame, variables: list[str]) -> tuple[pd.DataFrame, list[str]]:
    cols = existing_columns(df, variables)
    numeric_cols = [col for col in cols if pd.api.types.is_numeric_dtype(df[col])]
    if len(numeric_cols) < 2:
        raise ValueError("请至少选择 2 个定量变量")
    data = df[numeric_cols]
    return data, numeric_cols


def _resolve_components(method: str, feature_count: int, sample_count: int, params: dict, target_series=None) -> int:
    requested = int(params.get("components", 2) or 2)
    if requested < 1:
        raise ValueError("降维后变量个数必须大于等于 1")

    if method == "lda":
        if target_series is None:
            raise ValueError("LDA 需要目标变量")
        class_count = int(pd.Series(target_series).nunique(dropna=True))
        max_components = max(1, min(feature_count, class_count - 1))
        return min(requested, max_components)

    if method == "tsne":
        max_components = min(3, feature_count, sample_count)
        return min(requested, max_components)

    return min(requested, feature_count, sample_count)


def _fit_pca(X_scaled, params: dict):
    pca_mode = params.get("pca_mode", "variance_ratio")
    if pca_mode == "variance_ratio":
        variance_ratio = float(params.get("variance_ratio", 0.8) or 0.8)
        pca = PCA(n_components=variance_ratio, random_state=42)
        components = pca.fit_transform(X_scaled)
        n_comp = components.shape[1]
        return components, n_comp, pca
    requested = int(params.get("components", 2) or 2)
    n_comp = min(requested, X_scaled.shape[0], X_scaled.shape[1])
    pca = PCA(n_components=n_comp, random_state=42)
    components = pca.fit_transform(X_scaled)
    return components, n_comp, pca


def handle(df, variables, params):
    params = params or {}
    method = params.get("method", "pca")
    data, numeric_cols = _validated_numeric_frame(df, variables)
    X_scaled = StandardScaler().fit_transform(data)
    n_samples, n_features = X_scaled.shape

    if method == "pca":
        transformed, n_comp, model = _fit_pca(X_scaled, params)
        message = f"PCA降维完成，生成 {n_comp} 个主成分"
    elif method == "lda":
        target = params.get("target", "")
        if target not in df.columns:
            raise ValueError("请选择目标变量（分类变量）")
        y = LabelEncoder().fit_transform(df[target].astype(str))
        n_comp = _resolve_components("lda", n_features, n_samples, params, y)
        model = LinearDiscriminantAnalysis(n_components=n_comp)
        transformed = model.fit_transform(X_scaled, y)
        message = f"LDA降维完成，生成 {transformed.shape[1]} 个判别变量"
    elif method == "isomap":
        n_comp = _resolve_components("isomap", n_features, n_samples, params)
        n_neighbors = min(int(params.get("n_neighbors", 5) or 5), max(2, n_samples - 1))
        model = Isomap(n_components=n_comp, n_neighbors=n_neighbors)
        transformed = model.fit_transform(X_scaled)
        message = f"ISOMap降维完成，生成 {n_comp} 个变量"
    elif method == "lle":
        n_comp = _resolve_components("lle", n_features, n_samples, params)
        n_neighbors = min(int(params.get("n_neighbors", 5) or 5), max(2, n_samples - 1))
        model = LocallyLinearEmbedding(n_components=n_comp, n_neighbors=n_neighbors, method="standard", random_state=42)
        transformed = model.fit_transform(X_scaled)
        message = f"LLE降维完成，生成 {n_comp} 个变量"
    elif method == "kpca":
        n_comp = _resolve_components("kpca", n_features, n_samples, params)
        kernel = params.get("kernel", "rbf")
        model = KernelPCA(n_components=n_comp, kernel=kernel, random_state=42)
        transformed = model.fit_transform(X_scaled)
        message = f"KPCA降维完成，生成 {n_comp} 个变量"
    elif method == "tsne":
        n_comp = _resolve_components("tsne", n_features, n_samples, params)
        n_neighbors = min(int(params.get("n_neighbors", 5) or 5), max(2, n_samples - 1))
        perplexity = max(2, min(n_neighbors, n_samples - 1))
        model = TSNE(n_components=n_comp, perplexity=perplexity, random_state=42, init="pca", learning_rate="auto")
        transformed = model.fit_transform(X_scaled)
        message = f"t-SNE降维完成，生成 {n_comp} 个变量"
    else:
        raise ValueError("未知数据降维方法")

    transformed = np.asarray(transformed)
    if transformed.ndim == 1:
        transformed = transformed.reshape(-1, 1)

    df = df.drop(columns=numeric_cols)
    prefix = _output_prefix(method)
    for index in range(transformed.shape[1]):
        df[f"{prefix}{index + 1}"] = transformed[:, index]
    return df, message


async def validate_request(session_id: str, filepath: str, params: dict):
    from backend.services.file_service import load_dataframe
    from backend.services.variable_metadata_service import infer_variable_type

    params = params or {}
    variables = params.get("variables", []) or []
    method = params.get("method", "pca")
    df = load_dataframe(filepath)

    if len(variables) < 2:
        raise HTTPException(400, "请至少选择 2 个定量变量")

    for col in variables:
        if col not in df.columns:
            raise HTTPException(404, f"变量 {col} 不存在")
        if infer_variable_type(df[col], col) != "numeric":
            raise HTTPException(400, f"变量 {col} 不是定量变量，数据降维仅支持定量变量")
        if int(df[col].isna().sum()) > 0:
            raise HTTPException(400, f"变量 {col} 含有空值，请先进行缺失值处理")

    if method not in {"pca", "lda", "isomap", "lle", "kpca", "tsne"}:
        raise HTTPException(400, "数据降维方法不合法")

    try:
        components = int(params.get("components", 2) or 2)
    except (TypeError, ValueError):
        raise HTTPException(400, "降维后变量个数不合法")
    if components < 1:
        raise HTTPException(400, "降维后变量个数必须大于等于 1")

    if method == "pca":
        pca_mode = params.get("pca_mode", "variance_ratio")
        if pca_mode not in {"variance_ratio", "components"}:
            raise HTTPException(400, "PCA 参数模式不合法")
        if pca_mode == "variance_ratio":
            try:
                variance_ratio = float(params.get("variance_ratio", 0.8) or 0.8)
            except (TypeError, ValueError):
                raise HTTPException(400, "总方差解释率不合法")
            if not 0 < variance_ratio < 1:
                raise HTTPException(400, "总方差解释率必须在 0 到 1 之间")

    if method in {"isomap", "lle", "tsne"}:
        try:
            n_neighbors = int(params.get("n_neighbors", 5) or 5)
        except (TypeError, ValueError):
            raise HTTPException(400, "邻居数不合法")
        if n_neighbors < 2:
            raise HTTPException(400, "邻居数必须大于等于 2")

    if method == "kpca":
        kernel = params.get("kernel", "rbf")
        if kernel not in {"rbf", "poly", "sigmoid", "cosine"}:
            raise HTTPException(400, "KPCA 核函数不合法")

    if method == "lda":
        target = params.get("target", "")
        if not target:
            raise HTTPException(400, "请选择目标变量（分类变量）")
        if target not in df.columns:
            raise HTTPException(404, f"目标变量 {target} 不存在")
        if target in variables:
            raise HTTPException(400, "目标变量不能与待降维特征重复")
        if infer_variable_type(df[target], target) != "categorical":
            raise HTTPException(400, "LDA 要求目标变量为定类变量")
        if int(df[target].isna().sum()) > 0:
            raise HTTPException(400, f"目标变量 {target} 含有空值，请先进行缺失值处理")
