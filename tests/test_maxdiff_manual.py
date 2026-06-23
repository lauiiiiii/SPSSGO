# -*- coding: utf-8 -*-
"""
手动验证 MaxDiff 自动识别逻辑。

模拟场景：研究用户买手机最看重什么属性。
数据格式：每行=一个受访者的选择任务，列=选项变量。
值含义：1=被选为最重要(Best)，-1=被选为最不重要(Worst)，0=该轮未出现。
"""
import pandas as pd
import sys
sys.path.insert(0, ".")

from backend.analysis.methods import maxdiff


def build_pro_dataset():
    """
    MaxDiff Pro 原始数据。

    5 个受访者，每人做 3 轮选择任务。
    每轮从 6 个属性中随机展示 4 个，受访者选最重要和最不重要。
    列名 = 选项名（属性名）。
    """
    return pd.DataFrame({
        # 受访者1 的 3 轮选择
        "respondent": [
            "R1-T1", "R1-T2", "R1-T3",
            "R2-T1", "R2-T2", "R2-T3",
            "R3-T1", "R3-T2", "R3-T3",
            "R4-T1", "R4-T2", "R4-T3",
            "R5-T1", "R5-T2", "R5-T3",
        ],
        # 最重要选择（Best）
        "best_choice": [
            "价格", "电池", "拍照",
            "价格", "系统", "价格",
            "电池", "拍照", "电池",
            "系统", "价格", "品牌",
            "拍照", "电池", "价格",
        ],
        # 最不重要选择（Worst）
        "worst_choice": [
            "外观", "品牌", "系统",
            "外观", "外观", "外观",
            "品牌", "外观", "品牌",
            "外观", "外观", "外观",
            "品牌", "品牌", "外观",
        ],
        # 6 个选项变量（定类，值为选项名称）
        "价格": [
            "价格", "电池", "拍照",
            "价格", "系统", "价格",
            "电池", "拍照", "电池",
            "系统", "价格", "品牌",
            "拍照", "电池", "价格",
        ],
        "电池": [
            "价格", "电池", "拍照",
            "价格", "系统", "价格",
            "电池", "拍照", "电池",
            "系统", "价格", "品牌",
            "拍照", "电池", "价格",
        ],
        "拍照": [
            "价格", "电池", "拍照",
            "价格", "系统", "价格",
            "电池", "拍照", "电池",
            "系统", "价格", "品牌",
            "拍照", "电池", "价格",
        ],
        "外观": [
            "价格", "电池", "拍照",
            "价格", "系统", "价格",
            "电池", "拍照", "电池",
            "系统", "价格", "品牌",
            "拍照", "电池", "价格",
        ],
        "系统": [
            "价格", "电池", "拍照",
            "价格", "系统", "价格",
            "电池", "拍照", "电池",
            "系统", "价格", "品牌",
            "拍照", "电池", "价格",
        ],
        "品牌": [
            "价格", "电池", "拍照",
            "价格", "系统", "价格",
            "电池", "拍照", "电池",
            "系统", "价格", "品牌",
            "拍照", "电池", "价格",
        ],
    })


def build_summary_dataset():
    """
    MaxDiff 汇总数据：已统计好的次数。
    """
    return pd.DataFrame({
        "选项名": ["价格", "电池", "拍照", "外观", "系统", "品牌"],
        "最重要次数": [5, 4, 2, 0, 2, 2],
        "最不重要次数": [0, 0, 0, 7, 1, 7],
        "总出现次数": [15, 15, 15, 15, 15, 15],
    })


def test_pro_mode():
    print("=" * 60)
    print("测试 MaxDiff Pro 模式（原始数据）")
    print("=" * 60)

    df = build_pro_dataset()
    print(f"\n数据形状: {df.shape}")
    print(f"\n前 5 行:")
    print(df.head().to_string(index=False))

    result = maxdiff.run(
        df,
        {
            "best_variable": "best_choice",
            "worst_variable": "worst_choice",
            "option_variables": ["价格", "电池", "拍照", "外观", "系统", "品牌"],
        },
    )

    print(f"\n结果名称: {result['name']}")
    print(f"结果描述: {result['description']}")
    print(f"\n表头: {result['headers']}")
    print(f"\n结果表:")
    for row in result["rows"]:
        print(f"  {row[0]:<6} Best={row[1]:>2}  Worst={row[2]:>2}  净得分={row[3]:>3}  重要度={row[4]:>8}")

    # 验证 section
    for section in result["sections"]:
        print(f"\nSection: [{section['type']}] {section['title']}")
        if section["type"] == "table":
            print(f"  表头: {section['headers']}")
            print(f"  行数: {len(section['rows'])}")
        elif section["type"] == "charts":
            for chart in section["charts"]:
                print(f"  图表类型: {chart['chartType']}")
                print(f"  数据: {chart['data']}")
        elif section["type"] == "advice":
            print(f"  内容: {section['content'][:100]}...")
        elif section["type"] == "references":
            print(f"  文献数: {len(section['items'])}")


def test_summary_mode():
    print("\n" + "=" * 60)
    print("测试 MaxDiff 汇总模式")
    print("=" * 60)

    df = build_summary_dataset()
    print(f"\n数据形状: {df.shape}")
    print(f"\n数据:")
    print(df.to_string(index=False))

    result = maxdiff.run(
        df,
        {
            "best_count_variable": "最重要次数",
            "worst_count_variable": "最不重要次数",
            "total_count_variable": "总出现次数",
            "index_variable": "选项名",
        },
    )

    print(f"\n结果名称: {result['name']}")
    print(f"结果描述: {result['description']}")
    print(f"\n表头: {result['headers']}")
    print(f"\n结果表:")
    for row in result["rows"]:
        print(f"  {row[0]:<6} Best={row[1]:>2}  Worst={row[2]:>2}  净得分={row[3]:>3}  重要度={row[4]:>8}")


def test_auto_detection():
    """测试自动识别逻辑。"""
    print("\n" + "=" * 60)
    print("测试自动识别逻辑")
    print("=" * 60)

    # Pro 模式参数
    pro_params = {
        "best_variable": "best_choice",
        "worst_variable": "worst_choice",
        "option_variables": ["价格", "电池"],
    }
    mode = maxdiff._detect_mode(pro_params)
    print(f"\nPro 参数 -> 识别模式: {mode}")
    assert mode == "pro", f"期望 pro，得到 {mode}"

    # 汇总模式参数
    summary_params = {
        "best_count_variable": "最重要次数",
        "worst_count_variable": "最不重要次数",
        "total_count_variable": "总出现次数",
        "index_variable": "选项名",
    }
    mode = maxdiff._detect_mode(summary_params)
    print(f"汇总参数 -> 识别模式: {mode}")
    assert mode == "summary", f"期望 summary，得到 {mode}"

    # 无效参数
    bad_params = {"variables": ["q1", "q2"]}
    mode = maxdiff._detect_mode(bad_params)
    print(f"无效参数 -> 识别模式: {mode}")
    assert mode is None, f"期望 None，得到 {mode}"

    print("\n自动识别逻辑验证通过!")


if __name__ == "__main__":
    test_auto_detection()
    test_pro_mode()
    test_summary_mode()
    print("\n" + "=" * 60)
    print("所有测试通过!")
    print("=" * 60)
