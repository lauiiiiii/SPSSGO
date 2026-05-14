import pandas as pd

from backend.analysis.methods.kano import kano_analysis


def test_kano_numeric_answers_follow_spssau_score_order():
    pairs = []
    pairs += [(5, 4)] * 4
    pairs += [(2, 2)] * 42
    pairs += [(1, 5)] * 14
    pairs += [(1, 1)] * 6
    functional, dysfunctional = zip(*pairs)
    df = pd.DataFrame({"q1_1": functional, "q2_1": dysfunctional})

    result = kano_analysis(
        df,
        {
            "functional_vars": ["q1_1"],
            "dysfunctional_vars": ["q2_1"],
        },
    )

    assert result["sections"][2]["rows"][0] == [
        "q1_1 & q2_1",
        "6.061%",
        "0.000%",
        "0.000%",
        "63.636%",
        "21.212%",
        "9.091%",
        "无差异属性",
        "8.696%",
        "0.000%",
    ]
