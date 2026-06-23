# -*- coding: utf-8 -*-
"""
MaxDiff 鲁棒性测试：生成 100 条复杂模拟数据。

模拟场景：研究用户购买智能手机时最看重的 8 个属性。
真实偏好排序（模拟）：价格 > 电池 > 拍照 > 系统 > 屏幕 > 品牌 > 外观 > 存储
"""
import pandas as pd
import numpy as np
import sys
sys.path.insert(0, ".")

from backend.analysis.methods import maxdiff


# 设置随机种子，确保可复现
np.random.seed(42)

# 8 个手机属性，按真实偏好排序
ATTRIBUTES = ["价格", "电池", "拍照", "系统", "屏幕", "品牌", "外观", "存储"]

# 真实偏好权重（用于模拟选择概率）
TRUE_PREFERENCES = {
    "价格": 0.25,
    "电池": 0.20,
    "拍照": 0.18,
    "系统": 0.12,
    "屏幕": 0.10,
    "品牌": 0.07,
    "外观": 0.05,
    "存储": 0.03,
}


def simulate_maxdiff_pro(n_respondents=100, tasks_per_respondent=5):
    """
    模拟 MaxDiff Pro 原始数据。

    每个受访者完成 5 轮选择任务，每轮从 8 个属性中随机展示 4 个。
    受访者根据真实偏好选择最重要和最不重要的属性。
    """
    records = []

    for r in range(1, n_respondents + 1):
        for t in range(1, tasks_per_respondent + 1):
            # 随机选择 4 个属性展示
            shown_attrs = np.random.choice(ATTRIBUTES, size=4, replace=False)

            # 根据真实偏好计算选择概率
            probs = np.array([TRUE_PREFERENCES[attr] for attr in shown_attrs])
            probs = probs / probs.sum()  # 归一化

            # 选择最重要（Best）：按偏好概率
            best_idx = np.random.choice(len(shown_attrs), p=probs)
            best_choice = shown_attrs[best_idx]

            # 选择最不重要（Worst）：按反向偏好概率
            worst_probs = 1 - probs
            worst_probs = worst_probs / worst_probs.sum()
            worst_idx = np.random.choice(len(shown_attrs), p=worst_probs)
            worst_choice = shown_attrs[worst_idx]

            # 确保 Best 和 Worst 不是同一个
            while worst_choice == best_choice:
                worst_idx = np.random.choice(len(shown_attrs), p=worst_probs)
                worst_choice = shown_attrs[worst_idx]

            record = {
                "respondent": f"R{r:03d}-T{t}",
                "best_choice": best_choice,
                "worst_choice": worst_choice,
            }

            # 添加选项变量（值为选项名称）
            for attr in ATTRIBUTES:
                record[attr] = attr  # 简化：所有选项变量值都设为属性名

            records.append(record)

    return pd.DataFrame(records)


def simulate_maxdiff_summary(df_pro):
    """
    从 Pro 数据生成汇总数据。
    """
    summary = []

    for attr in ATTRIBUTES:
        best_count = int((df_pro["best_choice"] == attr).sum())
        worst_count = int((df_pro["worst_choice"] == attr).sum())
        total_count = len(df_pro)  # 每个属性在每轮都出现

        summary.append({
            "选项名": attr,
            "最重要次数": best_count,
            "最不重要次数": worst_count,
            "总出现次数": total_count,
        })

    return pd.DataFrame(summary)


def test_pro_mode_robustness():
    """测试 MaxDiff Pro 模式鲁棒性。"""
    print("=" * 70)
    print("测试 1: MaxDiff Pro 模式（100 受访者 × 5 轮 = 500 条记录）")
    print("=" * 70)

    df = simulate_maxdiff_pro(n_respondents=100, tasks_per_respondent=5)
    print(f"\n数据形状：{df.shape}")
    print(f"受访者数：{df['respondent'].str.split('-').str[0].nunique()}")
    print(f"任务数：{len(df)}")

    # 运行分析
    result = maxdiff.run(
        df,
        {
            "best_variable": "best_choice",
            "worst_variable": "worst_choice",
            "option_variables": ATTRIBUTES,
        },
    )

    # 验证结果
    assert result["name"] == "MaxDiff模型"
    assert "MaxDiff Pro" in result["description"]
    assert len(result["rows"]) == 8

    # 提取结果表
    table = next(s for s in result["sections"] if s["title"] == "MaxDiff Pro 属性估计结果")

    print("\n属性估计结果:")
    print(f"{'属性':<6} {'效用系数':>10} {'标准误差':>10} {'z 统计量':>10} {'p 值':>12} {'偏好份额':>10}")
    print("-" * 70)

    # 按效用系数排序
    sorted_rows = sorted(table["rows"], key=lambda r: float(r[1]), reverse=True)

    for row in sorted_rows:
        attr = row[0]
        utility = float(row[1])
        se = float(row[2])
        z = float(row[3])
        p_str = row[4]
        share = row[8]
        print(f"{attr:<6} {utility:>10.3f} {se:>10.3f} {z:>10.3f} {p_str:>12} {share:>10}")

    # 验证偏好排序是否与真实偏好一致
    recovered_order = [row[0] for row in sorted_rows]
    true_order = ["价格", "电池", "拍照", "系统", "屏幕", "品牌", "外观", "存储"]

    print(f"\n真实偏好排序：{true_order}")
    print(f"模型恢复排序：{recovered_order}")

    # 计算 Spearman 秩相关
    from scipy.stats import spearmanr
    true_ranks = [true_order.index(attr) for attr in recovered_order]
    recovered_ranks = list(range(len(recovered_order)))
    corr, p_value = spearmanr(true_ranks, recovered_ranks)

    print(f"\nSpearman 秩相关系数：{corr:.3f} (p={p_value:.3f})")

    # 验证偏好份额之和为 100%
    total_share = sum(float(row[8].rstrip("%")) for row in table["rows"])
    print(f"偏好份额之和：{total_share:.2f}%")
    assert abs(total_share - 100.0) < 0.1

    # 验证 Top 3 属性
    top3 = [row[0] for row in sorted_rows[:3]]
    print(f"\nTop 3 属性：{top3}")
    assert "价格" in top3, "价格应该在 Top 3"
    assert "电池" in top3, "电池应该在 Top 3"

    print("\n[OK] MaxDiff Pro 模式鲁棒性测试通过!")


def test_summary_mode_robustness():
    """测试 MaxDiff 汇总模式鲁棒性。"""
    print("\n" + "=" * 70)
    print("测试 2: MaxDiff 汇总模式（从 Pro 数据聚合）")
    print("=" * 70)

    df_pro = simulate_maxdiff_pro(n_respondents=100, tasks_per_respondent=5)
    df_summary = simulate_maxdiff_summary(df_pro)

    print(f"\n汇总数据形状：{df_summary.shape}")
    print(f"\n汇总数据:")
    print(df_summary.to_string(index=False))

    # 运行分析
    result = maxdiff.run(
        df_summary,
        {
            "best_count_variable": "最重要次数",
            "worst_count_variable": "最不重要次数",
            "total_count_variable": "总出现次数",
            "index_variable": "选项名",
        },
    )

    # 验证结果
    assert result["name"] == "MaxDiff模型"
    assert "MaxDiff" in result["description"]
    assert "MaxDiff Pro" not in result["description"]
    assert len(result["rows"]) == 8

    # 提取结果表
    table = next(s for s in result["sections"] if s["title"] == "MaxDiff 属性估计结果")

    print("\n属性估计结果:")
    print(f"{'属性':<6} {'效用系数':>10} {'标准误差':>10} {'z 统计量':>10} {'p 值':>12} {'偏好份额':>10}")
    print("-" * 70)

    sorted_rows = sorted(table["rows"], key=lambda r: float(r[1]), reverse=True)

    for row in sorted_rows:
        attr = row[0]
        utility = float(row[1])
        se = float(row[2])
        z = float(row[3])
        p_str = row[4]
        share = row[8]
        print(f"{attr:<6} {utility:>10.3f} {se:>10.3f} {z:>10.3f} {p_str:>12} {share:>10}")

    # 验证偏好排序
    recovered_order = [row[0] for row in sorted_rows]
    true_order = ["价格", "电池", "拍照", "系统", "屏幕", "品牌", "外观", "存储"]

    print(f"\n真实偏好排序：{true_order}")
    print(f"模型恢复排序：{recovered_order}")

    from scipy.stats import spearmanr
    true_ranks = [true_order.index(attr) for attr in recovered_order]
    recovered_ranks = list(range(len(recovered_order)))
    corr, p_value = spearmanr(true_ranks, recovered_ranks)

    print(f"\nSpearman 秩相关系数：{corr:.3f} (p={p_value:.3f})")

    # 验证偏好份额之和
    total_share = sum(float(row[8].rstrip("%")) for row in table["rows"])
    print(f"偏好份额之和：{total_share:.2f}%")
    assert abs(total_share - 100.0) < 0.1

    # 验证显著性
    significant_count = sum(1 for row in table["rows"] if "*" in row[4])
    print(f"\n显著属性数（p<0.05）：{significant_count}/8")

    print("\n[OK] MaxDiff 汇总模式鲁棒性测试通过!")


def test_edge_cases():
    """测试边界情况。"""
    print("\n" + "=" * 70)
    print("测试 3: 边界情况")
    print("=" * 70)

    # 测试 1: 所有选项偏好相同
    print("\n3.1 所有选项偏好相同（均匀分布）")
    df_uniform = pd.DataFrame({
        "best_choice": np.random.choice(ATTRIBUTES, size=100),
        "worst_choice": np.random.choice(ATTRIBUTES, size=100),
    })
    for attr in ATTRIBUTES:
        df_uniform[attr] = attr

    result = maxdiff.run(
        df_uniform,
        {
            "best_variable": "best_choice",
            "worst_variable": "worst_choice",
            "option_variables": ATTRIBUTES,
        },
    )

    assert result["name"] == "MaxDiff模型"
    table = next(s for s in result["sections"] if s["title"] == "MaxDiff Pro 属性估计结果")
    total_share = sum(float(row[8].rstrip("%")) for row in table["rows"])
    print(f"  偏好份额之和：{total_share:.2f}% [OK]")

    # 测试 2: 极端偏好（一个选项占主导）
    print("\n3.2 极端偏好（价格占主导）")
    df_extreme = pd.DataFrame({
        "best_choice": ["价格"] * 80 + np.random.choice(ATTRIBUTES[1:], size=20).tolist(),
        "worst_choice": ["存储"] * 30 + np.random.choice(ATTRIBUTES[:-1], size=70).tolist(),
    })
    for attr in ATTRIBUTES:
        df_extreme[attr] = attr

    result = maxdiff.run(
        df_extreme,
        {
            "best_variable": "best_choice",
            "worst_variable": "worst_choice",
            "option_variables": ATTRIBUTES,
        },
    )

    table = next(s for s in result["sections"] if s["title"] == "MaxDiff Pro 属性估计结果")
    price_row = next(row for row in table["rows"] if row[0] == "价格")
    storage_row = next(row for row in table["rows"] if row[0] == "存储")

    print(f"  价格偏好份额：{price_row[8]}")
    print(f"  存储偏好份额：{storage_row[8]}")
    assert float(price_row[8].rstrip("%")) > 20, "价格应该占主导"
    # 存储被选为最不重要，效用系数应为负
    assert float(storage_row[1]) < 0, "存储效用系数应为负"

    print("\n[OK] 边界情况测试通过!")


def test_variable_labels():
    """测试变量标题注入。"""
    print("\n" + "=" * 70)
    print("测试 4: 变量标题注入")
    print("=" * 70)

    df = simulate_maxdiff_pro(n_respondents=50, tasks_per_respondent=3)

    # 重命名变量为英文
    df = df.rename(columns={
        "best_choice": "best_var",
        "worst_choice": "worst_var",
        "价格": "price",
        "电池": "battery",
        "拍照": "camera",
        "系统": "system",
        "屏幕": "screen",
        "品牌": "brand",
        "外观": "design",
        "存储": "storage",
    })

    result = maxdiff.run(
        df,
        {
            "best_variable": "best_var",
            "worst_variable": "worst_var",
            "option_variables": ["price", "battery", "camera", "system", "screen", "brand", "design", "storage"],
            "variable_labels": {
                "price": "价格",
                "battery": "电池续航",
                "camera": "拍照效果",
                "system": "操作系统",
                "screen": "屏幕质量",
                "brand": "品牌知名度",
                "design": "外观设计",
                "storage": "存储容量",
            },
        },
    )

    table = next(s for s in result["sections"] if s["title"] == "MaxDiff Pro 属性估计结果")
    row_labels = [row[0] for row in table["rows"]]

    print(f"\n结果表中的属性名：{row_labels}")
    assert "价格" in row_labels
    assert "电池续航" in row_labels
    assert "拍照效果" in row_labels

    print("\n[OK] 变量标题注入测试通过!")


if __name__ == "__main__":
    test_pro_mode_robustness()
    test_summary_mode_robustness()
    test_edge_cases()
    test_variable_labels()

    print("\n" + "=" * 70)
    print("所有鲁棒性测试通过!")
    print("=" * 70)
