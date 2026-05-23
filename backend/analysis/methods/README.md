# 分析方法目录索引

这里只放具体分析方法入口文件。当前注册器按 `backend.analysis.methods` 下的 `*.py` 自动扫描，
所以这里暂时不要新增非方法用途的 `.py` 文件，也不要直接把方法文件搬进子目录。
要做公共能力，优先放到 `backend/analysis/common.py`、`backend/r_scripts/` 或后续单独的 helper 包里。

## 新增方法规则

- 每个方法文件必须声明 `METHOD_KEY`、`METHOD_META`、`run`。
- `METHOD_KEY` 一旦上线不要随便改，历史结果和前端配置都靠它识别。
- `METHOD_META["category"]` 必须使用已有分类；要新增分类，先改 `backend/analysis/categories.py`。
- 同类方法按 `METHOD_META["order"]` 排序，留 5 或 10 的间隔，后面插队才不难受。
- 不要为了归类移动旧文件。真要迁移目录，先改注册器支持递归扫描，并做兼容验证。
- 截图里列出的差异检验、回归/因果、数据检验、综合评价、高级问卷方法，后续对齐 SPSSAU/SPSSPRO 时统一按 [分析方法 R 对齐清单](../../../docs/ANALYSIS_R_ALIGNMENT.md) 走 R；Python 只做参数、桥接和结果透传。

## 常用方法

| 文件 | METHOD_KEY | 方法 |
| --- | --- | --- |
| `frequency.py` | `frequency` | 频数分析 |
| `cross_tabulation.py` | `cross_tabulation` | 卡方（交叉）分析 |
| `descriptive.py` | `descriptive` | 描述性统计 |
| `category_summary.py` | `category_summary` | 分类汇总 |
| `normality_test.py` | `normality_test` | 正态性分析 |
| `data_overview.py` | `data_overview` | 数据探查 |

## 问卷分析包

| 文件 | METHOD_KEY | 方法 |
| --- | --- | --- |
| `reliability.py` | `reliability` | 信度分析 |
| `factor_analysis.py` | `factor_analysis` | 效度分析 |
| `pearson_correlation.py` | `pearson_correlation` | 相关性分析 |
| `multiple_choice.py` | `multiple_choice` | 多选分析 |
| `survey_cross_tab.py` | `survey_cross_tab` | 交叉表（调研专项） |
| `correspondence_analysis.py` | `correspondence_analysis` | 对应分析 |
| `confirmatory_factor_analysis.py` | `confirmatory_factor_analysis` | 验证性因子分析 |
| `kano.py` | `kano` | Kano模型 |
| `choice_multi_multi.py` | `choice_multi_multi` | 多选-多选（交叉分析） |
| `choice_multi_single.py` | `choice_multi_single` | 多选-单选（对比分析） |
| `choice_single_multi.py` | `choice_single_multi` | 单选-多选（对比分析） |

## 差异对比分析包

| 文件 | METHOD_KEY | 方法 |
| --- | --- | --- |
| `one_sample_t_test.py` | `one_sample_t_test` | 单样本T检验 |
| `summary_t_test.py` | `summary_t_test` | 摘要T检验 |
| `post_hoc_multiple_comparison.py` | `post_hoc_multiple_comparison` | 事后多重比较 |
| `two_way_anova.py` | `two_way_anova` | 双因素方差分析 |
| `three_way_anova.py` | `three_way_anova` | 三因素方差分析 |
| `n_way_anova.py` | `n_way_anova` | 多因素方差分析 |
| `summary_oneway_anova.py` | `summary_oneway_anova` | 摘要单因素方差分析 |
| `ancova.py` | `ancova` | 协方差分析 |
| `manova.py` | `manova` | 多变量方差分析 |
| `one_sample_equivalence_test.py` | `one_sample_equivalence_test` | 单样本等价性检验 |
| `two_sample_equivalence_test.py` | `two_sample_equivalence_test` | 双样本等价性检验 |
| `paired_equivalence_test.py` | `paired_equivalence_test` | 配对样本等价性检验 |
| `anova_oneway.py` | `anova_oneway` | 单因素方差分析 |
| `chi_square.py` | `chi_square` | 卡方检验 |
| `independent_t_test.py` | `independent_t_test` | 独立样本T检验 |
| `paired_t_test.py` | `paired_t_test` | 配对样本T检验 |

## 回归 & 因果分析包

| 文件 | METHOD_KEY | 方法 |
| --- | --- | --- |
| `multiple_regression.py` | `multiple_regression` | 多元线性回归 |
| `vif.py` | `vif` | 多重共线性 VIF |
| `mediation.py` | `mediation` | 中介效应分析 |
| `moderation.py` | `moderation` | 调节作用 |

## 高级回归 & 因果分析包

| 文件 | METHOD_KEY | 方法 |
| --- | --- | --- |
| `path_analysis.py` | `path_analysis` | 路径分析 |
| `sem.py` | `sem` | 结构方程模型(SEM) |
| `parallel_mediation.py` | `parallel_mediation` | 平行中介效应 |
| `serial_mediation.py` | `serial_mediation` | 链式中介效应 |

## 数据检验

| 文件 | METHOD_KEY | 方法 |
| --- | --- | --- |
| `one_sample_wilcoxon.py` | `one_sample_wilcoxon` | 单样本Wilcoxon符号秩检验 |
| `wilcoxon_signed_rank_test.py` | `wilcoxon_signed_rank_test` | 配对样本Wilcoxon符号秩检验 |
| `mann_whitney_u_test.py` | `mann_whitney_u_test` | 独立样本MannWhitney检验 |
| `kruskal_wallis_test.py` | `kruskal_wallis_test` | 多独立样本Kruskal-Wallis检验 |
| `friedman_test.py` | `friedman_test` | 多配对样本Friedman检验 |
| `goodness_of_fit_chi_square.py` | `goodness_of_fit_chi_square` | 卡方拟合优度检验 |
| `cochrans_q_test.py` | `cochrans_q_test` | Cochran's Q检验 |
| `kappa_consistency.py` | `kappa_consistency` | Kappa一致性检验 |
| `kendall_consistency.py` | `kendall_consistency` | Kendall一致性检验 |
| `intraclass_correlation.py` | `intraclass_correlation` | 组内相关系数 |
| `correlation_auto_solver.py` | `correlation_auto_solver` | 相关性分析自动求解器 |
| `spearman_correlation.py` | `spearman_correlation` | Spearman 等级相关 |
| `mds.py` | `mds` | 多维尺度分析 |

## 综合评价

| 文件 | METHOD_KEY | 方法 |
| --- | --- | --- |
| `ahp_professional.py` | `ahp_professional` | 层次分析法（AHP专业版） |
| `ahp_simplified.py` | `ahp_simplified` | 层次分析法（AHP简化版） |
| `exploratory_factor_analysis.py` | `exploratory_factor_analysis` | 因子分析（探索性） |
| `data_envelopment_analysis.py` | `data_envelopment_analysis` | 数据包络分析 |
| `fuzzy_comprehensive_evaluation.py` | `fuzzy_comprehensive_evaluation` | 模糊综合评价 |
| `topsis.py` | `topsis` | 优劣解距离法(TOPSIS) |
| `rsr.py` | `rsr` | 秩和比综合评价法(RSR) |
| `coupling_coordination.py` | `coupling_coordination` | 耦合协调度 |
| `coefficient_variation.py` | `coefficient_variation` | 变异系数法 |
| `entropy_method.py` | `entropy_method` | 熵值法 |
| `critic_weight.py` | `critic_weight` | CRITIC权重法 |
| `independent_weight_coefficient.py` | `independent_weight_coefficient` | 独立性权系数法 |
| `grey_relational_analysis.py` | `grey_relational_analysis` | 灰色关联分析 |
| `vikor.py` | `vikor` | 多准则妥协排序法（VIKOR） |
| `ism.py` | `ism` | 解释结构模型（ISM） |

## 高级问卷分析包

| 文件 | METHOD_KEY | 方法 |
| --- | --- | --- |
| `nps.py` | `nps` | NPS净推荐值分析 |
| `discrimination.py` | `discrimination` | 区分度分析 |
| `conjoint.py` | `conjoint` | 联合分析 |
| `entropy_weight.py` | `entropy_weight` | 权重分析(熵权法) |
| `maxdiff.py` | `maxdiff` | MaxDiff模型 |
| `price_breakpoint.py` | `price_breakpoint` | 价格断裂点模型 |
| `turf.py` | `turf` | TURF分析 |
| `penalty_analysis.py` | `penalty_analysis` | 惩罚分析 |
| `bpto.py` | `bpto` | 品牌价格抵补模型BPTO |
| `cbc_conjoint.py` | `cbc_conjoint` | 联合分析CBC |
| `maxdiff_pro.py` | `maxdiff_pro` | MaxDiff Pro |

## 后续真拆目录时再做

如果方法数量继续变多，再做这三步，不要只移动文件：

1. 改 `backend/analysis/registry.py` 支持递归扫描子包。
2. 保持 `METHOD_KEY` 不变，确认历史结果、任务队列和前端调用不受影响。
3. 迁移前先补 smoke test：至少能加载全部 `METHOD_META`，并执行 2 到 3 个代表性方法。
