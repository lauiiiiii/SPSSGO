import numpy as np
import pandas as pd
import pywt
from fastapi import HTTPException
from scipy import fftpack, special, stats
from sklearn.preprocessing import PowerTransformer


METHOD_KEY = "transform"


def _transform_fourier(series: pd.Series) -> pd.Series:
    values = np.asarray(series, dtype=float)
    transformed = np.abs(np.fft.fft(values))
    return pd.Series(transformed, index=series.index)


def _transform_inverse_fourier(series: pd.Series) -> pd.Series:
    values = np.asarray(series, dtype=float)
    restored = np.real(np.fft.ifft(values))
    return pd.Series(restored, index=series.index)


def _transform_boxcox(series: pd.Series, lam):
    shift = 0.0
    if float(series.min()) <= 0:
        shift = abs(float(series.min())) + 1e-6
    shifted = series + shift
    if lam in (None, "", np.nan):
        transformed, used_lam = stats.boxcox(shifted)
    else:
        used_lam = float(lam)
        transformed = stats.boxcox(shifted, lmbda=used_lam)
    return pd.Series(transformed, index=series.index), used_lam, shift


def _inverse_boxcox(series: pd.Series, lam, shift):
    lam = float(lam or 0)
    shift = float(shift or 0)
    if lam == 0:
        restored = np.exp(series)
    else:
        restored = np.power(series * lam + 1, 1.0 / lam)
    restored = restored - shift
    return pd.Series(restored, index=series.index)


def _transform_cwt(series: pd.Series, wavelet_name: str) -> pd.Series:
    values = np.asarray(series, dtype=float)
    scales = np.arange(1, 2)
    coeffs, _ = pywt.cwt(values, scales, wavelet_name)
    denoised = np.real(coeffs[0])
    return pd.Series(denoised, index=series.index)


def _transform_dwt(series: pd.Series, wavelet_name: str) -> pd.Series:
    values = np.asarray(series, dtype=float)
    cA, cD = pywt.dwt(values, wavelet_name)
    zero_detail = np.zeros_like(cD)
    restored = pywt.idwt(cA, zero_detail, wavelet_name)
    restored = restored[:len(values)]
    return pd.Series(restored, index=series.index)


def _transform_johnson(series: pd.Series) -> pd.Series:
    transformed, _ = stats.yeojohnson(np.asarray(series, dtype=float))
    return pd.Series(transformed, index=series.index)


def _transform_yeojohnson(series: pd.Series) -> pd.Series:
    transformer = PowerTransformer(method="yeo-johnson", standardize=False)
    transformed = transformer.fit_transform(np.asarray(series, dtype=float).reshape(-1, 1)).ravel()
    return pd.Series(transformed, index=series.index)


def handle(df, variables, params):
    params = params or {}
    t_method = params.get("method", "boxcox")
    new_var = params.get("new_var", True)
    lam = params.get("lambda")
    shift = params.get("shift", 0)
    wavelet = params.get("wavelet", "haar")

    for col in variables:
        if col not in df.columns:
            continue
        series = pd.to_numeric(df[col], errors="coerce")

        if t_method == "fourier":
            result = _transform_fourier(series)
        elif t_method == "inverse_fourier":
            result = _transform_inverse_fourier(series)
        elif t_method == "boxcox":
            result, used_lam, used_shift = _transform_boxcox(series, lam)
            lam = used_lam
            shift = used_shift
        elif t_method == "inverse_boxcox":
            result = _inverse_boxcox(series, lam, shift)
        elif t_method == "cwt":
            result = _transform_cwt(series, wavelet)
        elif t_method == "dwt":
            result = _transform_dwt(series, wavelet)
        elif t_method == "johnson":
            result = _transform_johnson(series)
        elif t_method == "yeojohnson":
            result = _transform_yeojohnson(series)
        else:
            result = series

        if new_var:
            df[f"{col}_{t_method}"] = result
        else:
            df[col] = result

    return df, f"数据变换完成（{t_method}）"


async def validate_request(session_id: str, filepath: str, params: dict):
    from backend.services.file_service import load_dataframe
    from backend.services.variable_metadata_service import infer_variable_type

    params = params or {}
    variables = params.get("variables", []) or []
    method = params.get("method", "boxcox")
    df = load_dataframe(filepath)

    if len(variables) != 1:
        raise HTTPException(400, "数据变换要求且仅支持 1 个定量变量")

    col = variables[0]
    if col not in df.columns:
        raise HTTPException(404, f"变量 {col} 不存在")
    if infer_variable_type(df[col], col) != "numeric":
        raise HTTPException(400, "数据变换仅支持定量变量")
    if int(df[col].isna().sum()) > 0:
        raise HTTPException(400, f"变量 {col} 含有空值，请先进行缺失值处理")

    valid_methods = {"fourier", "inverse_fourier", "boxcox", "inverse_boxcox", "cwt", "dwt", "johnson", "yeojohnson"}
    if method not in valid_methods:
        raise HTTPException(400, "数据变换方式不合法")

    series = pd.to_numeric(df[col], errors="coerce")
    if method == "boxcox" and float(series.min()) <= 0 and params.get("lambda") in (None, "", np.nan):
        return
    if method == "inverse_boxcox":
        try:
            float(params.get("lambda", 0))
            float(params.get("shift", 0))
        except (TypeError, ValueError):
            raise HTTPException(400, "Box-Cox 逆变换的 lambda 或平移常数不合法")
    if method == "cwt":
        if params.get("wavelet", "morl") not in {"morl", "mexh", "gaus1", "cgau1"}:
            raise HTTPException(400, "连续小波基函数不合法")
    if method == "dwt":
        if params.get("wavelet", "haar") not in {"haar", "db2", "db4", "sym4"}:
            raise HTTPException(400, "离散小波基函数不合法")
