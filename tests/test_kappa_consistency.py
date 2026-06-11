import pandas as pd
import pytest
from sklearn.metrics import cohen_kappa_score

from backend.analysis.methods.kappa_consistency import METHOD_META, run, _kappa_stats


def _frame_from_matrix(matrix, row_labels, col_labels):
    rows = []
    for row_index, row_label in enumerate(row_labels):
        for col_index, col_label in enumerate(col_labels):
            rows.extend([[row_label, col_label]] * matrix[row_index][col_index])
    return pd.DataFrame(rows, columns=["老师0", "老师1"])


def test_simple_kappa_matches_fleiss_cohen_everitt_asymptotic():
    """
    主表 SE/SE0/Z/P/CI 走 Fleiss-Cohen-Everitt 1969 大样本渐近方差；
    详细结论里 Cohen 1960 经典手算近似 SE 作为另一种量级参考。
    """
    stats = _kappa_stats(
        [
            [0, 0, 2],
            [3, 0, 2],
            [8, 13, 22],
        ],
        None,
    )

    # po、pe、Kappa 是确定性公式，给定列联矩阵唯一合法解
    assert stats["n"] == pytest.approx(50)
    assert stats["po"] == pytest.approx(0.44)
    assert stats["pe"] == pytest.approx(0.482)
    assert stats["kappa"] == pytest.approx(-0.0810810811)
    # 主表 Fleiss-Cohen-Everitt 1969 渐近：SE0 用于检验、SE 用于 CI，两列不同值
    assert stats["se0"] == pytest.approx(0.0798490698)
    assert stats["se"] == pytest.approx(0.0537741185)
    assert stats["z"] == pytest.approx(-1.0154292506)
    assert stats["p"] == pytest.approx(0.3099012557)
    assert stats["ci_low"] == pytest.approx(-0.1864764167)
    assert stats["ci_high"] == pytest.approx(0.0243142546)
    # 量级参考：Cohen 1960 经典手算近似 SE=sqrt(po(1-po)/(N(1-pe)))
    assert stats["se_manual"] == pytest.approx(0.0975372417)
    assert stats["z_manual"] == pytest.approx(-0.8312833097)
    assert stats["p_manual"] == pytest.approx(0.405813601)
    assert stats["ci_low_manual"] == pytest.approx(-0.2722505619)
    assert stats["ci_high_manual"] == pytest.approx(0.1100883997)


def test_kappa_outputs_spss_style_result_table_and_heatmap():
    df = _frame_from_matrix(
        [
            [0, 0, 2],
            [3, 0, 2],
            [8, 13, 22],
        ],
        ["A", "B", "C"],
        ["A", "B", "C"],
    )

    result = run(df, {"rater1": "老师0", "rater2": "老师1"})

    assert METHOD_META["slots"][0]["key"] == "variables"
    assert METHOD_META["slots"][0]["min"] == 2
    assert METHOD_META["slots"][1]["key"] == "weight"
    assert METHOD_META["options"][0]["choices"] == ["简单Kappa", "线性加权Kappa", "平方加权Kappa", "Fleiss Kappa系数"]
    assert result["name"] == "Kappa一致性检验_老师0_老师1"

    main = next(section for section in result["sections"] if section["title"] == "输出结果1：Kappa系数结果表格")
    assert main["headers"] == ["名称", "Kappa值", "标准误(假定原假设)", "z 值", "p 值", "标准误", "95% CI"]
    assert main["rows"][0][0] == "老师0 & 老师1"
    assert main["rows"][0][1] == "-0.081"
    # Fleiss-Cohen-Everitt 1969 渐近：SE0=0.080(假定H0), SE=0.054(一般情况)
    assert main["rows"][0][2] == "0.080"
    assert main["rows"][0][3] == "-1.015"
    assert main["rows"][0][4] == "0.310"
    assert main["rows"][0][5] == "0.054"
    assert main["rows"][0][6] == "-0.186 ~ 0.024"

    titles = [section["title"] for section in result["sections"]]
    assert titles == [
        "分析配置",
        "分析步骤",
        "输出结果1：Kappa系数结果表格",
        "输出结果1.1：评价者交叉表",
        "详细结论",
        "智能分析",
        "输出结果2：Kappa相关系数矩阵热力图",
        "参考文献",
    ]
    detail = next(section for section in result["sections"] if section["title"] == "详细结论")
    assert "观察一致比例po=0.440" in detail["content"]
    assert "随机期望一致比例pe=0.482" in detail["content"]
    # 详细结论：主表给 Fleiss-Cohen-Everitt 1969 渐近，Cohen 1960 经典手算近似作另一种量级参考
    assert "Fleiss-Cohen-Everitt 1969 大样本渐近方差" in detail["content"]
    assert "Cohen 1960 经典手算近似" in detail["content"]

    config = next(section for section in result["sections"] if section["title"] == "分析配置")
    assert ["统计口径", "Fleiss-Cohen-Everitt 1969 大样本渐近方差"] in config["rows"]
    assert ["评价变量", "老师0、老师1"] in config["rows"]

    assert not any("一致性列表" in section.get("title", "") for section in result["sections"])

    # 评价者交叉表 section 必须包含矩阵和总计行，方便用户和外部参考软件的列联表逐格对照
    crosstab = next(section for section in result["sections"] if section["title"] == "输出结果1.1：评价者交叉表")
    assert crosstab["headers"][0] == "老师0\\老师1"
    assert crosstab["headers"][-1] == "总计"
    assert crosstab["rows"][-1][0] == "总计"

    chart_section = next(section for section in result["sections"] if section["title"] == "输出结果2：Kappa相关系数矩阵热力图")
    chart = chart_section["charts"][0]
    assert chart["chartType"] == "correlation_heatmap"
    assert chart["data"]["rowLabels"] == ["老师0", "老师1"]
    assert chart["data"]["values"][0][1] == pytest.approx(cohen_kappa_score(df["老师0"], df["老师1"]))


def test_kappa_accepts_multiple_variables_slot():
    df = pd.DataFrame({
        "老师0": ["从不", "偶尔", "经常", "偶尔"],
        "老师1": ["从不", "经常", "经常", "偶尔"],
        "老师2": ["偶尔", "偶尔", "经常", "从不"],
    })

    result = run(df, {"variables": ["老师0", "老师1", "老师2"]})

    main = next(section for section in result["sections"] if section["title"] == "输出结果1：Kappa系数结果表格")
    assert [row[0] for row in main["rows"]] == ["老师0 & 老师1", "老师0 & 老师2", "老师1 & 老师2"]
    chart_section = next(section for section in result["sections"] if section["title"] == "输出结果2：Kappa相关系数矩阵热力图")
    assert chart_section["charts"][0]["data"]["rowLabels"] == ["老师0", "老师1", "老师2"]


def test_kappa_supports_linear_weighted_kappa():
    df = pd.DataFrame({
        "r1": [1, 1, 1, 2, 2, 3, 3, 3],
        "r2": [1, 1, 2, 2, 3, 2, 3, 3],
    })

    result = run(df, {"rater1": "r1", "rater2": "r2", "kappa_type": "线性加权Kappa"})

    main = next(section for section in result["sections"] if section["title"] == "输出结果1：Kappa系数结果表格")
    assert main["rows"][0][1] == f"{cohen_kappa_score(df['r1'].astype(str), df['r2'].astype(str), weights='linear'):.3f}"
    config = next(section for section in result["sections"] if section["title"] == "分析配置")
    assert config["rows"][0] == ["算法", "线性加权Kappa"]


def test_kappa_supports_quadratic_weighted_kappa():
    df = pd.DataFrame({
        "r1": [1, 1, 1, 2, 2, 3, 3, 3],
        "r2": [1, 1, 2, 2, 3, 2, 3, 3],
    })

    result = run(df, {"rater1": "r1", "rater2": "r2", "kappa_type": "平方加权Kappa"})

    main = next(section for section in result["sections"] if section["title"] == "输出结果1：Kappa系数结果表格")
    assert main["rows"][0][1] == f"{cohen_kappa_score(df['r1'].astype(str), df['r2'].astype(str), weights='quadratic'):.3f}"
    config = next(section for section in result["sections"] if section["title"] == "分析配置")
    assert config["rows"][0] == ["算法", "平方加权Kappa"]


def test_kappa_supports_optional_sample_weight():
    df = pd.DataFrame({
        "r1": ["A", "A", "B", "B"],
        "r2": ["A", "B", "B", "B"],
        "w": [2, 1, 1, 2],
    })

    result = run(df, {"variables": ["r1", "r2"], "weight": "w"})

    config = next(section for section in result["sections"] if section["title"] == "分析配置")
    assert ["权重变量", "w"] in config["rows"]
    assert not any("一致性列表" in section.get("title", "") for section in result["sections"])


def test_kappa_ignores_invalid_optional_weight_instead_of_dropping_all_rows():
    df = pd.DataFrame({
        "r1": ["A", "A", "B", "B"],
        "r2": ["A", "B", "B", "B"],
        "w": ["", None, 0, -1],
    })

    result = run(df, {"variables": ["r1", "r2"], "weight": "w"})

    assert result["description"] != "有效样本不足。"
    config = next(section for section in result["sections"] if section["title"] == "分析配置")
    assert ["有效样本量", "4"] in config["rows"]
    assert any(row[0] == "权重变量" and "已按未加权分析" in row[1] for row in config["rows"])
    main = next(section for section in result["sections"] if section["title"] == "输出结果1：Kappa系数结果表格")
    assert main["rows"][0][1] == f"{cohen_kappa_score(df['r1'], df['r2']):.3f}"


def test_kappa_extracts_digits_from_string_weight_column():
    """
    业务里常见把 "学生1"~"学生50" 这种带前缀的 ID 列直接拖到权重槽里当频数权重。
    宽松解析时把字符串里的数字部分抽出来作为频数权重，避免主分析退化成未加权
    （关键体现是加权后 SE 大幅缩小、显著性大幅上升）。
    """
    df = pd.DataFrame({
        "r1": ["A", "B"] * 25,
        "r2": ["A", "A", "B", "B"] * 12 + ["A", "B"],
        "学生名": [f"学生{i}" for i in range(1, 51)],
    })

    result = run(df, {"variables": ["r1", "r2"], "weight": "学生名"})

    config = next(section for section in result["sections"] if section["title"] == "分析配置")
    weight_row = next(row for row in config["rows"] if row[0] == "权重变量")
    assert "已按字符串内数字部分作为频数权重" in weight_row[1]
    # 抽数字后权重总和 = 1+2+...+50 = 1275，远大于 50 行，主表 SE 应小于纯 50 行的水平
    main = next(section for section in result["sections"] if section["title"] == "输出结果1：Kappa系数结果表格")
    se_weighted = float(main["rows"][0][5])
    assert se_weighted < 0.05  # 未加权 N=50 时 SE 在 0.1~0.2 量级，加权后必然显著缩小


def test_kappa_identifier_pair_with_text_weight_falls_back_to_unweighted():
    df = pd.DataFrame({
        "学生名": [f"学生{i}" for i in range(1, 51)],
        "老师0": ["从不", "偶尔", "经常", "偶尔", "从不"] * 10,
        "老师1": ["从不", "偶尔", "经常", "偶尔", "从不"] * 10,
    })

    result = run(df, {"variables": ["学生名", "老师0"], "weight": "老师1"})

    assert result["description"] != "有效样本不足。"
    config = next(section for section in result["sections"] if section["title"] == "分析配置")
    assert any(row[0] == "权重变量" and "已按未加权分析" in row[1] for row in config["rows"])
    main = next(section for section in result["sections"] if section["title"] == "输出结果1：Kappa系数结果表格")
    assert main["rows"][0][0] == "学生名 & 老师0"
    assert main["rows"][0][1] == "0.000"


def test_kappa_ignores_weight_when_it_duplicates_analysis_variable():
    df = pd.DataFrame({
        "r1": ["A", "A", "B", "B"],
        "r2": ["A", "B", "B", "B"],
    })

    result = run(df, {"variables": ["r1", "r2"], "weight": "r1"})

    assert result["description"] != "有效样本不足。"
    config = next(section for section in result["sections"] if section["title"] == "分析配置")
    assert ["权重变量", "未设置"] in config["rows"]


def test_kappa_fleiss_type_has_clear_guardrail():
    df = pd.DataFrame({"a": ["是", "否"], "b": ["是", "是"]})

    result = run(df, {"rater1": "a", "rater2": "b", "kappa_type": "Fleiss Kappa系数"})

    assert "Fleiss Kappa 至少需要 3 个评价变量" in result["description"]


def test_kappa_fleiss_outputs_full_se_z_p_ci_via_fleiss_levin_paik_asymptotic():
    """
    Fleiss Kappa 主表 SE/Z/P/CI 走 Fleiss-Levin-Paik 2003 大样本渐近方差（H0=0 下），
    不再是占位符 "—"。3 评价者 × 16 对象，故意构造一致性较高的数据，应得显著正 Kappa。
    """
    df = pd.DataFrame({
        "r1": ["A"] * 8 + ["B"] * 8,
        "r2": ["A"] * 7 + ["B"] * 1 + ["A"] * 1 + ["B"] * 7,
        "r3": ["A"] * 8 + ["B"] * 8,
    })

    result = run(df, {"variables": ["r1", "r2", "r3"], "kappa_type": "Fleiss Kappa系数"})

    main = next(section for section in result["sections"] if section["title"] == "输出结果1：Kappa系数结果表格")
    row = main["rows"][0]
    assert row[0] == "整体一致性"
    # Fleiss Kappa 三个评价者高度一致，主表应得正 Kappa 且 SE/Z/P/CI 都不是占位符
    kappa_val = float(row[1])
    se0_val = float(row[2])
    z_val = float(row[3])
    se_val = float(row[5])
    assert kappa_val > 0.5
    assert se0_val > 0
    assert se_val > 0
    # Fleiss-Levin-Paik 没给单独的"一般情况 SE"，主表两列同值
    assert row[2] == row[5]
    assert z_val > 1.96
    # P 值显著（行末带星号或纯数字 0.000）
    assert "0.0" in row[4] or "0.000" in row[4]
    # 95% CI 不是占位符
    assert row[6] != "—"
    assert " ~ " in row[6]

    config = next(section for section in result["sections"] if section["title"] == "分析配置")
    assert ["统计口径", "Fleiss-Levin-Paik 2003 大样本渐近方差（H0=0）"] in config["rows"]
    detail = next(section for section in result["sections"] if section["title"] == "详细结论")
    assert "Fleiss-Levin-Paik 2003 大样本渐近方差" in detail["content"]


def test_kappa_allows_identifier_like_column_as_categorical():
    df = pd.DataFrame({
        "学生名": [f"学生{i}" for i in range(1, 51)],
        "老师0": ["从不", "偶尔", "经常", "偶尔", "从不"] * 10,
    })

    result = run(df, {"rater1": "学生名", "rater2": "老师0"})

    main = next(section for section in result["sections"] if section["title"] == "输出结果1：Kappa系数结果表格")
    assert main["rows"][0][0] == "学生名 & 老师0"
    assert main["rows"][0][1] == "0.000"
    assert main["rows"][0][3] == "—"
    assert not any("一致性列表" in section.get("title", "") for section in result["sections"])
