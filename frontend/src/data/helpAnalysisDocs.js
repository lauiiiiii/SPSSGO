import { extraAnalysisChildren } from './helpAnalysisDocsExtra'

function buildStepScreenshot(methodTitle, stepTitle, customHint) {
  return {
    title: '步骤截图占位',
    hint: customHint || `此处预留“${methodTitle} / ${stepTitle}”对应的界面截图。后续可补充方法选择界面、变量拖拽界面、参数设置界面或结果页面截图。`,
  }
}

function attachStepScreenshots(methodTitle, steps = []) {
  return steps.map((step) => ({
    ...step,
    screenshot: step.screenshot || buildStepScreenshot(methodTitle, step.title, step.screenshotHint),
  }))
}

function buildAnalysisChild(id, title, config = {}) {
  let sectionIndex = 1
  const sections = [
    {
      id: `${id}-purpose`,
      title: `${sectionIndex++}、作用与适用场景`,
      intro: config.intro || `${title}用于帮助你围绕当前研究问题完成对应的数据分析任务。`,
      paragraphs: config.purpose || [
        `${title}适合在你已经完成数据清洗后，用来回答“有什么差异、是否相关、能否预测、结构是否稳定”等问题。`,
      ],
    },
    {
      id: `${id}-io`,
      title: `${sectionIndex++}、输入输出描述`,
      paragraphs: config.io || [
        '输入：根据方法要求拖入一个或多个变量，并根据界面提示完成必要参数设置。',
        '输出：系统会生成表格结果、关键统计量以及可直接用于解释的分析说明。',
      ],
    },
    {
      id: `${id}-steps`,
      title: `${sectionIndex++}、操作步骤`,
      steps: attachStepScreenshots(title, config.steps || []),
    },
    {
      id: `${id}-reading`,
      title: `${sectionIndex++}、结果解读`,
      points: config.reading || [
        {
          title: '先判断方法是否匹配问题',
          text: '确认你现在看到的统计量，是否真的对应你要回答的研究问题，而不是只看显著性。',
        },
        {
          title: '再抓关键指标',
          text: '围绕当前方法最核心的统计量阅读结果，例如均值、p 值、相关系数、回归系数或拟合指标。',
        },
        {
          title: '最后写成解释语言',
          text: '把统计结果翻译成业务语言、研究语言或论文表达，而不是只停留在表格层面。',
        },
      ],
    },
  ]

  if (config.formulas?.length) {
    sections.push({
      id: `${id}-formula`,
      title: `${sectionIndex++}、计算公式`,
      formulas: config.formulas,
    })
  }

  if (config.codeBlocks?.length) {
    sections.push({
      id: `${id}-code`,
      title: `${sectionIndex++}、程序实现`,
      codeBlocks: config.codeBlocks,
    })
  }

  const noticeParagraphs = Array.isArray(config.notice)
    ? config.notice
    : [config.notice || '执行前请先确认变量类型、样本量和缺失情况，避免方法选择正确但变量条件不满足。']

  sections.push({
    id: `${id}-notice`,
    title: `${sectionIndex++}、注意事项`,
    paragraphs: noticeParagraphs,
  })

  return {
    id,
    title,
    pageTitle: title,
    sections,
  }
}

export const analysisChildren = [
  buildAnalysisChild('analysis-overview-doc', '分析总览', {
    intro: '数据分析模块适合在完成上传、清洗和变量确认之后进入。它的核心流程不是“点一下就出结果”，而是先明确问题，再按方法要求把变量放对位置。',
    purpose: [
      '如果你希望快速上手整个分析工作流，可以先看这页。它会告诉你从选方法、拖变量、设参数到解释结果的通用顺序。',
      '后续每一个具体分析方法都提供独立教程页，你可以在左侧继续点开相应方法查看更细的操作说明。',
    ],
    io: [
      '输入：一份已经上传并完成基础清洗的数据集，以及你想回答的分析问题。',
      '输出：方法配置、结构化结果表、AI 辅助解读，以及可复制到报告中的解释文本。',
    ],
    steps: [
      {
        title: '先明确研究问题',
        text: '先判断你是做现状描述、差异比较、相关关系、结构检验还是预测建模。问题一旦明确，方法选择就会更快。',
      },
      {
        title: '从左侧选择分析方法',
        text: '在分析面板中点击具体方法，阅读方法简介和变量槽位提示，先看“需要什么变量”，再开始拖拽。',
      },
      {
        title: '把变量拖入正确槽位',
        text: '严格区分因变量、自变量、分组变量、量表题项等角色，变量位置放错会直接影响结果含义。',
      },
      {
        title: '查看结果并形成结论',
        text: '执行后优先阅读结果页中的核心统计量和解释说明，再决定是否继续加做其他分析方法。',
      },
    ],
    reading: [
      {
        title: '方法要回答问题，而不是替代问题',
        text: '比如你要比较 2 组差异，应先想到 t 检验；要比较 3 组及以上差异，应优先考虑方差分析。',
      },
      {
        title: '变量角色比参数更重要',
        text: '很多分析报错或结论异常，并不是算法问题，而是变量放错位置、变量类型不匹配或样本条件不满足。',
      },
      {
        title: '解释时要回到业务或研究语境',
        text: '不要只写“显著/不显著”，更要说明差异方向、关系强弱、影响路径和实际意义。',
      },
    ],
    notice: [
      '建议先完成缺失值、异常值、编码、量表方向等基础数据处理，再进入正式分析。',
      '如果一个问题需要多种方法支持，推荐先做描述性统计，再逐步进入差异、相关、回归或结构分析。',
    ],
  }),
  buildAnalysisChild('analysis-data-overview', '数据概览', {
    intro: '数据概览用于快速盘点当前数据集的样本规模、变量类型、缺失情况和变量列表，是正式分析前最适合先看的入口。',
    purpose: [
      '当你刚上传一份数据，或者接手别人整理过的数据时，优先用数据概览确认字段是否完整、类型是否合理、缺失是否明显。',
    ],
    io: [
      '输入：一个或多个需要查看的数据变量。',
      '输出：变量概况、样本量、类型分布和缺失比例，用于决定后续分析或数据处理路径。',
    ],
    steps: [
      {
        title: '选择“数据概览”方法',
        text: '在数据概览分类下点击“数据概览”，进入当前数据集的概览界面。',
      },
      {
        title: '拖入需要查看的变量',
        text: '可以一次拖入多个变量，优先检查核心指标、分组变量和后续分析会用到的关键字段。',
      },
      {
        title: '执行并查看基础概况',
        text: '关注样本量、变量类型、缺失数量和字段命名，确认是否存在文本列混入、空列或编码异常。',
      },
    ],
    reading: [
      {
        title: '先看缺失比例',
        text: '如果缺失比例较高，后续很多统计方法都会受到影响，建议先去数据处理模块完成缺失值处理。',
      },
      {
        title: '再看变量类型',
        text: '定量、定类和文本变量的判断会直接影响你后面能否使用相关、t 检验、回归等方法。',
      },
      {
        title: '最后检查变量命名',
        text: '变量命名清晰，会明显降低后续拖拽变量和解释结果时的认知负担。',
      },
    ],
    formulas: [
      {
        title: '缺失比例',
        text: '数据概览里最常见的一个指标是每个变量的缺失比例，用来判断后续是否需要清洗。',
        latex: String.raw`$$
\mathrm{MissingRate}(x)=\frac{\#\{x_i\ \text{缺失}\}}{n}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        text: '下面的示例展示了如何快速查看样本量、类型和缺失比例。',
        code: String.raw`summary = pd.DataFrame({
    "dtype": df.dtypes.astype(str),
    "missing_count": df.isna().sum(),
    "missing_rate": df.isna().mean().round(4),
})

summary["non_missing"] = len(df) - summary["missing_count"]`,
      },
    ],
    notice: '如果你发现变量类型不合理，例如数值列被识别成文本列，建议先回到数据处理模块做编码或类型修正。',
  }),
  buildAnalysisChild('analysis-frequency', '频数分析', {
    intro: '频数分析用于统计一个变量中每个取值出现的次数和百分比，特别适合单选题、性别、地区、学历、满意度等级等分类变量。',
    io: [
      '输入：1 个需要统计频次的变量，可为定类变量，也可为离散型定量变量。',
      '输出：每个类别的频数、百分比和累计百分比，帮助你快速把握分布结构。',
    ],
    steps: [
      {
        title: '选择“频数分析”',
        text: '在数据概览分类下点击“频数分析”，进入单变量分布统计页面。',
      },
      {
        title: '拖入分析变量',
        text: '把需要统计的变量拖入分析槽位。如果是问卷单选题，建议先确认数据标签已经设置好。',
      },
      {
        title: '执行并查看分布表',
        text: '重点关注每个类别的样本数量和比例，判断是否存在极端偏斜、极少数类别或编码异常。',
      },
    ],
    reading: [
      {
        title: '先看频数',
        text: '频数能告诉你每个类别有多少样本，适合判断样本是否过少或类别是否过碎。',
      },
      {
        title: '再看百分比',
        text: '百分比更适合用于报告表达，尤其在样本总量较大时，比直接写频数更便于比较。',
      },
      {
        title: '最后看累计百分比',
        text: '如果变量本身有等级顺序，累计百分比可以帮助你更快判断总体集中在哪些类别。',
      },
    ],
    formulas: [
      {
        title: '频数与百分比',
        latex: String.raw`$$
n_k = \sum_{i=1}^{n} I(x_i = k),\qquad
p_k = \frac{n_k}{n}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`freq = df["gender"].value_counts(dropna=False)
percent = df["gender"].value_counts(normalize=True, dropna=False).mul(100).round(2)

result = pd.DataFrame({
    "频数": freq,
    "百分比(%)": percent,
})`,
      },
    ],
    notice: '如果变量原始值是 1、2、3 这类编码，建议先设置数据标签，否则结果页会不够直观。',
  }),
  buildAnalysisChild('analysis-descriptive', '描述性统计', {
    intro: '描述性统计适合快速了解定量变量的中心位置、离散程度和整体分布特征，是很多正式分析前的第一步。',
    io: [
      '输入：1 个或多个定量变量。',
      '输出：均值、标准差、最小值、最大值等描述指标，帮助你理解变量的大致水平和波动范围。',
    ],
    steps: [
      {
        title: '选择“描述性统计”',
        text: '在数据概览分类下点击“描述性统计”，进入多变量描述统计界面。',
      },
      {
        title: '拖入定量变量',
        text: '建议先拖入核心因变量或量表总分，再逐步加入其他控制变量、背景变量和关键指标。',
      },
      {
        title: '执行并查看统计表',
        text: '重点关注每个变量的均值、标准差、最小值和最大值，初步判断取值范围是否合理。',
      },
    ],
    reading: [
      {
        title: '均值反映总体水平',
        text: '均值越高，说明该变量在样本中的整体水平越高，但需要结合量表范围一起解释。',
      },
      {
        title: '标准差反映离散程度',
        text: '标准差越大，说明样本差异越明显；如果标准差过小，说明变量可能分布过于集中。',
      },
      {
        title: '极值用于发现异常',
        text: '最小值和最大值能帮助你快速发现不可能的录入值、异常编码或量表方向错误。',
      },
    ],
    formulas: [
      {
        title: '均值与标准差',
        latex: String.raw`$$
\bar{x} = \frac{1}{n}\sum_{i=1}^{n}x_i,\qquad
s = \sqrt{\frac{1}{n-1}\sum_{i=1}^{n}(x_i-\bar{x})^2}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`desc = df[["score", "anxiety", "support"]].agg(
    ["count", "mean", "std", "min", "max"]
).T

desc = desc.rename(columns={
    "count": "样本量",
    "mean": "均值",
    "std": "标准差",
    "min": "最小值",
    "max": "最大值",
})`,
      },
    ],
    notice: '如果描述性统计已经暴露出异常值、取值越界或极端偏态，建议先回到数据处理模块处理后再做推断统计。',
  }),
  buildAnalysisChild('analysis-category-summary', '分类汇总', {
    intro: '分类汇总用于按一个分类变量分组，汇总一个或多个定量变量的样本量、均值和极值，适合先做分组概览再决定是否进入差异检验。',
    io: [
      '输入：1 个分类变量，外加 1 个或多个需要按组汇总的定量变量。',
      '输出：每个组别下的样本量、均值、最小值和最大值等统计结果。',
    ],
    steps: [
      {
        title: '选择“分类汇总”',
        text: '在数据概览分类下点击“分类汇总”，准备按分组变量查看不同类别下的基本统计情况。',
      },
      {
        title: '拖入分类变量和汇总变量',
        text: '把分组变量拖入“分类变量”，再把要观察的定量指标拖入“汇总变量”。',
      },
      {
        title: '执行并比较各组结果',
        text: '先比较样本量是否平衡，再对比组均值和范围差异，判断是否值得进一步做 t 检验或方差分析。',
      },
    ],
    reading: [
      {
        title: '先看组样本量',
        text: '如果某一组样本过少，后续推断检验的稳定性会受影响，需要谨慎解释。',
      },
      {
        title: '再看组均值',
        text: '分类汇总本身不能判断差异是否显著，但可以帮助你先看到差异方向和大致幅度。',
      },
      {
        title: '极值有助于发现组内异常',
        text: '如果某组最小值或最大值明显异常，建议进一步查看该组原始数据。',
      },
    ],
    formulas: [
      {
        title: '分组均值',
        latex: String.raw`$$
\bar{x}_g = \frac{1}{n_g}\sum_{i: G_i=g} x_i
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`summary = (
    df.groupby("group")["score"]
      .agg(["count", "mean", "min", "max"])
      .rename(columns={
          "count": "样本量",
          "mean": "均值",
          "min": "最小值",
          "max": "最大值",
      })
)`,
      },
    ],
    notice: '如果你的目标是判断组间差异是否显著，分类汇总只是预览步骤，后续仍应继续使用 t 检验或方差分析。',
  }),
  buildAnalysisChild('analysis-cross-tabulation', '列联（交叉）分析', {
    intro: '列联（交叉）分析用于同时查看两个分类变量的交叉分布，并结合卡方检验与关联强度评价类别之间的关系。',
    io: [
      '输入：2 个分类变量，分别作为行变量和列变量。',
      '输出：交叉频数、理论频数、卡方检验结果和关联强度指标。',
    ],
    steps: [
      {
        title: '选择“列联（交叉）分析”',
        text: '在数据概览分类下点击该方法，准备查看两个分类变量之间的分布关系。',
      },
      {
        title: '分别拖入行变量和列变量',
        text: '建议优先选择本身具有业务含义的分类变量，例如性别、地区、学历、购买意愿等级等。',
      },
      {
        title: '执行并查看交叉表',
        text: '先观察哪些类别组合的频数更高，再结合卡方检验结果判断这种分布差异是否具有统计学意义。',
      },
    ],
    reading: [
      {
        title: '先看交叉频数',
        text: '交叉频数告诉你每一个类别组合出现了多少样本，是理解结构差异的基础。',
      },
      {
        title: '再看理论频数与显著性',
        text: '如果卡方检验显著，说明两个分类变量之间不是随机独立分布；理论频数则可帮助你判断前提条件是否基本满足。',
      },
      {
        title: '最后结合关联强度解释',
        text: '即便显著，也要看关系强弱，不要把“显著”误当成“关联很强”。',
      },
    ],
    formulas: [
      {
        title: '卡方与 Cramer’s V',
        latex: String.raw`$$
\chi^2 = \sum_{i=1}^{r}\sum_{j=1}^{c}\frac{(O_{ij}-E_{ij})^2}{E_{ij}}
$$
$$
V = \sqrt{\frac{\chi^2}{n \cdot \min(r-1,c-1)}}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`table = pd.crosstab(df["gender"], df["purchase_intent"])
chi2, p, dof, expected = chi2_contingency(table)

cramers_v = np.sqrt(chi2 / (table.to_numpy().sum() * min(table.shape[0] - 1, table.shape[1] - 1)))`,
      },
    ],
    notice: '如果某些格子的理论频数过低，卡方检验结果会变得不稳定，必要时可考虑合并类别后再分析。',
  }),
  buildAnalysisChild('analysis-normality', '正态性分析', {
    intro: '正态性分析用于判断变量是否近似服从正态分布，常用于为 t 检验、方差分析、Pearson 相关和线性回归做前提检查。',
    io: [
      '输入：1 个或多个定量变量。',
      '输出：每个变量的 Shapiro-Wilk 检验统计量与显著性，用于辅助判断正态性。',
    ],
    steps: [
      {
        title: '选择“正态性分析”',
        text: '在数据概览分类下点击“正态性分析”，进入正态性检验页面。',
      },
      {
        title: '拖入定量变量',
        text: '把需要判断正态性的变量拖入分析区，通常优先检查因变量、量表总分或模型残差。',
      },
      {
        title: '执行并查看检验结果',
        text: '关注 Shapiro-Wilk 的统计量和 p 值，必要时结合直方图、箱型图一起判断。',
      },
    ],
    reading: [
      {
        title: 'p 值只是辅助判断',
        text: '样本量很大时，轻微偏离正态也可能显著；样本量很小时，不显著也不代表一定正态。',
      },
      {
        title: '建议结合图形一起看',
        text: '如果分布明显偏斜、长尾或多峰，仅依靠一个 p 值往往不够。',
      },
      {
        title: '不要把正态性看成绝对门槛',
        text: '很多方法在样本量足够时对轻微偏离仍有一定稳健性，应结合研究情境综合判断。',
      },
    ],
    formulas: [
      {
        title: 'Shapiro-Wilk 统计量',
        latex: String.raw`$$
W = \frac{\left(\sum_{i=1}^{n} a_i x_{(i)}\right)^2}{\sum_{i=1}^{n}(x_i-\bar{x})^2}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`from scipy.stats import shapiro

for col in ["score", "anxiety"]:
    stat, p = shapiro(df[col].dropna())
    print(col, stat, p)`,
      },
    ],
    notice: '如果变量明显不服从正态分布，可考虑做数据变换，或改用 Spearman 相关、非参数检验等替代方法。',
  }),
  buildAnalysisChild('analysis-reliability', '信度分析', {
    intro: '信度分析用于评估一组量表题项是否稳定地测量同一个潜在概念，最常见指标是 Cronbach’s α。',
    io: [
      '输入：来自同一量表、量纲一致、方向一致的多个题项变量。',
      '输出：总体 Cronbach’s α、逐项统计、删除题项后的 α 变化等结果。',
    ],
    steps: [
      {
        title: '选择“信度分析”',
        text: '在问卷分析包下点击“信度分析”，准备评估量表内部一致性。',
      },
      {
        title: '拖入同一量表的题项',
        text: '只放入同一个维度或同一份量表的题项；如果有反向题，先确认已经完成反向计分。',
      },
      {
        title: '执行并查看总体 α 系数',
        text: '先关注总体 Cronbach’s α 水平，再观察逐项统计与“删除题项后 α”是否有明显改善。',
      },
    ],
    reading: [
      {
        title: '先看总体 α',
        text: '通常 α 越高说明内部一致性越好，但过高也可能提示题项内容过于重复。',
      },
      {
        title: '再看 CITC 和删除项后 α',
        text: '如果某题的项总相关很低，且删除它后 α 明显提高，说明该题可能需要重新审视。',
      },
      {
        title: '量表修改要有理论依据',
        text: '不要只为了追求更高 α 就机械删除题项，应结合题目语义和量表结构一起判断。',
      },
    ],
    formulas: [
      {
        title: 'Cronbach’s α',
        latex: String.raw`$$
\alpha = \frac{k}{k-1}\left(1-\frac{\sum_{j=1}^{k}s_j^2}{s_T^2}\right)
$$`,
        text: '其中，$k$ 为题项数，$s_j^2$ 为各题项方差，$s_T^2$ 为量表总分方差。',
      },
    ],
    codeBlocks: [
      {
        title: 'R 示例',
        code: String.raw`items <- na.omit(df[, c("q1", "q2", "q3", "q4")])
k <- ncol(items)
item_var <- sum(apply(items, 2, var))
total_var <- var(rowSums(items))

alpha <- k / (k - 1) * (1 - item_var / total_var)
print(round(alpha, 4))`,
      },
    ],
    notice: '当前版本中，信度分析由 R 引擎执行；请先确认生产环境已安装 R 与所需 R 包。信度分析前请确认题项方向一致。如果反向题没有先处理，α 系数会被明显拉低。',
  }),
  buildAnalysisChild('analysis-validity', '效度分析', {
    intro: '效度分析在这里主要指 KMO 与 Bartlett 球形检验，用于判断题项之间是否存在足够相关性，从而适合继续做因子分析。',
    io: [
      '输入：同一量表或同一维度下的多个题项变量，通常至少 3 个。',
      '输出：KMO 值、Bartlett 检验结果，以及对是否适合做因子分析的判断。',
    ],
    steps: [
      {
        title: '选择“效度分析”',
        text: '在问卷分析包下点击“效度分析”，进入因子分析前提检验界面。',
      },
      {
        title: '拖入量表题项',
        text: '只放入你希望一起考察结构效度的一组题项，确保变量量纲一致且缺失处理已完成。',
      },
      {
        title: '执行并查看 KMO 与 Bartlett 结果',
        text: '通常先看 KMO 是否达到常用标准，再看 Bartlett 是否显著，随后再决定是否进入探索或验证性因子分析。',
      },
    ],
    reading: [
      {
        title: 'KMO 反映抽样适切性',
        text: 'KMO 越高，说明变量之间共享方差越充分，越适合提取公共因子。',
      },
      {
        title: 'Bartlett 检验反映相关矩阵是否可分解',
        text: '如果 Bartlett 显著，通常说明变量之间并非相互独立，适合继续做因子分析。',
      },
      {
        title: '前提满足后再进入因子分析',
        text: '效度分析不是最终结构结论，而是判断“适不适合做因子分析”的前置步骤。',
      },
    ],
    formulas: [
      {
        title: 'KMO 与 Bartlett',
        latex: String.raw`$$
\mathrm{KMO}=\frac{\sum\sum r_{ij}^2}{\sum\sum r_{ij}^2+\sum\sum p_{ij}^2}
$$
$$
\chi^2 = -\left(n-1-\frac{2p+5}{6}\right)\ln|R|
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'R 示例',
        code: String.raw`items <- na.omit(df[, c("q1", "q2", "q3", "q4", "q5")])
corr_matrix <- cor(items)
inv_corr <- solve(corr_matrix)
partial <- -cov2cor(inv_corr)
diag(partial) <- 0

corr_sq <- corr_matrix ^ 2
partial_sq <- partial ^ 2
diag(corr_sq) <- 0
diag(partial_sq) <- 0
kmo <- sum(corr_sq) / (sum(corr_sq) + sum(partial_sq))

p <- ncol(corr_matrix)
chi2 <- -(nrow(items) - 1 - (2 * p + 5) / 6) * log(det(corr_matrix))`,
      },
    ],
    notice: '当前版本中，效度分析/因子分析前提检验由 R 引擎执行；请先确认生产环境已安装 R 与所需 R 包。如果 KMO 很低或 Bartlett 不显著，通常不建议直接做因子分析，应先检查题项设计、样本量和题项相关性。',
  }),
  buildAnalysisChild('analysis-pearson', '相关性分析', {
    intro: '相关性分析用于衡量两个或多个定量变量之间的线性相关程度，适合研究变量间是否同向或反向变化。',
    io: [
      '输入：2 个或以上定量变量。',
      '输出：相关系数矩阵、显著性水平，以及各变量之间关系方向与强弱的解释。',
    ],
    steps: [
      {
        title: '选择“相关性分析”',
        text: '在问卷分析包下点击该方法，进入相关矩阵分析页面。',
      },
      {
        title: '拖入需要分析的变量',
        text: '建议只放入理论上有关系、且量纲明确的定量变量，不要把完全无关的变量一股脑放进去。',
      },
      {
        title: '执行并查看相关矩阵',
        text: '重点观察相关系数的正负、绝对值大小和显著性，再判断变量关系是否符合理论预期。',
      },
    ],
    reading: [
      {
        title: '先看方向',
        text: '正相关表示一个变量升高时另一个也倾向升高，负相关则表示一高一低。',
      },
      {
        title: '再看强度',
        text: '绝对值越大，线性关系越强，但“强弱”标准需要结合学科背景理解，不能机械套用。',
      },
      {
        title: '相关不等于因果',
        text: '即使相关显著，也不能仅凭这一结果直接下因果结论，后续还需要设计或模型支持。',
      },
    ],
    formulas: [
      {
        title: 'Pearson 相关系数',
        latex: String.raw`$$
r_{xy}=\frac{\sum_{i=1}^{n}(x_i-\bar{x})(y_i-\bar{y})}{\sqrt{\sum_{i=1}^{n}(x_i-\bar{x})^2}\sqrt{\sum_{i=1}^{n}(y_i-\bar{y})^2}}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`corr = df[["support", "anxiety", "performance"]].corr(method="pearson")
print(corr)

stat, p = pearsonr(df["support"], df["anxiety"])
print("r =", round(stat, 4), "p =", round(p, 6))`,
      },
    ],
    notice: 'Pearson 更适合定量变量、线性关系和近似正态情形；如果分布严重偏态或数据为等级变量，可考虑 Spearman。',
  }),
  buildAnalysisChild('analysis-multiple-choice', '多选分析', {
    intro: '多选分析适合处理同一题目拆分成多个 0/1 选项列的场景，用来统计各选项被选择的次数和选择率。',
    io: [
      '输入：同一多选题对应的多个选项变量，通常每列表示一个选项是否被选择。',
      '输出：各选项的被选频次、被选率和排序结果。',
    ],
    steps: [
      {
        title: '选择“多选分析”',
        text: '在问卷分析包下点击“多选分析”，进入多选题汇总页面。',
      },
      {
        title: '拖入同一题目的所有选项列',
        text: '确保这些变量确实属于同一题，不同题目的选项列不要混在一起统计。',
      },
      {
        title: '执行并比较各选项热度',
        text: '查看哪些选项被选择最多，是否存在明显头部选项、冷门选项或群体偏好差异。',
      },
    ],
    reading: [
      {
        title: '先看选择频次',
        text: '频次直接反映每个选项被选中的人数，适合看“谁最常被选”。',
      },
      {
        title: '再看选择率',
        text: '选择率更适合做报告表达，尤其当样本量固定时，比绝对频次更易比较。',
      },
      {
        title: '不要把多选率相加理解成 100%',
        text: '多选题中一个人可以同时选择多个选项，因此所有选项比例之和通常会超过 100%。',
      },
    ],
    formulas: [
      {
        title: '选项被选率',
        latex: String.raw`$$
\mathrm{Rate}_j=\frac{\sum_{i=1}^{n} x_{ij}}{n}
$$`,
        text: '其中 $x_{ij}=1$ 表示第 $i$ 位受访者选择了第 $j$ 个选项。',
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`option_cols = ["opt_a", "opt_b", "opt_c", "opt_d"]
counts = df[option_cols].sum()
rates = (counts / len(df)).round(4)

result = pd.DataFrame({
    "选择频次": counts,
    "选择率": rates,
}).sort_values("选择频次", ascending=False)`,
      },
    ],
    notice: '多选分析要求各选项列编码一致。若有“是/否”“选中/未选中”混用，请先统一为 0/1 或同一规则。',
  }),
  buildAnalysisChild('analysis-survey-cross-tab', '交叉表（调研专项）', {
    intro: '交叉表（调研专项）适合问卷研究场景，除了交叉频数外，还会同步展示行百分比和列百分比，便于分析不同人群偏好差异。',
    io: [
      '输入：2 个调研类分类变量，例如人群属性题和态度题、偏好题。',
      '输出：交叉频数、行百分比、列百分比以及卡方检验结果。',
    ],
    steps: [
      {
        title: '选择“交叉表（调研专项）”',
        text: '在问卷分析包下点击该方法，进入更适合调研场景的交叉分析界面。',
      },
      {
        title: '拖入两个调研变量',
        text: '建议一个变量代表人群属性，另一个变量代表态度、偏好或行为结果，这样更容易形成有意义的解释。',
      },
      {
        title: '执行并综合查看频数与百分比',
        text: '先看交叉频数，再结合行百分比和列百分比判断不同人群是否存在明显偏好差异。',
      },
    ],
    reading: [
      {
        title: '行百分比适合看“同一人群内部怎么分布”',
        text: '如果行变量是性别，行百分比更适合看男女性别内部在某选项上的偏好差异。',
      },
      {
        title: '列百分比适合看“某选项由谁组成”',
        text: '如果列变量是偏好等级，列百分比更适合看某一偏好等级里主要由哪些人群构成。',
      },
      {
        title: '最终仍要回到卡方检验',
        text: '百分比能帮助你看结构差异，但是否达到统计学意义，还要结合卡方检验一起判断。',
      },
    ],
    formulas: [
      {
        title: '行百分比与列百分比',
        latex: String.raw`$$
\mathrm{Row\%}_{ij}=\frac{n_{ij}}{\sum_j n_{ij}},\qquad
\mathrm{Col\%}_{ij}=\frac{n_{ij}}{\sum_i n_{ij}}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`table = pd.crosstab(df["gender"], df["brand"])
row_pct = pd.crosstab(df["gender"], df["brand"], normalize="index").round(4)
col_pct = pd.crosstab(df["gender"], df["brand"], normalize="columns").round(4)
chi2, p, dof, expected = chi2_contingency(table)`,
      },
    ],
    notice: '调研专项交叉分析更适合解释问卷结构差异，但前提仍是类别设置清晰、样本数足够且各类别不宜过碎。',
  }),
  buildAnalysisChild('analysis-correspondence', '对应分析', {
    intro: '对应分析用于把两个分类变量的列联结构映射到低维空间中，帮助你观察哪些类别彼此更接近、哪些类别更远离。',
    io: [
      '输入：2 个分类变量，通常来自问卷偏好题、品牌认知题、人群细分题等。',
      '输出：类别坐标、解释维度和类别接近关系，用于做结构可视化。',
    ],
    steps: [
      {
        title: '选择“对应分析”',
        text: '在问卷分析包下点击“对应分析”，进入类别结构映射页面。',
      },
      {
        title: '拖入两个分类变量',
        text: '优先选择类别数量适中、且业务上有解释意义的两个变量，避免类别过多导致图形难以阅读。',
      },
      {
        title: '执行并查看类别坐标',
        text: '观察哪些类别在二维空间中更接近，从而判断它们在受访者回答结构上是否更相似。',
      },
    ],
    reading: [
      {
        title: '点越近，结构越相似',
        text: '在对应分析图中，两个类别点越接近，通常表示它们在联合分布结构上越相似。',
      },
      {
        title: '解释维度要结合业务语义',
        text: '坐标轴本身并不自动等于某个含义，通常需要结合变量类别特征给出解释。',
      },
      {
        title: '它更适合探索结构，不是显著性检验替代品',
        text: '对应分析可以帮助你看结构，但是否存在显著关联，仍建议结合卡方检验一起判断。',
      },
    ],
    formulas: [
      {
        title: '标准化残差矩阵',
        latex: String.raw`$$
P=\frac{N}{n},\qquad
S = D_r^{-1/2}(P-rc^\top)D_c^{-1/2}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`table = pd.crosstab(df["city"], df["brand"])
P = table / table.to_numpy().sum()
r = P.sum(axis=1).to_numpy().reshape(-1, 1)
c = P.sum(axis=0).to_numpy().reshape(1, -1)
S = (P.to_numpy() - r @ c) / np.sqrt(r @ c)

U, s, VT = np.linalg.svd(S, full_matrices=False)
row_coord = U[:, :2] * s[:2]
col_coord = VT.T[:, :2] * s[:2]`,
      },
    ],
    notice: '对应分析更适合探索类别接近结构。如果类别极少或极端不平衡，结果图形的解释价值会明显下降。',
  }),
  buildAnalysisChild('analysis-cfa', '验证性因子分析', {
    intro: '验证性因子分析用于检验你预设的量表结构是否成立，常用于问卷量表开发、结构验证和模型拟合检验。',
    io: [
      '输入：按理论结构分组后的多个题项集合，每组题项对应一个潜变量因子。',
      '输出：拟合指标、因子载荷、误差项、判别效度与模型调整建议。',
    ],
    steps: [
      {
        title: '选择“验证性因子分析”',
        text: '在问卷分析包下点击该方法，进入多因子量表结构验证界面。',
      },
      {
        title: '为每个因子分别拖入题项',
        text: '按理论维度把题项分别拖入因子槽位；如果因子数量超过初始槽位，可继续新增因子。',
      },
      {
        title: '执行并查看拟合指标',
        text: '先看 χ²/df、RMSEA、CFI、TLI 等主要拟合指标，再查看各题项载荷和判别效度结果。',
      },
    ],
    reading: [
      {
        title: '先看模型整体拟合',
        text: '如果整体拟合指标较差，说明当前结构与数据不够匹配，后续需要谨慎解释局部载荷结果。',
      },
      {
        title: '再看标准化因子载荷',
        text: '载荷越高，说明题项越能代表对应潜变量；过低载荷往往提示题项质量需要检查。',
      },
      {
        title: '最后看判别效度和修正建议',
        text: '如果因子之间重叠太强，或修正指数集中在某些误差项上，说明结构可能仍需优化。',
      },
    ],
    formulas: [
      {
        title: '测量模型',
        latex: String.raw`$$
\mathbf{x} = \Lambda \mathbf{\xi} + \mathbf{\delta}
$$`,
      },
      {
        title: '常见拟合指标',
        latex: String.raw`$$
\chi^2/df,\quad \mathrm{RMSEA},\quad \mathrm{CFI},\quad \mathrm{TLI}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'R 示例',
        text: '下面示例展示了验证性因子分析的典型写法，使用 lavaan 定义测量模型。',
        code: String.raw`library(lavaan)

model_desc <- '
Factor1 =~ q1 + q2 + q3
Factor2 =~ q4 + q5 + q6
'

fit <- cfa(model_desc, data = na.omit(df))
summary(fit, fit.measures = TRUE, standardized = TRUE)`,
      },
    ],
    notice: '当前版本中，验证性因子分析由 R 引擎执行；请先确认生产环境已安装 R 与所需 R 包。验证性因子分析高度依赖理论结构。不要把它当成“自动分组工具”，而应把它视为对既有测量模型的检验。',
  }),
  buildAnalysisChild('analysis-kano', 'Kano模型', {
    intro: 'Kano模型用于根据正向题和反向题的配对回答，把产品属性分类为魅力型、期望型、必备型、无差异型等类别。',
    io: [
      '输入：按一一对应关系整理好的正向题变量和反向题变量。',
      '输出：每个属性的 Kano 分类结果及类别分布，帮助你判断不同功能特征的优先级。',
    ],
    steps: [
      {
        title: '选择“Kano模型”',
        text: '在问卷分析包下点击“Kano模型”，进入属性分类分析页面。',
      },
      {
        title: '按顺序拖入正向题和反向题',
        text: '正向题和反向题必须一一对应，顺序不一致会导致属性分类错误。',
      },
      {
        title: '执行并查看各属性分类',
        text: '重点关注每个属性最终归入哪一类，再结合业务目标决定保留、加强还是弱化。',
      },
    ],
    reading: [
      {
        title: '必备型是底线需求',
        text: '缺少时会强烈不满，但存在时未必明显提升满意度，适合优先保障。',
      },
      {
        title: '魅力型更适合制造惊喜',
        text: '没有时用户未必介意，但一旦提供往往能明显提升满意度。',
      },
      {
        title: '分类结果要结合样本结构',
        text: '如果受访者人群差异大，Kano 结果也可能随样本构成变化，必要时可进一步做人群细分分析。',
      },
    ],
    formulas: [
      {
        title: 'Kano 分类映射',
        latex: String.raw`$$
\mathrm{Kano}(f_i,d_i)=\mathrm{Map}(f_i,d_i)
$$`,
        text: '其中 $f_i$ 为正向题回答，$d_i$ 为反向题回答，二者通过 Kano 判定表映射为 A/O/M/I/R/Q 等类别。',
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`kano_map = {
    ("喜欢", "不喜欢"): "魅力型",
    ("理应如此", "不能接受"): "必备型",
    ("期望如此", "可以忍受"): "期望型",
}

def classify_pair(func_answer, dys_answer):
    return kano_map.get((func_answer, dys_answer), "无差异型")`,
      },
    ],
    notice: 'Kano 的关键不是公式复杂，而是题目设计必须规范、正反向题必须配对正确，否则分类结果会失真。',
  }),
  buildAnalysisChild('analysis-independent-t', '独立样本T检验', {
    intro: '独立样本T检验用于比较两个独立组别在某个连续变量上的均值差异，常见于性别差异、实验组与对照组差异等问题。',
    io: [
      '输入：1 个二分类分组变量，以及 1 个或多个需要比较的定量检验变量。',
      '输出：分组描述统计、方差齐性检验、t 检验结果和效应量。',
    ],
    steps: [
      {
        title: '选择“独立样本T检验”',
        text: '在差异对比分析包下点击该方法，进入两组均值比较页面。',
      },
      {
        title: '拖入分组变量和检验变量',
        text: '分组变量必须只有 2 组，检验变量应为定量变量；如果分组变量不止 2 组，应改用方差分析。',
      },
      {
        title: '执行并查看检验表',
        text: '先看两组描述统计，再看 Levene 方差齐性检验，最后根据对应行读取 t 检验结果和 p 值。',
      },
    ],
    reading: [
      {
        title: '先看均值方向',
        text: '即使显著，也需要知道到底是哪一组更高、均值差了多少，才方便写结论。',
      },
      {
        title: '再看显著性和方差齐性',
        text: '如果方差齐性不满足，要优先读取“不等方差假定”那一行的 t 检验结果。',
      },
      {
        title: '最后看效应量',
        text: 'p 值告诉你“有没有差异”，效应量则更接近“差异有多大”，两者都要看。',
      },
    ],
    formulas: [
      {
        title: '独立样本 t 统计量',
        latex: String.raw`$$
t = \frac{\bar{x}_1-\bar{x}_2}{\sqrt{s_p^2\left(\frac{1}{n_1}+\frac{1}{n_2}\right)}}
$$`,
      },
      {
        title: 'Cohen’s d',
        latex: String.raw`$$
d=\frac{\bar{x}_1-\bar{x}_2}{s_p}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`group_a = df.loc[df["gender"] == 0, "score"].dropna()
group_b = df.loc[df["gender"] == 1, "score"].dropna()

stat, p = ttest_ind(group_a, group_b, equal_var=True)

sp = np.sqrt(((len(group_a)-1)*group_a.var(ddof=1) + (len(group_b)-1)*group_b.var(ddof=1)) / (len(group_a)+len(group_b)-2))
d = (group_a.mean() - group_b.mean()) / sp`,
      },
    ],
    notice: '独立样本T检验只适合两组比较。如果你的分组变量有 3 组及以上，请改用单因素方差分析。',
  }),
  buildAnalysisChild('analysis-paired-t', '配对样本T检验', {
    intro: '配对样本T检验用于比较同一批受试者在两个时间点、两种条件或前后测之间的均值差异。',
    io: [
      '输入：2 个一一对应的定量变量，例如前测与后测、干预前与干预后、A 条件与 B 条件。',
      '输出：配对描述统计、均值差、t 检验结果和效应量。',
    ],
    steps: [
      {
        title: '选择“配对样本T检验”',
        text: '在差异对比分析包下点击该方法，进入同一样本前后比较页面。',
      },
      {
        title: '拖入两个配对变量',
        text: '这两个变量必须来自同一批样本的一一对应测量，而不是来自两组不同人。',
      },
      {
        title: '执行并查看差值结果',
        text: '重点关注均值差的方向、t 值和 p 值，判断干预、时间或条件变化是否显著。',
      },
    ],
    reading: [
      {
        title: '先看差值方向',
        text: '要明确是前高后低，还是后高前低，差异方向决定了结论表述方式。',
      },
      {
        title: '再看显著性',
        text: '如果 p 值显著，说明同一样本在两个时点或条件下的平均水平有统计学差异。',
      },
      {
        title: '配对设计通常更敏感',
        text: '因为控制了个体差异，配对设计往往比独立样本设计更容易识别真实变化。',
      },
    ],
    formulas: [
      {
        title: '配对样本 t 统计量',
        latex: String.raw`$$
d_i = x_{1i}-x_{2i},\qquad
t = \frac{\bar{d}}{s_d/\sqrt{n}}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`before = df["pre_score"].dropna()
after = df["post_score"].dropna()
stat, p = ttest_rel(before, after)

diff = before - after
effect = diff.mean() / diff.std(ddof=1)`,
      },
    ],
    notice: '如果两列数据不是同一样本的前后测，而是两组独立个体，请不要使用配对样本T检验。',
  }),
  buildAnalysisChild('analysis-anova', '单因素方差分析', {
    intro: '单因素方差分析用于比较 3 组及以上组别在一个连续变量上的均值差异，是多组比较的经典方法。',
    io: [
      '输入：1 个分组变量（3 组及以上），以及 1 个或多个定量检验变量。',
      '输出：分组描述统计、方差分析表、F 检验结果和事后比较结果。',
    ],
    steps: [
      {
        title: '选择“单因素方差分析”',
        text: '在差异对比分析包下点击该方法，进入多组均值比较页面。',
      },
      {
        title: '拖入分组变量和检验变量',
        text: '分组变量应包含 3 组及以上，检验变量应为定量变量；如需多指标比较，可一次放入多个检验变量。',
      },
      {
        title: '设置事后比较方法',
        text: '根据需要选择 LSD、Bonferroni 或 Tukey，用于在整体差异显著后继续比较具体哪几组不同。',
      },
      {
        title: '执行并查看 ANOVA 表与事后检验',
        text: '先判断整体 F 检验是否显著，再查看事后比较定位具体差异组别。',
      },
    ],
    reading: [
      {
        title: '先看整体 F 检验',
        text: '如果整体 F 不显著，通常不再强调组间具体两两差异。',
      },
      {
        title: '再看组均值方向',
        text: '即使整体显著，也需要知道哪组更高、差异大概有多大，不能只写“存在差异”。',
      },
      {
        title: '最后看事后比较',
        text: '事后比较能明确告诉你具体是哪些组之间存在显著差异，是写结论时最常用的部分。',
      },
    ],
    formulas: [
      {
        title: 'F 统计量',
        latex: String.raw`$$
F = \frac{MS_{between}}{MS_{within}}
$$`,
      },
      {
        title: 'Eta squared',
        latex: String.raw`$$
\eta^2 = \frac{SS_{between}}{SS_{total}}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`groups = [group["score"].dropna().values for _, group in df.groupby("teaching_method")]
f_stat, p = f_oneway(*groups)

tukey = pairwise_tukeyhsd(
    endog=df["score"].dropna(),
    groups=df.loc[df["score"].notna(), "teaching_method"],
    alpha=0.05,
)`,
      },
    ],
    notice: '如果你的分组变量只有 2 组，优先使用独立样本T检验；如果是同一样本重复测量，则需要考虑配对或重复测量设计。',
  }),
  buildAnalysisChild('analysis-chi-square', '卡方检验', {
    intro: '卡方检验用于检验两个分类变量之间是否存在统计学显著关联，常见于问卷分类题、人群特征题和行为结果题分析。',
    io: [
      '输入：2 个分类变量。',
      '输出：交叉频数、卡方值、自由度、显著性和关联强度指标。',
    ],
    steps: [
      {
        title: '选择“卡方检验”',
        text: '在差异对比分析包下点击该方法，进入分类变量关联检验页面。',
      },
      {
        title: '拖入两个分类变量',
        text: '优先选择分类意义明确、类别数适中的变量。若类别极多，建议先合理合并。',
      },
      {
        title: '执行并查看卡方结果',
        text: '先浏览交叉频数，再看卡方值和 p 值，最后结合关联强度判断关系是否足够明显。',
      },
    ],
    reading: [
      {
        title: '卡方显著表示“有关联”',
        text: '它说明两个分类变量的分布不是独立的，但并不直接告诉你关系有多强。',
      },
      {
        title: '交叉表帮助解释方向',
        text: '具体是哪些类别组合更高、更低，需要回到交叉表本身去解释。',
      },
      {
        title: '显著不代表关系强',
        text: '如果样本量很大，轻微差异也可能显著，因此建议同时查看 Cramer’s V 等强度指标。',
      },
    ],
    formulas: [
      {
        title: '卡方检验',
        latex: String.raw`$$
\chi^2 = \sum_{i=1}^{r}\sum_{j=1}^{c}\frac{(O_{ij}-E_{ij})^2}{E_{ij}}
$$`,
      },
      {
        title: 'Cramer’s V',
        latex: String.raw`$$
V=\sqrt{\frac{\chi^2}{n\cdot \min(r-1,c-1)}}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`table = pd.crosstab(df["gender"], df["satisfaction_level"])
chi2, p, dof, expected = chi2_contingency(table)
cramers_v = np.sqrt(chi2 / (table.to_numpy().sum() * min(table.shape[0]-1, table.shape[1]-1)))`,
      },
    ],
    notice: '如果某些类别样本极少或理论频数过低，建议先合并类别，否则卡方检验结果可能不稳。',
  }),
  buildAnalysisChild('analysis-regression', '多元线性回归', {
    intro: '多元线性回归用于分析多个自变量对一个连续因变量的预测作用，是解释影响因素和构建预测模型的常用方法。',
    io: [
      '输入：1 个连续因变量，以及 1 个或多个定量自变量。',
      '输出：模型摘要、方程整体检验、回归系数、显著性和多重共线性信息。',
    ],
    steps: [
      {
        title: '选择“多元线性回归”',
        text: '在回归与因果分析包下点击该方法，进入回归建模界面。',
      },
      {
        title: '拖入因变量和自变量',
        text: '把要解释或预测的指标放入因变量，把可能影响它的指标放入自变量。建议先保证量纲、方向和缺失情况都已处理完毕。',
      },
      {
        title: '执行并查看模型结果',
        text: '先看模型整体是否有效，再看每个自变量的回归系数、显著性与方向。',
      },
    ],
    reading: [
      {
        title: '先看模型整体有效性',
        text: '如果整体 F 检验不显著，说明这组自变量作为整体并没有形成一个有效预测模型。',
      },
      {
        title: '再看系数方向与显著性',
        text: '系数正负表示影响方向，显著性表示这个影响是否具有统计学证据支持。',
      },
      {
        title: '最后看解释度与共线性',
        text: 'R² 告诉你模型解释了多少变异，VIF 则帮助你判断自变量之间是否过于重叠。',
      },
    ],
    formulas: [
      {
        title: '多元线性回归方程',
        latex: String.raw`$$
Y = \beta_0 + \beta_1X_1 + \beta_2X_2 + \cdots + \beta_pX_p + \varepsilon
$$`,
      },
      {
        title: '决定系数',
        latex: String.raw`$$
R^2 = 1 - \frac{SSE}{SST}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`X = sm.add_constant(df[["support", "self_efficacy", "stress"]])
y = df["anxiety"]

model = sm.OLS(y, X, missing="drop").fit()
print(model.summary())`,
      },
    ],
    notice: '如果自变量是分类变量，请先考虑做虚拟变量转换；如果变量间共线性过高，回归系数会变得不稳定。',
  }),
  buildAnalysisChild('analysis-mediation', '中介效应分析', {
    intro: '中介效应分析用于检验一个变量是否通过另一个中介变量，间接影响最终结果变量。',
    io: [
      '输入：1 个自变量 X、1 个中介变量 M、1 个因变量 Y。',
      '输出：路径回归结果、直接效应、间接效应和总效应的解释。',
    ],
    steps: [
      {
        title: '选择“中介效应分析”',
        text: '在回归与因果分析包下点击该方法，进入三变量路径检验界面。',
      },
      {
        title: '分别拖入 X、M、Y',
        text: '确保变量角色清晰：X 是前因，M 是中介路径中的传递变量，Y 是最终结果。',
      },
      {
        title: '执行并查看路径结果',
        text: '重点看 X→M、M→Y 以及 X→Y 的路径是否显著，再判断是否存在中介作用。',
      },
    ],
    reading: [
      {
        title: '先看路径是否成立',
        text: '如果关键路径本身不成立，中介解释通常也站不住脚。',
      },
      {
        title: '再看直接效应与间接效应',
        text: '如果加入中介后 X→Y 仍显著，可能是部分中介；若不再显著，则可能接近完全中介。',
      },
      {
        title: '中介分析仍然依赖理论',
        text: '统计上的中介关系并不自动等于真实因果机制，仍需结合研究设计和理论路径解释。',
      },
    ],
    formulas: [
      {
        title: '三步回归路径',
        latex: String.raw`$$
M = aX + e_1,\qquad
Y = cX + e_2,\qquad
Y = c'X + bM + e_3
$$
$$
\mathrm{IndirectEffect}=ab
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`m_model = sm.OLS(df["M"], sm.add_constant(df[["X"]]), missing="drop").fit()
y_total = sm.OLS(df["Y"], sm.add_constant(df[["X"]]), missing="drop").fit()
y_direct = sm.OLS(df["Y"], sm.add_constant(df[["X", "M"]]), missing="drop").fit()

a = m_model.params["X"]
b = y_direct.params["M"]
indirect = a * b`,
      },
    ],
    notice: '中介分析默认建立在理论路径清晰的前提上。若变量时间顺序不明确，解释时要避免把统计路径直接写成确定因果。',
  }),
  buildAnalysisChild('analysis-moderation', '调节作用', {
    intro: '调节作用用于检验某个变量 W 是否会改变自变量 X 对因变量 Y 的影响方向或影响强度。',
    io: [
      '输入：1 个自变量 X、1 个调节变量 W、1 个因变量 Y。',
      '输出：主效应、交互项效应以及调节是否成立的解释。',
    ],
    steps: [
      {
        title: '选择“调节作用”',
        text: '在回归与因果分析包下点击该方法，进入交互作用检验页面。',
      },
      {
        title: '分别拖入 X、W、Y',
        text: 'X 是主要预测变量，W 是可能改变 X 作用强度的调节变量，Y 是结果变量。',
      },
      {
        title: '执行并重点查看交互项',
        text: '调节成立与否的关键在于交互项 X×W 是否显著，而不仅仅是主效应显著。',
      },
    ],
    reading: [
      {
        title: '交互项是核心',
        text: '如果交互项不显著，通常不能认为调节效应成立。',
      },
      {
        title: '方向解释比显著更重要',
        text: '即使交互显著，也要解释“W 越高时，X 对 Y 的影响是增强了还是减弱了”。',
      },
      {
        title: '建议进一步画简单斜率图',
        text: '调节效应的最终解释往往需要配合简单斜率或分组线图，帮助读者直观看懂交互关系。',
      },
    ],
    formulas: [
      {
        title: '交互回归方程',
        latex: String.raw`$$
Y = \beta_0 + \beta_1X + \beta_2W + \beta_3(XW) + \varepsilon
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`df["XW"] = df["X"] * df["W"]
X = sm.add_constant(df[["X", "W", "XW"]])
y = df["Y"]

model = sm.OLS(y, X, missing="drop").fit()
print(model.params)`,
      },
    ],
    notice: '为了降低多重共线性的影响，调节分析前通常建议先对连续变量做中心化处理，再构造交互项。',
  }),
  buildAnalysisChild('analysis-vif', '多重共线性 VIF', {
    intro: '多重共线性 VIF 用于判断多个自变量之间是否过于相似或重叠，是回归建模前后都非常值得检查的指标。',
    io: [
      '输入：2 个或以上用于建模的定量自变量。',
      '输出：每个变量的 VIF 值，用于评估共线性风险。',
    ],
    steps: [
      {
        title: '选择“多重共线性 VIF”',
        text: '在回归与因果分析包下点击该方法，进入共线性检测界面。',
      },
      {
        title: '拖入多个自变量',
        text: '把准备进入回归模型的自变量一起拖入，通常至少需要 2 个变量才有检测意义。',
      },
      {
        title: '执行并查看各变量 VIF',
        text: '对每个变量分别查看 VIF 值，识别是否存在明显共线性风险。',
      },
    ],
    reading: [
      {
        title: 'VIF 越高，共线性越强',
        text: '较高的 VIF 说明一个变量能被其他变量较好预测，进入回归时容易导致系数不稳定。',
      },
      {
        title: '共线性会影响系数解释',
        text: '即使模型整体显著，如果共线性过强，单个系数的方向和显著性都可能变得不可靠。',
      },
      {
        title: '处理方式要结合业务意义',
        text: '常见处理包括删变量、合并变量、降维或重新定义指标，但不能只按数值机械剔除。',
      },
    ],
    formulas: [
      {
        title: '方差膨胀因子',
        latex: String.raw`$$
\mathrm{VIF}_j = \frac{1}{1-R_j^2}
$$`,
        text: '其中 $R_j^2$ 表示把第 $j$ 个自变量作为因变量、用其他自变量回归得到的决定系数。',
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`X = df[["x1", "x2", "x3"]].dropna()
X = sm.add_constant(X)

vif = pd.DataFrame({
    "variable": X.columns,
    "VIF": [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
})`,
      },
    ],
    notice: 'VIF 只是共线性的诊断工具，不应孤立使用。是否删除变量，还要结合理论意义、模型目标和替代方案一起判断。',
  }),
  buildAnalysisChild('analysis-spearman', 'Spearman 等级相关', {
    intro: 'Spearman 等级相关适用于等级变量、偏态分布变量，或两个变量之间仅满足单调关系而不满足线性关系的场景。',
    io: [
      '输入：2 个或以上变量，常用于等级变量或明显非正态的定量变量。',
      '输出：Spearman 相关系数矩阵及显著性水平。',
    ],
    steps: [
      {
        title: '选择“Spearman 等级相关”',
        text: '在数据检验分类下点击该方法，进入非参数相关分析页面。',
      },
      {
        title: '拖入需要比较的变量',
        text: '如果变量本质上是等级分或问卷等级选项，Spearman 往往比 Pearson 更合适。',
      },
      {
        title: '执行并查看相关矩阵',
        text: '重点看相关方向、强弱和显著性，并判断它是否比 Pearson 更符合你的数据特征。',
      },
    ],
    reading: [
      {
        title: '它看的是排序关系',
        text: 'Spearman 更关注变量排序是否同升同降，因此对异常值和非正态分布更稳健。',
      },
      {
        title: '解释方式与 Pearson 相似',
        text: '仍然要看方向和强度，但需要强调它描述的是等级或单调关系。',
      },
      {
        title: '不等于线性相关',
        text: '即使 Spearman 显著，也不代表变量之间一定存在严格线性关系。',
      },
    ],
    formulas: [
      {
        title: 'Spearman 相关系数',
        latex: String.raw`$$
\rho = 1 - \frac{6\sum_{i=1}^{n} d_i^2}{n(n^2-1)}
$$`,
        text: '其中 $d_i$ 表示第 $i$ 个样本在两变量秩次上的差值。',
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`corr, p = spearmanr(df[["rank_a", "rank_b", "rank_c"]].dropna())
print(corr)
print(p)`,
      },
    ],
    notice: '如果变量本身是等级变量、打分等级或明显偏态分布，Spearman 往往比 Pearson 更稳妥。',
  }),
  buildAnalysisChild('analysis-mds', '多维尺度分析', {
    intro: '多维尺度分析用于把变量或对象之间的距离关系压缩到二维空间，帮助你观察“谁更接近谁、谁更疏远谁”的结构。',
    io: [
      '输入：2 个或以上可比较结构接近性的变量。',
      '输出：二维坐标、对象间相对位置和结构接近图。',
    ],
    steps: [
      {
        title: '选择“多维尺度分析”',
        text: '在数据检验分类下点击该方法，进入结构映射分析界面。',
      },
      {
        title: '拖入需要比较结构的变量',
        text: '这些变量应具有可比较的相关或距离结构，否则二维映射很难给出有意义解释。',
      },
      {
        title: '执行并观察二维坐标',
        text: '查看哪些变量在平面上靠近，哪些明显分离，再结合变量语义理解潜在结构。',
      },
    ],
    reading: [
      {
        title: '坐标位置看相对关系，不看绝对数值',
        text: 'MDS 的重点是对象间相对远近，而不是某个坐标值本身有独立含义。',
      },
      {
        title: '距离越近，结构越相似',
        text: '如果两个变量点位很近，说明它们在整体关系结构上更接近。',
      },
      {
        title: '仍然需要回到原变量解释',
        text: 'MDS 更像一种结构可视化工具，最终解释依然要结合变量的实际含义。',
      },
    ],
    formulas: [
      {
        title: 'Stress 函数',
        latex: String.raw`$$
\mathrm{Stress} = \sqrt{\frac{\sum_{i<j}(d_{ij}-\hat{d}_{ij})^2}{\sum_{i<j}d_{ij}^2}}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`corr = df[["x1", "x2", "x3", "x4"]].corr().abs()
dist = 1 - corr

mds = MDS(n_components=2, dissimilarity="precomputed", random_state=42)
coords = mds.fit_transform(dist.values)

result = pd.DataFrame(coords, index=dist.index, columns=["Dim1", "Dim2"])`,
      },
    ],
    notice: 'MDS 更适合做结构探索和可视化表达，不适合单独承担显著性检验结论。',
  }),
  ...extraAnalysisChildren,
]
