# 统计分析方法参数文档

本文档由 `scripts/generate_analysis_method_docs.py` 根据后端 `METHOD_META` 自动生成。

接口入口：

```http
POST /api/execute-method/{session_id}
Content-Type: application/json
Authorization: Bearer <access_token>
```

查看单个方法参数详情：

```http
GET /api/methods/{method_key}
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

当前共整理 80 个统计分析方法。

## 数据探查

### `frequency` - 频数分析

- 分类：数据探查
- 说明：统计各类别的频次和百分比分布
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variable | 分析变量 | 单选，任意变量 | 放入需要统计频次的变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "variable": "变量1"
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variable": "变量1"
}
```

### `cross_tabulation` - 列联（交叉）分析

- 分类：数据探查
- 说明：查看两个分类变量的交叉分布，并给出卡方检验与关联强度
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| var1 | 行变量 | 单选，定类变量 | 放入第一个分类变量 |
| var2 | 列变量 | 单选，定类变量 | 放入第二个分类变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "var1": "分类变量1",
  "var2": "分类变量1"
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "var1": "分类变量1",
  "var2": "分类变量1"
}
```

### `descriptive` - 描述性统计

- 分类：数据探查
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

- 分类：数据探查
- 说明：按分类变量分组汇总一个或多个定量变量的样本量、均值和极值
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| group_var | 分类变量 | 单选，定类变量 | 放入用于分组汇总的分类变量 |
| summary_vars | 汇总变量 | 多选，定量变量，至少 1 个 | 放入需要按组汇总的定量变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "group_var": "分类变量1",
  "summary_vars": [
    "数值变量1"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "group_var": "分类变量1",
  "summary_vars": [
    "数值变量1"
  ]
}
```

### `normality_test` - 正态性分析

- 分类：数据探查
- 说明：使用 Shapiro-Wilk 检验判断变量是否服从正态分布
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 分析变量 | 多选，定量变量，至少 1 个 | 放入需要检验正态性的变量 |

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

### `data_overview` - 数据探查

- 分类：数据探查
- 说明：快速查看数据集规模、变量类型、缺失情况和变量明细
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 变量 | 多选，任意变量，至少 1 个 | 放入需要概览的一个或多个变量 |

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
| variables | 分析变量 | 多选，定量变量，至少 2 个 | 放入同一量表的所有题项 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| type | 类型 | "Cronbach's α" | Cronbach's α |  |

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ],
  "type": "Cronbach's α"
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "items_groups": {
    "分析变量": [
      "数值变量1",
      "数值变量2"
    ]
  }
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

无额外选项。

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2",
    "数值变量3"
  ]
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
  "scale_name": "量表"
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

无额外选项。

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
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

无额外选项。

前端槽位示例：

```json
{
  "variables": [
    "分类变量1",
    "分类变量2"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "分类变量1",
    "分类变量2"
  ]
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

无额外选项。

前端槽位示例：

```json
{
  "var1": "分类变量1",
  "var2": "分类变量1"
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "var1": "分类变量1",
  "var2": "分类变量1"
}
```

### `correspondence_analysis` - 对应分析

- 分类：问卷分析包
- 说明：对两个分类变量的列联表进行降维，观察类别之间的接近关系
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| var1 | 行变量 | 单选，定类变量 | 放入第一个分类变量 |
| var2 | 列变量 | 单选，定类变量 | 放入第二个分类变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "var1": "分类变量1",
  "var2": "分类变量1"
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "var1": "分类变量1",
  "var2": "分类变量1"
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

无额外选项。

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
  ]
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
  ]
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

无额外选项。

前端槽位示例：

```json
{
  "functional_vars": [
    "分类变量1"
  ],
  "dysfunctional_vars": [
    "分类变量1"
  ]
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
  ]
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

前端槽位示例：

```json
{
  "test_vars": [
    "数值变量1"
  ],
  "test_value": "0"
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "test_vars": [
    "数值变量1"
  ],
  "test_value": "0"
}
```

### `summary_t_test` - 摘要T检验

- 分类：差异对比分析包
- 说明：以简化摘要形式呈现T检验核心结果
- 参数构建器：`t_test`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| group_var | 分组变量 | 单选，定类变量 | 放入二分类分组变量 |
| test_vars | 检验变量 | 多选，定量变量，至少 1 个 | 放入检验变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "group_var": "分类变量1",
  "test_vars": [
    "数值变量1"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "group_var": "分类变量1",
  "dependent": [
    "数值变量1"
  ]
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
| test_vars | 检验变量 | 多选，定量变量 | 放入需要比较的定量变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| method | 比较方法 | "LSD方法(默认)" | LSD方法(默认), Scheffe, Tukey, Bonferroni校正, sidak, Tamhane T2(方差不齐), SNK Q检验, Duncan检验, Games-Howell(方差不齐) |  |
| use_letters | 字母标记法 | false | true, false |  |
| include_effect_size | 效应量 | false | true, false |  |
| show_p_marks | P值标识 | true | true, false |  |

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
  "show_p_marks": true
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
  "show_p_marks": true
}
```

### `two_way_anova` - 双因素方差分析

- 分类：差异对比分析包
- 说明：检验两个分类因素及其交互作用对因变量的影响
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| factors | 分组变量X | 多选，定类变量 | 放入2个分组因素 |
| dependent | 因变量Y | 单选，定量变量 | 放入因变量 |
| covariates | 协变量 | 多选，定量变量 | 可选，放入需要控制的协变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_interaction | 分析交互效应 | true | true, false |  |
| do_post_hoc | 事后多重比较 | false | true, false |  |
| post_hoc_method | 方法选择 | "LSD" | LSD, bonf, sidak |  |

前端槽位示例：

```json
{
  "factors": [
    "分类变量1",
    "分类变量2"
  ],
  "dependent": "数值变量1",
  "covariates": [],
  "include_interaction": true,
  "do_post_hoc": false,
  "post_hoc_method": "LSD"
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
  "covariates": [],
  "include_interaction": true,
  "do_post_hoc": false,
  "post_hoc_method": "LSD"
}
```

### `three_way_anova` - 三因素方差分析

- 分类：差异对比分析包
- 说明：检验三个分类因素及其交互作用对因变量的影响
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| factors | 分组变量X | 多选，定类变量 | 放入3个分组因素 |
| dependent | 因变量Y | 单选，定量变量 | 放入因变量 |
| covariates | 协变量 | 多选，定量变量 | 可选，放入需要控制的协变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| include_interaction | 分析交互效应 | true | true, false |  |
| second_order_interaction | 二阶交互效应 | true | true, false |  |
| third_order_interaction | 三阶交互效应 | false | true, false |  |
| include_effect_size | 效应量 | false | true, false |  |
| do_post_hoc | 事后多重比较 | false | true, false |  |
| post_hoc_method | 方法选择 | "LSD" | LSD, Tukey法, Bonferroni校正, Sidak法 |  |

前端槽位示例：

```json
{
  "factors": [
    "分类变量1",
    "分类变量2",
    "分类变量3"
  ],
  "dependent": "数值变量1",
  "covariates": [],
  "include_interaction": true,
  "second_order_interaction": true,
  "third_order_interaction": false,
  "include_effect_size": false,
  "do_post_hoc": false,
  "post_hoc_method": "LSD"
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
  "covariates": [],
  "include_interaction": true,
  "second_order_interaction": true,
  "third_order_interaction": false,
  "include_effect_size": false,
  "do_post_hoc": false,
  "post_hoc_method": "LSD"
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
| do_post_hoc | 事后多重比较 | false | true, false |  |
| post_hoc_method | 方法选择 | "LSD" | LSD, Tukey法, Bonferroni校正, Sidak法 | 默认不进行事后多重比较，可选比如LSD等事后多重比较检验方法。 |
| include_effect_size | 效应量 | false | true, false | 选中后结果表格中会输出效应量。 |

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
  "include_effect_size": false
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
  "include_effect_size": false
}
```

### `summary_oneway_anova` - 摘要单因素方差分析

- 分类：差异对比分析包
- 说明：以简化摘要形式呈现单因素方差分析核心结果
- 参数构建器：`anova`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| group_var | 分组变量 | 单选，定类变量 | 放入分组变量 |
| test_vars | 检验变量 | 多选，定量变量，至少 1 个 | 放入检验变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| post_hoc | 事后比较 | "Bonferroni" | LSD, Bonferroni, Tukey |  |

前端槽位示例：

```json
{
  "group_var": "分类变量1",
  "test_vars": [
    "数值变量1"
  ],
  "post_hoc": "Bonferroni"
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "group_var": "分类变量1",
  "dependent": [
    "数值变量1"
  ],
  "post_hoc": "Bonferroni"
}
```

### `ancova` - 协方差分析

- 分类：差异对比分析包
- 说明：在控制协变量影响后比较组间均值差异
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| group_var | 分组变量 | 单选，定类变量 | 放入分组变量 |
| covariates | 协变量 | 多选，定量变量，至少 1 个 | 放入协变量 |
| dependent | 因变量 | 单选，定量变量 | 放入因变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "group_var": "分类变量1",
  "covariates": [
    "数值变量1"
  ],
  "dependent": "数值变量1"
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "group_var": "分类变量1",
  "covariates": [
    "数值变量1"
  ],
  "dependent": "数值变量1"
}
```

### `manova` - 多变量方差分析

- 分类：差异对比分析包
- 说明：同时检验多个因变量在组间的总体差异
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| group_var | 分组变量 | 单选，定类变量 | 放入分组变量 |
| dependent_vars | 因变量 | 多选，定量变量，至少 2 个 | 放入两个及以上因变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "group_var": "分类变量1",
  "dependent_vars": [
    "数值变量1",
    "数值变量2"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "group_var": "分类变量1",
  "dependent_vars": [
    "数值变量1",
    "数值变量2"
  ]
}
```

### `one_sample_equivalence_test` - 单样本等价性检验

- 分类：差异对比分析包
- 说明：使用 TOST 检验单样本均值是否落在等价区间内
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variable | 检验变量 | 单选，定量变量 | 放入检验变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| reference_value | 参考值 | "0" | 0, 1, 5 |  |
| margin | 等价界值 | "1" | 0.5, 1, 2 |  |

前端槽位示例：

```json
{
  "variable": "数值变量1",
  "reference_value": "0",
  "margin": "1"
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variable": "数值变量1",
  "reference_value": "0",
  "margin": "1"
}
```

### `two_sample_equivalence_test` - 双样本等价性检验

- 分类：差异对比分析包
- 说明：使用 TOST 检验两个独立样本均值差是否落在等价区间内
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| group_var | 分组变量 | 单选，定类变量 | 放入二分类分组变量 |
| test_var | 检验变量 | 单选，定量变量 | 放入检验变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| margin | 等价界值 | "1" | 0.5, 1, 2 |  |

前端槽位示例：

```json
{
  "group_var": "分类变量1",
  "test_var": "数值变量1",
  "margin": "1"
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "group_var": "分类变量1",
  "test_var": "数值变量1",
  "margin": "1"
}
```

### `paired_equivalence_test` - 配对样本等价性检验

- 分类：差异对比分析包
- 说明：使用 TOST 检验配对样本差值是否落在等价区间内
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| var1 | 变量1 | 单选，定量变量 | 放入第一个配对变量 |
| var2 | 变量2 | 单选，定量变量 | 放入第二个配对变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| margin | 等价界值 | "1" | 0.5, 1, 2 |  |

前端槽位示例：

```json
{
  "var1": "数值变量1",
  "var2": "数值变量1",
  "margin": "1"
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "var1": "数值变量1",
  "var2": "数值变量1",
  "margin": "1"
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

前端槽位示例：

```json
{
  "group_var": "分类变量1",
  "test_vars": [
    "数值变量1"
  ],
  "post_hoc": "LSD"
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
- 说明：检验两个分类变量之间是否存在显著关联
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| var1 | 行变量 | 单选，定类变量 | 放入第一个分类变量 |
| var2 | 列变量 | 单选，定类变量 | 放入第二个分类变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "var1": "分类变量1",
  "var2": "分类变量1"
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "var1": "分类变量1",
  "var2": "分类变量1"
}
```

### `independent_t_test` - 独立样本T检验

- 分类：差异对比分析包
- 说明：比较两个独立组别在某个连续变量上的均值差异
- 参数构建器：`t_test`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| group_var | 分组变量 | 单选，定类变量 | 放入分组变量（如性别，须为2组） |
| test_vars | 检验变量 | 多选，定量变量，至少 1 个 | 放入需要检验差异的定量变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "group_var": "分类变量1",
  "test_vars": [
    "数值变量1"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "group_var": "分类变量1",
  "dependent": [
    "数值变量1"
  ]
}
```

### `paired_t_test` - 配对样本T检验

- 分类：差异对比分析包
- 说明：比较同一组受试者在两个条件/时间点上的均值差异
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| var1 | 变量X1 | 多选，定量变量 | 放入第一组配对测量变量 |
| var2 | 变量X2 | 多选，定量变量 | 放入第二组配对测量变量，数量和顺序需与变量X1一致 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "var1": [
    "数值变量1"
  ],
  "var2": [
    "数值变量2"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "var1": [
    "数值变量1"
  ],
  "var2": [
    "数值变量2"
  ]
}
```

## 回归 & 因果分析包

### `mediation` - 中介效应分析

- 分类：回归&因果分析包
- 说明：使用 R/lavaan 检验中介变量 M 在自变量 X 和因变量 Y 之间的中介作用
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| x | 自变量(X) | 单选，定量变量 | 放入自变量 |
| m | 中介变量(M) | 单选，定量变量 | 放入中介变量 |
| y | 因变量(Y) | 单选，定量变量 | 放入因变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "x": "数值变量1",
  "m": "数值变量1",
  "y": "数值变量1"
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "x": "数值变量1",
  "m": "数值变量1",
  "y": "数值变量1"
}
```

### `multiple_regression` - 多元线性回归

- 分类：回归&因果分析包
- 说明：分析多个自变量对一个因变量的预测作用
- 参数构建器：`regression`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| dependent | 因变量(Y) | 单选，定量变量 | 放入因变量 |
| predictors | 自变量(X) | 多选，定量变量，至少 1 个 | 放入一个或多个自变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "dependent": "数值变量1",
  "predictors": [
    "数值变量1"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "dependent": "数值变量1",
  "predictors": [
    "数值变量1"
  ]
}
```

### `vif` - 多重共线性 VIF

- 分类：回归&因果分析包
- 说明：检测多个自变量之间是否存在多重共线性
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 分析变量 | 多选，定量变量，至少 2 个 | 放入需要检测共线性的变量（至少2个） |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

### `moderation` - 调节作用

- 分类：回归&因果分析包
- 说明：检验调节变量 W 是否改变了自变量 X 对因变量 Y 的影响（分层回归）
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| x | 自变量(X) | 单选，定量变量 | 放入自变量 |
| w | 调节变量(W) | 单选，定量变量 | 放入调节变量 |
| y | 因变量(Y) | 单选，定量变量 | 放入因变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "x": "数值变量1",
  "w": "数值变量1",
  "y": "数值变量1"
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "x": "数值变量1",
  "w": "数值变量1",
  "y": "数值变量1"
}
```

## 数据检验

### `one_sample_wilcoxon` - 单样本Wilcoxon符号秩检验

- 分类：数据检验
- 说明：检验样本中位数是否显著偏离给定检验值
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variable | 检验变量 | 单选，定量变量 | 放入需要检验的变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| test_value | 检验值 | "0" | 0, 1, 3, 5 |  |

前端槽位示例：

```json
{
  "variable": "数值变量1",
  "test_value": "0"
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variable": "数值变量1",
  "test_value": "0"
}
```

### `wilcoxon_signed_rank_test` - 配对样本Wilcoxon符号秩检验

- 分类：数据检验
- 说明：比较两个配对样本在中位数水平上的差异
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| var1 | 变量1 | 单选，定量变量 | 放入第一个配对变量 |
| var2 | 变量2 | 单选，定量变量 | 放入第二个配对变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "var1": "数值变量1",
  "var2": "数值变量1"
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "var1": "数值变量1",
  "var2": "数值变量1"
}
```

### `mann_whitney_u_test` - 独立样本MannWhitney检验

- 分类：数据检验
- 说明：比较两个独立组在秩次分布上的差异
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| group_var | 分组变量 | 单选，定类变量 | 放入二分类分组变量 |
| test_var | 检验变量 | 单选，定量变量 | 放入检验变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "group_var": "分类变量1",
  "test_var": "数值变量1"
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "group_var": "分类变量1",
  "test_var": "数值变量1"
}
```

### `kruskal_wallis_test` - 多独立样本Kruskal-Wallis检验

- 分类：数据检验
- 说明：比较三个及以上独立组在秩次分布上的差异
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| group_var | 分组变量 | 单选，定类变量 | 放入分组变量（3组及以上） |
| test_var | 检验变量 | 单选，定量变量 | 放入检验变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "group_var": "分类变量1",
  "test_var": "数值变量1"
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "group_var": "分类变量1",
  "test_var": "数值变量1"
}
```

### `friedman_test` - 多配对样本Friedman检验

- 分类：数据检验
- 说明：比较三个及以上配对样本在秩次上的差异
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 配对变量 | 多选，定量变量，至少 3 个 | 放入三个及以上配对变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2",
    "数值变量3"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2",
    "数值变量3"
  ]
}
```

### `goodness_of_fit_chi_square` - 卡方拟合优度检验

- 分类：数据检验
- 说明：检验样本分布是否符合给定理论分布
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variable | 分类变量 | 单选，定类变量 | 放入分类变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "variable": "分类变量1"
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variable": "分类变量1"
}
```

### `cochrans_q_test` - Cochran's Q检验

- 分类：数据检验
- 说明：比较三个及以上相关二分类变量的比例差异
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 二分类变量 | 多选，定类变量，至少 3 个 | 放入三个及以上二分类变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "variables": [
    "分类变量1",
    "分类变量2",
    "分类变量3"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "分类变量1",
    "分类变量2",
    "分类变量3"
  ]
}
```

### `kappa_consistency` - Kappa一致性检验

- 分类：数据检验
- 说明：评估两个评价者或两次分类结果之间的一致性
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| rater1 | 评价者1 | 单选，定类变量 | 放入第一个分类变量 |
| rater2 | 评价者2 | 单选，定类变量 | 放入第二个分类变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "rater1": "分类变量1",
  "rater2": "分类变量1"
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "rater1": "分类变量1",
  "rater2": "分类变量1"
}
```

### `kendall_consistency` - Kendall一致性检验

- 分类：数据检验
- 说明：评估多个评价对象排序结果之间的一致性程度
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 评价变量 | 多选，定量变量，至少 2 个 | 放入多个评价者或多轮排序结果 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

### `intraclass_correlation` - 组内相关系数

- 分类：数据检验
- 说明：评估多个评价者或重复测量之间的一致性可靠性
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 评价变量 | 多选，定量变量，至少 2 个 | 放入多个评价者或重复测量变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

### `correlation_auto_solver` - 相关性分析自动求解器

- 分类：数据检验
- 说明：自动识别变量特征并推荐合适的相关或一致性分析方法
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 分析变量 | 多选，任意变量，至少 2 个 | 放入需要自动判断方法的两个或多个变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "variables": [
    "变量1",
    "变量2"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "变量1",
    "变量2"
  ]
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

无额外选项。

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

### `mds` - 多维尺度分析

- 分类：数据检验
- 说明：基于变量间距离关系建立二维空间坐标，用于观察接近结构
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 分析变量 | 多选，定量变量，至少 2 个 | 放入需要比较结构接近性的变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

## 综合评价

### `ahp_professional` - 层次分析法（AHP专业版）

- 分类：综合评价
- 说明：提供判断矩阵、一致性检验和综合得分的更完整 AHP 输出
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 准则指标 | 多选，定量变量，至少 2 个 | 放入用于构造 AHP 权重的准则变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

### `ahp_simplified` - 层次分析法（AHP简化版）

- 分类：综合评价
- 说明：基于指标平均重要度近似构造判断矩阵并计算权重
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 准则指标 | 多选，定量变量，至少 2 个 | 放入用于构造 AHP 权重的准则变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

### `exploratory_factor_analysis` - 因子分析（探索性）

- 分类：综合评价
- 说明：通过探索性因子分析识别潜在结构与指标归类
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 分析变量 | 多选，定量变量，至少 3 个 | 放入探索性因子分析变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2",
    "数值变量3"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2",
    "数值变量3"
  ]
}
```

### `data_envelopment_analysis` - 数据包络分析

- 分类：综合评价
- 说明：使用 CCR 模型近似计算各决策单元的相对效率
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| input_vars | 投入指标 | 多选，定量变量，至少 1 个 | 放入投入指标 |
| output_vars | 产出指标 | 多选，定量变量，至少 1 个 | 放入产出指标 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "input_vars": [
    "数值变量1"
  ],
  "output_vars": [
    "数值变量1"
  ]
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
  ]
}
```

### `fuzzy_comprehensive_evaluation` - 模糊综合评价

- 分类：综合评价
- 说明：通过模糊隶属度和加权合成得到综合评价结果
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 评价指标 | 多选，定量变量，至少 2 个 | 放入评价指标 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

### `topsis` - 优劣解距离法(TOPSIS)

- 分类：综合评价
- 说明：基于与理想解和负理想解的距离进行综合排序
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 评价指标 | 多选，定量变量，至少 2 个 | 放入综合评价指标 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

### `rsr` - 秩和比综合评价法(RSR)

- 分类：综合评价
- 说明：通过指标排序后的秩和比值进行综合评价
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 评价指标 | 多选，定量变量，至少 2 个 | 放入综合评价指标 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

### `coupling_coordination` - 耦合协调度

- 分类：综合评价
- 说明：衡量多个子系统之间的耦合关系与协调发展水平
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| group1_vars | 子系统1指标 | 多选，定量变量，至少 1 个 | 放入子系统1指标 |
| group2_vars | 子系统2指标 | 多选，定量变量，至少 1 个 | 放入子系统2指标 |
| group3_vars | 子系统3指标 | 多选，定量变量 | 可选：放入子系统3指标 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "group1_vars": [
    "数值变量1"
  ],
  "group2_vars": [
    "数值变量1"
  ],
  "group3_vars": [
    "数值变量1"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "group1_vars": [
    "数值变量1"
  ],
  "group2_vars": [
    "数值变量1"
  ],
  "group3_vars": [
    "数值变量1"
  ]
}
```

### `coefficient_variation` - 变异系数法

- 分类：综合评价
- 说明：使用变异系数衡量指标离散程度并进行客观赋权
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 评价指标 | 多选，定量变量，至少 2 个 | 放入综合评价指标 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

### `entropy_method` - 熵值法

- 分类：综合评价
- 说明：依据指标离散程度自动分配客观权重并计算综合得分
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 评价指标 | 多选，定量变量，至少 2 个 | 放入综合评价指标 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

### `critic_weight` - CRITIC权重法

- 分类：综合评价
- 说明：综合考虑指标对比强度与冲突性进行客观赋权
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 评价指标 | 多选，定量变量，至少 2 个 | 放入综合评价指标 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

### `independent_weight_coefficient` - 独立性权系数法

- 分类：综合评价
- 说明：依据指标独立性和离散程度构造综合客观权重
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 评价指标 | 多选，定量变量，至少 2 个 | 放入综合评价指标 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

### `grey_relational_analysis` - 灰色关联分析

- 分类：综合评价
- 说明：通过比较序列与参考序列的接近程度评估关联强弱
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| reference_var | 参考序列 | 单选，定量变量 | 放入参考变量 |
| compare_vars | 比较序列 | 多选，定量变量，至少 1 个 | 放入比较变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "reference_var": "数值变量1",
  "compare_vars": [
    "数值变量1"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "reference_var": "数值变量1",
  "compare_vars": [
    "数值变量1"
  ]
}
```

### `vikor` - 多准则妥协排序法（VIKOR）

- 分类：综合评价
- 说明：根据群体效用与个体遗憾构建折中排序
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 评价指标 | 多选，定量变量，至少 2 个 | 放入综合评价指标 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

### `ism` - 解释结构模型（ISM）

- 分类：综合评价
- 说明：基于变量间关系构建多层级的解释结构
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables | 结构变量 | 多选，定量变量，至少 3 个 | 放入需要构建结构层级的变量 |

额外选项：

| 参数 key | 名称 | 默认值 | 可选值 | 说明 |
| --- | --- | --- | --- | --- |
| threshold | 关系阈值 | "0.3" | 0.3, 0.4, 0.5 |  |

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2",
    "数值变量3"
  ],
  "threshold": "0.3"
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
  "threshold": "0.3"
}
```

## 高级问卷分析包

### `choice_multi_multi` - 选择题【多选&多选】

- 分类：高级问卷分析包
- 说明：比较两组多选题之间的联合选择结构，适合研究题项组合与共现关系
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| variables_a | 多选题A | 多选，定类变量，至少 2 个 | 放入第一组多选题变量 |
| variables_b | 多选题B | 多选，定类变量，至少 2 个 | 放入第二组多选题变量 |

额外选项：

无额外选项。

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
  ]
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
  ]
}
```

### `choice_multi_single` - 选择题【多选&单选】

- 分类：高级问卷分析包
- 说明：比较不同单选分组在多选题上的选择偏好差异
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| multiple_vars | 多选题变量 | 多选，定类变量，至少 2 个 | 放入同一题目的多选拆分变量 |
| single_var | 单选分组变量 | 单选，定类变量 | 放入用于分组的单选题变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "multiple_vars": [
    "分类变量1",
    "分类变量2"
  ],
  "single_var": "分类变量1"
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "multiple_vars": [
    "分类变量1",
    "分类变量2"
  ],
  "single_var": "分类变量1"
}
```

### `choice_single_multi` - 选择题【单选&多选】

- 分类：高级问卷分析包
- 说明：从单选结果出发，分析不同单选人群在多选题上的偏好扩展
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| single_var | 单选变量 | 单选，定类变量 | 放入单选题变量 |
| multiple_vars | 多选题变量 | 多选，定类变量，至少 2 个 | 放入同一题目的多选拆分变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "single_var": "分类变量1",
  "multiple_vars": [
    "分类变量1",
    "分类变量2"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "single_var": "分类变量1",
  "multiple_vars": [
    "分类变量1",
    "分类变量2"
  ]
}
```

### `nps` - NPS净推荐值分析

- 分类：高级问卷分析包
- 说明：基于 0-10 推荐评分计算贬损者、被动者、推荐者及净推荐值
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| score_var | NPS评分变量 | 单选，定量变量 | 放入 0-10 推荐评分变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "score_var": "数值变量1"
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "score_var": "数值变量1"
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

无额外选项。

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
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

无额外选项。

前端槽位示例：

```json
{
  "score_var": "数值变量1",
  "attribute_vars": [
    "分类变量1",
    "分类变量2"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "score_var": "数值变量1",
  "attribute_vars": [
    "分类变量1",
    "分类变量2"
  ]
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

无额外选项。

前端槽位示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "数值变量1",
    "数值变量2"
  ]
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

无额外选项。

前端槽位示例：

```json
{
  "variables": [
    "分类变量1",
    "分类变量2"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "分类变量1",
    "分类变量2"
  ]
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

无额外选项。

前端槽位示例：

```json
{
  "too_cheap": "数值变量1",
  "cheap": "数值变量1",
  "expensive": "数值变量1",
  "too_expensive": "数值变量1"
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "too_cheap": "数值变量1",
  "cheap": "数值变量1",
  "expensive": "数值变量1",
  "too_expensive": "数值变量1"
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

前端槽位示例：

```json
{
  "variables": [
    "分类变量1",
    "分类变量2"
  ],
  "combo_size": "3"
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "分类变量1",
    "分类变量2"
  ],
  "combo_size": "3"
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

无额外选项。

前端槽位示例：

```json
{
  "satisfaction_var": "数值变量1",
  "attribute_vars": [
    "数值变量1"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "satisfaction_var": "数值变量1",
  "attribute_vars": [
    "数值变量1"
  ]
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

无额外选项。

前端槽位示例：

```json
{
  "choice_var": "分类变量1",
  "brand_var": "分类变量1",
  "price_var": "数值变量1"
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "choice_var": "分类变量1",
  "brand_var": "分类变量1",
  "price_var": "数值变量1"
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

无额外选项。

前端槽位示例：

```json
{
  "choice_var": "分类变量1",
  "attribute_vars": [
    "分类变量1",
    "分类变量2"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "choice_var": "分类变量1",
  "attribute_vars": [
    "分类变量1",
    "分类变量2"
  ]
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

无额外选项。

前端槽位示例：

```json
{
  "variables": [
    "分类变量1",
    "分类变量2"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "variables": [
    "分类变量1",
    "分类变量2"
  ]
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

无额外选项。

前端槽位示例：

```json
{
  "dependent": "数值变量1",
  "predictors": [
    "数值变量1",
    "数值变量2"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "dependent": "数值变量1",
  "predictors": [
    "数值变量1",
    "数值变量2"
  ]
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

无额外选项。

前端槽位示例：

```json
{
  "measurement_vars": [
    "数值变量1",
    "数值变量2",
    "数值变量3"
  ]
}
```

`POST /api/execute-method/{session_id}` 最终 `params` 示例：

```json
{
  "measurement_vars": [
    "数值变量1",
    "数值变量2",
    "数值变量3"
  ]
}
```

### `parallel_mediation` - 平行中介效应

- 分类：高级回归&因果分析包
- 说明：检验多个中介变量是否并行传递自变量对因变量的影响
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| x | 自变量(X) | 单选，定量变量 | 放入自变量 |
| mediators | 中介变量(M) | 多选，定量变量，至少 2 个 | 放入并行中介变量 |
| y | 因变量(Y) | 单选，定量变量 | 放入因变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "x": "数值变量1",
  "mediators": [
    "数值变量1",
    "数值变量2"
  ],
  "y": "数值变量1"
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
  "y": "数值变量1"
}
```

### `serial_mediation` - 链式中介效应

- 分类：高级回归&因果分析包
- 说明：检验多个中介变量按顺序传递影响的链式作用
- 参数构建器：`direct`

变量槽位：

| 参数 key | 名称 | 类型 | 说明 |
| --- | --- | --- | --- |
| x | 自变量(X) | 单选，定量变量 | 放入自变量 |
| mediators | 链式中介变量(M) | 多选，定量变量，至少 2 个 | 按顺序放入中介变量 |
| y | 因变量(Y) | 单选，定量变量 | 放入因变量 |

额外选项：

无额外选项。

前端槽位示例：

```json
{
  "x": "数值变量1",
  "mediators": [
    "数值变量1",
    "数值变量2"
  ],
  "y": "数值变量1"
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
  "y": "数值变量1"
}
```
