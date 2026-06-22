# -*- coding: utf-8 -*-
# 联合分析（Conjoint Analysis）：基于虚拟变量回归估计属性水平效用与属性重要性。
# 对齐 SPSSAU 输出颗粒度：汇总表 + 饼图 + 估计结果 + ANOVA + ols回归模型拟合优度 + 联合分析模型拟合度 + 分析建议 + 智能分析
from backend.analysis.common import *

METHOD_KEY = "conjoint"
METHOD_META = {
    'label': '联合分析',
    'category': '高级问卷分析包',
    'description': '估计用户对多个属性水平的偏好权重',
    'order': 150,
    'slots': [
        {
            'key': 'score_var',
            'label': '偏好评分变量',
            'type': 'single',
            'accept': 'numeric',
            'hint': '放入评分或偏好变量',
        },
        {
            'key': 'attribute_vars',
            'label': '属性变量',
            'type': 'multiple',
            'accept': 'categorical',
            'min': 2,
            'hint': '放入属性水平变量',
        },
    ],
    'options': [
        {
            'key': 'save_utility',
            'label': '保存效用值',
            'type': 'checkbox',
            'default': False,
            'hint': '点击后会新生成标题来标识效用值，选中后每次分析均会得到新标题。',
        },
        {
            'key': 'save_residual',
            'label': '保存残差和预测值',
            'type': 'checkbox',
            'default': False,
            'hint': '将残差和预测值分别以标题形式保存起来，选中后每次分析均会得到新标题。',
        },
    ],
    'param_builder': 'direct',
}


def _build_formula(const, attribute_vars, design_terms):
    """构造回归方程字符串（含截距）。"""
    parts = [f"{_fmt(const, 4)}"]
    for attr, level, coef in design_terms:
        sign = "+" if coef >= 0 else "-"
        parts.append(f"{sign}{_fmt(abs(coef), 4)}*{attr}({level})")
    return "\u0176 = " + " ".join(parts)


def run(df, params):
    """
    联合分析入口：虚拟变量回归估计属性水平效用和属性重要性。

    @param df: 当前数据集
    @param params: score_var, attribute_vars, save_utility, save_residual
    @return: 对齐 SPSSAU 的结果 sections
    """
    score_var = params.get("score_var", "")
    attribute_vars = _resolve_cols(df, params.get("attribute_vars", []))
    if score_var not in df.columns:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"评分变量 {score_var} 不存在。"}
    if len(attribute_vars) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "至少需要 2 个属性变量。"}

    # 只有勾选时才保存，不勾选不生成
    save_utility = params.get("save_utility") is True
    save_residual = params.get("save_residual") is True

    temp = df[[score_var] + attribute_vars].copy()
    temp[score_var] = pd.to_numeric(temp[score_var], errors="coerce")
    temp = temp.dropna(subset=[score_var] + attribute_vars)
    if len(temp) < 8:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "有效样本不足，联合分析建议至少保留 8 条完整记录。"}

    # ===== 2阶模型：完整虚拟变量编码 =====
    design = pd.get_dummies(temp[attribute_vars].astype(str), drop_first=True, dtype=float)
    if design.empty:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "属性水平不足，无法建立联合分析模型。"}

    y = temp[score_var].astype(float)
    X2 = sm.add_constant(design)
    model2 = sm.OLS(y, X2).fit()
    n = int(model2.nobs)

    # ===== 属性水平效用值 + 属性重要性 =====
    # 对齐 SPSSAU：参考水平效用值 = 0 - 其他水平系数之和（而非直接设为0）
    # 这样效用值范围才正确，重要性占比才不会失真
    # 水平项显示完整虚拟变量列名（如"轮廓_1.0"），与 SPSSAU 一致
    utility_rows = []
    importance_map = {}
    for attr in attribute_vars:
        columns = [col for col in design.columns if col.startswith(f"{attr}_")]
        levels = sorted(temp[attr].astype(str).unique().tolist())
        base_level = levels[0] if levels else ""
        effects = {}
        for column in columns:
            level = column.split("_", 1)[1]
            effects[level] = float(model2.params.get(column, 0.0))
        # 参考水平效用值 = 0 - 其他水平系数之和（SPSSAU 算法）
        effects[base_level] = -sum(effects.values())
        for level in levels:
            # 显示完整列名：属性_水平值（如"轮廓_1.0"）
            display_name = f"{attr}_{level}"
            utility_rows.append([attr, display_name, _fmt(effects.get(level, 0.0), 4)])
        values = list(effects.values()) or [0.0]
        importance_map[attr] = max(values) - min(values)

    total_range = sum(importance_map.values()) or 1.0
    importance_sorted = sorted(importance_map.items(), key=lambda x: x[1], reverse=True)
    importance_rows = []
    for attr, value in importance_sorted:
        pct = value / total_range * 100
        importance_rows.append([attr, _fmt(value, 4), f"{_fmt(pct, 1)}%"])

    # ===== 结果汇总表（合并属性重要性 + 水平效用值） =====
    summary_headers = ["属性", "重要性值", "重要性占比", "水平项", "效用值"]
    summary_rows = []
    for attr, imp_val, imp_pct in importance_rows:
        attr_levels = [row for row in utility_rows if row[0] == attr]
        for idx, level_row in enumerate(attr_levels):
            summary_rows.append([
                attr if idx == 0 else "",
                imp_val if idx == 0 else "",
                imp_pct if idx == 0 else "",
                level_row[1],
                level_row[2],
            ])

    # ===== 饼图：属性重要性占比 =====
    pie_labels = [row[0] for row in importance_rows]
    pie_values = [float(row[1]) for row in importance_rows]
    pie_chart = {
        "chartType": "category_distribution",
        "title": "属性重要性占比",
        "data": {
            "variable": "属性",
            "labels": pie_labels,
            "counts": pie_values,
            "percents": [round(float(row[2].rstrip("%")), 4) for row in importance_rows],
            "total": round(sum(pie_values), 4),
            "defaultMode": "pie",
        },
    }

    # ===== 估计结果表：回归系数 + 标准误 + t值 + p值 =====
    # 对齐 SPSSAU：列名"水平"，截距行属性"-"水平"const"，基准水平显示"(参考项)"且统计量"-"
    estimate_headers = ["属性", "水平", "回归系数", "标准误", "t值", "显著性p值"]
    estimate_rows = []
    const_val = float(model2.params.get("const", 0.0))
    const_se = float(model2.bse.get("const", 0.0))
    const_t = float(model2.tvalues.get("const", 0.0))
    const_p = float(model2.pvalues.get("const", 0.0))
    estimate_rows.append(["-", "const", _fmt(const_val, 4), _fmt(const_se, 4), _fmt(const_t, 4), _fmt(const_p, 4)])
    for attr in attribute_vars:
        columns = [col for col in design.columns if col.startswith(f"{attr}_")]
        levels = sorted(temp[attr].astype(str).unique().tolist())
        base_level = levels[0] if levels else ""
        # 基准水平：显示"XX(参考项)"，统计量全部"-"
        estimate_rows.append([attr, f"{attr}_{base_level}(参考项)", "-", "-", "-", "-"])
        for column in columns:
            level = column.split("_", 1)[1]
            coef = float(model2.params.get(column, 0.0))
            se = float(model2.bse.get(column, 0.0))
            t_val = float(model2.tvalues.get(column, 0.0))
            p_val = float(model2.pvalues.get(column, 0.0))
            # 显示完整列名：属性_水平值
            estimate_rows.append(["", column, _fmt(coef, 4), _fmt(se, 4), _fmt(t_val, 4), _fmt(p_val, 4)])

    # ===== 模型公式 =====
    design_terms = []
    for attr in attribute_vars:
        columns = [col for col in design.columns if col.startswith(f"{attr}_")]
        if not columns:
            continue
        level = columns[0].split("_", 1)[1]
        coef = float(model2.params.get(columns[0], 0.0))
        design_terms.append((attr, level, coef))
    formula_text = _build_formula(const_val, attribute_vars, design_terms)

    # ===== ANOVA 表：整体模型方差分析（对齐 SPSSAU） =====
    try:
        anova_rows = []
        total_ss = float(model2.centered_tss) if hasattr(model2, "centered_tss") else float(model2.ssr + model2.ess)
        # 回归项
        model_ss = float(model2.ess)
        model_df = int(model2.df_model)
        anova_rows.append([
            "回归",
            _fmt(model_df, 0),
            _fmt(model_ss, 4),
            _fmt(model_ss / model_df if model_df > 0 else 0.0, 4),
            _fmt(model2.fvalue, 3),
            _fmt(model2.f_pvalue, 4),
            "***" if model2.f_pvalue < 0.001 else ("**" if model2.f_pvalue < 0.01 else ("*" if model2.f_pvalue < 0.05 else "")),
        ])
        # 残差行
        resid_ss = float(model2.ssr)
        resid_df = int(model2.df_resid)
        anova_rows.append([
            "残差",
            _fmt(resid_df, 0),
            _fmt(resid_ss, 4),
            _fmt(resid_ss / resid_df if resid_df > 0 else 0.0, 4),
            "—",
            "—",
            "",
        ])
        # 合计行
        anova_rows.append([
            "总计",
            _fmt(n - 1, 0),
            _fmt(total_ss, 4),
            "—",
            "—",
            "—",
            "",
        ])
    except Exception:
        anova_rows = []

    # ===== 预测值表 =====
    if save_residual:
        y_pred = model2.fittedvalues
        y_actual = y.values
        residuals = y_actual - y_pred
        predict_headers = ["序号", "实际值", "预测值", "残差"]
        predict_rows = []
        for i in range(min(n, 50)):  # 最多显示前50条
            predict_rows.append([
                str(i + 1),
                _fmt(y_actual[i], 4),
                _fmt(y_pred[i], 4),
                _fmt(residuals[i], 4),
            ])

    # ===== ols回归模型拟合优度（对齐 SPSSAU：单行显示整体模型指标） =====
    model_fit_headers = ["模型", "R\u00B2", "调整R\u00B2", "F值", "标准误差"]
    model_fit_rows = [
        ["ols回归模型拟合优度", _fmt(model2.rsquared, 3), _fmt(model2.rsquared_adj, 3), _fmt(model2.fvalue, 3), _fmt(float(np.sqrt(model2.mse_resid)), 3)],
    ]

    # ===== 联合分析模型拟合度（对齐 SPSSAU：Pearson + Kendall） =====
    try:
        y_pred_full = model2.fittedvalues
        pearson_r, pearson_p = stats.pearsonr(y, y_pred_full)
        kendall_tau, kendall_p = stats.kendalltau(y, y_pred_full)
        fit_quality_headers = ["指标", "值"]
        fit_quality_rows = [
            ["Pearson相关系数", _fmt(pearson_r, 4)],
            ["p值", _fmt(pearson_p, 4)],
            ["Kendall相关系数", _fmt(kendall_tau, 4)],
            ["p值", _fmt(kendall_p, 4)],
        ]
    except Exception:
        fit_quality_headers = ["指标", "值"]
        fit_quality_rows = [
            ["Pearson相关系数", "—"],
            ["p值", "—"],
            ["Kendall相关系数", "—"],
            ["p值", "—"],
        ]

    # ===== 分析建议（对齐 SPSSAU） =====
    advice_lines = [
        "联合分析估计结果展示数学原理上的中间计算过程。",
        "第一：联合分析的数学原理为进行线性 ols 回归，其得到的回归系数值即为水平的效用值。",
        "第二：同一属性内的第 1 个水平作为参考项，因而无数据结果。",
        f"第三：模型方差分析的结果{'通过' if model2.f_pvalue < 0.05 else '未通过'}线性回归检验，如果通过 F 检验(p 值<0.05)即说明模型有效，即意味着联合分析模型的结果有意义。",
        f"第四：ols 回归模型拟合优度指标中的 R 方值越大，意味着属性对于轮廓打分的解释越大。",
        "第五：联合分析模型拟合度可分析模型优劣情况，并提供 Pearson 相关系数和 Kendall 相关系数，该系数越大意味着模型的拟合优度佳，如果 p 值<0.05，此时可能意味着模型拟合结果无法正常使用。",
        "第六：相关系数的计算意义为轮廓得分与预测轮廓得分之间的相关关系。",
    ]
    advice_text = "\n".join(advice_lines)

    # ===== 智能分析 =====
    top_attr = importance_sorted[0][0] if importance_sorted else attribute_vars[0]
    smart_text = (
        f"联合分析完成，共纳入 {n} 条有效记录。"
        f"当前最重要的属性为 {top_attr}，其重要性占比为 {importance_rows[0][2] if importance_rows else '—'}。"
    )

    # ===== 组装 sections（对齐 SPSSAU 输出顺序） =====
    sections = [
        _sec_table(
            "联合分析结果汇总",
            summary_headers,
            summary_rows,
            description="上表展示了各属性的重要性值、重要性占比、各水平的效用值。属性重要性值越大表示该属性对偏好的影响程度越大。",
        ),
        _sec_advice(advice_text),
        _sec_smart(smart_text),
        _sec_charts("属性重要性占比", [pie_chart]),
        _sec_table(
            "联合分析(Conjoint Analysis)估计结果",
            estimate_headers,
            estimate_rows,
            description="以每个属性的首个水平为参照水平（系数强制为 0），其余水平的系数表示相对该参照水平的效用差异。",
            note=formula_text,
        ),
    ]

    if anova_rows:
        sections.append(_sec_table(
            "方差分析（ANOVA）",
            ["项", "自由度", "SS", "MS", "F值", "p值", "显著性"],
            anova_rows,
            description="方差分析用于检验模型的整体显著性，p<0.05 表示模型对偏好评分有显著解释力。",
        ))

    sections.extend([
        _sec_table(
            "ols回归模型拟合优度",
            model_fit_headers,
            model_fit_rows,
            description="R\u00B2 越高模型解释力越强，调整 R\u00B2 考虑了自变量个数的惩罚。",
        ),
        _sec_table(
            "联合分析模型拟合度",
            fit_quality_headers,
            fit_quality_rows,
            description="Pearson 和 Kendall 相关系数反映实际偏好评分与模型预测值的相关性，值越接近 1 拟合越好，p<0.05 表示相关性显著。",
        ),
        _sec_refs(_REFS_CONJOINT),
    ])

    result = {
        "name": METHOD_META["label"],
        "headers": summary_headers,
        "rows": summary_rows,
        "description": f"联合分析完成，共纳入 {n} 条有效记录，最重要的属性为 {top_attr}。",
        "sections": sections,
    }

    # 保存效用值和残差/预测值为新变量
    score_columns = []
    if save_utility:
        # 为每个属性生成效用值列（参考水平效用值 = 0 - 其他系数之和，对齐 SPSSAU）
        for attr in attribute_vars:
            levels = sorted(temp[attr].astype(str).unique().tolist())
            base_level = levels[0] if levels else ""
            columns = [col for col in design.columns if col.startswith(f"{attr}_")]
            effects = {}
            for column in columns:
                level = column.split("_", 1)[1]
                effects[level] = float(model2.params.get(column, 0.0))
            effects[base_level] = -sum(effects.values())
            utility_col = temp[attr].astype(str).map(effects).values.tolist()
            score_columns.append({
                "base_name": f"效用值_{attr}",
                "values": utility_col,
            })

    if save_residual:
        y_pred = model2.fittedvalues.tolist()
        y_actual = y.values.tolist()
        residuals_list = [y_actual[i] - y_pred[i] for i in range(n)]
        score_columns.extend([
            {"base_name": "预测值", "values": y_pred},
            {"base_name": "残差", "values": residuals_list},
        ])

    if score_columns:
        result["score_columns"] = score_columns

    return result
