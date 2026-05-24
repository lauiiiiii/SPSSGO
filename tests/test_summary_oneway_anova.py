from backend.analysis.methods.summary_oneway_anova import run


def test_summary_oneway_anova_uses_group_summary_statistics():
    result = run(None, {
        "groups": [
            {"label": "样本1", "n": "111", "mean": "2", "std": "3"},
            {"label": "样本2", "n": "111", "mean": "3", "std": "4"},
            {"label": "样本3", "n": "111", "mean": "3", "std": "4"},
        ],
        "confidence_level": "95",
    })

    assert result["name"] == "摘要单因素方差分析"
    assert result["headers"] == ["组", "数据量", "标准差", "F", "P"]
    assert result["rows"][0] == ["样本1", "111", "3.000", "2.707", "0.068"]
    assert "不同分组样本之间不存在显著差异" in result["description"]


def test_summary_oneway_anova_requires_at_least_three_groups():
    result = run(None, {
        "groups": [
            {"label": "样本1", "n": "10", "mean": "1", "std": "1"},
            {"label": "样本2", "n": "10", "mean": "2", "std": "1"},
        ],
    })

    assert "至少需要 3 组" in result["description"]
