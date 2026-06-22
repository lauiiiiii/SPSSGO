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

综合评价里有些算法可以纯矩阵计算，但只要目标是对齐 SPSSAU/SPSSPRO 输出，就按 R 脚本落地，别在 Python 里各写一套口径。DEA 现阶段先按 scipy `linprog` 显式线性规划复现，已补测试；后续如果迁 R，必须保持下面这套输出颗粒度不降级。

| METHOD_KEY | 方法 | R 脚本 |
| --- | --- | --- |
| `ahp_professional` | 层次分析法（AHP专业版） | `ahp_professional.R` |
| `ahp_simplified` | 层次分析法（AHP快速版） | `ahp_simplified.R` |
| `exploratory_factor_analysis` | 因子分析（探索性） | `exploratory_factor_analysis.R` |
| `data_envelopment_analysis` | 数据包络分析 | Python 显式线性规划复现；后续迁 `data_envelopment_analysis.R` |
| `fuzzy_comprehensive_evaluation` | 模糊综合评价 | Python 显式复现；后续迁 `fuzzy_comprehensive_evaluation.R` |
| `topsis` | 优劣解距离法(TOPSIS) | Python 显式复现；后续迁 `topsis.R` |
| `rsr` | 秩和比综合评价法(RSR) | `rsr.R` |
| `coupling_coordination` | 耦合协调度 | `coupling_coordination.R` |
| `coefficient_variation` | 变异系数法（信息量权重） | Python 显式公式复现；后续迁 `coefficient_variation.R` |
| `entropy_method` | 熵值法 | Python 显式公式复现；后续迁 `entropy_method.R` |
| `critic_weight` | CRITIC权重法 | `critic_weight.R` |
| `independent_weight_coefficient` | 独立性权系数法 | Python 显式复现（已对齐 SPSSPRO 口径：复相关系数R → 1/R → 归一化权重） |
| `grey_relational_analysis` | 灰色关联分析 | Python 显式公式复现；后续迁 `grey_relational_analysis.R` |
| `vikor` | 多准则妥协排序法（VIKOR） | `vikor.R` |
| `ism` | 解释结构模型（ISM） | `ism.R` |

### DEA 对齐颗粒度

截图对比结论：SPSSAU 的 DEA 入口比 SPSSPRO 多了“非负平移”和“保存效益”，SPSSPRO 的结果页层级更清楚；SPSSGO 取两者并集，但核心表格字段按 SPSSPRO 的 BCC 结果颗粒度落地。

| 对齐点 | SPSSAU | SPSSPRO | SPSSGO 当前口径 |
| --- | --- | --- | --- |
| 变量角色 | 投入(X)、产出(Y)、标签可选 | 投入指标、产出指标、索引项可选 | `input_vars`、`output_vars`、`index_var` |
| 模型类型 | `BCC（默认）` / `CCR` | `BCC` / `CCR` | `dea_type=BCC/CCR`，默认 BCC |
| 非正数处理 | 支持“非负平移”，提示平移单位为最小值绝对值+0.01 | 截图未见该选项 | 支持 `non_negative_translation`，默认开启 |
| 保存结果 | 支持“保存效益”到新标题 | 截图未见该选项 | 支持 `save_efficiency`，生成新数据版本保存综合效益 |
| 主结果表 | 输出效益/效率表、松弛变量、有效性 | `技术效益`、`规模效益`、`综合效益`、`S-`、`S+`、`有效性` | BCC 完整输出这些字段；CCR 输出综合效益和松弛变量 |
| 图表 | 效率趋势/效益图 | 效益有效性折线图 | 统一走 `metric_comparison`，BCC 三序列 |
| 补充结果 | 规模报酬、松弛变量分析、说明块 | 规模报酬分析、图表说明、分析步骤 | 输出规模报酬表、逐指标松弛变量表、配置和样本处理 |

DEA 有效性判断固定为：综合效益接近 1 且 `S-`、`S+` 均为 0 时为 `DEA强有效`；综合效益接近 1 但存在松弛为 `DEA弱有效`；综合效益小于 1 为 `非DEA有效`。这里别改成只看 BCC 技术效益，不然后面规模无效但技术有效的样本会被误判。

### 模糊综合评价对齐颗粒度

截图对比结论：SPSSAU 对模糊算子的解释更细，SPSSPRO 的入口补了索引项和变量权重选择；SPSSGO 取两者并集，保留样本为行、评价项为列的现有数据方向。

| 对齐点 | SPSSAU | SPSSPRO | SPSSGO 当前口径 |
| --- | --- | --- | --- |
| 变量角色 | 评价项、评价指标权重可选 | 评价变量、索引项可选 | `variables`、`index_var`；`weight_var` 仅在自定义权重时显示 |
| 变量权重 | 可输出权重计算结果 | 支持熵权法、不设置权重、自定义权重 | `weight_method=entropy/equal/custom`，默认熵权法；自定义权重时才显示权重槽 |
| 模糊算子 | 提供四类算子并有推荐说明 | 提供四类算子下拉 | `fuzzy_operator` 四类全支持，默认加权平均型 |
| 主结果 | 权重计算、分析建议、智能分析、综合得分 | 权重计算、分析步骤、详细结论 | 输出算法配置、样本处理、算子说明、权重表、隶属度矩阵、综合得分表、排序图 |
| 图表 | 结果以表格为主 | 结果页结构化 | 综合得分排序走 `metric_comparison` |

模糊算子固定含义：`main_factor_decision`=主因素决定型 `M(∧,V)`，更多考虑指标权重，不推荐；`main_factor_prominent`=主因素突出型 `M(*,V)`，在主因素决定型基础上修正输入数据上界，不推荐；`bounded_sum_min`=取小与有界型 `M(∧,+)`，更多使用输入数据信息，推荐；`weighted_average`=加权平均型 `M(*,+)`，综合利用指标权重和输入数据信息，推荐。默认值必须保持 `weighted_average`，别回退到主因素类算子。

### TOPSIS 对齐颗粒度

截图对比结论：SPSSAU 把 `TOPSIS` 和 `熵权TOPSIS` 拆成两个入口，SPSSPRO 把它们合并为 `优劣解距离法(TOPSIS)`，通过“变量权重”选择熵权法、不设置权重或自定义权重。SPSSGO 采用 SPSSPRO 的单入口结构，同时把 SPSSAU 的两个名称保留为搜索别名。

| 对齐点 | SPSSAU | SPSSPRO | SPSSGO 当前口径 |
| --- | --- | --- | --- |
| 方法入口 | `TOPSIS`、`熵权TOPSIS` 两个入口 | `优劣解距离法(TOPSIS)` 一个入口 | `topsis` 一个入口，别名含 `TOPSIS`、`熵权TOPSIS` |
| 变量角色 | TOPSIS 为评价指标；熵权TOPSIS 额外支持标签和指标权重 | 正向指标、负向指标、索引项 | `positive_vars`、`negative_vars`、`index_var` |
| 变量权重 | 普通 TOPSIS 不自动赋权；熵权TOPSIS 自动熵权 | 熵权法、不设置权重、自定义权重 | `weight_method=entropy/equal/custom`，默认熵权法 |
| 自定义权重 | 熵权TOPSIS 可勾选指标权重 | 支持自定义权重 | `weight_var` 仅在自定义权重时显示，也支持 API 传 `custom_weights/weights` |
| 保存过程 | 支持保存过程值 | 截图未见保存过程项 | `save_process` 保存 D+、D-、相对接近度 C、排序结果 |
| 主结果 | 权重表、TOPSIS 计算表、理想解、描述统计、分析建议 | 权重计算、TOPSIS 计算结果、结构化分析步骤 | 输出算法配置、样本处理、权重表、TOPSIS 结果、正负理想解、描述统计、排序图 |

默认权重方式固定为 `entropy`，因为它能覆盖 SPSSAU 的熵权TOPSIS；普通 TOPSIS 用 `equal` 表示“不设置权重”。这里不要再拆第二个后端方法，否则搜索、历史任务和保存过程值会出现两套口径。

### 熵值法对齐颗粒度

截图对比结论：SPSSPRO 的熵值法入口明确区分正向指标和负向指标，并默认给权重、图表、综合得分和排名；SPSSAU 额外提供“保存综合得分”和“非负平移”。SPSSGO 取两者并集，旧参数 `variables` 继续按正向指标兼容。

| 对齐点 | SPSSAU | SPSSPRO | SPSSGO 当前口径 |
| --- | --- | --- | --- |
| 变量角色 | 分析项，界面不强制拆正负向 | 正向指标、负向指标 | `positive_vars`、`negative_vars`；老 `variables` 按正向指标兼容 |
| 非正数处理 | 支持“非负平移”，平移单位为最小值绝对值+0.01 | 截图未见独立选项 | 支持 `non_negative_translation`，默认关闭，开启后只作用于熵权计算矩阵 |
| 保存结果 | 支持“保存综合得分” | 输出综合得分表和排名 | `save_composite_score` 生成新数据版本保存 `CompScore_熵值法` |
| 主结果 | 权重结果，可保存综合得分 | 权重表、权重图、综合得分表、排名、分析步骤 | 输出算法配置、样本处理、权重表、权重图、综合得分表和概况 |

熵值法的标准化方向固定为：正向指标 `(x-min)/(max-min)`，负向指标 `(max-x)/(max-min)`；常量列给 1 兜底。非负平移不要改成覆盖原始数据，它只处理进入熵权公式的计算矩阵。

### CRITIC 权重法对齐颗粒度

截图对比结论：SPSSPRO 和 SPSSAU 的 CRITIC 权重法是同一类客观赋权方法，核心都是“指标变异性 × 指标冲突性 = 信息量，再归一化为权重”；差异在结果页颗粒度，SPSSPRO 更强调分析步骤和详细结论，SPSSAU 额外展示描述统计并提供“保存综合得分”。SPSSGO 取两者并集，但默认不输出综合得分排序表。

| 对齐点 | SPSSAU | SPSSPRO | SPSSGO 当前口径 |
| --- | --- | --- | --- |
| 变量角色 | 分析项/定量指标 | 定量变量 | `variables`，至少 2 个数值型指标 |
| 保存结果 | 支持“保存综合得分” | 截图未见该选项 | `save_composite_score`，默认关闭，开启后保存 `CompScore_CRITIC权重法` |
| 指标变异性 | 输出标准差，并在描述统计中重复展示 | 权重表字段为指标变异性 | 使用原始有效样本的样本标准差，不做 min-max 标准化后再算标准差 |
| 指标冲突性 | 由相关系数得到 | 由相关系数得到 | `Σ(1-rjk)`，对角线固定为 1，常量列相关缺失时按 0 兜底 |
| 主结果 | 权重表、分析建议、权重图、描述统计、参考文献 | 权重表、权重图、分析步骤、详细结论、参考文献 | 输出算法配置、样本处理、分析步骤、权重表、重要度图、描述统计、详细结论、建议、智能分析和参考文献 |
| 图表 | 权重柱形图/条形图/饼状图 | 指标重要度直方图 | 统一走 `metric_comparison`，默认柱形图，按权重降序展示 |

CRITIC 的权重表字段固定为：`项`、`指标变异性`、`指标冲突性`、`信息量`、`权重(%)`。这里别回退成旧版 `标准差/冲突性/信息量/权重`，也别默认输出综合得分 Top10；截图里的主报告重点是指标权重，不是评价对象排序。

### RSR/WRSR 对齐颗粒度

截图对比结论：SPSSAU 入口叫 `WRSR秩和比`，SPSSPRO 入口叫 `秩和比综合评价法(RSR)`。两者不是两个独立方法，WRSR 是带权重的 RSR。SPSSGO 采用一个 `rsr` 入口，用变量权重区分普通 RSR 和加权 WRSR。

| 对齐点 | SPSSAU | SPSSPRO | SPSSGO 当前口径 |
| --- | --- | --- | --- |
| 方法入口 | `WRSR秩和比` | `秩和比综合评价法(RSR)` | `rsr` 一个入口，别名含 `RSR`、`WRSR`、`WRSR秩和比` |
| 变量角色 | 高优指标、低优指标、标签可选 | 正向指标、负向指标、索引项 | `positive_vars`、`negative_vars`、`index_var` |
| 编秩方法 | 整次法、非整次法 | 非整秩方法等选项 | `rank_method=integer/fractional`，默认整次法；整次法使用 1 到 N 的样本排序秩次，非整次法按极差线性换算为非整秩 |
| 分档数量 | 3-5 档 | 3-7 档 | `division_count=3..7`，默认 3 档 |
| 变量权重 | 默认不设置，可勾选指标权重 | 熵权法、不设置权重、自定义权重 | `weight_method=equal/entropy/custom`，默认不设置权重 |
| 主结果 | RSR/WRSR 排序、分档、结果说明 | 权重计算、统计计算、分布表、线性回归、综合图 | 输出算法配置、样本处理、权重表、统计计算、排序、分布表、Probit 回归、分档规则和综合图 |

默认权重方式固定为 `equal`，因为教学和论文里普通 RSR 更常见；熵权法和自定义权重会自动切换为 WRSR 输出。老参数 `variables` 仍按正向指标兼容，别删除，否则历史任务会断。

### 灰色关联分析对齐颗粒度

截图对比结论：SPSSPRO 的灰色关联分析入口按“特征序列、母序列、索引项”拆槽，并显式暴露无量纲处理方式和分辨系数ρ；结果页强调算法配置、分析结果、分析步骤、灰色关联系数和关联度排序。SPSSGO 采用 SPSSPRO 入口，旧 `reference_var` / `compare_vars` 继续兼容。

| 对齐点 | SPSSAU | SPSSPRO | SPSSGO 当前口径 |
| --- | --- | --- | --- |
| 变量角色 | 参考序列、比较序列 | 特征序列、母序列、索引项可选 | `feature_vars`、`mother_var`、`index_var`；兼容 `compare_vars`、`reference_var` |
| 无量纲处理 | 常见初值化、均值化 | 初值化、均值化、不处理 | `dimensionless_method=initial/mean/none`，默认均值化 |
| 分辨系数 | 通常取 ρ=0.5 | 输入分辨系数ρ，提示 ρ∈(0,1) | `rho`，默认 0.5，校验 0<ρ<1 |
| 主结果 | 灰色关联度和排序 | 灰色关联系数、灰色关联度、分析步骤、详细结论 | 输出算法配置、样本处理、分析结果、分析步骤、关联系数表、关联度表和排序图 |
| 图表 | 通常以表格为主 | 截图未见核心图表 | 关联度排序走 `metric_comparison`，默认柱形图 |

灰色关联分析固定按“行=观测点、列=序列”理解数据方向；关联系数表输出每个观测点的局部接近程度，关联度表输出各特征序列关联系数均值和排名。无量纲方式不要偷换成 min-max 标准化，否则会和截图里的初值化/均值化口径不一致。

## 高级问卷分析包

| METHOD_KEY | 方法 | R 脚本 | 对齐要求 |
| --- | --- | --- | --- |
| `nps` | NPS净推荐值分析 | `nps.R` | 描述统计可简单，但分组/区间/显著性扩展走 R |
| `discrimination` | 区分度分析 | `discrimination.R` | 已有 R 脚本；高低分组检验继续放 R |
| `conjoint` | 联合分析 | `conjoint.py` | Python 实现（statsmodels OLS），已于 2026-06 对齐 SPSSAU 颗粒度 |
| `entropy_weight` | 权重分析 | Python 分派；AHP 复用 `ahp_simplified.R`，熵值法/优序图法显式复现 | 入口按 SPSSAU 下拉合并 `AHP权重`、`熵值法`、`优序图法`；老任务未传 `analysis_method` 时继续走原熵权法 |
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
