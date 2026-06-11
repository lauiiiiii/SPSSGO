# R Scripts

此目录用于存放由 Python 后端调用的 `Rscript` 脚本。

当前约定：

- 入口调用由 [r_runner.py](/c:/Users/Administrator.DESKTOP-854VSP0/Desktop/API自助模式/spssgo/backend/r_runner.py) 统一负责
- 脚本文件放在本目录
- 推荐输出 JSON 到标准输出，便于 Python 侧统一解析
- 如需接收参数，优先通过 `--input <json_path>` 读取输入文件
- 对齐 SPSSAU/SPSSPRO 的统计计算优先写在 R 脚本里；Python 方法文件不要手写模型公式或复刻检验量
- 需要迁到 R 的方法清单见 [分析方法 R 对齐清单](../../docs/ANALYSIS_R_ALIGNMENT.md)

建议后续按方法拆分脚本，例如：

- `efa.R`
- `reliability.R`
- `cfa.R`

当前已落地：

- `health_check.R`：用于验证 `Rscript` 调用链路是否可用
- `reliability.R`：信度分析（Cronbach's alpha）R 版本
- `exploratory_factor_analysis.R`：探索性因子分析（KMO、Bartlett、特征值、旋转载荷）
- `confirmatory_factor_analysis.R`：验证性因子分析（CFA，基于 lavaan）
- `sem.R`：结构方程模型（SEM，基于 lavaan）
- `path_analysis.R`：路径分析（基于 lavaan）
- `mediation.R`：中介效应分析（基于 lavaan + Bootstrap）
- `parallel_mediation.R`：平行中介效应（基于 lavaan + Bootstrap）
- `serial_mediation.R`：链式中介效应（基于 lavaan + Bootstrap）
- `moderation.R`：调节效应分析（分层回归、简单斜率、Johnson-Neyman 区间）
- `intraclass_correlation.R`：组内相关系数（ICC 多口径）
- `kendall_consistency.R`：Kendall一致性检验（Kendall's W，行内平均秩和并列秩修正）
- `discrimination.R`：区分度/项目分析
- `n_way_anova.R`：多因素方差分析（无交互主效应模型、截距、事后比较）

运行 `reliability.R` 需要：

- 已安装 R
- `Rscript` 可执行
- 已安装 `jsonlite` 包

运行 `exploratory_factor_analysis.R` 需要：

- 已安装 R
- `Rscript` 可执行
- 已安装 `jsonlite` 包
- 不依赖额外统计扩展包，当前版本优先使用 R 自带 `factanal`

运行 `confirmatory_factor_analysis.R` 需要：

- 已安装 R
- `Rscript` 可执行
- 已安装 `jsonlite` 包
- 已安装 `lavaan` 包

运行 `sem.R` 需要：

- 已安装 R
- `Rscript` 可执行
- 已安装 `jsonlite` 包
- 已安装 `lavaan` 包

运行路径分析、中介效应、平行中介、链式中介需要：

- 已安装 R
- `Rscript` 可执行
- 已安装 `jsonlite` 包
- 已安装 `lavaan` 包

运行调节效应、组内相关系数、Kendall一致性检验、区分度分析需要：

- 已安装 R
- `Rscript` 可执行
- 已安装 `jsonlite` 包

运行多因素方差分析需要：

- 已安装 R
- `Rscript` 可执行
- 已安装 `jsonlite` 包

示例：

```r
install.packages(c("jsonlite", "lavaan"), repos = "https://cloud.r-project.org")
```
