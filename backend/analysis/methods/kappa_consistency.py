# -*- coding: utf-8 -*-
# Kappa一致性检验：主表 SE/SE0/Z/P/CI 走 Fleiss-Cohen-Everitt 1969 大样本渐近方差
# （statsmodels.cohens_kappa 内部实现）；详细结论再附 Cohen 1960 经典手算近似 SE 当另一种参考。
# 注：Kappa 本身 (po-pe)/(1-pe) 是确定性公式，主表数值给定列联矩阵唯一合法解。
import warnings

from backend.analysis.common import *
from statsmodels.stats.inter_rater import cohens_kappa

# 95% 置信区间用正态分位点，固定写出来避免每次现算
_NORMAL_95 = 1.959963984540054

METHOD_KEY = "kappa_consistency"
METHOD_META = {
    "label": "Kappa一致性检验",
    "category": "数据检验",
    "description": "评估两个评价者或两次分类结果之间的一致性",
    "order": 65,
    "slots": [
        {
            "key": "variables",
            "label": "变量X",
            "type": "multiple",
            "accept": "any",
            "min": 2,
            "hint": "放入两个及以上定量或定类变量",
        },
        {
            "key": "weight",
            "label": "权重",
            "type": "single",
            "accept": "numeric",
            "required": False,
            "hint": "可选，放入一个样本权重变量；无有效正权重时按未加权分析",
        },
    ],
    "options": [
        {
            "key": "kappa_type",
            "label": "方法",
            "choices": ["简单Kappa", "线性加权Kappa", "平方加权Kappa", "Fleiss Kappa系数"],
            "default": "简单Kappa",
            "hint": "加权Kappa适合有序分类；Fleiss Kappa需要三列及以上评价结果。",
        },
    ],
    "param_builder": "direct",
}


_TYPE_CONFIG = {
    "简单Kappa": {"label": "简单Kappa", "weights": None},
    "线性加权Kappa": {"label": "线性加权Kappa", "weights": "linear"},
    "加权Kappa(线性Cohens)": {"label": "线性加权Kappa", "weights": "linear"},
    "平方加权Kappa": {"label": "平方加权Kappa", "weights": "quadratic"},
    "加权 Kappa(二次Cohens)": {"label": "平方加权Kappa", "weights": "quadratic"},
}

def _as_list(value):
    if value is None or value == "":
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple)):
        return list(value)
    return []


def _analysis_variables(params):
    variables = _as_list(params.get("variables"))
    for legacy_key in ("rater1", "rater2"):
        legacy_value = params.get(legacy_key)
        if legacy_value and legacy_value not in variables:
            variables.append(legacy_value)
    return variables


def _weight_variable(params):
    weight = params.get("weight")
    if isinstance(weight, (list, tuple)):
        return weight[0] if weight else ""
    return weight or ""


def _p_with_sig(p_value):
    if p_value is None or not np.isfinite(p_value):
        return "—"
    if p_value < 0.001:
        return f"{_fmt(p_value, 3)}****"
    if p_value < 0.01:
        return f"{_fmt(p_value, 3)}***"
    if p_value < 0.05:
        return f"{_fmt(p_value, 3)}**"
    if p_value < 0.1:
        return f"{_fmt(p_value, 3)}*"
    return _fmt(p_value, 3)


def _sort_categories(values):
    def sort_key(value):
        number = _safe_float(value, None)
        if number is None:
            return (1, str(value))
        return (0, number)

    return sorted([str(value) for value in values], key=sort_key)


def _empty_stats():
    return {
        "n": np.nan,
        "po": np.nan,
        "pe": np.nan,
        "kappa": np.nan,
        "se0": np.nan,
        "z": np.nan,
        "p": np.nan,
        "se": np.nan,
        "ci_low": np.nan,
        "ci_high": np.nan,
        # Cohen 1960 经典手算近似 SE 当详细结论里的另一种参考口径
        # SE_manual = sqrt(po(1-po)/(N(1-pe)))；不区分 H0 / 一般 SE，量级一致但精度低于渐近公式
        "se_manual": np.nan,
        "z_manual": np.nan,
        "p_manual": np.nan,
        "ci_low_manual": np.nan,
        "ci_high_manual": np.nan,
    }


def _classic_manual_se_backup(po, pe, n, kappa):
    """
    Cohen 1960 早期手算近似 SE = sqrt(po(1-po)/(N(1-pe)))，作为详细结论里的另一种参考口径。
    主表口径已经统一走 Fleiss-Cohen-Everitt 1969 大样本渐近，这里只是给用户一个量级对照。
    """
    denom = 1 - pe
    empty = {
        "se_manual": np.nan,
        "z_manual": np.nan,
        "p_manual": np.nan,
        "ci_low_manual": np.nan,
        "ci_high_manual": np.nan,
    }
    if not np.isfinite(denom) or denom <= 0:
        return empty
    variance = po * (1 - po) / (n * denom)
    if not np.isfinite(variance) or variance < 0:
        return empty
    se_manual = float(np.sqrt(variance))
    if se_manual <= 0:
        return {**empty, "se_manual": _safe_float(se_manual)}
    z_manual = kappa / se_manual
    p_manual = 2 * (1 - stats.norm.cdf(abs(z_manual))) if np.isfinite(z_manual) else np.nan
    return {
        "se_manual": _safe_float(se_manual),
        "z_manual": _safe_float(z_manual),
        "p_manual": _safe_float(p_manual),
        "ci_low_manual": _safe_float(kappa - _NORMAL_95 * se_manual),
        "ci_high_manual": _safe_float(kappa + _NORMAL_95 * se_manual),
    }


def _simple_kappa_stats(contingency):
    """
    简单 Cohen Kappa 主表统计量。

    - SE0：原假设 Kappa=0 下的渐近标准误，用于 Z = kappa/SE0 和显著性检验
    - SE ：一般情况渐近标准误，用于 95% CI = kappa ± 1.96·SE
    两列对应两个不同的方差公式，主表分别展示。
    详细结论再附 Cohen 1960 经典手算近似 SE 当另一种量级参考。

    Kappa、po、pe 按 Cohen 1960 原始公式手算（确定性公式，给定列联矩阵唯一解）。
    @param contingency: 方形列联矩阵
    """
    matrix = np.asarray(contingency, dtype=float)
    n = float(np.nansum(matrix))
    if n <= 0 or matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        return _empty_stats()

    row_totals = matrix.sum(axis=1)
    col_totals = matrix.sum(axis=0)
    po = float(np.trace(matrix) / n)
    pe = float(np.dot(row_totals, col_totals) / (n ** 2))
    denom = 1 - pe
    if not np.isfinite(denom) or denom <= 0:
        stats_result = _empty_stats()
        stats_result.update({"n": n, "po": po, "pe": pe})
        return stats_result

    kappa = (po - pe) / denom

    # Fleiss-Cohen-Everitt 1969 大样本渐近：主表 SE/SE0/Z/P/CI 全部来自这里
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            sm_result = cohens_kappa(matrix, wt=None, return_results=True)
        se0 = _safe_float(sm_result.get("std_kappa0"))
        se = _safe_float(sm_result.get("std_kappa"))
        z_value = _safe_float(sm_result.get("z_value"))
        p_value = _safe_float(sm_result.get("pvalue_two_sided"))
        ci_low = _safe_float(sm_result.get("kappa_low"))
        ci_high = _safe_float(sm_result.get("kappa_upp"))
    except Exception:
        se0 = se = z_value = p_value = ci_low = ci_high = np.nan

    stats_result = {
        "n": n,
        "po": po,
        "pe": pe,
        "kappa": _safe_float(kappa),
        "se0": se0,
        "z": z_value,
        "p": p_value,
        "se": se,
        "ci_low": ci_low,
        "ci_high": ci_high,
    }
    stats_result.update(_classic_manual_se_backup(po, pe, n, kappa))
    return stats_result


def _weighted_kappa_stats(contingency, weight_type):
    """加权 Kappa：走 statsmodels.cohens_kappa 渐近方差，跟简单 Kappa 主表同源。
    加权情形没有对应的经典手算近似公式，所以详细结论里不再提供另一种参考口径。"""
    matrix = np.asarray(contingency, dtype=float)
    n = float(np.nansum(matrix))
    if n <= 0 or matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        return _empty_stats()
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            result = cohens_kappa(matrix, wt=weight_type, return_results=True)
    except Exception:
        stats_result = _empty_stats()
        stats_result.update({"n": n})
        return stats_result
    return {
        "n": n,
        "po": np.nan,
        "pe": np.nan,
        "kappa": _safe_float(result.get("kappa")),
        "se0": _safe_float(result.get("std_kappa0")),
        "z": _safe_float(result.get("z_value")),
        "p": _safe_float(result.get("pvalue_two_sided")),
        "se": _safe_float(result.get("std_kappa")),
        "ci_low": _safe_float(result.get("kappa_low")),
        "ci_high": _safe_float(result.get("kappa_upp")),
        # 加权 Kappa 没有经典手算近似公式，留空避免详细结论里硬塞
        "se_manual": np.nan,
        "z_manual": np.nan,
        "p_manual": np.nan,
        "ci_low_manual": np.nan,
        "ci_high_manual": np.nan,
    }


def _kappa_stats(contingency, weight_type):
    if weight_type is None:
        return _simple_kappa_stats(contingency)
    return _weighted_kappa_stats(contingency, weight_type)


def _fleiss_kappa_stats(frame):
    """
    Fleiss Kappa：多评价者整体一致性。

    - Kappa 数值用 statsmodels.fleiss_kappa 算（Fleiss 1971 标准公式）
    - SE/Z/P/CI 按 Fleiss-Levin-Paik 2003 (3rd ed.) p.609 给的 H0=0 下大样本渐近公式：
        SE0 = sqrt( 2 / (N·m·(m-1)) · (Σpj² - (2m-3)·(Σpj²)² + 2·(m-2)·Σpj³) ) / (1 - Σpj²)
      其中 N=评价对象数、m=每对象评价者数、pj=第 j 类的整体边际比例。
      要求 balanced design（每个对象的评价者数一致），SPSSGO 主流程已保证。
    - 95% CI = kappa ± 1.96·SE0；和加权 Kappa 一样，没有第二套手算近似公式可作量级备份。
    """
    from statsmodels.stats.inter_rater import aggregate_raters, fleiss_kappa

    stats_result = _empty_stats()
    stats_result["n"] = float(len(frame))
    try:
        values, _ = aggregate_raters(frame.to_numpy())
    except Exception:
        return stats_result

    matrix = np.asarray(values, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] < 2 or matrix.shape[1] < 2:
        return stats_result

    row_sums = matrix.sum(axis=1)
    # balanced design 校验：每个对象评价者数必须一致；不一致直接退回只输出 kappa
    if not np.allclose(row_sums, row_sums[0]) or row_sums[0] < 2:
        try:
            stats_result["kappa"] = _safe_float(fleiss_kappa(matrix, method="fleiss"))
        except Exception:
            pass
        return stats_result

    n_subjects = int(matrix.shape[0])
    m_raters = int(row_sums[0])
    total = n_subjects * m_raters
    p_j = matrix.sum(axis=0) / total
    sum_p2 = float(np.sum(p_j ** 2))
    sum_p3 = float(np.sum(p_j ** 3))
    denom = 1 - sum_p2
    try:
        kappa = float(fleiss_kappa(matrix, method="fleiss"))
    except Exception:
        kappa = np.nan
    stats_result["kappa"] = _safe_float(kappa)

    if denom <= 0 or m_raters < 2 or not np.isfinite(kappa):
        return stats_result

    var_numer = sum_p2 - (2 * m_raters - 3) * sum_p2 ** 2 + 2 * (m_raters - 2) * sum_p3
    var0 = 2.0 / (n_subjects * m_raters * (m_raters - 1)) * var_numer / (denom ** 2)
    if not np.isfinite(var0) or var0 < 0:
        return stats_result
    se0 = float(np.sqrt(var0))
    if se0 <= 0:
        return stats_result
    z_value = kappa / se0
    p_value = 2 * (1 - stats.norm.cdf(abs(z_value))) if np.isfinite(z_value) else np.nan
    stats_result.update({
        "se0": _safe_float(se0),
        # Fleiss-Levin-Paik 没给单独的"一般情况 SE"公式，主流商业软件这两列直接同值
        "se": _safe_float(se0),
        "z": _safe_float(z_value),
        "p": _safe_float(p_value),
        "ci_low": _safe_float(kappa - _NORMAL_95 * se0),
        "ci_high": _safe_float(kappa + _NORMAL_95 * se0),
    })
    return stats_result


def _strength_text(kappa):
    if not np.isfinite(kappa):
        return "无法判断"
    if kappa < 0:
        return "低于随机一致"
    if kappa < 0.2:
        return "极低一致性"
    if kappa < 0.4:
        return "一般一致性"
    if kappa < 0.6:
        return "中等一致性"
    if kappa < 0.8:
        return "较强一致性"
    return "很强一致性"


def _contingency_table(temp, rater1, rater2, categories):
    if "__weight__" in temp.columns:
        table = pd.crosstab(
            temp[rater1],
            temp[rater2],
            values=temp["__weight__"],
            aggfunc="sum",
            dropna=False,
        ).fillna(0)
    else:
        table = pd.crosstab(temp[rater1], temp[rater2])
    table = table.reindex(index=categories, columns=categories, fill_value=0)
    table["总计"] = table.sum(axis=1)
    total_row = table.sum(axis=0)
    rows = [[idx, *[_fmt_count(value) for value in table.loc[idx].tolist()]] for idx in categories]
    rows.append(["总计", *[_fmt_count(value) for value in total_row.tolist()]])
    return ["评价者1\\评价者2", *categories, "总计"], rows


def _fmt_count(value):
    number = _safe_float(value)
    if np.isfinite(number) and abs(number - round(number)) < 1e-9:
        return str(int(round(number)))
    return _fmt(number, 3)


def _heatmap_chart(variables, matrix):
    return {
        "chartType": "correlation_heatmap",
        "title": "Kappa相关系数矩阵热力图",
        "data": {
            "rowLabels": variables,
            "colLabels": variables,
            "values": matrix,
            "displayModes": [
                {"key": "all", "label": "全显示(默认)", "values": matrix},
            ],
            "defaultDisplayMode": "all",
        },
    }


def _smart_text(pair_label, type_label, stats_result):
    kappa = stats_result["kappa"]
    p_value = stats_result["p"]
    if np.isfinite(p_value):
        sig_text = "呈现显著性" if p_value < 0.05 else "未呈现显著性"
        reject_text = "拒绝" if p_value < 0.05 else "不能拒绝"
        p_text = f"p值为{_fmt(p_value, 3)}，{sig_text}，{reject_text}原假设"
    else:
        p_text = "显著性暂不可判断"
    return (
        f"{type_label}结果显示：基于变量{pair_label}，Kappa值为{_fmt(kappa, 3)}，"
        f"{p_text}；一致性程度为{_strength_text(kappa)}。"
    )


def _analysis_steps(algorithm_label, variables, weight_var):
    weight_text = f"；权重变量为{weight_var}" if weight_var else ""
    if algorithm_label == "Fleiss Kappa系数":
        return (
            f"1. 将{len(variables)}个评价变量按完整样本合并，任一评价变量缺失则剔除整行。\n"
            "2. 将每行样本视为同一对象被多个评价者分类，汇总各类别被评价次数；要求每个对象的评价者数一致（balanced design）。\n"
            "3. 按 Fleiss 1971 标准公式计算整体 Fleiss Kappa，用于判断多评价者分类结果的一致性。\n"
            "4. 标准误走 Fleiss-Levin-Paik 2003 大样本渐近方差（H0=0 下）：Z=Kappa/SE0、P=2(1-Φ(|Z|))、95%CI=Kappa±1.96·SE0；主表两列同值。\n"
            "5. 结合 Kappa 判断区间输出结论。"
        )
    return (
        f"1. 对评价变量按完整样本剔除缺失值{weight_text}；类别先做空白裁剪和整数型浮点归一化，避免被切成多余分类。\n"
        "2. 对每一对评价变量构造同分类水平的方形列联矩阵，计算观察一致比例 po 和随机期望一致比例 pe。\n"
        "3. 简单 Kappa 按 k=(po-pe)/(1-pe) 计算；线性/平方加权 Kappa 按分类顺序距离加权。\n"
        "4. 主表标准误走 Fleiss-Cohen-Everitt 1969 大样本渐近方差：\"标准误(假定原假设)\"用于检验 Kappa=0、\"标准误\"用于 95% CI，两者对应两个不同的方差公式。\n"
        "5. 详细结论再附 Cohen 1960 经典手算近似 SE=sqrt(po(1-po)/(N(1-pe))) 作为另一种量级参考；并用热力图与评价者交叉表展示两两一致性。"
    )


def _detail_text(algorithm_label, variables, sample_size, first_pair_label, first_stats, pair_count):
    parts = [
        f"本次使用{algorithm_label}评估{', '.join(variables)}之间的一致性，有效样本量为{sample_size}。",
    ]
    if algorithm_label == "Fleiss Kappa系数":
        parts.append(
            f"整体Kappa值为{_fmt(first_stats.get('kappa'), 3)}，用于描述多个评价变量的整体一致性。"
        )
        if np.isfinite(first_stats.get("se0", np.nan)):
            parts.append(
                f"按 Fleiss-Levin-Paik 2003 大样本渐近方差（H0=0 下）："
                f"SE={_fmt(first_stats.get('se0'), 3)}，"
                f"Z={_fmt(first_stats.get('z'), 3)}，"
                f"P={_fmt(first_stats.get('p'), 3)}，"
                f"95%CI={_fmt(first_stats.get('ci_low'), 3)} ~ {_fmt(first_stats.get('ci_high'), 3)}。"
            )
    elif np.isfinite(first_stats.get("po", np.nan)) and np.isfinite(first_stats.get("pe", np.nan)):
        parts.append(
            f"以{first_pair_label}为例，观察一致比例po={_fmt(first_stats.get('po'), 3)}，"
            f"随机期望一致比例pe={_fmt(first_stats.get('pe'), 3)}，Kappa={_fmt(first_stats.get('kappa'), 3)}。"
        )
        parts.append(
            f"主表按 Fleiss-Cohen-Everitt 1969 大样本渐近方差："
            f"标准误(假定原假设)={_fmt(first_stats.get('se0'), 3)}，"
            f"标准误={_fmt(first_stats.get('se'), 3)}，"
            f"Z={_fmt(first_stats.get('z'), 3)}，"
            f"P={_fmt(first_stats.get('p'), 3)}，"
            f"95%CI={_fmt(first_stats.get('ci_low'), 3)} ~ {_fmt(first_stats.get('ci_high'), 3)}。"
        )
        # Cohen 1960 经典手算近似 SE，作为另一种量级参考，精度低于渐近公式
        if np.isfinite(first_stats.get("se_manual", np.nan)):
            parts.append(
                f"另一种量级参考（Cohen 1960 经典手算近似 SE=sqrt(po(1-po)/(N(1-pe)))）："
                f"SE={_fmt(first_stats.get('se_manual'), 3)}，"
                f"Z={_fmt(first_stats.get('z_manual'), 3)}，"
                f"P={_fmt(first_stats.get('p_manual'), 3)}，"
                f"95%CI={_fmt(first_stats.get('ci_low_manual'), 3)} ~ {_fmt(first_stats.get('ci_high_manual'), 3)}。"
            )
    else:
        parts.append(
            f"{first_pair_label}的Kappa值为{_fmt(first_stats.get('kappa'), 3)}，"
            "加权Kappa的标准误和置信区间按statsmodels的权重矩阵口径输出。"
        )
    if pair_count > 1:
        parts.append(f"本次共输出{pair_count}组两两Kappa，主表用于精确查看，热力图用于快速比较。")
    parts.append("判断区间：Kappa<0.2为极低，0.2~0.4为一般，0.4~0.6为中等，0.6~0.8为较强，0.8~1.0为很强。")
    return "\n".join(parts)


def _resolve_weight_series(series):
    """
    解析权重列，对字符串型 ID 列做宽松兜底。

    业务里常见把"学生1"~"学生50"这种带前缀的 ID 列直接拖到权重槽里当频数权重。
    严格的 pd.to_numeric 会把整列判为非数值，导致主分析退化成未加权，
    有效样本量、SE、显著性都被大幅低估。这里加一层正则兜底：
    只有在 pd.to_numeric 真的解析失败（列本质是字符串）时才走正则，
    避免把用户输入的负数（例如 -1、-2）被正则吞成正数。
    返回 (numeric_series, used_regex_extraction)
    """
    numeric = pd.to_numeric(series, errors="coerce")
    if (numeric.notna() & (numeric > 0)).sum() >= 2:
        return numeric.astype(float), False

    non_null = series.dropna()
    if len(non_null) == 0:
        return numeric.astype(float), False
    failed_count = int(numeric.loc[non_null.index].isna().sum())
    # 至少过半非空值都被 pd.to_numeric 判 NaN，才认为这列是字符串型，启用正则兜底
    if failed_count < len(non_null) / 2:
        return numeric.astype(float), False

    raw = series.astype(str)
    # 抽第一段非负数字（含小数）；"学生1"->1, "学生 12 号"->12, "1.5kg"->1.5
    extracted = raw.str.extract(r"(\d+(?:\.\d+)?)", expand=False)
    fallback = pd.to_numeric(extracted, errors="coerce")
    if (fallback.notna() & (fallback > 0)).sum() >= 2:
        return fallback.astype(float), True
    return numeric.astype(float), False


def _prepare_pair_frame(df, variables, weight_var):
    """
    准备两两Kappa样本。

    @param df: 原始数据
    @param variables: 评价变量列表
    @param weight_var: 可选样本权重变量
    @return: 清洗后的样本和实际权重说明
    """
    temp = df[list(variables)].dropna().copy()
    weight_info = {
        "variable": "",
        "label": "未设置",
        "missing_rule": "任一评价变量缺失时剔除整行样本",
    }
    if weight_var:
        weight_values, extracted = _resolve_weight_series(df.loc[temp.index, weight_var])
        positive_mask = weight_values.notna() & (weight_values > 0)
        if int(positive_mask.sum()) >= 2:
            temp = temp.loc[positive_mask].copy()
            temp["__weight__"] = weight_values.loc[temp.index].astype(float)
            extra = "已按字符串内数字部分作为频数权重" if extracted else ""
            label = f"{weight_var}（{extra}）" if extra else weight_var
            weight_info = {
                "variable": weight_var,
                "label": label,
                "missing_rule": "任一评价变量缺失，或权重变量缺失/非正时剔除整行样本",
            }
        else:
            # 权重列是可选增强项，空权重不能把主分析卡死。
            weight_info = {
                "variable": "",
                "label": f"{weight_var}（无有效正权重，已按未加权分析）",
                "missing_rule": "任一评价变量缺失时剔除整行样本；权重无有效正值时自动按未加权分析",
            }
    for var in variables:
        temp[var] = _normalize_category_series(temp[var])
    return temp, weight_info


def _normalize_category_series(series):
    """
    把评价变量值归一化成统一的字符串类别，避免数据脏污引发的虚假分类：
    - 整数型浮点（1.0、2.0）渲染成 "1"、"2"，避免和别处的 "1" 被算成两类
    - 前后空格统一裁剪，避免 "经常" 和 "经常 " 被切成两类
    """
    def render(value):
        if isinstance(value, (int, np.integer)):
            return str(int(value))
        if isinstance(value, float):
            if not np.isfinite(value):
                return str(value).strip()
            if abs(value - round(value)) < 1e-9:
                return str(int(round(value)))
            return str(value).strip()
        if isinstance(value, np.floating):
            value = float(value)
            if not np.isfinite(value):
                return str(value).strip()
            if abs(value - round(value)) < 1e-9:
                return str(int(round(value)))
            return str(value).strip()
        return str(value).strip()

    return series.map(render)


def _pair_result(df, variables, weight_var, weight_type):
    temp, weight_info = _prepare_pair_frame(df, variables, weight_var)
    empty_return = (temp, [], {}, {}, "", [], weight_info, [])
    if len(temp) < 2:
        return (*empty_return[:4], "有效样本不足。", *empty_return[5:])

    pair_rows = []
    pair_stats = {}
    pair_categories = {}
    # 每对 rater 的交叉表（headers + rows），按 pair_rows 顺序排列，给"评价者交叉表"诊断 section 用
    pair_tables = []
    for rater1, rater2 in combinations(variables, 2):
        categories = _sort_categories(pd.concat([temp[rater1], temp[rater2]]).unique())
        if len(categories) < 2:
            return (*empty_return[:4], "分类水平不足，无法计算 Kappa。", *empty_return[5:])
        if weight_type and len(categories) < 3:
            return (*empty_return[:4], "加权Kappa至少需要 3 个有序分类水平。", *empty_return[5:])
        table_cols = [rater1, rater2, "__weight__"] if weight_info["variable"] else [rater1, rater2]
        ct_headers, ct_rows = _contingency_table(temp[table_cols], rater1, rater2, categories)
        contingency = np.array([[float(value) for value in row[1:-1]] for row in ct_rows[:-1]], dtype=float)
        stats_result = _kappa_stats(contingency, weight_type)
        ci_text = (
            f"{_fmt(stats_result['ci_low'], 3)} ~ {_fmt(stats_result['ci_high'], 3)}"
            if np.isfinite(stats_result["ci_low"]) and np.isfinite(stats_result["ci_high"])
            else "—"
        )
        pair_label = f"{rater1} & {rater2}"
        pair_rows.append([
            pair_label,
            _fmt(stats_result["kappa"], 3),
            _fmt(stats_result["se0"], 3),
            _fmt(stats_result["z"], 3),
            _p_with_sig(stats_result["p"]),
            _fmt(stats_result["se"], 3),
            ci_text,
        ])
        pair_stats[(rater1, rater2)] = stats_result
        pair_categories[(rater1, rater2)] = categories
        # 交叉表头第一列改成实际的 rater1\rater2，方便用户和第三方软件的列联表逐格对照
        custom_headers = [f"{rater1}\\{rater2}", *ct_headers[1:]]
        pair_tables.append({"pair": pair_label, "headers": custom_headers, "rows": ct_rows})

    matrix = []
    for row_var in variables:
        row = []
        for col_var in variables:
            if row_var == col_var:
                row.append(1.0)
            else:
                key = (row_var, col_var) if (row_var, col_var) in pair_stats else (col_var, row_var)
                value = pair_stats.get(key, {}).get("kappa", np.nan)
                row.append(float(value) if np.isfinite(value) else 0)
        matrix.append(row)
    return temp, pair_rows, pair_stats, pair_categories, "", matrix, weight_info, pair_tables


def run(df, params):
    """
    Kappa 一致性检验。

    @param df: 数据 DataFrame
    @param params: variables 为两个及以上评价变量，weight 为可选样本权重；兼容旧 rater1/rater2
    @return: Kappa 主检验表、评价者交叉表、热力图、智能分析建议和参考文献
    """
    variables = _resolve_cols(df, _analysis_variables(params))
    weight_var = _weight_variable(params)
    if weight_var in variables:
        weight_var = ""
    if weight_var and weight_var not in df.columns:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "权重变量不存在。"}
    if len(variables) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "Kappa一致性检验至少需要 2 个评价变量。"}

    kappa_type = params.get("kappa_type") or params.get("type") or "简单Kappa"
    type_config = _TYPE_CONFIG.get(kappa_type, _TYPE_CONFIG["简单Kappa"])

    pair_tables = []
    if kappa_type == "Fleiss Kappa系数":
        if len(variables) < 3:
            return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "Fleiss Kappa 至少需要 3 个评价变量。"}
        temp = df[variables].dropna().copy()
        for var in variables:
            temp[var] = _normalize_category_series(temp[var])
        if len(temp) < 2:
            return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足。"}
        stats_result = _fleiss_kappa_stats(temp)
        ci_text = (
            f"{_fmt(stats_result['ci_low'], 3)} ~ {_fmt(stats_result['ci_high'], 3)}"
            if np.isfinite(stats_result["ci_low"]) and np.isfinite(stats_result["ci_high"])
            else "—"
        )
        main_rows = [[
            "整体一致性",
            _fmt(stats_result["kappa"], 3),
            _fmt(stats_result["se0"], 3),
            _fmt(stats_result["z"], 3),
            _p_with_sig(stats_result["p"]),
            _fmt(stats_result["se"], 3),
            ci_text,
        ]]
        pair_stats = {}
        pair_categories = {}
        heatmap_matrix = [[1.0 if i == j else 0 for j in range(len(variables))] for i in range(len(variables))]
        algorithm_label = "Fleiss Kappa系数"
        weight_info = {
            "variable": "",
            "label": "Fleiss Kappa不使用样本权重" if weight_var else "未设置",
            "missing_rule": "任一评价变量缺失时剔除整行样本",
        }
    else:
        temp, main_rows, pair_stats, pair_categories, error, heatmap_matrix, weight_info, pair_tables = _pair_result(
            df,
            variables,
            weight_var,
            type_config["weights"],
        )
        if error:
            return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": error}
        algorithm_label = type_config["label"]

    result_section = _sec_table(
        "输出结果1：Kappa系数结果表格",
        ["名称", "Kappa值", "标准误(假定原假设)", "z 值", "p 值", "标准误", "95% CI"],
        main_rows,
        note="注：****、***、**、* 分别代表0.1%、1%、5%、10%的显著性水平。",
        description="上表按 Fleiss-Cohen-Everitt 1969 大样本渐近方差输出：标准误(假定原假设) 用于检验 Kappa=0、标准误 用于 95% CI，两者对应两个不同的方差公式。详细结论里另附 Cohen 1960 经典手算近似 SE 作为量级参考。",
    )

    if kappa_type == "Fleiss Kappa系数":
        first_stats = stats_result
    else:
        first_stats = next(iter(pair_stats.values()), {"kappa": np.nan, "p": np.nan})
    first_pair_label = main_rows[0][0] if main_rows else "整体一致性"
    smart = _smart_text(first_pair_label, algorithm_label, first_stats)
    pair_count = len(main_rows)
    sections = [
        _sec_table(
            "分析配置",
            ["项目", "内容"],
            [
                ["算法", algorithm_label],
                [
                    "统计口径",
                    "Fleiss-Levin-Paik 2003 大样本渐近方差（H0=0）"
                    if algorithm_label == "Fleiss Kappa系数"
                    else "Fleiss-Cohen-Everitt 1969 大样本渐近方差",
                ],
                ["评价变量", "、".join(variables)],
                ["权重变量", weight_info["label"]],
                ["有效样本量", str(len(temp))],
                ["缺失值处理", weight_info["missing_rule"]],
            ],
        ),
        _sec_advice(
            _analysis_steps(algorithm_label, variables, weight_info["variable"]),
            title="分析步骤",
        ),
        result_section,
    ]
    # 评价者交叉表：Kappa 数值一旦和外部参考软件对不上，必然是这里的格子归类不同，给出后让用户逐格比对
    if pair_tables:
        for index, table in enumerate(pair_tables, start=1):
            suffix = f"（{table['pair']}）" if len(pair_tables) > 1 else ""
            sections.append(
                _sec_table(
                    f"输出结果1.{index}：评价者交叉表{suffix}",
                    table["headers"],
                    table["rows"],
                    description="上表为该评价对的列联计数矩阵，是 Kappa 计算的全部输入：对角线为两评价者判定一致的样本数，非对角线为不一致样本数；行/列总计为各评价者的边际分布。若与第三方软件结果有出入，可直接逐格比对此表，差异通常来自缺失值剔除规则、字符串空格、数值类型或类别切分不同。",
                )
            )
    sections.extend([
        _sec_advice(
            _detail_text(algorithm_label, variables, len(temp), first_pair_label, first_stats, pair_count),
            title="详细结论",
        ),
        _sec_smart(smart),
        _sec_charts(
            "输出结果2：Kappa相关系数矩阵热力图",
            [_heatmap_chart(variables, heatmap_matrix)],
            "上图展示两两Kappa值，主要通过颜色深浅比较一致性大小；对角线为变量自身一致性。",
        ),
        _sec_refs(_REFS_GENERAL + [
            "[3] Cohen J. A coefficient of agreement for nominal scales[J]. Educational and Psychological Measurement, 1960, 20(1):37-46.",
            "[4] Fleiss J L, Cohen J, Everitt B S. Large sample standard errors of kappa and weighted kappa[J]. Psychological Bulletin, 1969, 72(5):323-327.",
            "[5] Fleiss J L. Measuring nominal scale agreement among many raters[J]. Psychological Bulletin, 1971, 76(5):378-382.",
            "[6] Fleiss J L, Cohen J. The equivalence of weighted kappa and the intraclass correlation coefficient as measures of reliability[J]. Educational and Psychological Measurement, 1973, 33(3):613-619.",
            "[7] Landis J R, Koch G G. The measurement of observer agreement for categorical data[J]. Biometrics, 1977, 33(1):159-174.",
            "[8] Fleiss J L, Levin B, Paik M C. Statistical Methods for Rates and Proportions[M]. 3rd ed. Hoboken: Wiley, 2003: 598-626.",
        ]),
    ])
    return {
        "name": f"Kappa一致性检验_{'_'.join(variables[:3])}",
        "headers": result_section["headers"],
        "rows": result_section["rows"],
        "description": smart,
        "sections": sections,
    }
