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
      paragraphs: config.purpose || [],
    },
    {
      id: `${id}-io`,
      title: `${sectionIndex++}、输入输出描述`,
      paragraphs: config.io || [
        '输入：根据方法要求拖入一个或多个变量，并完成必要参数设置。',
        '输出：系统会生成统计结果、结构化表格和可用于报告撰写的解释说明。',
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
      points: config.reading || [],
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

  sections.push({
    id: `${id}-notice`,
    title: `${sectionIndex++}、注意事项`,
    paragraphs: Array.isArray(config.notice) ? config.notice : [config.notice || '若当前版本尚未显示该方法入口，可先将本页作为分析设计与结果说明模板。'],
  })

  return {
    id,
    title,
    pageTitle: title,
    sections,
  }
}

function buildCompositeEvalChild(id, title, metricName, extra = {}) {
  return buildAnalysisChild(id, title, {
    intro: extra.intro || `${title}用于在多指标场景下完成综合排序、赋权评价或结构识别，适合评价对象较多、指标较复杂的研究任务。`,
    io: extra.io || [
      '输入：多个用于综合评价的数值型指标，部分方法还会区分投入指标、产出指标或参考序列。',
      '输出：权重结果、综合得分、排序结果或结构层级，用于支持评价、筛选和决策。',
    ],
    steps: extra.steps || [
      { title: `选择“${title}”`, text: '进入该方法页后，先确认你的指标方向已经统一，必要时先做标准化和逆向处理。' },
      { title: '拖入评价指标', text: '把参与综合评价的指标放入对应槽位。如果方法要求分组输入，请先分清子系统或投入产出角色。' },
      { title: '执行并查看结果', text: `重点查看${metricName}，再结合排序或权重结果判断最优对象、关键指标或结构层级。` },
    ],
    reading: extra.reading || [
      { title: '先看主指标', text: `${metricName}通常是这一类方法最核心的输出，应先据此判断排序、效率或协调水平。` },
      { title: '再看权重或结构来源', text: '如果方法包含权重、层级或关联度输出，需要进一步理解结论为什么会是这样。' },
      { title: '最后回到业务解释', text: '综合评价结果最终要回到管理、资源配置、绩效比较或结构识别场景。' },
    ],
    formulas: extra.formulas || [],
    codeBlocks: extra.codeBlocks || [],
    notice: extra.notice || '执行前建议先确认所有指标方向一致、量纲可比，必要时先做标准化和正向化处理。',
  })
}

const compositeEvaluationChildren = [
  buildCompositeEvalChild('analysis-ahp-pro', '层次分析法（AHP专业版）', '权重、一致性比率和综合得分', {
    formulas: [{ title: '一致性指标', latex: String.raw`$$CI=\frac{\lambda_{\max}-n}{n-1},\quad CR=\frac{CI}{RI}$$` }],
    codeBlocks: [{ title: 'Python 示例', code: String.raw`eigvals, eigvecs = np.linalg.eig(matrix)\nweights = np.abs(eigvecs[:, np.argmax(eigvals.real)].real)\nweights = weights / weights.sum()` }],
  }),
  buildCompositeEvalChild('analysis-efa', '因子分析（探索性）', 'KMO、Bartlett 和因子载荷', {
    formulas: [{ title: '因子模型', latex: String.raw`$$x=\Lambda f+\varepsilon$$` }],
  }),
  buildCompositeEvalChild('analysis-dea', '数据包络分析', '效率值', {
    io: ['输入：一个或多个投入指标、一个或多个产出指标。', '输出：各决策单元的相对效率值和有效性判断。'],
    formulas: [{ title: 'CCR 效率思想', latex: String.raw`$$\max \ h_0=\frac{\sum_r u_r y_{r0}}{\sum_i v_i x_{i0}}$$` }],
  }),
  buildCompositeEvalChild('analysis-fuzzy', '模糊综合评价', '隶属度和综合得分', {
    formulas: [{ title: '模糊合成', latex: String.raw`$$B=W\circ R$$` }],
  }),
  buildCompositeEvalChild('analysis-topsis-new', '优劣解距离法(TOPSIS)', '贴近度', {
    formulas: [{ title: '贴近度', latex: String.raw`$$C_i=\frac{D_i^-}{D_i^++D_i^-}$$` }],
  }),
  buildCompositeEvalChild('analysis-rsr', '秩和比综合评价法(RSR)', 'RSR 值', {
    formulas: [{ title: 'RSR 公式', latex: String.raw`$$RSR_i=\frac{\sum_{j=1}^{m}R_{ij}}{mn}$$` }],
  }),
  buildCompositeEvalChild('analysis-coupling', '耦合协调度', '耦合度与协调度', {
    formulas: [{ title: '协调度', latex: String.raw`$$D=\sqrt{C\times T}$$` }],
  }),
  buildCompositeEvalChild('analysis-ahp-simple', '层次分析法（AHP简化版）', '权重和一致性比率'),
  buildCompositeEvalChild('analysis-entropy-method', '熵值法', '熵值、差异系数和权重', {
    formulas: [{ title: '熵值', latex: String.raw`$$e_j=-k\sum_i p_{ij}\ln p_{ij}$$` }],
  }),
  buildCompositeEvalChild('analysis-critic', 'CRITIC权重法', '信息量和权重', {
    formulas: [{ title: 'CRITIC 信息量', latex: String.raw`$$C_j=\sigma_j\sum_k(1-r_{jk})$$` }],
  }),
  buildCompositeEvalChild('analysis-independent-weight', '独立性权系数法', '独立性、权系数和权重'),
  buildCompositeEvalChild('analysis-cv-method', '变异系数法', '变异系数和权重', {
    formulas: [{ title: '变异系数', latex: String.raw`$$CV_j=\frac{\sigma_j}{\bar{x}_j}$$` }],
  }),
  buildCompositeEvalChild('analysis-grey', '灰色关联分析', '关联度', {
    io: ['输入：1 个参考序列和 1 个或多个比较序列。', '输出：各比较序列相对于参考序列的灰色关联度。'],
    formulas: [{ title: '灰关联系数', latex: String.raw`$$\xi_i(k)=\frac{\Delta_{\min}+\rho\Delta_{\max}}{\Delta_i(k)+\rho\Delta_{\max}}$$` }],
  }),
  buildCompositeEvalChild('analysis-vikor', '多准则妥协排序法（VIKOR）', 'S、R 和 Q 值', {
    formulas: [{ title: 'VIKOR 折中值', latex: String.raw`$$Q_i=v\frac{S_i-S^*}{S^--S^*}+(1-v)\frac{R_i-R^*}{R^--R^*}$$` }],
  }),
  buildCompositeEvalChild('analysis-ism', '解释结构模型（ISM）', '层级结构', {
    formulas: [{ title: '可达矩阵', latex: String.raw`$$R=A+I+A^2+\cdots+A^{k}$$` }],
  }),
]

const extendedStatChildren = [
  buildAnalysisChild('analysis-one-sample-t', '单样本T检验', {
    intro: '单样本T检验用于判断样本均值是否显著偏离某个理论值、标准值或目标值。',
    io: ['输入：1 个或多个定量变量，以及检验值。', '输出：t 值、p 值、均值差和置信区间。'],
    formulas: [{ title: '单样本T统计量', latex: String.raw`$$t=\frac{\bar{x}-\mu_0}{s/\sqrt{n}}$$` }],
  }),
  buildAnalysisChild('analysis-one-sample-wilcoxon', '单样本Wilcoxon符号秩检验', {
    intro: '单样本 Wilcoxon 符号秩检验适用于样本不满足正态性假设时，对给定中位数进行非参数检验。',
    io: ['输入：1 个定量变量和检验值。', '输出：Wilcoxon 统计量和显著性结果。'],
  }),
  buildAnalysisChild('analysis-paired-wilcoxon', '配对样本Wilcoxon符号秩检验', {
    intro: '配对样本 Wilcoxon 符号秩检验适用于两个配对样本的非参数比较。',
    io: ['输入：2 个配对变量。', '输出：W 值和显著性结果。'],
  }),
  buildAnalysisChild('analysis-mann-whitney', '独立样本MannWhitney检验', {
    intro: 'Mann-Whitney U 检验适用于两个独立样本的非参数比较。',
    io: ['输入：1 个二分类分组变量和 1 个检验变量。', '输出：U 值和显著性结果。'],
  }),
  buildAnalysisChild('analysis-kruskal', '多独立样本Kruskal-Wallis检验', {
    intro: 'Kruskal-Wallis 检验适用于三个及以上独立样本的非参数比较。',
    io: ['输入：1 个分组变量和 1 个检验变量。', '输出：H 值和显著性结果。'],
  }),
  buildAnalysisChild('analysis-friedman', '多配对样本Friedman检验', {
    intro: 'Friedman 检验适用于三个及以上配对样本的非参数比较。',
    io: ['输入：3 个及以上配对变量。', '输出：Friedman χ² 和显著性结果。'],
  }),
  buildAnalysisChild('analysis-gof-chi', '卡方拟合优度检验', {
    intro: '卡方拟合优度检验用于判断样本频数分布是否符合某个理论分布。',
    io: ['输入：1 个分类变量。', '输出：观测频数、理论频数和拟合优度卡方结果。'],
  }),
  buildAnalysisChild('analysis-cochrans-q', "Cochran's Q检验", {
    intro: "Cochran's Q 检验用于比较三个及以上相关样本在二分类结果上的比例差异。",
    io: ['输入：3 个及以上二分类变量。', '输出：Q 值和显著性结果。'],
  }),
  buildAnalysisChild('analysis-kappa', 'Kappa一致性检验', {
    intro: 'Kappa 一致性检验用于评估两个评价者或两次分类结果之间的一致性。',
    io: ['输入：2 个分类变量。', '输出：观察一致率和 Kappa 系数。'],
  }),
  buildAnalysisChild('analysis-kendall-consistency', 'Kendall一致性检验', {
    intro: 'Kendall 一致性检验用于评估多个评价结果之间的一致性程度。',
    io: ['输入：2 个及以上评价变量。', '输出：Kendall’s W、卡方值和显著性结果。'],
  }),
  buildAnalysisChild('analysis-icc', '组内相关系数', {
    intro: '组内相关系数用于评估多个评价者或重复测量之间的一致性和可靠性。',
    io: ['输入：2 个及以上评价变量。', '输出：ICC 和方差分析相关统计量。'],
  }),
  buildAnalysisChild('analysis-correlation-auto-solver', '相关性分析自动求解器', {
    intro: '相关性分析自动求解器用于在你不确定该用 Pearson、Spearman、Kappa、ICC 还是 Cochran’s Q 时，自动识别变量特征并给出推荐方法。',
    io: ['输入：2 个或多个待分析变量，可混合连续数值、等级变量、分类变量或二分类变量。', '输出：变量识别结果、推荐方法列表，以及首选方法的自动求解结果。'],
    steps: [
      { title: '选择“相关性分析自动求解器”', text: '先进入该方法页，把你暂时不确定该如何处理的变量一起放进来。' },
      { title: '拖入待判断变量', text: '可以一次放入多个变量，系统会自动识别是连续数值、等级变量、分类变量还是二分类变量。' },
      { title: '执行并查看推荐方法', text: '先看变量识别结果，再看推荐方法列表，最后阅读自动求解出的首选结果。' },
    ],
    reading: [
      { title: '先看识别类型', text: '自动求解器会先判断每个变量更像连续变量、等级变量还是分类变量，这一步决定后续推荐路径。' },
      { title: '再看推荐理由', text: '推荐方法不仅看变量是否数值型，也会考虑正态性、变量数量以及是否属于二分类一致性场景。' },
      { title: '自动结果适合快速起步', text: '如果你只是想先知道大概该用哪种分析，它非常方便；但正式研究仍建议回到对应专业方法页做完整分析。' },
    ],
    formulas: [
      { title: 'Pearson 相关思想', latex: String.raw`$$r=\frac{\sum(x_i-\bar{x})(y_i-\bar{y})}{\sqrt{\sum(x_i-\bar{x})^2\sum(y_i-\bar{y})^2}}$$` },
      { title: 'Spearman 等级相关思想', latex: String.raw`$$\rho = 1-\frac{6\sum d_i^2}{n(n^2-1)}$$` },
    ],
    notice: '自动求解器更适合作为“方法推荐入口”。如果你的研究目标已经非常明确，例如就是要做一致性评价或二分类重复测量检验，建议直接进入对应方法。',
  }),
  buildAnalysisChild('analysis-posthoc', '事后多重比较', {
    intro: '事后多重比较用于在方差分析显著后，进一步识别具体哪些组之间存在差异。',
    io: ['输入：1 个分组变量、多个检验变量和多重比较方法。', '输出：方差分析总表、均值对比图、两两组别差异和校正后的显著性结果。'],
  }),
  buildAnalysisChild('analysis-two-way-anova', '双因素方差分析', {
    intro: '双因素方差分析用于同时检验两个分类因素及其交互作用对因变量的影响。',
    io: ['输入：2 个分类因素、1 个因变量，可选协变量。', '输出：方差分析表、均值对比图、交叉均值表、缺失汇总和可选事后比较结果。'],
  }),
  buildAnalysisChild('analysis-three-way-anova', '三因素方差分析', {
    intro: '三因素方差分析用于同时检验三个分类因素及其交互作用对因变量的影响。',
    io: ['输入：3 个分类因素、1 个因变量，可选协变量。', '输出：方差分析表、两两均值对比图、组合均值表、缺失汇总和可选事后比较结果。'],
  }),
  buildAnalysisChild('analysis-n-way-anova', '多因素方差分析', {
    intro: '多因素方差分析用于检验多个分类因素对因变量的共同影响。',
    io: ['输入：多个分类因素和 1 个因变量。', '输出：主效应、交互作用和模型摘要。'],
  }),
  buildAnalysisChild('analysis-summary-anova', '摘要单因素方差分析', {
    intro: '摘要单因素方差分析以更简洁的方式呈现单因素方差分析的核心结果。',
  }),
  buildAnalysisChild('analysis-summary-t', '摘要T检验', {
    intro: '摘要T检验用于以更简洁的方式呈现 T 检验核心结果。',
  }),
  buildAnalysisChild('analysis-ancova', '协方差分析', {
    intro: '协方差分析用于在控制协变量影响后比较不同组之间的因变量差异。',
    io: ['输入：1 个分组变量、1 个因变量和 1 个或多个协变量。', '输出：组间效应、协变量效应和模型摘要。'],
  }),
  buildAnalysisChild('analysis-manova', '多变量方差分析', {
    intro: '多变量方差分析适用于多个因变量同时存在且彼此可能相关的组间比较场景。',
    io: ['输入：1 个分组变量和 2 个及以上因变量。', '输出：Wilks’ Lambda 等多元检验统计量。'],
  }),
  buildAnalysisChild('analysis-one-sample-equivalence', '单样本等价性检验', {
    intro: '单样本等价性检验用于判断样本均值是否在给定参考值的等价区间内。',
  }),
  buildAnalysisChild('analysis-two-sample-equivalence', '双样本等价性检验', {
    intro: '双样本等价性检验用于判断两个独立样本的均值差是否落在预设等价区间内。',
  }),
  buildAnalysisChild('analysis-paired-equivalence', '配对样本等价性检验', {
    intro: '配对样本等价性检验用于判断配对样本差值是否落在预设等价区间内。',
  }),
]

export const extraAnalysisChildren = [
  buildAnalysisChild('analysis-choice-mm', '多选-多选（交叉分析）', {
    intro: '多选-多选（交叉分析）适合同时比较两道多选题的联合选择结构，常用于产品组合、内容偏好或渠道搭配研究。',
    purpose: [
      '当两道题都是“可多选”的时候，你通常更关心哪些选项会被同一批受访者一起选中，以及哪些组合最常同时出现。',
    ],
    io: [
      '输入：两组多选题拆分后的二分类 0-1 变量，每组变量数至少为 2。',
      '输出：两组多选题各自的多重响应频率、交叉分析表、卡方检验和交叉图。',
    ],
    steps: [
      { title: '选择该分析方法', text: '先在问卷类分析目录里进入“多选-多选（交叉分析）”。' },
      { title: '分别拖入两组多选题变量', text: '每组变量都应属于同一题，且选项编码一致，避免把不同题混入同一个集合。' },
      { title: '执行并查看组合热度', text: '重点看哪些选项组合同时出现频率最高，再判断产品、功能或内容之间的搭配倾向。' },
    ],
    reading: [
      { title: '先看高频组合', text: '高频组合通常代表用户在真实选择时倾向同时拥有或同时偏好这些选项。' },
      { title: '再看组合覆盖面', text: '如果某些组合频次高但样本面很窄，需要结合总体样本规模综合判断。' },
      { title: '最后回到业务场景', text: '多选与多选的联合结构很适合用于套餐设计、推荐搭配或组合营销。' },
    ],
    formulas: [
      {
        title: '联合选择频次',
        latex: String.raw`$$
c_{ab}=\sum_{i=1}^{n} I(A_{ia}=1 \land B_{ib}=1)
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`joint = []
for a in group_a_cols:
    for b in group_b_cols:
        count = ((df[a] == 1) & (df[b] == 1)).sum()
        joint.append((a, b, count))

result = pd.DataFrame(joint, columns=["题A选项", "题B选项", "联合频次"])`,
      },
    ],
    notice: '若多选题不是拆分后的 0/1 结构，建议先做数据整理，再进行该分析。',
  }),
  buildAnalysisChild('analysis-choice-ms', '多选-单选（对比分析）', {
    intro: '多选-单选（对比分析）适合比较“不同单选人群”在多选题上的选择偏好差异。',
    purpose: [
      '典型场景是：用一道人群题或分层题做分组，再看不同组别在某道多选题上最常选择哪些选项。',
    ],
    io: [
      '输入：1 个单选题变量，以及 1 组多选题 0/1 选项列。',
      '输出：各单选组别在不同多选选项上的选择率和差异结构。',
    ],
    steps: [
      { title: '选择该分析方法', text: '进入“多选-单选（对比分析）”后，先确认哪一道题负责分组、哪一道题负责看偏好。' },
      { title: '拖入单选题与多选题', text: '把单选题放入分组区，把同一题目的多选选项列放入多选区。' },
      { title: '执行并查看组间差异', text: '关注不同组在各选项上的选择率高低，识别最典型的人群偏好差异。' },
    ],
    reading: [
      { title: '先看组内选择率', text: '组内选择率能告诉你某一人群在该多选题上最偏好什么。' },
      { title: '再看组间对比', text: '同一个多选选项在不同单选组中的差异，往往是最有解释价值的部分。' },
      { title: '适合做人群画像', text: '这类结果很适合用于用户细分、内容分层和差异化推荐。' },
    ],
    formulas: [
      {
        title: '分组选择率',
        latex: String.raw`$$
p_{ag}=\frac{\sum_{i=1}^{n} I(A_{ia}=1 \land G_i=g)}{\sum_{i=1}^{n} I(G_i=g)}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`rows = []
for group_value, part in df.groupby("gender"):
    for col in multi_cols:
        rate = part[col].mean()
        rows.append((group_value, col, rate))

result = pd.DataFrame(rows, columns=["组别", "选项", "选择率"])`,
      },
    ],
  }),
  buildAnalysisChild('analysis-choice-sm', '单选-多选（对比分析）', {
    intro: '单选-多选（对比分析）适合从单选结果出发，分析某一单选结果对应的人群在多选题上的偏好扩展。',
    purpose: [
      '与“多选&单选”相比，这个视角更适合先锁定一个单选结果变量，再观察该结果背后的人群选择画像。',
    ],
    io: [
      '输入：1 个单选题变量，以及 1 组多选题 0/1 选项列。',
      '输出：以单选结果为核心的多选偏好分布与画像差异。',
    ],
    steps: [
      { title: '选择该分析方法', text: '进入“单选-多选（对比分析）”，明确你想先看哪个单选结果。' },
      { title: '设置单选结果与多选画像变量', text: '把结果性单选题放入前位，把用来做画像的多选题选项列放入分析区。' },
      { title: '执行并读取画像结构', text: '查看不同单选结果对应的人群，在多选偏好上有哪些明显差异。' },
    ],
    reading: [
      { title: '先看单选结果分层', text: '不同单选结果往往对应不同类型的人群，先确认各组样本量是否足够。' },
      { title: '再看多选偏好画像', text: '多选题能帮助你把单选结果背后的人群特征补得更完整。' },
      { title: '适合做结果反向解释', text: '如果你先看到了某种选择结果，这类方法很适合继续追问“这群人还喜欢什么”。' },
    ],
    formulas: [
      {
        title: '结果分层下的画像比例',
        latex: String.raw`$$
p_{ga}=\frac{\sum_{i=1}^{n} I(G_i=g \land A_{ia}=1)}{\sum_{i=1}^{n} I(G_i=g)}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`profile = (
    df.groupby("purchase_level")[multi_cols]
      .mean()
      .reset_index()
)`,
      },
    ],
  }),
  buildAnalysisChild('analysis-nps', 'NPS净推荐值分析', {
    intro: 'NPS 净推荐值分析用于衡量用户推荐意愿，是品牌满意度、客户忠诚度和服务体验研究中的高频指标。',
    purpose: [
      'NPS 最常见于 0 到 10 分的推荐意愿题，通过把受访者分为推荐者、中立者和贬损者，快速得到总体口碑倾向。',
    ],
    io: [
      '输入：1 个 0-10 分推荐意愿变量。',
      '输出：推荐者比例、中立者比例、贬损者比例和 NPS 值。',
    ],
    steps: [
      { title: '选择“NPS净推荐值分析”', text: '进入方法页后，确认你的推荐题分值范围是 0-10。' },
      { title: '拖入推荐意愿变量', text: '把推荐打分题拖入分析区，并先检查异常值或非标准编码。' },
      { title: '执行并查看 NPS 结构', text: '重点关注推荐者和贬损者的比例差，以及整体 NPS 是否为正。' },
    ],
    reading: [
      { title: 'NPS 为正值通常是基本盘', text: '正值说明推荐者比例高于贬损者，但高低仍需结合行业标准判断。' },
      { title: '别只看总分', text: '推荐者、中立者、贬损者各自占比同样重要，它们决定了 NPS 的来源结构。' },
      { title: '适合继续做人群拆分', text: '把 NPS 再按地区、年龄、渠道或品牌使用年限拆开，往往更有业务价值。' },
    ],
    formulas: [
      {
        title: 'NPS 公式',
        latex: String.raw`$$
\mathrm{NPS} = (\%Promoters - \%Detractors)\times 100
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`score = df["nps_score"]
promoters = ((score >= 9) & (score <= 10)).mean()
detractors = (score <= 6).mean()
nps = (promoters - detractors) * 100`,
      },
    ],
  }),
  buildAnalysisChild('analysis-discrimination', '区分度分析', {
    intro: '区分度分析用于判断题项是否能够有效区分高水平与低水平样本，常用于量表编制和题项筛选。',
    purpose: [
      '如果一个题项无法把高分组和低分组区分开，它的测量价值通常有限，因此区分度分析很适合放在量表修订前。',
    ],
    io: [
      '输入：若干题项变量，以及可用于分组的总分或总量表分。',
      '输出：高低组差异、题项区分指数或题项相关结果。',
    ],
    steps: [
      { title: '选择“区分度分析”', text: '进入后先确认使用总分分组，还是按上 27% / 下 27% 方法分组。' },
      { title: '拖入题项与总分变量', text: '把单题变量与总分变量分别放入对应槽位，确保总分不缺失。' },
      { title: '执行并识别低区分题项', text: '重点查看哪些题项在高低组之间差异很小，或与总分关系很弱。' },
    ],
    reading: [
      { title: '区分度越高越好', text: '高分组在该题上的得分应明显高于低分组，才能说明题项有筛分能力。' },
      { title: '低区分题项要重点复核', text: '如果一个题项区分度过低，建议检查题意、方向、翻译或题目难度。' },
      { title: '不要只靠单一阈值删题', text: '删题前还要结合内容效度、信度和理论含义综合判断。' },
    ],
    formulas: [
      {
        title: '高低组区分指数',
        latex: String.raw`$$
D = \bar{X}_{high} - \bar{X}_{low}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`q27 = df["total_score"].quantile(0.27)
q73 = df["total_score"].quantile(0.73)
high = df.loc[df["total_score"] >= q73, "item1"]
low = df.loc[df["total_score"] <= q27, "item1"]

discrimination = high.mean() - low.mean()`,
      },
    ],
  }),
  buildAnalysisChild('analysis-conjoint', '联合分析', {
    intro: '联合分析用于估计用户对多个属性水平的偏好权重，帮助你理解“用户在综合权衡后更看重什么”。',
    purpose: [
      '它常用于产品配置、服务方案、套餐组合和营销方案设计，通过多个属性的联合呈现来还原真实选择情境。',
    ],
    io: [
      '输入：属性、属性水平，以及受访者对配置卡片的评分、排序或选择结果。',
      '输出：各属性水平效用值、属性重要性和推荐组合。',
    ],
    steps: [
      { title: '选择“联合分析”', text: '先确认你的实验设计已经形成属性-水平组合，并整理成分析数据表。' },
      { title: '配置属性和偏好结果', text: '把各属性列和评分/排序结果列拖入相应位置，确保实验设计编码一致。' },
      { title: '执行并查看效用结构', text: '重点关注各水平效用值和属性重要性，再反推最优产品组合。' },
    ],
    reading: [
      { title: '效用值看偏好方向', text: '某一水平的效用越高，通常表示受访者越偏好该配置。' },
      { title: '属性重要性看决策权重', text: '重要性越高，说明该属性在整体权衡中影响越大。' },
      { title: '适合模拟产品组合', text: '联合分析的核心价值不只是解释现状，更适合反推更优配置方案。' },
    ],
    formulas: [
      {
        title: '总效用',
        latex: String.raw`$$
U(x)=\sum_{j=1}^{m}\sum_{k=1}^{K_j}\beta_{jk}x_{jk}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`X = pd.get_dummies(df[["brand", "price", "capacity"]], drop_first=True)
y = df["preference_score"]

model = sm.OLS(y, sm.add_constant(X)).fit()
part_worth = model.params`,
      },
    ],
  }),
  buildAnalysisChild('analysis-path', '路径分析', {
    intro: '路径分析用于检验多个观测变量之间的直接效应和间接效应结构，是介于回归模型和 SEM 之间的一类路径建模方法。',
    purpose: [
      '当你的变量都是观测变量，且已经有较明确的路径假设时，路径分析可以比单个回归更完整地呈现变量间作用关系。',
    ],
    io: [
      '输入：多个观测变量及其预设路径结构。',
      '输出：路径系数、直接效应、间接效应和整体结构解释。',
    ],
    steps: [
      { title: '选择“路径分析”', text: '先根据理论画出变量之间的影响方向，再进入路径分析页面。' },
      { title: '配置路径结构和变量', text: '把起点变量、中间变量、终点变量依次配置好，避免路径方向填反。' },
      { title: '执行并查看路径系数', text: '先看关键路径是否显著，再回到整体路径链条解释影响过程。' },
    ],
    reading: [
      { title: '先看核心主路径', text: '优先验证理论上最关键的那条路径是否成立。' },
      { title: '再看间接通道', text: '如果中间变量路径显著，说明变量关系可能并不是简单的一步到位。' },
      { title: '路径模型重在结构解释', text: '比起单条回归，它更适合讲清楚“影响是如何层层传递的”。' },
    ],
    formulas: [
      {
        title: '路径方程',
        latex: String.raw`$$
Y = \beta_1X_1 + \beta_2X_2 + \cdots + \varepsilon
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`model_desc = """
M ~ X
Y ~ X + M
"""

model = Model(model_desc)
model.fit(df[["X", "M", "Y"]].dropna())`,
      },
    ],
  }),
  buildAnalysisChild('analysis-sem', '结构方程模型(SEM)', {
    intro: '结构方程模型（SEM）用于同时估计测量模型和结构模型，适合处理潜变量、复杂路径和理论模型检验。',
    purpose: [
      '当你的研究既关心潜变量是否被正确测量，也关心潜变量之间的路径关系时，SEM 会比单独做 CFA 或回归更完整。',
    ],
    io: [
      '输入：潜变量对应题项、潜变量之间的结构路径设定以及完整样本数据。',
      '输出：拟合指标、因子载荷、结构路径系数、直接/间接效应和模型修正信息。',
    ],
    steps: [
      { title: '选择“结构方程模型(SEM)”', text: '进入后先确认你的模型既包含测量部分，也包含结构路径部分。' },
      { title: '配置潜变量与路径关系', text: '分别指定每个潜变量的题项，以及潜变量之间的因果路径或相关关系。' },
      { title: '执行并查看整体拟合与路径结果', text: '先看拟合指标是否可接受，再解释路径系数和潜变量关系。' },
    ],
    reading: [
      { title: '先看模型是否整体站得住', text: '拟合指标不过关时，路径显著与否都要谨慎解释。' },
      { title: '再看测量与结构两层结果', text: 'SEM 既要看载荷和信效度，也要看潜变量之间的路径关系。' },
      { title: '适合理论验证型研究', text: '它非常适合用于验证既有理论框架，而不是盲目地自动找关系。' },
    ],
    formulas: [
      {
        title: 'SEM 一般形式',
        latex: String.raw`$$
\eta = B\eta + \Gamma\xi + \zeta,\qquad
x=\Lambda_x \xi + \delta,\qquad
y=\Lambda_y \eta + \varepsilon
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`model_desc = """
Eta1 =~ q1 + q2 + q3
Eta2 =~ q4 + q5 + q6
Eta2 ~ Eta1
"""

model = Model(model_desc)
model.fit(df.dropna())`,
      },
    ],
    notice: 'SEM 对样本量、模型设定和理论合理性要求都较高。如果当前版本尚未开放入口，可先把本页作为建模规划模板。',
  }),
  buildAnalysisChild('analysis-entropy-weight', '权重分析(熵权法)', {
    intro: '权重分析（熵权法）用于根据指标离散程度自动分配权重，适合多指标综合评价和客观赋权场景。',
    io: [
      '输入：多个参与综合评价的定量指标。',
      '输出：各指标权重、综合得分和对象排序结果。',
    ],
    steps: [
      { title: '选择“权重分析(熵权法)”', text: '进入后先确认所有指标方向已经统一，正向和逆向指标不要混用未处理数据。' },
      { title: '拖入评价指标', text: '把所有用于综合评价的指标一起拖入，并先处理量纲差异与缺失值。' },
      { title: '执行并查看权重结果', text: '重点观察哪些指标被赋予更高权重，再查看综合得分排序。' },
    ],
    reading: [
      { title: '离散度越大，权重通常越高', text: '熵权法会给信息量更大的指标更高权重，因此结果具有明显的数据驱动特征。' },
      { title: '适合客观赋权', text: '当你不希望完全依赖主观打分时，熵权法是一种常用的客观赋权方法。' },
      { title: '仍需结合业务判断', text: '某个指标权重低，并不代表它业务上不重要，只是当前样本中的区分信息较少。' },
    ],
    formulas: [
      {
        title: '熵值与权重',
        latex: String.raw`$$
p_{ij}=\frac{x_{ij}}{\sum_{i=1}^{n}x_{ij}},\qquad
e_j=-k\sum_{i=1}^{n}p_{ij}\ln p_{ij},\qquad
w_j=\frac{1-e_j}{\sum_{j=1}^{m}(1-e_j)}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`X = df[["x1", "x2", "x3"]].astype(float)
P = X / X.sum(axis=0)
k = 1 / np.log(len(X))
E = -(k * (P * np.log(P.replace(0, np.nan))).sum(axis=0)).fillna(0)
W = (1 - E) / (1 - E).sum()`,
      },
    ],
  }),
  buildAnalysisChild('analysis-maxdiff', 'MaxDiff模型', {
    intro: 'MaxDiff 模型用于在多个属性或选项中识别“最偏好”和“最不偏好”，适合做优先级排序和偏好强度比较。',
    io: [
      '输入：MaxDiff 任务设计数据，以及受访者在每个任务中的最喜欢/最不喜欢选择结果。',
      '输出：各选项效用值、偏好排序和相对差异结构。',
    ],
    steps: [
      { title: '选择“MaxDiff模型”', text: '先确认你的问卷已经按 MaxDiff 方式采集了最好/最差选择结果。' },
      { title: '导入任务与选择数据', text: '把每个受访者每一轮任务中看到的选项与选择结果整理为分析表。' },
      { title: '执行并查看偏好排序', text: '重点看各选项的相对效用值和最终排序，而不是只看原始被选次数。' },
    ],
    reading: [
      { title: '效用值反映相对偏好强度', text: '效用越高，说明该选项越可能被当作“最佳”；效用越低，则更接近“最差”。' },
      { title: '适合做优先级排序', text: '相比简单评分题，MaxDiff 更能拉开选项差异，排序辨识度更高。' },
      { title: '模型结果比原始频次更重要', text: '原始选中次数只是表面现象，真正推荐读取的是估计后的效用分值。' },
    ],
    formulas: [
      {
        title: 'MaxDiff 选择概率',
        latex: String.raw`$$
P_{ij}=\frac{\exp(u_j)}{\sum_{k \in C_i}\exp(u_k)}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`utility = pd.Series(index=item_names, data=0.0)
for item in item_names:
    best = (df["best_item"] == item).sum()
    worst = (df["worst_item"] == item).sum()
    utility[item] = best - worst

ranking = utility.sort_values(ascending=False)`,
      },
    ],
  }),
  buildAnalysisChild('analysis-price-breakpoint', '价格断裂点模型', {
    intro: '价格断裂点模型用于识别消费者在不同价格区间上的心理接受边界，常见于价格敏感度和定价研究。',
    io: [
      '输入：受访者关于“太便宜、便宜、贵、太贵”等价格判断数据。',
      '输出：可接受价格区间、最佳价格点和价格敏感结构。',
    ],
    steps: [
      { title: '选择“价格断裂点模型”', text: '进入后先确认你采集的是标准价格敏感度题型。' },
      { title: '拖入价格判断变量', text: '把“太便宜、便宜、贵、太贵”等价格列按顺序配置好。' },
      { title: '执行并查看价格交点', text: '重点关注最佳价格点、可接受价格区间以及价格过高/过低的边界。' },
    ],
    reading: [
      { title: '核心是看交点', text: '价格断裂点分析通常不是只看均值，而是看不同判断曲线的交点位置。' },
      { title: '适合做价格带判断', text: '它很适合帮助你判断“价格过低会被怀疑，价格过高会被拒绝”的区间。' },
      { title: '适合和品牌细分一起看', text: '不同品牌认知或不同消费层级的人群，价格断裂点通常也不同。' },
    ],
    formulas: [
      {
        title: '最佳价格点思想',
        latex: String.raw`$$
\mathrm{OPP} = \text{Intersection}(\mathrm{TooCheap},\ \mathrm{TooExpensive})
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`price_grid = np.arange(df[["too_cheap", "too_expensive"]].min().min(), df[["too_cheap", "too_expensive"]].max().max(), 1)
too_cheap_curve = [(df["too_cheap"] >= p).mean() for p in price_grid]
too_exp_curve = [(df["too_expensive"] <= p).mean() for p in price_grid]`,
      },
    ],
  }),
  buildAnalysisChild('analysis-parallel-mediation', '平行中介效应', {
    intro: '平行中介效应用于检验多个中介变量是否并行地传递自变量对因变量的影响。',
    io: [
      '输入：1 个自变量 X、多个平行中介变量 M1...Mk、1 个因变量 Y。',
      '输出：各中介路径的间接效应、总间接效应和直接效应。',
    ],
    steps: [
      { title: '选择“平行中介效应”', text: '进入后先确认多个中介变量之间是并行关系，而不是先后链式关系。' },
      { title: '配置 X、多个 M 和 Y', text: '依次放入自变量、各个中介变量和因变量，确保变量角色清晰。' },
      { title: '执行并查看各中介通道', text: '重点比较每条中介路径的大小和显著性，识别主要传导机制。' },
    ],
    reading: [
      { title: '每个中介都应单独看', text: '平行中介的重点是比较哪一条间接路径更强，而不是只看总间接效应。' },
      { title: '总效应来自多条路径叠加', text: '多个中介变量共同作用时，总间接效应往往比单一中介更复杂。' },
      { title: '适合机制对比研究', text: '它非常适合用来回答“同一个影响是通过哪几条机制同时发挥作用的”。' },
    ],
    formulas: [
      {
        title: '平行中介总间接效应',
        latex: String.raw`$$
\mathrm{IE}_{total}=a_1b_1+a_2b_2+\cdots+a_kb_k
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`indirect_1 = a1 * b1
indirect_2 = a2 * b2
total_indirect = indirect_1 + indirect_2`,
      },
    ],
  }),
  buildAnalysisChild('analysis-serial-mediation', '链式中介效应', {
    intro: '链式中介效应用于检验影响是否通过多个中介变量按顺序逐层传递到最终结果变量。',
    io: [
      '输入：1 个自变量 X、顺序中介变量链、1 个因变量 Y。',
      '输出：各路径段系数、链式间接效应和整体路径解释。',
    ],
    steps: [
      { title: '选择“链式中介效应”', text: '进入后先确认中介变量之间存在理论上的先后顺序，而不是并列关系。' },
      { title: '按链条顺序配置变量', text: '依次放入 X、M1、M2...、Y，确保中介变量顺序与你的理论模型一致。' },
      { title: '执行并查看链式路径', text: '重点看整条链式间接效应是否显著，以及哪一段路径最关键。' },
    ],
    reading: [
      { title: '顺序关系是链式模型核心', text: '如果中介变量之间没有明确顺序，链式中介的解释会很脆弱。' },
      { title: '链式效应强调逐层传递', text: '它适合回答“影响是如何一步一步传导到最终结果的”。' },
      { title: '适合机制展开型论文', text: '链式中介特别适合理论路径较完整、变量层次较清晰的研究设计。' },
    ],
    formulas: [
      {
        title: '链式中介间接效应',
        latex: String.raw`$$
\mathrm{IE}_{serial}=a_1 d_{21} b_2
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`serial_indirect = a1 * d21 * b2
print("serial indirect =", serial_indirect)`,
      },
    ],
  }),
  buildAnalysisChild('analysis-turf', 'TURF分析', {
    intro: 'TURF 分析用于寻找在给定数量限制下覆盖最多受众的选项组合，常见于产品组合、内容配置和渠道投放决策。',
    io: [
      '输入：多个可选项目的触达/选择 0/1 数据。',
      '输出：不同组合的总覆盖率、增量覆盖率和最优组合方案。',
    ],
    steps: [
      { title: '选择“TURF分析”', text: '进入后先确认你的数据已经整理成项目是否覆盖/是否被选择的 0/1 结构。' },
      { title: '拖入候选项目变量', text: '把所有候选项目一起拖入，并设置组合数量限制，例如最多选 3 个。' },
      { title: '执行并比较覆盖率', text: '重点看不同组合的总覆盖和增量贡献，识别最划算的组合。' },
    ],
    reading: [
      { title: '总覆盖率是核心指标', text: 'TURF 的目标是用有限资源覆盖尽可能多的人，而不是单看某个项目自己热不热门。' },
      { title: '增量覆盖比重复覆盖更重要', text: '如果新加入项目覆盖到的还是同一批人，它的边际价值就不高。' },
      { title: '适合组合优化', text: '非常适合用于 SKU 组合、栏目组合和触点组合优化。' },
    ],
    formulas: [
      {
        title: '组合覆盖率',
        latex: String.raw`$$
\mathrm{Reach}(S)=\frac{\left|\bigcup_{j\in S}A_j\right|}{N}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`best = None
for combo in combinations(item_cols, 3):
    reach = (df[list(combo)].sum(axis=1) > 0).mean()
    if best is None or reach > best[1]:
        best = (combo, reach)`,
      },
    ],
  }),
  buildAnalysisChild('analysis-penalty', '惩罚分析', {
    intro: '惩罚分析用于识别哪些属性表现偏低时会显著拖累总体满意度，常见于服务改进和产品优化研究。',
    io: [
      '输入：各属性表现评价变量，以及总体满意度或总体推荐意愿变量。',
      '输出：各属性的惩罚值、改进优先级和满意度下拉幅度。',
    ],
    steps: [
      { title: '选择“惩罚分析”', text: '进入后先明确哪个变量代表总体满意度，哪些变量代表属性表现。' },
      { title: '拖入满意度与属性变量', text: '把总体结果指标和各项属性评分分别放入对应区域。' },
      { title: '执行并识别高惩罚属性', text: '重点找出那些一旦表现较低，就会明显拉低总体满意度的属性。' },
    ],
    reading: [
      { title: '惩罚值越高越值得优先改进', text: '高惩罚属性通常是服务短板或核心痛点，优先修复更容易带来总体满意度提升。' },
      { title: '要结合属性现状一起看', text: '如果某属性惩罚高但当前表现已经很好，改进优先级未必高于“惩罚高且表现差”的属性。' },
      { title: '适合做问题排序', text: '它很适合把“用户最不满意什么”转成清晰的优化优先级。' },
    ],
    formulas: [
      {
        title: '惩罚值思想',
        latex: String.raw`$$
\mathrm{Penalty}_j=\bar{Y}_{high,j}-\bar{Y}_{low,j}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`high = df.loc[df["service_speed"] >= 4, "overall_sat"]
low = df.loc[df["service_speed"] <= 2, "overall_sat"]
penalty = high.mean() - low.mean()`,
      },
    ],
  }),
  buildAnalysisChild('analysis-bpto', '品牌价格抵补模型BPTO', {
    intro: '品牌价格抵补模型 BPTO 用于分析品牌偏好与价格敏感之间的权衡关系，适合研究品牌溢价和价格替代区间。',
    io: [
      '输入：品牌偏好数据、价格水平数据，以及选择或购买意愿结果。',
      '输出：品牌效用、价格效用和品牌对价格的抵补能力。',
    ],
    steps: [
      { title: '选择“品牌价格抵补模型BPTO”', text: '先确认你的数据同时包含品牌信息和价格信息，且有对应选择结果。' },
      { title: '拖入品牌、价格和结果变量', text: '分别配置品牌属性、价格属性和选择结果，以便估计品牌与价格的权衡关系。' },
      { title: '执行并查看抵补结果', text: '重点观察品牌优势能抵消多大幅度的价格上涨，以及不同品牌之间的溢价空间。' },
    ],
    reading: [
      { title: '品牌效应和价格效应要一起看', text: 'BPTO 的关键不是单看品牌喜好，而是看品牌优势能否覆盖价格劣势。' },
      { title: '适合做品牌溢价判断', text: '如果某品牌能抵补更高价格，通常说明它有更强的品牌溢价空间。' },
      { title: '适合做竞争定位', text: 'BPTO 非常适合拿来比较品牌之间的价格替代关系和竞争边界。' },
    ],
    formulas: [
      {
        title: '品牌-价格效用',
        latex: String.raw`$$
U_{bi}=\alpha_b+\beta \cdot Price_i
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`X = pd.get_dummies(df[["brand"]], drop_first=True)
X["price"] = df["price"]
y = df["choice"]

model = sm.Logit(y, sm.add_constant(X)).fit(disp=False)`,
      },
    ],
  }),
  buildAnalysisChild('analysis-cbc', '联合分析CBC', {
    intro: '联合分析 CBC 是基于选择任务的联合分析方法，适合模拟更接近真实购买决策的选择场景。',
    io: [
      '输入：选择任务设计表、属性水平组合和每轮任务的实际选择结果。',
      '输出：属性水平效用、选择概率和市场份额模拟结果。',
    ],
    steps: [
      { title: '选择“联合分析CBC”', text: '进入后先确认你的联合分析数据来自 choice-based conjoint 任务。' },
      { title: '配置属性与选择结果', text: '把各轮任务中的属性水平组合和受访者选择结果映射到同一任务表中。' },
      { title: '执行并查看效用与份额模拟', text: '重点关注水平效用值和不同方案的模拟选择概率。' },
    ],
    reading: [
      { title: 'CBC 更接近真实选择', text: '它不是让用户直接打分，而是在多个方案中做选择，因此更贴近现实购买情境。' },
      { title: '适合做市场模拟', text: 'CBC 的强项是拿来模拟不同产品组合进入市场后的相对吸引力。' },
      { title: '结果要结合任务设计解释', text: '如果实验设计不平衡或属性过多，CBC 结果解释会明显受影响。' },
    ],
    formulas: [
      {
        title: 'CBC 选择概率',
        latex: String.raw`$$
P_{ij}=\frac{\exp(U_{ij})}{\sum_{k\in C_i}\exp(U_{ik})}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`X = pd.get_dummies(task_df[["brand", "price", "package"]], drop_first=True)
y = task_df["chosen"]

model = sm.Logit(y, sm.add_constant(X)).fit(disp=False)`,
      },
    ],
  }),
  buildAnalysisChild('analysis-maxdiff-pro', 'MaxDiff Pro', {
    intro: 'MaxDiff Pro 可以理解为更强调个体层效用恢复和高级模拟能力的 MaxDiff 扩展分析，适合精细化偏好排序。',
    io: [
      '输入：标准 MaxDiff 任务数据，以及需要做个体层细分或高级模拟的样本数据。',
      '输出：个体层偏好分数、群体细分排序和进阶模拟结果。',
    ],
    steps: [
      { title: '选择“MaxDiff Pro”', text: '进入后先确认你不仅需要总体排序，还希望看到更细的个体层差异。' },
      { title: '导入完整任务数据', text: '把每个受访者在每轮任务中的曝光项、最佳项和最差项一并整理导入。' },
      { title: '执行并查看个体层偏好', text: '重点看不同人群、不同个体在偏好结构上的差异，而不只是总体平均排序。' },
    ],
    reading: [
      { title: '更强调个体层差异', text: 'MaxDiff Pro 的价值通常不在总体排序，而在细分人群甚至个体层面的偏好恢复。' },
      { title: '适合高级分群', text: '如果你要基于偏好做聚类、定制推荐或差异化投放，这类结果非常有用。' },
      { title: '数据质量要求更高', text: '因为模型更细，任务设计质量和样本量对结果稳定性的影响也更大。' },
    ],
    formulas: [
      {
        title: '个体层效用思想',
        latex: String.raw`$$
u_{ij}=\mu_j+v_{ij}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 示例',
        code: String.raw`individual_scores = raw_maxdiff.groupby(["resp_id", "item"]).agg(
    best=("is_best", "sum"),
    worst=("is_worst", "sum"),
)
individual_scores["score"] = individual_scores["best"] - individual_scores["worst"]`,
      },
    ],
    notice: '如果当前版本尚未开放 MaxDiff Pro 入口，可先把本页作为题型设计、结果解读和后续功能说明模板。',
  }),
  ...extendedStatChildren,
  ...compositeEvaluationChildren,
]
