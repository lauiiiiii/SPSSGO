# 统计分析方法参数文档

本文档由 `scripts/generate_analysis_method_docs.py` 根据后端 `METHOD_META` 自动生成。

接口入口：

```http
POST /api/execute-method/{session_id}
Content-Type: application/json
Authorization: Bearer <access_token>
```

统一请求体：

```json
{
  "method": "frequency",
  "params": {}
}
```

说明：

- `method` 使用下方每个标题里的方法 key。
- `params` 是后端真正执行时读取的参数结构。
- “前端槽位示例”对应 `/api/methods` 返回的变量槽位；部分方法会通过参数构建器转换成最终 `params`。
- 变量名必须来自 `GET /api/variables/{session_id}` 返回的变量列表。
- 差异检验、回归/因果、数据检验、综合评价和高级问卷方法做 SPSSAU/SPSSPRO 对齐时，按 [分析方法 R 对齐清单](./ANALYSIS_R_ALIGNMENT.md) 优先走 R 脚本；Python 只做参数整理、R bridge 和结果透传。

当前共整理 81 个统计分析方法。

## 常用方法

### `frequency` - 频数分析

- 分类：常用方法
- 说明：统计各类别的频次和百分比分布
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 分析变量 | 多选，任意变量，至少 1 个 | 放入需要统计频次的变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "variables": [
    "变量1"
  ],
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "变量1"
  ],
  "include_missing_analysis": false
}
```

### `cross_tabulation` - 卡方（交叉）分析

- 分类：常用方法
- 说明：用于探索多组变量之间交叉列联分布和关联强度
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| group_var | 变量 | 单选，任意变量 | 放入 1 个分组变量 |
| variables | 变量X | 多选，任意变量，至少 1 个 | 放入 1 个或多个需要交叉分析的 X 变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| percent_base | 占比口径 | "百分数(按列)" | 百分数(按列), 百分数(按行) |  |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "group_var": "变量1",
  "variables": [
    "变量1"
  ],
  "percent_base": "百分数(按列)",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "group_var": "变量1",
  "variables": [
    "变量1"
  ],
  "percent_base": "百分数(按列)",
  "include_missing_analysis": false
}
```

### `descriptive` - 描述性统计

- 分类：常用方法
- 说明：计算各变量的均值、标准差、最小值、最大值等描述性指标
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 分析变量 | 多选，定量变量，至少 1 个 | 放入需要描述的定量变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "variables": [
    "数值变量1"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1"
  ]
}
```

### `category_summary` - 分类汇总

- 分类：常用方法
- 说明：按分类变量分组汇总一个或多个定量变量的统计量
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| group_var | 变量 | 单选，定类变量 | 放入用于分组汇总的分类变量 |
| summary_vars | 变量 | 多选，定量变量，至少 1 个 | 放入需要按组汇总的定量变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| summary_type | 类型 | ["均值"] | n, 均值, 计数, 中位数, 标准差, 平均值±标准差, 求和, 最大值, 最小值, 25分位数, 75分位数, 90分位数, 95分位数, 99分位数, 标准误, 均值95% CI(LL), 均值95% CI(UL), 极差, 四分位间距, 方差, 峰度, 偏度 |  |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "group_var": "分类变量1",
  "summary_vars": [
    "数值变量1"
  ],
  "summary_type": [
    "均值"
  ],
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "group_var": "分类变量1",
  "summary_vars": [
    "数值变量1"
  ],
  "summary_type": [
    "均值"
  ],
  "include_missing_analysis": false
}
```

### `normality_test` - 正态性分析

- 分类：常用方法
- 说明：综合输出正态性检验表、直方图、P-P 图和 Q-Q 图
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 分析变量 | 多选，定量变量，至少 1 个 | 放入需要检验正态性的变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "variables": [
    "数值变量1"
  ],
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1"
  ],
  "include_missing_analysis": false
}
```

### `data_overview` - 数据探查

- 分类：常用方法
- 说明：全面检查数据集规模、变量类型、缺失与异常，评估数据可用度
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 变量 | 多选，任意变量，至少 1 个 | 放入需要探查的一个或多个变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "variables": [
    "变量1"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "变量1"
  ]
}
```

## 问卷分析包

### `reliability` - 信度分析

- 分类：问卷分析包
- 说明：信度分析用于分析问卷中各题目的可靠性，检验量表内部一致性
- 参数构建器：`reliability`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| dimension1_vars | 维度1 | 多选，定量变量 | 放入维度1对应的题项 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| type | 类型 | "Cronbach's α" | Cronbach's α, 折半系数, McDonald Omega, theta系数 |  |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "dimension1_vars": [
    "数值变量1"
  ],
  "type": "Cronbach's α",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "items_groups": {
    "维度1": [
      "数值变量1"
    ]
  },
  "type": "Cronbach's α"
}
```

### `factor_analysis` - 效度分析

- 分类：问卷分析包
- 说明：通过 KMO 和 Bartlett 球形检验判断数据是否适合做因子分析
- 参数构建器：`factor`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 分析变量 | 多选，定量变量，至少 3 个 | 放入同一量表的所有题项（至少3个） |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| factor_count | 维度个数设置 | "auto" |  |  |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2",
    "数值变量3"
  ],
  "factor_count": "auto",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "items": [
    "数值变量1",
    "数值变量2",
    "数值变量3"
  ],
  "scale_name": "量表",
  "factor_count": "auto"
}
```

### `pearson_correlation` - 相关性分析

- 分类：问卷分析包
- 说明：分析两个或多个定量变量之间的线性相关程度
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 分析变量 | 多选，定量变量，至少 2 个 | 放入需要分析相关性的变量（至少2个） |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| correlation_method | 相关系数 | "Pearson相关系数" | Pearson相关系数, Spearman相关系数, Kendall相关系数 |  |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ],
  "correlation_method": "Pearson相关系数",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ],
  "correlation_method": "Pearson相关系数",
  "include_missing_analysis": false
}
```

### `multiple_choice` - 多选分析

- 分类：问卷分析包
- 说明：对同一多选题拆分后的多个选项变量进行选择频次统计
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 多选题变量 | 多选，定类变量，至少 2 个 | 放入同一多选题的多个选项变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| count_value | 计数值 | "1" | 1, 2, 0 | 默认按照数字1作为选中项标记进行计算，可设置数字2或者数字0作为某项种类的标记。 |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "variables": [
    "分类变量1",
    "分类变量2"
  ],
  "count_value": "1",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "分类变量1",
    "分类变量2"
  ],
  "count_value": "1",
  "include_missing_analysis": false
}
```

### `choice_multi_multi` - 多选-多选（交叉分析）

- 分类：问卷分析包
- 说明：分析两组多选题选项之间的联合选择分布和差异情况
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables_a | 二分类0-1变量 | 多选，定类变量，至少 2 个 | 放入第一组多选题变量，变量数至少为2 |
| variables_b | 二分类0-1变量 | 多选，定类变量，至少 2 个 | 放入第二组多选题变量，变量数至少为2 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| count_value | 计数值 | "1" | 1, 2, 0 | 默认按照数字1作为选中项标记进行计算，可设置数字2或者数字0作为某项种类的标记。 |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "variables_a": [
    "分类变量1",
    "分类变量2"
  ],
  "variables_b": [
    "分类变量1",
    "分类变量2"
  ],
  "count_value": "1",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables_a": [
    "分类变量1",
    "分类变量2"
  ],
  "variables_b": [
    "分类变量1",
    "分类变量2"
  ],
  "count_value": "1",
  "include_missing_analysis": false
}
```

### `choice_multi_single` - 多选-单选（对比分析）

- 分类：问卷分析包
- 说明：分析多选题选项在不同单选分组中的分布与差异情况
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| multiple_vars | 二分类0-1变量 | 多选，定类变量，至少 2 个 | 放入同一题目的多选拆分变量 |
| single_var | 单选分组变量 | 单选，定类变量 | 放入用于分组的单选题变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| count_value | 计数值 | "1" | 1, 2, 0 | 默认按照数字1作为选中项标记进行计算，可设置数字2或者数字0作为某项种类的标记。 |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "multiple_vars": [
    "分类变量1",
    "分类变量2"
  ],
  "single_var": "分类变量1",
  "count_value": "1",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "multiple_vars": [
    "分类变量1",
    "分类变量2"
  ],
  "single_var": "分类变量1",
  "count_value": "1",
  "include_missing_analysis": false
}
```

### `choice_single_multi` - 单选-多选（对比分析）

- 分类：问卷分析包
- 说明：基于卡方检验分析单选题与多选题选项之间是否存在显著差异
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| single_var | 单选变量 | 单选，定类变量 | 放入单选题变量 |
| multiple_vars | 二分类0-1变量 | 多选，定类变量，至少 2 个 | 放入同一题目的多选拆分变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| count_value | 计数值 | "1" | 1, 2, 0 | 默认按照数字1作为选中项标记进行计算，可设置数字2或者数字0作为某项种类的标记。 |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "single_var": "分类变量1",
  "multiple_vars": [
    "分类变量1",
    "分类变量2"
  ],
  "count_value": "1",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "single_var": "分类变量1",
  "multiple_vars": [
    "分类变量1",
    "分类变量2"
  ],
  "count_value": "1",
  "include_missing_analysis": false
}
```

### `survey_cross_tab` - 交叉表（调研专项）

- 分类：问卷分析包
- 说明：输出交叉频数、行百分比和列百分比，适合调研问卷分析场景
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| var1 | 行变量 | 单选，定类变量 | 放入第一个调研变量 |
| var2 | 列变量 | 单选，定类变量 | 放入第二个调研变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "var1": "分类变量1",
  "var2": "分类变量1",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "var1": "分类变量1",
  "var2": "分类变量1",
  "include_missing_analysis": false
}
```

### `correspondence_analysis` - 对应分析

- 分类：问卷分析包
- 说明：用于可视化探索多组定类变量之间的关系
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 变量 | 多选，定类变量，至少 2 个 | 放入用于对应分析的定类变量，变量数至少为2 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "variables": [
    "分类变量1",
    "分类变量2"
  ],
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "分类变量1",
    "分类变量2"
  ],
  "include_missing_analysis": false
}
```

### `confirmatory_factor_analysis` - 验证性因子分析

- 分类：问卷分析包
- 说明：支持多因子测量模型的验证性因子分析，输出拟合指标、标准化残差和修正建议
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| factor1_vars | 因子1题项 | 多选，定量变量，至少 2 个 | 放入因子1对应的题项 |
| factor2_vars | 因子2题项 | 多选，定量变量 | 可选：放入因子2对应的题项 |
| factor3_vars | 因子3题项 | 多选，定量变量 | 可选：放入因子3对应的题项 |
| factor4_vars | 因子4题项 | 多选，定量变量 | 可选：放入因子4对应的题项 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| second_order_model | 二阶因子模型 | false |  |  |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "factor1_vars": [
    "数值变量1",
    "数值变量2"
  ],
  "factor2_vars": [
    "数值变量1"
  ],
  "factor3_vars": [
    "数值变量1"
  ],
  "factor4_vars": [
    "数值变量1"
  ],
  "second_order_model": false,
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "factor1_vars": [
    "数值变量1",
    "数值变量2"
  ],
  "factor2_vars": [
    "数值变量1"
  ],
  "factor3_vars": [
    "数值变量1"
  ],
  "factor4_vars": [
    "数值变量1"
  ],
  "second_order_model": false,
  "include_missing_analysis": false
}
```

### `kano` - Kano模型

- 分类：问卷分析包
- 说明：基于正向题与反向题的配对回答识别题项的Kano类别
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| functional_vars | 正向题 | 多选，定类变量，至少 1 个 | 按顺序放入正向题变量 |
| dysfunctional_vars | 反向题 | 多选，定类变量，至少 1 个 | 按顺序放入与正向题一一对应的反向题变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "functional_vars": [
    "分类变量1"
  ],
  "dysfunctional_vars": [
    "分类变量1"
  ],
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "functional_vars": [
    "分类变量1"
  ],
  "dysfunctional_vars": [
    "分类变量1"
  ],
  "include_missing_analysis": false
}
```

## 差异对比分析包

### `one_sample_t_test` - 单样本T检验

- 分类：差异对比分析包
- 说明：检验样本均值是否显著偏离给定检验值
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| test_vars | 检验变量 | 多选，定量变量，至少 1 个 | 放入需要进行检验的变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| test_value | 检验值 | "0" | 0, 1, 3, 5 |  |
| output_normality | 输出正态性检验图 | false |  |  |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "test_vars": [
    "数值变量1"
  ],
  "test_value": "0",
  "output_normality": false,
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "test_vars": [
    "数值变量1"
  ],
  "test_value": "0",
  "output_normality": false,
  "include_missing_analysis": false
}
```

### `summary_t_test` - 摘要T检验

- 分类：差异对比分析包
- 说明：适用于只有汇总数据时，检验均值或均值差是否符合指定假设
- 参数构建器：`direct`

变量槽位：

无变量槽位。

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| test_type | 检验类型 | "one_sample" | one_sample, independent |  |
| confidence_level | 置信水平 | "95" | 90, 95, 99 |  |
| alternative | 假设检验 | "等于" | 等于, 大于, 小于 |  |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "test_type": "one_sample",
  "confidence_level": "95",
  "alternative": "等于",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "test_type": "one_sample",
  "confidence_level": "95",
  "alternative": "等于",
  "include_missing_analysis": false
}
```

### `post_hoc_multiple_comparison` - 事后多重比较

- 分类：差异对比分析包
- 说明：在方差分析显著后，对组间差异进行事后多重比较
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| group_var | 分组变量 | 单选，定类变量 | 放入分组变量（3组及以上） |
| test_vars | 检验变量 | 多选，定量变量，至少 1 个 | 放入需要比较的定量变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| method | 比较方法 | "LSD方法(默认)" | LSD方法(默认), Scheffe, Tukey, Bonferroni校正, sidak, Tamhane T2(方差不齐), SNK Q检验, Duncan检验, Games-Howell(方差不齐) |  |
| use_letters | 字母标记法 | false |  |  |
| include_effect_size | 效应量 | false |  |  |
| show_p_marks | P值标识 | true |  |  |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "group_var": "分类变量1",
  "test_vars": [
    "数值变量1"
  ],
  "method": "LSD方法(默认)",
  "use_letters": false,
  "include_effect_size": false,
  "show_p_marks": true,
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "group_var": "分类变量1",
  "test_vars": [
    "数值变量1"
  ],
  "method": "LSD方法(默认)",
  "use_letters": false,
  "include_effect_size": false,
  "show_p_marks": true,
  "include_missing_analysis": false
}
```

### `two_way_anova` - 双因素方差分析

- 分类：差异对比分析包
- 说明：检验两个分类因素及其交互作用对因变量的影响
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| factors | 分组变量X | 多选，定类变量，至少 2 个 | 放入2个分组因素 |
| dependent | 因变量Y | 单选，定量变量 | 放入因变量 |
| covariates | 协变量 | 多选，定量变量 | 可选，放入需要控制的协变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_interaction | 分析交互效应 | true |  |  |
| do_post_hoc | 事后多重比较 | false |  |  |
| post_hoc_method | 方法选择 | "LSD" | LSD, bonf, sidak |  |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "factors": [
    "分类变量1",
    "分类变量2"
  ],
  "dependent": "数值变量1",
  "covariates": [
    "数值变量1"
  ],
  "include_interaction": true,
  "do_post_hoc": false,
  "post_hoc_method": "LSD",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "factors": [
    "分类变量1",
    "分类变量2"
  ],
  "dependent": "数值变量1",
  "covariates": [
    "数值变量1"
  ],
  "include_interaction": true,
  "do_post_hoc": false,
  "post_hoc_method": "LSD",
  "include_missing_analysis": false
}
```

### `three_way_anova` - 三因素方差分析

- 分类：差异对比分析包
- 说明：检验三个分类因素及其交互作用对因变量的影响
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| factors | 分组变量X | 多选，定类变量，至少 3 个 | 放入3个分组因素 |
| dependent | 因变量Y | 单选，定量变量 | 放入因变量 |
| covariates | 协变量 | 多选，定量变量 | 可选，放入需要控制的协变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_interaction | 分析交互效应 | true |  |  |
| second_order_interaction | 二阶交互效应 | true |  |  |
| third_order_interaction | 三阶交互效应 | false |  |  |
| include_effect_size | 效应量 | false |  |  |
| do_post_hoc | 事后多重比较 | false |  |  |
| post_hoc_method | 方法选择 | "LSD" | LSD, Tukey法, Bonferroni校正, Sidak法 |  |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "factors": [
    "分类变量1",
    "分类变量2",
    "分类变量3"
  ],
  "dependent": "数值变量1",
  "covariates": [
    "数值变量1"
  ],
  "include_interaction": true,
  "second_order_interaction": true,
  "third_order_interaction": false,
  "include_effect_size": false,
  "do_post_hoc": false,
  "post_hoc_method": "LSD",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "factors": [
    "分类变量1",
    "分类变量2",
    "分类变量3"
  ],
  "dependent": "数值变量1",
  "covariates": [
    "数值变量1"
  ],
  "include_interaction": true,
  "second_order_interaction": true,
  "third_order_interaction": false,
  "include_effect_size": false,
  "do_post_hoc": false,
  "post_hoc_method": "LSD",
  "include_missing_analysis": false
}
```

### `n_way_anova` - 多因素方差分析

- 分类：差异对比分析包
- 说明：检验多个分类因素对因变量的影响
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| dependent | Y | 单选，定量变量 | 放入因变量 |
| factors | X | 多选，定类变量，至少 2 个 | 放入2个及以上分组因素 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| do_post_hoc | 事后多重比较 | false |  |  |
| post_hoc_method | 方法选择 | "LSD" | LSD, Tukey法, Bonferroni校正, Sidak法 | 默认不进行事后多重比较，可选比如LSD等事后多重比较检验方法。 |
| include_effect_size | 效应量 | false |  | 选中后结果表格中会输出效应量。 |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "dependent": "数值变量1",
  "factors": [
    "分类变量1",
    "分类变量2"
  ],
  "do_post_hoc": false,
  "post_hoc_method": "LSD",
  "include_effect_size": false,
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "dependent": "数值变量1",
  "factors": [
    "分类变量1",
    "分类变量2"
  ],
  "do_post_hoc": false,
  "post_hoc_method": "LSD",
  "include_effect_size": false,
  "include_missing_analysis": false
}
```

### `summary_oneway_anova` - 摘要单因素方差分析

- 分类：差异对比分析包
- 说明：适用于只有汇总数据时，检验多组均值是否存在差异
- 参数构建器：`direct`

变量槽位：

无变量槽位。

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| confidence_level | 置信度级别 | "95" | 99, 95, 90 |  |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "confidence_level": "95",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "confidence_level": "95",
  "include_missing_analysis": false
}
```

### `ancova` - 协方差分析

- 分类：差异对比分析包
- 说明：在控制协变量影响后比较组间均值差异
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| dependent | 因变量 | 单选，定量变量 | 放入因变量 |
| group_var | 分组变量 | 多选，定类变量，至少 1 个 | 放入1个或多个分组变量 |
| covariates | 协变量 | 多选，定量变量，至少 1 个 | 放入协变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_interaction | 平行性检验 | false |  | 模型中建立分组变量与协变量之间的交互项，用于检查回归斜率齐性。 |
| include_effect_size | 效应量 | false |  | 选中后主体间效应表会输出偏η²。 |
| do_post_hoc | 事后多重比较 | false |  |  |
| post_hoc_method | 方法选择 | "LSD" | LSD, Bonferroni校正, Sidak法, Tukey法 | 默认不进行事后多重比较，可选 LSD 等方法。 |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "dependent": "数值变量1",
  "group_var": [
    "分类变量1"
  ],
  "covariates": [
    "数值变量1"
  ],
  "include_interaction": false,
  "include_effect_size": false,
  "do_post_hoc": false,
  "post_hoc_method": "LSD",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "dependent": "数值变量1",
  "group_var": [
    "分类变量1"
  ],
  "covariates": [
    "数值变量1"
  ],
  "include_interaction": false,
  "include_effect_size": false,
  "do_post_hoc": false,
  "post_hoc_method": "LSD",
  "include_missing_analysis": false
}
```

### `manova` - 多变量方差分析

- 分类：差异对比分析包
- 说明：同时检验多个因变量在组间的总体差异
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| dependent_vars | 因变量 | 多选，定量变量，至少 2 个 | 放入两个及以上因变量 |
| group_var | 分组变量 | 多选，定类变量，至少 1 个 | 放入1个或多个分组变量 |
| covariates | 协变量 | 多选，定量变量 | 可选，放入协变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "dependent_vars": [
    "数值变量1",
    "数值变量2"
  ],
  "group_var": [
    "分类变量1"
  ],
  "covariates": [
    "数值变量1"
  ],
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "dependent_vars": [
    "数值变量1",
    "数值变量2"
  ],
  "group_var": [
    "分类变量1"
  ],
  "covariates": [
    "数值变量1"
  ],
  "include_missing_analysis": false
}
```

### `one_sample_equivalence_test` - 单样本等价检验

- 分类：差异对比分析包
- 说明：单样本等价检验用于检验单个总体的参数是否与某个目标值处于预先定义的等价区间内。
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variable | 变量 | 单选，定量变量 | 拖入变量到此区域 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| alternative | 备择假设 | "下限<检验均值-目标值<上限" | 下限<检验均值-目标值<上限, 检验均值>目标值, 检验均值<目标值, 检验均值-目标值>下限, 检验均值-目标值<上限 |  |
| target_value | 目标值 | "0" |  |  |
| lower | 下限 | "-0.1" |  |  |
| upper | 上限 | "0.1" |  |  |
| scale_by_target | 乘以目标值 | true |  | 勾选后，下限和上限按目标值比例换算，例如目标值为2、上下限为±0.1时，等价区间为±0.2。 |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "variable": "数值变量1",
  "alternative": "下限<检验均值-目标值<上限",
  "target_value": "0",
  "lower": "-0.1",
  "upper": "0.1",
  "scale_by_target": true,
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variable": "数值变量1",
  "alternative": "下限<检验均值-目标值<上限",
  "target_value": "0",
  "lower": "-0.1",
  "upper": "0.1",
  "scale_by_target": true,
  "include_missing_analysis": false
}
```

### `two_sample_equivalence_test` - 双样本等价检验

- 分类：差异对比分析包
- 说明：双样本等价检验用于验证两个独立总体的参数均值差异是否在预设的等价区间内。
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| test_var | 检验样本 | 单选，定量变量 | 拖入变量到此区域 |
| group_var | 二分类 | 单选，定类变量 | 拖入变量到此区域 |
| reference_var | 参考样本 | 单选，定量变量 | 拖入变量到此区域 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| data_format | 检验数据形式 | "样本在同一列" | 样本在同一列, 样本在不同列 |  |
| reference_level | 参考水平 | "" |  |  |
| relationship | 相关假设 | "检验均值 - 参考均值" | 检验均值 - 参考均值, 检验均值/参考均值, 检验均值/参考均值(通过对数变换) |  |
| alternative | 备择假设 | "下限<检验均值 - 参考均值<上限" | 下限<检验均值 - 参考均值<上限, 检验均值>参考均值, 检验均值<参考均值, 检验均值 - 参考均值>下限, 检验均值 - 参考均值<上限 |  |
| lower | 下限 | "-0.1" |  |  |
| upper | 上限 | "0.1" |  |  |
| scale_by_reference | 乘以参考均值 | true |  |  |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "test_var": "数值变量1",
  "group_var": "分类变量1",
  "reference_var": "数值变量1",
  "data_format": "样本在同一列",
  "reference_level": "",
  "relationship": "检验均值 - 参考均值",
  "alternative": "下限<检验均值 - 参考均值<上限",
  "lower": "-0.1",
  "upper": "0.1",
  "scale_by_reference": true,
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "test_var": "数值变量1",
  "group_var": "分类变量1",
  "reference_var": "数值变量1",
  "data_format": "样本在同一列",
  "reference_level": "",
  "relationship": "检验均值 - 参考均值",
  "alternative": "下限<检验均值 - 参考均值<上限",
  "lower": "-0.1",
  "upper": "0.1",
  "scale_by_reference": true,
  "include_missing_analysis": false
}
```

### `paired_equivalence_test` - 配对样本等价检验

- 分类：差异对比分析包
- 说明：配对样本等价检验用于验证配对数据的差异是否在预设等价区间内。
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| test_var | 检验变量 | 单选，定量变量 | 拖入变量到此区域 |
| reference_var | 参考变量 | 单选，定量变量 | 拖入变量到此区域 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| relationship | 相关假设 | "检验均值 - 参考均值" | 检验均值 - 参考均值, 检验均值/参考均值, 检验均值/参考均值(通过对数变换) |  |
| alternative | 备择假设 | "下限<检验均值 - 参考均值<上限" | 下限<检验均值 - 参考均值<上限, 检验均值>参考均值, 检验均值<参考均值, 检验均值 - 参考均值>下限, 检验均值 - 参考均值<上限 |  |
| lower | 下限 | "-0.1" |  |  |
| upper | 上限 | "0.1" |  |  |
| scale_by_reference | 乘以参考均值 | true |  |  |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "test_var": "数值变量1",
  "reference_var": "数值变量1",
  "relationship": "检验均值 - 参考均值",
  "alternative": "下限<检验均值 - 参考均值<上限",
  "lower": "-0.1",
  "upper": "0.1",
  "scale_by_reference": true,
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "test_var": "数值变量1",
  "reference_var": "数值变量1",
  "relationship": "检验均值 - 参考均值",
  "alternative": "下限<检验均值 - 参考均值<上限",
  "lower": "-0.1",
  "upper": "0.1",
  "scale_by_reference": true,
  "include_missing_analysis": false
}
```

### `anova_oneway` - 单因素方差分析

- 分类：差异对比分析包
- 说明：比较三个及以上组别在某个连续变量上的均值差异
- 参数构建器：`anova`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| group_var | 分组变量 | 单选，定类变量 | 放入分组变量（须为3组及以上） |
| test_vars | 检验变量 | 多选，定量变量，至少 1 个 | 放入需要检验差异的定量变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| post_hoc | 事后比较 | "LSD" | LSD, Bonferroni, Tukey |  |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "group_var": "分类变量1",
  "test_vars": [
    "数值变量1"
  ],
  "post_hoc": "LSD",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "group_var": "分类变量1",
  "dependent": [
    "数值变量1"
  ],
  "post_hoc": "LSD"
}
```

### `chi_square` - 卡方检验

- 分类：差异对比分析包
- 说明：用于探索多组定类变量之间的差异性分析
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| var1 | 变量X | 单选，定类变量 | 放入 1 个定类分组变量 |
| variables | 变量Y | 多选，定类变量，至少 1 个 | 放入 1 个或多个定类分析变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| test_type | 类型 | "Pearson卡方检验" | Pearson卡方检验, Yates校正卡方检验, Fisher精确检验, 自动卡方检验 |  |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "var1": "分类变量1",
  "variables": [
    "分类变量1"
  ],
  "test_type": "Pearson卡方检验",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "var1": "分类变量1",
  "variables": [
    "分类变量1"
  ],
  "test_type": "Pearson卡方检验",
  "include_missing_analysis": false
}
```

### `independent_t_test` - 独立样本T检验

- 分类：差异对比分析包
- 说明：比较两个独立组别在一个或多个定量变量上的均值差异
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| group_var | 变量X | 单选，定类变量 | 样本在同一列时放入二分类变量 |
| test_vars | 变量Y | 多选，定量变量，至少 1 个 | 放入需要检验差异的定量变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| data_format | 检验数据形式 | "样本在同一列" | 样本在同一列, 样本在不同列 |  |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "group_var": "分类变量1",
  "test_vars": [
    "数值变量1"
  ],
  "data_format": "样本在同一列",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "group_var": "分类变量1",
  "test_vars": [
    "数值变量1"
  ],
  "data_format": "样本在同一列",
  "include_missing_analysis": false
}
```

### `paired_t_test` - 配对样本T检验

- 分类：差异对比分析包
- 说明：比较同一组受试者在两个条件/时间点上的均值差异
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| var1 | 变量X1 | 多选，定量变量，至少 1 个 | 放入第一组配对测量变量 |
| var2 | 变量X2 | 多选，定量变量，至少 1 个 | 放入第二组配对测量变量，数量和顺序需与变量X1一致 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "var1": [
    "数值变量1"
  ],
  "var2": [
    "数值变量1"
  ],
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "var1": [
    "数值变量1"
  ],
  "var2": [
    "数值变量1"
  ],
  "include_missing_analysis": false
}
```

## 回归 & 因果分析包

### `mediation` - 中介效应

- 分类：回归&因果分析包
- 说明：用于探究是否是哪些变量影响 X-->Y 这个流程的因素。
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| y | 变量Y | 单选，定量变量 | 拖入因变量Y |
| x | 变量X | 多选，定量变量，至少 1 个 | 拖入变量X |
| mediators | 中介变量M | 多选，定量变量，至少 1 个 | 拖入中介变量M |
| controls | 控制变量 | 多选，定量变量 | 拖入控制变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| bootstrap_reps | bootstrap抽样次数 | "auto" | {'value': 'auto', 'label': '自动'}, {'value': '1000', 'label': '1000'}, {'value': '500', 'label': '500'}, {'value': '2000', 'label': '2000'}, {'value': '5000', 'label': '5000'} |  |
| bootstrap_method | bootstrap类型 | "percentile" | {'value': 'percentile', 'label': '百分位bootstrap法'}, {'value': 'bias_corrected', 'label': '偏差校正bootstrap法'} |  |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "y": "数值变量1",
  "x": [
    "数值变量1"
  ],
  "mediators": [
    "数值变量1"
  ],
  "controls": [
    "数值变量1"
  ],
  "bootstrap_reps": "auto",
  "bootstrap_method": "percentile",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "y": "数值变量1",
  "x": [
    "数值变量1"
  ],
  "mediators": [
    "数值变量1"
  ],
  "controls": [
    "数值变量1"
  ],
  "bootstrap_reps": "auto",
  "bootstrap_method": "percentile",
  "include_missing_analysis": false
}
```

### `parallel_mediation` - 平行中介效应

- 分类：回归&因果分析包
- 说明：检验多个中介变量是否并行传递自变量对因变量的影响
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| x | 自变量(X) | 单选，定量变量 | 放入自变量 |
| mediators | 中介变量(M) | 多选，定量变量，至少 2 个 | 放入并行中介变量 |
| y | 因变量(Y) | 单选，定量变量 | 放入因变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "x": "数值变量1",
  "mediators": [
    "数值变量1",
    "数值变量2"
  ],
  "y": "数值变量1",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "x": "数值变量1",
  "mediators": [
    "数值变量1",
    "数值变量2"
  ],
  "y": "数值变量1",
  "include_missing_analysis": false
}
```

### `serial_mediation` - 链式中介

- 分类：回归&因果分析包
- 说明：检验多个中介变量按顺序传递影响的链式作用
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| y | 变量Y | 单选，定量变量 | 拖入因变量Y |
| x | 变量X | 多选，定量变量，至少 1 个 | 拖入变量X |
| mediators | 链式中介变量M | 多选，定量变量，至少 2 个 | 按链式顺序拖入中介变量M |
| controls | 控制变量 | 多选，定量变量 | 拖入控制变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| bootstrap_reps | bootstrap抽样次数 | "auto" | {'value': 'auto', 'label': '自动'}, {'value': '1000', 'label': '1000'}, {'value': '500', 'label': '500'}, {'value': '2000', 'label': '2000'}, {'value': '5000', 'label': '5000'} |  |
| bootstrap_method | bootstrap类型 | "percentile" | {'value': 'percentile', 'label': '百分位bootstrap法'}, {'value': 'bias_corrected', 'label': '偏差校正bootstrap法'} |  |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "y": "数值变量1",
  "x": [
    "数值变量1"
  ],
  "mediators": [
    "数值变量1",
    "数值变量2"
  ],
  "controls": [
    "数值变量1"
  ],
  "bootstrap_reps": "auto",
  "bootstrap_method": "percentile",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "y": "数值变量1",
  "x": [
    "数值变量1"
  ],
  "mediators": [
    "数值变量1",
    "数值变量2"
  ],
  "controls": [
    "数值变量1"
  ],
  "bootstrap_reps": "auto",
  "bootstrap_method": "percentile",
  "include_missing_analysis": false
}
```

### `moderated_mediation` - 调节中介

- 分类：回归&因果分析包
- 说明：检验调节变量 Z 是否改变 X 通过中介变量 M 影响 Y 的间接效应
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| y | 因变量Y | 单选，定量变量 | 拖入因变量Y |
| x | 自变量X | 单选，定量变量 | 拖入自变量X |
| mediators | 中介变量M | 多选，定量变量，至少 1 个 | 拖入中介变量M |
| z | 调节变量Z | 单选，定量变量 | 拖入调节变量Z |
| controls | 控制变量 | 多选，定量变量 | 拖入控制变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| moderate_x_m | X→M | false |  |  |
| moderate_m_y | M→Y | false |  |  |
| moderate_x_y | X→Y | false |  |  |
| moderator_levels | 调节水平值 | "mean_sd" | {'value': 'mean_sd', 'label': '均值±1SD'}, {'value': 'quantile', 'label': '分位数'} |  |
| bootstrap_reps | bootstrap抽样次数 | "auto" | {'value': 'auto', 'label': '自动'}, {'value': '1000', 'label': '1000'}, {'value': '500', 'label': '500'}, {'value': '2000', 'label': '2000'}, {'value': '5000', 'label': '5000'} |  |
| bootstrap_method | bootstrap类型 | "percentile" | {'value': 'percentile', 'label': '百分位bootstrap法'}, {'value': 'bias_corrected', 'label': '偏差校正bootstrap法'} |  |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "y": "数值变量1",
  "x": "数值变量1",
  "mediators": [
    "数值变量1"
  ],
  "z": "数值变量1",
  "controls": [
    "数值变量1"
  ],
  "moderate_x_m": false,
  "moderate_m_y": false,
  "moderate_x_y": false,
  "moderator_levels": "mean_sd",
  "bootstrap_reps": "auto",
  "bootstrap_method": "percentile",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "y": "数值变量1",
  "x": "数值变量1",
  "mediators": [
    "数值变量1"
  ],
  "z": "数值变量1",
  "controls": [
    "数值变量1"
  ],
  "moderate_x_m": false,
  "moderate_m_y": false,
  "moderate_x_y": false,
  "moderator_levels": "mean_sd",
  "bootstrap_reps": "auto",
  "bootstrap_method": "percentile",
  "include_missing_analysis": false
}
```

### `vif` - 共线性分析

- 分类：回归&因果分析包
- 说明：检测多个自变量之间是否存在共线性
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 分析变量 | 多选，定量变量，至少 2 个 | 放入需要检测共线性的变量（至少2个） |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ],
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ],
  "include_missing_analysis": false
}
```

### `multiple_regression` - 线性回归（最小二乘法）

- 分类：回归&因果分析包
- 说明：一元/多元线性回归，用最小二乘法分析 X 对 Y 的线性影响
- 参数构建器：`regression`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| dependent | 因变量(Y) | 单选，定量变量 | 放入单个定量因变量 |
| predictors | 自变量(X) | 多选，任意变量，至少 1 个 | 放入一个或多个定量/定类自变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "dependent": "数值变量1",
  "predictors": [
    "变量1"
  ],
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "dependent": "数值变量1",
  "predictors": [
    "变量1"
  ],
  "include_missing_analysis": false
}
```

### `moderation` - 调节作用

- 分类：回归&因果分析包
- 说明：检验调节变量 W 是否改变了自变量 X 对因变量 Y 的影响（分层回归）
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| y | 因变量(Y) | 单选，定量变量 | 放入因变量 |
| x | 自变量(X) | 单选，任意变量 | 放入自变量 |
| w | 调节变量(W) | 单选，任意变量 | 放入调节变量 |
| controls | 控制变量 | 多选，定量变量 | 可选，放入需要控制的变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| moderation_type | 调节类型 | "X定量W定量(默认)" | X定量W定量(默认), X定量W定类, X定类W定量 | 因变量Y固定为定量变量；当X或W为定类变量时会按哑变量进入模型。 |
| data_process | 数据处理 | "中心化(默认)" | 中心化(默认), 标准化, 不处理 | 仅处理定量自变量X和定量调节变量W；因变量和控制变量不处理。 |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "y": "数值变量1",
  "x": "变量1",
  "w": "变量1",
  "controls": [
    "数值变量1"
  ],
  "moderation_type": "X定量W定量(默认)",
  "data_process": "中心化(默认)",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "y": "数值变量1",
  "x": "变量1",
  "w": "变量1",
  "controls": [
    "数值变量1"
  ],
  "moderation_type": "X定量W定量(默认)",
  "data_process": "中心化(默认)",
  "include_missing_analysis": false
}
```

## 数据检验

### `one_sample_wilcoxon` - 单样本Wilcoxon符号秩检验

- 分类：数据检验
- 说明：检验一个或多个样本中位数是否显著偏离给定检验值
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| test_vars | 检验变量 | 多选，定量变量，至少 1 个 | 放入需要逐个检验的定量变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| test_value | 检验值 | "0" |  | 自动选择关闭时生效，可输入任意数字。 |
| auto_test_value | 自动选择检验值 | true |  | 勾选后每个变量使用自身均值作为检验值，和 SPSSPRO 的自动检验值口径保持一致。 |
| output_normality | 输出正态性检验图 | true |  |  |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "test_vars": [
    "数值变量1"
  ],
  "test_value": "0",
  "auto_test_value": true,
  "output_normality": true,
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "test_vars": [
    "数值变量1"
  ],
  "test_value": "0",
  "auto_test_value": true,
  "output_normality": true,
  "include_missing_analysis": false
}
```

### `wilcoxon_signed_rank_test` - 配对样本Wilcoxon符号秩检验

- 分类：数据检验
- 说明：比较一组或多组配对样本在中位数水平上的差异
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| var1 | 变量X1 | 多选，定量变量，至少 1 个 | 放入第一组配对测量变量 |
| var2 | 变量X2 | 多选，定量变量，至少 1 个 | 放入第二组配对测量变量，数量和顺序需与变量X1一致 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| output_normality | 输出正态性检验图 | true |  | 输出每组配对差值的正态性检验和直方图，便于和配对样本T检验互相参照。 |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "var1": [
    "数值变量1"
  ],
  "var2": [
    "数值变量1"
  ],
  "output_normality": true,
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "var1": [
    "数值变量1"
  ],
  "var2": [
    "数值变量1"
  ],
  "output_normality": true,
  "include_missing_analysis": false
}
```

### `mann_whitney_u_test` - 独立样本MannWhitney检验

- 分类：数据检验
- 说明：比较两个独立组在一个或多个定量变量上的秩次分布差异
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| group_var | 变量X | 单选，任意变量 | 放入分组变量；2组直接检验，3组及以上自动两两比较 |
| test_vars | 变量Y | 多选，定量变量，至少 1 个 | 放入需要逐个检验的定量变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| output_normality | 输出正态性检验图 | true |  | 输出各检验变量的正态性检验和直方图，便于和独立样本T检验互相参照。 |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "group_var": "变量1",
  "test_vars": [
    "数值变量1"
  ],
  "output_normality": true,
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "group_var": "变量1",
  "test_vars": [
    "数值变量1"
  ],
  "output_normality": true,
  "include_missing_analysis": false
}
```

### `kruskal_wallis_test` - 多独立样本Kruskal-Wallis检验

- 分类：数据检验
- 说明：比较独立组在一个或多个定量变量上的秩次分布差异
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| group_var | 变量X | 单选，任意变量 | 请输入分组变量 |
| test_vars | 变量Y | 多选，定量变量，至少 1 个 | 请输入变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| output_normality | 输出正态性检验图 | true |  | 输出各检验变量的正态性检验和直方图，便于和单因素方差分析互相参照。 |
| pairwise_compare | 输出两两比较 | true |  | 整体检验显著时，可参考Mann-Whitney两两比较定位差异来源。 |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "group_var": "变量1",
  "test_vars": [
    "数值变量1"
  ],
  "output_normality": true,
  "pairwise_compare": true,
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "group_var": "变量1",
  "test_vars": [
    "数值变量1"
  ],
  "output_normality": true,
  "pairwise_compare": true,
  "include_missing_analysis": false
}
```

### `friedman_test` - 多配对样本Friedman检验

- 分类：数据检验
- 说明：比较三个及以上配对样本在秩次上的差异
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 变量X | 多选，任意变量，至少 3 个 | 放入3个及以上配对测量变量；量表题会按数值转换后检验 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| output_normality | 输出正态性检验图 | true |  | 输出各变量正态性检验和直方图，便于和重复测量方差分析互相参照。 |
| pairwise_compare | 输出两两比较 | true |  | Friedman显著时，可参考Wilcoxon两两比较定位差异来源。 |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "variables": [
    "变量1",
    "变量2",
    "变量3"
  ],
  "output_normality": true,
  "pairwise_compare": true,
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "变量1",
    "变量2",
    "变量3"
  ],
  "output_normality": true,
  "pairwise_compare": true,
  "include_missing_analysis": false
}
```

### `goodness_of_fit_chi_square` - 卡方拟合优度检验

- 分类：数据检验
- 说明：判断期望频数与观察频数是否有显著差异
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variable | 变量 | 单选，定类变量 | 请输入变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "variable": "分类变量1",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variable": "分类变量1",
  "include_missing_analysis": false
}
```

### `cochrans_q_test` - Cochran's Q检验

- 分类：数据检验
- 说明：比较三个及以上相关二分类变量的比例差异
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 变量 | 多选，定类变量，至少 3 个 | 放入三个及以上二分类变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "variables": [
    "分类变量1",
    "分类变量2",
    "分类变量3"
  ],
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "分类变量1",
    "分类变量2",
    "分类变量3"
  ],
  "include_missing_analysis": false
}
```

### `kappa_consistency` - Kappa一致性检验

- 分类：数据检验
- 说明：评估两个评价者或两次分类结果之间的一致性
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 变量X | 多选，任意变量，至少 2 个 | 放入两个及以上定量或定类变量 |
| weight | 权重 | 单选，定量变量 | 可选，放入一个样本权重变量；无有效正权重时按未加权分析 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| kappa_type | 方法 | "简单Kappa" | 简单Kappa, 线性加权Kappa, 平方加权Kappa, Fleiss Kappa系数 | 加权Kappa适合有序分类；Fleiss Kappa需要三列及以上评价结果。 |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "variables": [
    "变量1",
    "变量2"
  ],
  "weight": "数值变量1",
  "kappa_type": "简单Kappa",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "变量1",
    "变量2"
  ],
  "weight": "数值变量1",
  "kappa_type": "简单Kappa",
  "include_missing_analysis": false
}
```

### `kendall_consistency` - Kendall一致性检验

- 分类：数据检验
- 说明：评估多位评价者对同一批评价对象排序结果的一致性程度
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 评价对象变量 | 多选，定量变量，至少 2 个 | 放入被评价对象/指标列；每行代表一位评价者或专家的评分 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ],
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ],
  "include_missing_analysis": false
}
```

### `intraclass_correlation` - ICC组内相关系数

- 分类：数据检验
- 说明：评估多个评价者或重复测量之间的一致性可靠性
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 评价变量 | 多选，定量变量，至少 2 个 | 放入多个评价者或重复测量变量；ID列若被拖入也会按普通定量列参与计算 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| icc_type | ICC类型 | "双向混合/随机 绝对一致性" | 双向混合/随机 绝对一致性, 双向混合/随机 一致性, 单向随机 绝对一致性 | 选择ICC模型类型：绝对一致、一致性或单向随机。 |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ],
  "icc_type": "双向混合/随机 绝对一致性",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ],
  "icc_type": "双向混合/随机 绝对一致性",
  "include_missing_analysis": false
}
```

### `correlation_auto_solver` - 相关与一致性推荐

- 分类：数据检验
- 说明：自动识别变量特征并推荐合适的相关或一致性分析方法
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 分析变量 | 多选，任意变量，至少 2 个 | 放入需要自动判断方法的两个或多个变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "variables": [
    "变量1",
    "变量2"
  ],
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "变量1",
    "变量2"
  ],
  "include_missing_analysis": false
}
```

### `spearman_correlation` - Spearman 等级相关

- 分类：数据检验
- 说明：分析两个或多个变量之间的等级相关程度（非参数）
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 分析变量 | 多选，定量变量，至少 2 个 | 放入需要分析相关性的变量（至少2个） |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ],
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ],
  "include_missing_analysis": false
}
```

### `mds` - 多维尺度分析MDS

- 分类：数据检验
- 说明：基于距离矩阵把对象映射到低维空间，用于观察对象之间的相似与差异结构
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 分析变量 | 多选，定量变量，至少 2 个 | 放入需要构造距离矩阵或已经组成距离矩阵的变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| data_format | 数据格式 | "根据数据创建距离矩阵" | 根据数据创建距离矩阵, 数据为距离矩阵 |  |
| analysis_dimension | 分析维度 | "按变量（列）" | 按变量（列）, 按变量（行） |  |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ],
  "data_format": "根据数据创建距离矩阵",
  "analysis_dimension": "按变量（列）",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ],
  "data_format": "根据数据创建距离矩阵",
  "analysis_dimension": "按变量（列）",
  "include_missing_analysis": false
}
```

## 综合评价

### `ahp_professional` - 层次分析法（AHP专业版）

- 分类：综合评价
- 说明：构建目标-指标-方案三层 AHP 决策模型，输出权重、一致性检验和方案排序
- 参数构建器：`direct`

变量槽位：

无变量槽位。

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| weight_method | 计算方法 | "sum_product" | {'value': 'sum_product', 'label': '和积法'}, {'value': 'root', 'label': '方根法'}, {'value': 'eigen', 'label': '特征向量法'} |  |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "weight_method": "sum_product",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "weight_method": "sum_product",
  "include_missing_analysis": false
}
```

### `ahp_simplified` - 层次分析法（AHP快速版）

- 分类：综合评价
- 说明：支持手填判断矩阵或按变量自动估权，快速计算 AHP 权重和一致性检验
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 准则指标 | 多选，定量变量 | 数据自动估权模式下放入用于构造 AHP 权重的准则变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| input_mode | 输入方式 | "matrix" | {'value': 'matrix', 'label': '手填判断矩阵'}, {'value': 'data_auto', 'label': '按变量自动估权'} |  |
| weight_method | 计算方法 | "sum_product" | {'value': 'sum_product', 'label': '和积法'}, {'value': 'root', 'label': '方根法'}, {'value': 'eigen', 'label': '特征向量法'} |  |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "variables": [
    "数值变量1"
  ],
  "input_mode": "matrix",
  "weight_method": "sum_product",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1"
  ],
  "input_mode": "matrix",
  "weight_method": "sum_product",
  "include_missing_analysis": false
}
```

### `exploratory_factor_analysis` - 探索性因子分析（EFA）

- 分类：综合评价
- 说明：通过探索性因子分析识别潜在结构与指标归类
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 分析变量 | 多选，定量变量，至少 3 个 | 放入探索性因子分析变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| factor_count_mode | 因子个数 | "auto" | {'value': 'auto', 'label': '自动抽取'}, {'value': 'fixed', 'label': '固定个数'} | 自动抽取按特征根大于1的准则确定因子数；固定个数可手动指定提取的因子数量。 |
| factor_count | 固定因子数 | 2 |  | 当因子个数选择「固定个数」时生效，需输入正整数。 |
| save_factor_scores | 保存因子得分 | false |  | 将因子得分保存为新的标题，选中后每次分析均会新增生成标题，标题名称类似为FactorScore_****。 |
| output_correlation_matrix | 相关系数矩阵 | false |  | 选中后会输出相关系数矩阵，用于分析相关关系情况。 |
| save_composite_score | 保存综合得分 | false |  | 将综合得分保存为新的标题，选中后每次分析均会新增生成标题，标题名称类似为CompScore_****。 |
| rotation_method | 旋转方法 | "varimax" | {'value': 'varimax', 'label': '最大方差法Varimax(默认)'}, {'value': 'promax', 'label': '最优斜交法Promax'} | 旋转方法用于让因子结构更清晰，Varimax适合相互独立因子，Promax适合因子间可能相关的情况。 |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2",
    "数值变量3"
  ],
  "factor_count_mode": "auto",
  "factor_count": 2,
  "save_factor_scores": false,
  "output_correlation_matrix": false,
  "save_composite_score": false,
  "rotation_method": "varimax",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2",
    "数值变量3"
  ],
  "factor_count_mode": "auto",
  "factor_count": 2,
  "save_factor_scores": false,
  "output_correlation_matrix": false,
  "save_composite_score": false,
  "rotation_method": "varimax",
  "include_missing_analysis": false
}
```

### `data_envelopment_analysis` - 数据包络分析

- 分类：综合评价
- 说明：使用 BCC/CCR 模型比较决策单元的相对投入产出效率
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| input_vars | 投入指标 | 多选，定量变量，至少 1 个 | 放入投入指标 |
| output_vars | 产出指标 | 多选，定量变量，至少 1 个 | 放入产出指标 |
| index_var | 索引项 | 单选，任意变量 | 可选，放入决策单元名称或编号 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| dea_type | 类型 | "BCC" | {'value': 'BCC', 'label': 'BCC（默认）'}, {'value': 'CCR', 'label': 'CCR'} | BCC 为可变规模报酬模型，可拆分技术效益和规模效益；CCR 为固定规模报酬模型。 |
| non_negative_translation | 非负平移 | true |  | 如果有数据小于等于0，此时平移单位为：最小值的绝对值+0.01，保证数据全部为正数可正常计算。 |
| save_efficiency | 保存效益 | false |  | 点击后会新生成标题来保存效益值，选中后每次分析均会得到新标题。 |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "input_vars": [
    "数值变量1"
  ],
  "output_vars": [
    "数值变量1"
  ],
  "index_var": "变量1",
  "dea_type": "BCC",
  "non_negative_translation": true,
  "save_efficiency": false,
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "input_vars": [
    "数值变量1"
  ],
  "output_vars": [
    "数值变量1"
  ],
  "index_var": "变量1",
  "dea_type": "BCC",
  "non_negative_translation": true,
  "save_efficiency": false,
  "include_missing_analysis": false
}
```

### `fuzzy_comprehensive_evaluation` - 模糊综合评价

- 分类：综合评价
- 说明：通过指标权重、模糊算子和评价集隶属度得到综合评价结果
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 评价项 | 多选，定量变量，至少 2 个 | 放入评价指标 |
| index_var | 索引项 | 单选，定类变量 | 可选，放入样本名称或编号 |
| weight_var | 评价指标权重 | 单选，定量变量 | 可选，选择自定义权重时按评价项顺序读取前 N 个有效数值 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| weight_method | 变量权重 | "entropy" | {'value': 'entropy', 'label': '熵权法'}, {'value': 'equal', 'label': '不设置权重'}, {'value': 'custom', 'label': '自定义权重'} | 熵权法按指标离散程度自动赋权；不设置权重表示等权；自定义权重需放入评价指标权重列或通过 API 传 custom_weights/weights。 |
| fuzzy_operator | 模糊算子 | "weighted_average" | {'value': 'main_factor_decision', 'label': '主因素决定型：M(∧,V)', 'recommendation': '更多考虑指标权重，输入数据在一定程度上不会有明显影响，不推荐使用。'}, {'value': 'main_factor_prominent', 'label': '主因素突出型：M(*,V)', 'recommendation': '在主因素决定型基础上修正输入数据的上界程度，不推荐使用。'}, {'value': 'bounded_sum_min', 'label': '取小与有界型：M(∧,+)', 'recommendation': '更多使用输入数据信息，推荐使用。'}, {'value': 'weighted_average', 'label': '加权平均型：M(*,+)', 'recommendation': '综合利用指标权重和输入数据信息，推荐使用。'} | 主因素决定型 M(∧,V)：更多考虑指标权重，不推荐。
主因素突出型 M(*,V)：修正输入数据上界，不推荐。
取小与有界型 M(∧,+)：更多使用输入数据信息，推荐。
加权平均型 M(*,+)：综合利用权重和输入信息，推荐。 |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ],
  "index_var": "分类变量1",
  "weight_method": "entropy",
  "fuzzy_operator": "weighted_average",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ],
  "index_var": "分类变量1",
  "weight_method": "entropy",
  "fuzzy_operator": "weighted_average",
  "include_missing_analysis": false
}
```

### `topsis` - 优劣解距离法(TOPSIS)

- 分类：综合评价
- 说明：基于正负理想解距离评价方案优劣，支持等权、熵权和自定义权重
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| positive_vars | 变量 | 多选，定量变量 | 拖入正向指标 |
| negative_vars | 变量 | 多选，定量变量 | 拖入负向指标 |
| index_var | 变量 | 单选，定类变量 | 可选，放入样本名称或编号 |
| weight_var | 变量 | 单选，定量变量 | 选择自定义权重时，按指标顺序读取前 N 个有效数值 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| weight_method | 变量权重 | "entropy" | {'value': 'entropy', 'label': '熵权法'}, {'value': 'equal', 'label': '不设置权重'}, {'value': 'custom', 'label': '自定义权重'} | 熵权法对应 SPSSAU 的熵权TOPSIS；不设置权重对应普通 TOPSIS；自定义权重需放入指标权重列或通过 API 传 custom_weights/weights。 |
| save_process | 保存过程值 | false |  | 选中后生成新数据版本，保存 D+、D-、相对接近度 C 和排序结果。 |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "positive_vars": [
    "数值变量1"
  ],
  "negative_vars": [
    "数值变量1"
  ],
  "index_var": "分类变量1",
  "weight_method": "entropy",
  "save_process": false,
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "positive_vars": [
    "数值变量1"
  ],
  "negative_vars": [
    "数值变量1"
  ],
  "index_var": "分类变量1",
  "weight_method": "entropy",
  "save_process": false,
  "include_missing_analysis": false
}
```

### `rsr` - 秩和比综合评价法(RSR/WRSR)

- 分类：综合评价
- 说明：通过指标秩次计算 RSR/WRSR 综合得分，支持正负向指标、权重和 Probit 分档
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| positive_vars | 变量 | 多选，定量变量 | 拖入越大越好的指标 |
| negative_vars | 变量 | 多选，定量变量 | 拖入越小越好的指标 |
| index_var | 变量 | 单选，定类变量 | 可选，放入样本名称或编号 |
| weight_var | 变量 | 单选，定量变量 | 选择自定义权重时，按指标顺序读取前 N 个有效数值 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| rank_method | 编秩方法 | "integer" | {'value': 'integer', 'label': '整次法'}, {'value': 'fractional', 'label': '非整次法'} | 整次法按样本排序秩次计算，并列值取平均秩；非整次法按极差线性换算为非整秩。 |
| division_count | 分档数量 | "3" | {'value': '3', 'label': '3档'}, {'value': '4', 'label': '4档'}, {'value': '5', 'label': '5档'}, {'value': '6', 'label': '6档'}, {'value': '7', 'label': '7档'} | 支持 3-7 档；分档阈值基于 Probit 回归结果生成。 |
| weight_method | 变量权重 | "equal" | {'value': 'equal', 'label': '不设置权重'}, {'value': 'entropy', 'label': '熵权法'}, {'value': 'custom', 'label': '自定义权重'} | 不设置权重为普通 RSR；熵权法和自定义权重为加权 WRSR。 |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "positive_vars": [
    "数值变量1"
  ],
  "negative_vars": [
    "数值变量1"
  ],
  "index_var": "分类变量1",
  "rank_method": "integer",
  "division_count": "3",
  "weight_method": "equal",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "positive_vars": [
    "数值变量1"
  ],
  "negative_vars": [
    "数值变量1"
  ],
  "index_var": "分类变量1",
  "rank_method": "integer",
  "division_count": "3",
  "weight_method": "equal",
  "include_missing_analysis": false
}
```

### `coupling_coordination` - 耦合协调度

- 分类：综合评价
- 说明：衡量多个系统或指标之间的耦合关系与协调发展水平，支持正负向指标、协调指数、权重和数据区间化
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| positive_vars | 变量 | 多选，定量变量 | 拖入越大越好的指标 |
| negative_vars | 变量 | 多选，定量变量 | 拖入越小越好的指标 |
| coordination_index_var | 变量 | 单选，定量变量 | 可选，放入已计算好的协调指数T |
| label_vars | 变量 | 多选，定类变量 | 可选，最多 2 个标签变量，用于标识样本 |
| weight_var | 变量 | 单选，定量变量 | 选择自定义权重时，按指标顺序读取前 N 个有效数值 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| weight_method | 指标权重 | "equal" | {'value': 'equal', 'label': '不设置权重'}, {'value': 'entropy', 'label': '熵权法'}, {'value': 'custom', 'label': '自定义权重'} | 默认各指标权重相等；熵权法按离散程度赋权；自定义权重需放入指标权重列或通过 API 传 custom_weights/weights。 |
| data_intervalization | 数据区间化 | true |  | 将同趋势化后的数据压缩到 0.01~0.99，避免 0 值导致耦合度退化或不稳定。 |
| save_process | 保存计算值 | false |  | 选中后生成新数据版本，保存耦合度C、协调指数T、耦合协调度D和协调等级。 |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "positive_vars": [
    "数值变量1"
  ],
  "negative_vars": [
    "数值变量1"
  ],
  "coordination_index_var": "数值变量1",
  "label_vars": [
    "分类变量1"
  ],
  "weight_method": "equal",
  "data_intervalization": true,
  "save_process": false,
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "positive_vars": [
    "数值变量1"
  ],
  "negative_vars": [
    "数值变量1"
  ],
  "coordination_index_var": "数值变量1",
  "label_vars": [
    "分类变量1"
  ],
  "weight_method": "equal",
  "data_intervalization": true,
  "save_process": false,
  "include_missing_analysis": false
}
```

### `coefficient_variation` - 变异系数法（信息量权重）

- 分类：综合评价
- 说明：使用变异系数衡量指标离散程度并进行客观赋权，兼容 SPSSAU 信息量权重口径
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 评价指标 | 多选，定量变量，至少 2 个 | 放入需要计算信息量权重的定量指标 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ],
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ],
  "include_missing_analysis": false
}
```

### `entropy_method` - 熵值法

- 分类：综合评价
- 说明：依据指标离散程度自动分配客观权重并计算综合得分
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| positive_vars | 正向指标 / 变量 | 多选，定量变量 | 拖入越大越好的指标 |
| negative_vars | 负向指标 / 变量 | 多选，定量变量 | 拖入越小越好的指标 |
| index_var | 索引项 / 变量 | 单选，定类变量 | 可选，放入样本名称或编号 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| non_negative_translation | 非负平移 | false |  | 如果熵权计算矩阵中有数据小于等于0，平移单位为最小值的绝对值+0.01，保证数据全部为正数后计算。 |
| save_composite_score | 保存综合得分 | false |  | 选中后生成新数据版本，保存本次熵值法综合得分。 |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "positive_vars": [
    "数值变量1",
    "数值变量2"
  ],
  "negative_vars": [
    "数值变量3"
  ],
  "index_var": "分类变量1",
  "non_negative_translation": false,
  "save_composite_score": false,
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "positive_vars": [
    "数值变量1",
    "数值变量2"
  ],
  "negative_vars": [
    "数值变量3"
  ],
  "index_var": "分类变量1",
  "non_negative_translation": false,
  "save_composite_score": false,
  "include_missing_analysis": false
}
```

### `critic_weight` - CRITIC权重法

- 分类：综合评价
- 说明：综合考虑指标对比强度与冲突性进行客观赋权
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 评价指标 | 多选，定量变量，至少 2 个 | 放入需要计算 CRITIC 权重的定量指标 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| save_composite_score | 保存综合得分 | false |  | 选中后生成新数据版本，按 CRITIC 权重保存综合得分；未设置方向时默认各指标越大越好。 |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ],
  "save_composite_score": false,
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ],
  "save_composite_score": false,
  "include_missing_analysis": false
}
```

### `independent_weight_coefficient` - 独立性权系数法

- 分类：综合评价
- 说明：依据各指标与其他指标之间的复相关系数确定客观权重，复相关系数越大说明信息重复越多、权重越小
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 评价指标 | 多选，定量变量，至少 2 个 | 放入综合评价指标 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ],
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ],
  "include_missing_analysis": false
}
```

### `grey_relational_analysis` - 灰色关联分析

- 分类：综合评价
- 说明：通过特征序列与母序列的几何形态相似程度评估关联强弱
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| feature_vars | 变量 | 多选，定量变量，至少 2 个 | 放入至少 2 个需要和母序列比较的定量变量 |
| mother_var | 变量 | 单选，定量变量 | 放入 1 个作为关联对象的定量变量 |
| index_var | 变量 | 单选，定类变量 | 可选，放入观测点名称或编号 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| dimensionless_method | 无量纲处理方式 | "mean" | initial=初值化, mean=均值化, none=不处理 | 初值化适合稳定递增或递减的数据；均值化适合没有明显升降趋势的数据；不处理直接使用原始数值。 |
| rho | 分辨系数ρ | 0.5 | 0<ρ<1 | 分辨系数ρ∈(0,1)，ρ越小分辨力越大，通常取ρ=0.5。 |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "feature_vars": [
    "数值变量1",
    "数值变量2"
  ],
  "mother_var": "数值变量3",
  "index_var": "分类变量1",
  "dimensionless_method": "mean",
  "rho": 0.5,
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "feature_vars": [
    "数值变量1",
    "数值变量2"
  ],
  "mother_var": "数值变量3",
  "index_var": "分类变量1",
  "dimensionless_method": "mean",
  "rho": 0.5,
  "include_missing_analysis": false
}
```

旧参数 `reference_var` / `compare_vars` 仍可兼容，当前入口优先使用 `mother_var` / `feature_vars`。

### `vikor` - 多准则妥协解排序法（VIKOR）

- 分类：综合评价
- 说明：根据群体效用与个体遗憾构建折中排序，支持正负向指标、熵权/等权/自定义权重和决策系数 v
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| positive_vars | 正向指标 | 多选，定量变量 | 拖入正向指标（越大越好） |
| negative_vars | 负向指标 | 多选，定量变量 | 拖入负向指标（越小越好） |
| index_var | 索引项 | 单选，分类变量 | 可选，放入样本名称或编号 |
| weight_var | 指标权重 | 单选，定量变量 | 自定义权重时按指标顺序读取前 N 个有效数值 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| weight_method | 加权方式 | entropy | entropy / equal / custom | 熵权法、权重相同、自定义权重 |
| v_coefficient | 决策机制系数v | 0.5 | 0~1 数值 | v>0.5 侧重群体效用，v<0.5 侧重个体遗憾 |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "positive_vars": ["q2"],
  "negative_vars": ["q3", "q4"],
  "index_var": "样本编号",
  "weight_method": "entropy",
  "v_coefficient": 0.5,
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "positive_vars": ["q2"],
  "negative_vars": ["q3", "q4"],
  "weight_method": "entropy",
  "v_coefficient": 0.5,
  "include_missing_analysis": false
}
```

### `ism` - 解释结构模型法（ISM）

- 分类：综合评价
- 说明：通过可达矩阵分析要素间的层级结构关系，支持邻接矩阵/可达矩阵输入和多种分解方式
- 参数构建器：`direct`

变量槽位：无（使用矩阵输入）

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| elements | 要素名称 | [] | 字符串数组 | 要素名称列表，至少 2 个 |
| matrix | 矩阵数据 | [] | n×n 二维数组 | 邻接矩阵或可达矩阵（0/1 方阵） |
| data_type | 数据类型 | adjacency | adjacency / reachability | 邻接矩阵或可达矩阵 |
| decomposition_method | 分解方式 | up | hierarchy / up / down | 层次分解、结果优先-UP型、原因优先-DOWN型 |

前端槽位示例：

```json
{
  "elements": ["要素1", "要素2", "要素3", "要素4"],
  "matrix": [
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1],
    [0, 0, 0, 0]
  ],
  "data_type": "adjacency",
  "decomposition_method": "up"
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "elements": ["要素1", "要素2", "要素3", "要素4"],
  "matrix": [
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1],
    [0, 0, 0, 0]
  ],
  "data_type": "adjacency",
  "decomposition_method": "up"
}
```

## 高级问卷分析包

### `nps` - NPS净推荐值分析

- 分类：高级问卷分析包
- 说明：基于 0-10 推荐评分计算贬损者、被动者、推荐者及净推荐值
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| score_var | NPS评分变量 | 单选，定量变量 | 放入 0-10 推荐评分变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "score_var": "数值变量1",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "score_var": "数值变量1",
  "include_missing_analysis": false
}
```

### `discrimination` - 区分度分析

- 分类：高级问卷分析包
- 说明：检验题项是否能够有效区分高水平与低水平样本
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 题项变量 | 多选，定量变量，至少 2 个 | 放入量表题项 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ],
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ],
  "include_missing_analysis": false
}
```

### `conjoint` - 联合分析

- 分类：高级问卷分析包
- 说明：估计用户对多个属性水平的偏好权重
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| score_var | 偏好评分变量 | 单选，定量变量 | 放入评分或偏好变量 |
| attribute_vars | 属性变量 | 多选，定类变量，至少 2 个 | 放入属性水平变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "score_var": "数值变量1",
  "attribute_vars": [
    "分类变量1",
    "分类变量2"
  ],
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "score_var": "数值变量1",
  "attribute_vars": [
    "分类变量1",
    "分类变量2"
  ],
  "include_missing_analysis": false
}
```

### `entropy_weight` - 权重分析(熵权法)

- 分类：高级问卷分析包
- 说明：依据指标离散程度自动分配客观权重
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 指标变量 | 多选，定量变量，至少 2 个 | 放入综合评价指标 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ],
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ],
  "include_missing_analysis": false
}
```

### `maxdiff` - MaxDiff模型

- 分类：高级问卷分析包
- 说明：基于最好/最差选择结果恢复偏好强度与优先级排序
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | MaxDiff任务变量 | 多选，定类变量，至少 2 个 | 放入 MaxDiff 任务相关变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "variables": [
    "分类变量1",
    "分类变量2"
  ],
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "分类变量1",
    "分类变量2"
  ],
  "include_missing_analysis": false
}
```

### `price_breakpoint` - 价格断裂点模型

- 分类：高级问卷分析包
- 说明：识别价格敏感度研究中的心理接受边界与关键交点
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| too_cheap | 太便宜 | 单选，定量变量 | 放入“太便宜”价格变量 |
| cheap | 便宜 | 单选，定量变量 | 放入“便宜”价格变量 |
| expensive | 贵 | 单选，定量变量 | 放入“贵”价格变量 |
| too_expensive | 太贵 | 单选，定量变量 | 放入“太贵”价格变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "too_cheap": "数值变量1",
  "cheap": "数值变量1",
  "expensive": "数值变量1",
  "too_expensive": "数值变量1",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "too_cheap": "数值变量1",
  "cheap": "数值变量1",
  "expensive": "数值变量1",
  "too_expensive": "数值变量1",
  "include_missing_analysis": false
}
```

### `turf` - TURF分析

- 分类：高级问卷分析包
- 说明：寻找在给定数量约束下覆盖最多受众的最优选项组合
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 覆盖项变量 | 多选，定类变量，至少 2 个 | 放入 0/1 覆盖变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| combo_size | 组合大小 | "3" | 2, 3, 4 |  |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "variables": [
    "分类变量1",
    "分类变量2"
  ],
  "combo_size": "3",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "分类变量1",
    "分类变量2"
  ],
  "combo_size": "3",
  "include_missing_analysis": false
}
```

### `penalty_analysis` - 惩罚分析

- 分类：高级问卷分析包
- 说明：识别属性表现偏低时对总体满意度的拖累程度
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| satisfaction_var | 总体满意度 | 单选，定量变量 | 放入总体满意度变量 |
| attribute_vars | 属性表现变量 | 多选，定量变量，至少 1 个 | 放入属性评分变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "satisfaction_var": "数值变量1",
  "attribute_vars": [
    "数值变量1"
  ],
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "satisfaction_var": "数值变量1",
  "attribute_vars": [
    "数值变量1"
  ],
  "include_missing_analysis": false
}
```

### `bpto` - 品牌价格抵补模型BPTO

- 分类：高级问卷分析包
- 说明：评估品牌优势是否足以抵补价格劣势
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| choice_var | 选择结果 | 单选，定类变量 | 放入选择结果变量 |
| brand_var | 品牌变量 | 单选，定类变量 | 放入品牌变量 |
| price_var | 价格变量 | 单选，定量变量 | 放入价格变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "choice_var": "分类变量1",
  "brand_var": "分类变量1",
  "price_var": "数值变量1",
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "choice_var": "分类变量1",
  "brand_var": "分类变量1",
  "price_var": "数值变量1",
  "include_missing_analysis": false
}
```

### `cbc_conjoint` - 联合分析CBC

- 分类：高级问卷分析包
- 说明：基于选择任务的联合分析，更贴近真实购买场景
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| choice_var | 选择结果 | 单选，定类变量 | 放入选择任务结果变量 |
| attribute_vars | 属性变量 | 多选，定类变量，至少 2 个 | 放入 CBC 属性变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "choice_var": "分类变量1",
  "attribute_vars": [
    "分类变量1",
    "分类变量2"
  ],
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "choice_var": "分类变量1",
  "attribute_vars": [
    "分类变量1",
    "分类变量2"
  ],
  "include_missing_analysis": false
}
```

### `maxdiff_pro` - MaxDiff Pro

- 分类：高级问卷分析包
- 说明：强调个体层效用恢复与高级模拟能力的 MaxDiff 扩展方法
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | MaxDiff任务变量 | 多选，定类变量，至少 2 个 | 放入 MaxDiff 任务变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "variables": [
    "分类变量1",
    "分类变量2"
  ],
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "分类变量1",
    "分类变量2"
  ],
  "include_missing_analysis": false
}
```

## 高级回归 & 因果分析包

### `path_analysis` - 路径分析

- 分类：高级回归&因果分析包
- 说明：分析多个观测变量之间的直接路径与间接路径
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| dependent | 因变量(Y) | 单选，定量变量 | 放入最终结果变量 |
| predictors | 路径变量 | 多选，定量变量，至少 2 个 | 放入参与路径模型的变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "dependent": "数值变量1",
  "predictors": [
    "数值变量1",
    "数值变量2"
  ],
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "dependent": "数值变量1",
  "predictors": [
    "数值变量1",
    "数值变量2"
  ],
  "include_missing_analysis": false
}
```

### `sem` - 结构方程模型(SEM)

- 分类：高级回归&因果分析包
- 说明：同时估计测量模型和结构模型，适合潜变量与复杂理论检验
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| measurement_vars | 测量题项 | 多选，定量变量，至少 3 个 | 放入潜变量题项 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_missing_analysis | 输出缺失分析 | false |  |  |

前端槽位示例：

```json
{
  "measurement_vars": [
    "数值变量1",
    "数值变量2",
    "数值变量3"
  ],
  "include_missing_analysis": false
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "measurement_vars": [
    "数值变量1",
    "数值变量2",
    "数值变量3"
  ],
  "include_missing_analysis": false
}
```
