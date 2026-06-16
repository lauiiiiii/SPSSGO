# 分析方法 R 对齐清单

这份文档只管统计口径对齐，不管前端展示。截图里这些方法后续对齐 SPSSAU/SPSSPRO 时，统计计算默认优先放到 `backend/r_scripts/`，Python 方法文件只做参数整理、临时数据写入、调用 R、解析 JSON；明确标注为 Python 显式公式复现的方法除外。

## 硬规则

- 对齐适配时不要在 Python 里临时拼统计公式、手算检验量或复刻 R 包结果；明确标注为 Python 显式公式复现的方法必须把公式 helper 和测试一起补齐。
- Python 层只保留 `METHOD_META`、参数校验、列名解析、R bridge、错误兜底和结果透传。
- R 脚本负责模型公式、检验、事后比较、拟合指标、效应量和核心表格口径。
- 一个方法一个 R 脚本，脚本名默认和 `METHOD_KEY` 一致，例如 `n_way_anova.R`。
- R 输出统一 JSON 到 stdout；不要输出调试文本，不然后端 JSON 解析会炸。
- R 依赖写进 `backend/r_scripts/README.md`，新增包时同步更新安装说明。

## 差异对比分析包

这些方法后续做 SPSSPRO/SPSSAU 口径对齐时走 R。当前已是 Python 计算的，不要继续在 Python 里补复杂统计细节，下一次改口径直接迁到 R。

| METHOD_KEY | 方法 | R 脚本 | 对齐要求 |
| --- | --- | --- | --- |
| `summary_oneway_anova` | 摘要单因素方差分析 | `summary_oneway_anova.R` | 用 R 产出 ANOVA 主表和摘要解读 |
| `ancova` | 协方差分析 | `ancova.R` | 用 R 的 `lm/aov/anova` 口径，协变量、组别效应都在 R 里算 |
| `manova` | 多变量方差分析 | `manova.R` | 用 R 的 `manova`/`summary.manova`，不要 Python 复刻多元检验 |
| `one_sample_equivalence_test` | 单样本等价性检验 | `one_sample_equivalence_test.R` | TOST 口径在 R 里统一 |
| `two_sample_equivalence_test` | 双样本等价性检验 | `two_sample_equivalence_test.R` | 两独立样本 TOST 口径在 R 里统一 |
| `paired_equivalence_test` | 配对样本等价性检验 | `paired_equivalence_test.R` | 配对 TOST 口径在 R 里统一 |
| `n_way_anova` | 多因素方差分析 | `n_way_anova.R` | 已迁到 R；无交互主效应模型由 R 负责 |
| `anova_oneway` | 单因素方差分析 | `anova_oneway.R` | ANOVA、事后比较、效应量都放 R |
| `independent_t_test` | 独立样本T检验 | `independent_t_test.R` | t 检验、方差齐性、效应量在 R 里算 |
| `chi_square` | 卡方检验 | `chi_square.R` | 卡方、期望频数、效应量在 R 里算 |
| `paired_t_test` | 配对样本T检验 | `paired_t_test.R` | 配对差异、置信区间、效应量在 R 里算 |

## 回归与因果分析包

| METHOD_KEY | 方法 | R 脚本 | 对齐要求 |
| --- | --- | --- | --- |
| `moderation` | 调节作用 | `moderation.R` | 已有 R 脚本；交互项、简单斜率、Johnson-Neyman 继续放 R |
| `multiple_regression` | 多元线性回归 | `multiple_regression.R` | 回归系数、模型摘要、诊断指标用 R 对齐 |
| `vif` | 多重共线性 VIF | `vif.R` | VIF/Tolerance 口径用 R 对齐 |
| `mediation` | 中介效应分析 | `mediation.R` | 已有 R 脚本；Bootstrap 和路径估计继续放 R |

## 数据检验

| METHOD_KEY | 方法 | R 脚本 | 对齐要求 |
| --- | --- | --- | --- |
| `one_sample_wilcoxon` | 单样本Wilcoxon符号秩检验 | `one_sample_wilcoxon.R` | 非参数检验统计量、秩、P 值用 R |
| `wilcoxon_signed_rank_test` | 配对样本Wilcoxon符号秩检验 | `wilcoxon_signed_rank_test.R` | 配对秩检验口径用 R |
| `mann_whitney_u_test` | 独立样本MannWhitney检验 | `mann_whitney_u_test.R` | U/W 统计量、秩均值、P 值用 R |
| `kruskal_wallis_test` | 多独立样本Kruskal-Wallis检验 | `kruskal_wallis_test.R` | H 检验、秩均值和事后比较用 R |
| `friedman_test` | 多配对样本Friedman检验 | `friedman_test.R` | Friedman 统计量和多重比较用 R |
| `goodness_of_fit_chi_square` | 卡方拟合优度检验 | `goodness_of_fit_chi_square.R` | 拟合优度卡方和期望分布用 R |
| `cochrans_q_test` | Cochran's Q检验 | `cochrans_q_test.R` | Q 检验和配对二分类口径用 R |
| `kappa_consistency` | Kappa一致性检验 | statsmodels.cohens_kappa / fleiss_kappa | 简单 Kappa、线性加权 Kappa、平方加权 Kappa 主表 SE/SE0/Z/P/CI 走 Fleiss-Cohen-Everitt 1969 大样本渐近方差（statsmodels.cohens_kappa 内部实现）：标准误(假定原假设) 用于检验、标准误 用于 95% CI，两者对应两个不同方差公式；Fleiss Kappa 主表 SE/Z/P/CI 走 Fleiss-Levin-Paik 2003 (3rd ed.) p.609 H0=0 下大样本渐近方差，主表两个 SE 列同值；po、pe、Kappa 按 Cohen 1960 / Fleiss 1971 原始公式显式手算（确定性公式，唯一解）；简单 Kappa 详细结论附 Cohen 1960 经典手算近似 SE=sqrt(po(1-po)/(N(1-pe))) 作为量级参考；权重列支持字符串型 ID 列的数字部分抽取兜底（例如"学生1..学生50"抽成 1..50 当频数权重）；新增评价者交叉表 section，方便和外部参考软件的列联表逐格对照 |
| `kendall_consistency` | Kendall一致性检验 | `kendall_consistency.R` | Kendall W 和显著性检验用 R |
| `intraclass_correlation` | ICC组内相关系数 | `intraclass_correlation.R` | 已有 R 脚本；ICC 多口径继续放 R |
| `correlation_auto_solver` | 相关与一致性推荐 | `correlation_auto_solver.R` | 自动分派规则可在 Python，具体检验用 R |
| `mds` | 多维尺度分析MDS | Python 显式公式复现 | 按距离矩阵双中心化和特征分解求二维坐标；原始数据可按列/按行构造欧氏距离矩阵，距离矩阵模式支持下三角矩阵补全 |
| `spearman_correlation` | Spearman 等级相关 | 复用 `pearson_correlation` 的 Spearman 口径 | 单独入口固定使用 `Spearman相关系数`，表格、P 值、热力图、样本量和常量变量处理跟相关性分析保持一致 |

## 综合评价

综合评价里有些算法可以纯矩阵计算，但只要目标是对齐 SPSSAU/SPSSPRO 输出，就按 R 脚本落地，别在 Python 里各写一套口径。

| METHOD_KEY | 方法 | R 脚本 |
| --- | --- | --- |
| `ahp_professional` | 层次分析法（AHP专业版） | `ahp_professional.R` |
| `ahp_simplified` | 层次分析法（AHP快速版） | `ahp_simplified.R` |
| `exploratory_factor_analysis` | 因子分析（探索性） | `exploratory_factor_analysis.R` |
| `data_envelopment_analysis` | 数据包络分析 | `data_envelopment_analysis.R` |
| `fuzzy_comprehensive_evaluation` | 模糊综合评价 | `fuzzy_comprehensive_evaluation.R` |
| `topsis` | 优劣解距离法(TOPSIS) | `topsis.R` |
| `rsr` | 秩和比综合评价法(RSR) | `rsr.R` |
| `coupling_coordination` | 耦合协调度 | `coupling_coordination.R` |
| `coefficient_variation` | 变异系数法 | `coefficient_variation.R` |
| `entropy_method` | 熵值法 | `entropy_method.R` |
| `critic_weight` | CRITIC权重法 | `critic_weight.R` |
| `independent_weight_coefficient` | 独立性权系数法 | `independent_weight_coefficient.R` |
| `grey_relational_analysis` | 灰色关联分析 | `grey_relational_analysis.R` |
| `vikor` | 多准则妥协排序法（VIKOR） | `vikor.R` |
| `ism` | 解释结构模型（ISM） | `ism.R` |

## 高级问卷分析包

| METHOD_KEY | 方法 | R 脚本 | 对齐要求 |
| --- | --- | --- | --- |
| `nps` | NPS净推荐值分析 | `nps.R` | 描述统计可简单，但分组/区间/显著性扩展走 R |
| `discrimination` | 区分度分析 | `discrimination.R` | 已有 R 脚本；高低分组检验继续放 R |
| `conjoint` | 联合分析 | `conjoint.R` | 效用估计、重要性和模型输出用 R |
| `entropy_weight` | 权重分析(熵权法) | `entropy_weight.R` | 对齐时和综合评价熵权法保持同一 R 口径 |
| `maxdiff` | MaxDiff模型 | `maxdiff.R` | 偏好强度、份额和排序用 R |
| `price_breakpoint` | 价格断裂点模型 | `price_breakpoint.R` | 交点、曲线和价格区间用 R |
| `turf` | TURF分析 | `turf.R` | 组合覆盖搜索和输出口径用 R |
| `penalty_analysis` | 惩罚分析 | `penalty_analysis.R` | 惩罚值、提升空间和分组口径用 R |
| `bpto` | 品牌价格抵补模型BPTO | `bpto.R` | 价格抵补和份额模拟用 R |
| `cbc_conjoint` | 联合分析CBC | `cbc_conjoint.R` | CBC 效用估计和模拟用 R |
| `maxdiff_pro` | MaxDiff Pro | `maxdiff_pro.R` | 个体层效用和高级模拟用 R |

## 高级回归与因果分析包

| METHOD_KEY | 方法 | R 脚本 | 对齐要求 |
| --- | --- | --- | --- |
| `path_analysis` | 路径分析 | `path_analysis.R` | 已有 R 脚本；路径估计和拟合指标继续放 R |
| `sem` | 结构方程模型(SEM) | `sem.R` | 已有 R 脚本；lavaan 是唯一统计口径 |
| `parallel_mediation` | 平行中介效应 | `parallel_mediation.R` | 已有 R 脚本；Bootstrap 和间接效应继续放 R |
| `serial_mediation` | 链式中介效应 | `serial_mediation.R` | 已有 R 脚本；链式间接效应继续放 R |
