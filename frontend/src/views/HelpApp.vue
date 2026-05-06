<template>
  <div class="help-page">
    <header class="help-topbar">
      <a href="/" class="help-brand">
        <img src="/logo.png" alt="spssgo" />
      </a>

      <nav class="help-topnav" aria-label="顶部导航">
        <a href="/about">产品介绍</a>
        <a href="/help" class="active">帮助中心</a>
      </nav>

      <div class="help-topbar-actions">
        <a class="help-login-btn" href="/login?redirect=%2Fworkspace">进入工作台</a>
      </div>
    </header>

    <div class="help-shell">
      <aside class="help-sidebar">
        <div class="help-sidebar-title">帮助分类</div>
        <div v-for="group in helpGroups" :key="group.id" class="help-sidebar-group">
          <button
            class="help-sidebar-item"
            :class="{ active: currentGroupId === group.id && !activeChildId }"
            type="button"
            @click="activateGroup(group.id)"
          >
            <span>{{ group.title }}</span>
            <span
              class="help-sidebar-arrow"
              :class="{ 'help-sidebar-arrow--empty': !group.children?.length }"
            >
              {{ group.children?.length ? '⌄' : '' }}
            </span>
          </button>

          <div v-if="group.children?.length && expandedGroupId === group.id" class="help-sidebar-children">
            <button
              v-for="child in group.children"
              :key="child.id"
              class="help-sidebar-child"
              :class="{ active: activeDocId === child.id }"
              type="button"
              @click="activateDoc(group.id, child.id)"
            >
              {{ child.title }}
            </button>
          </div>
        </div>
      </aside>

      <main class="help-main">
        <div class="help-main-head">
          <button class="help-menu-btn" type="button" @click="sidebarOpen = !sidebarOpen">
            ☰
          </button>
          <div>
            <p class="help-breadcrumb">帮助中心 / {{ activeGroup.title }}<span v-if="activeDoc.id !== activeGroup.id"> / {{ activeDoc.title }}</span></p>
            <h1>{{ activeDoc.pageTitle || activeDoc.title }}</h1>
          </div>
        </div>

        <div class="help-mobile-sidebar" :class="{ open: sidebarOpen }">
          <template v-for="group in helpGroups" :key="group.id">
            <button
              class="help-mobile-sidebar-item"
              :class="{ active: currentGroupId === group.id && !activeChildId }"
              type="button"
              @click="activateGroup(group.id, true)"
            >
              {{ group.title }}
            </button>
            <button
              v-for="child in group.children || []"
              :key="child.id"
              class="help-mobile-sidebar-item help-mobile-sidebar-item--child"
              :class="{ active: activeDocId === child.id }"
              type="button"
              @click="activateDoc(group.id, child.id, true)"
            >
              {{ child.title }}
            </button>
          </template>
        </div>

        <div class="help-content-layout">
          <article class="help-article">
            <section
              v-for="section in activeDoc.sections"
              :key="section.id"
              :id="section.id"
              class="help-section"
            >
              <div class="help-section-head">
                <h2>{{ section.title }}</h2>
                <p v-if="section.intro">{{ section.intro }}</p>
              </div>

              <div v-if="section.paragraphs?.length" class="help-paragraphs">
                <p v-for="text in section.paragraphs" :key="text">{{ text }}</p>
              </div>

              <div v-if="section.points?.length" class="help-point-list">
                <div v-for="point in section.points" :key="point.title" class="help-point-card">
                  <h3>{{ point.title }}</h3>
                  <p>{{ point.text }}</p>
                </div>
              </div>

              <div v-if="section.steps?.length" class="help-step-list">
                <div v-for="(step, index) in section.steps" :key="step.title" class="help-step-card">
                  <div class="help-step-index">{{ index + 1 }}</div>
                  <div class="help-step-content">
                    <h3>{{ step.title }}</h3>
                    <p>{{ step.text }}</p>
                    <div v-if="step.screenshot" class="help-step-shot">
                      <div class="help-step-shot-head">{{ step.screenshot.title || '截图占位' }}</div>
                      <div class="help-step-shot-box">
                        <span>待补充截图</span>
                      </div>
                      <p class="help-step-shot-note">{{ step.screenshot.hint || '后续可在此处补充当前步骤的界面截图。' }}</p>
                    </div>
                  </div>
                </div>
              </div>

              <div v-if="section.qa?.length" class="help-qa-list">
                <div v-for="item in section.qa" :key="item.q" class="help-qa-card">
                  <h3>{{ item.q }}</h3>
                  <p>{{ item.a }}</p>
                </div>
              </div>

              <div v-if="section.formulas?.length" class="help-formula-list">
                <div v-for="formula in section.formulas" :key="formula.title" class="help-formula-card">
                  <h3>{{ formula.title }}</h3>
                  <p v-if="formula.text">{{ formula.text }}</p>
                  <div class="help-formula-block">
                    <FormulaBlock :formula="formula.latex" />
                  </div>
                </div>
              </div>

              <div v-if="section.codeBlocks?.length" class="help-code-list">
                <div v-for="block in section.codeBlocks" :key="block.title" class="help-code-card">
                  <p v-if="block.text">{{ block.text }}</p>
                  <div class="help-code-block">
                    <CodeBlock :code="block.code" language="Python" />
                  </div>
                </div>
              </div>
            </section>
          </article>

          <aside class="help-outline">
            <a class="help-feedback-btn" href="mailto:jahe@jahe.top">建议反馈</a>
            <div class="help-outline-card">
              <a
                v-for="section in activeDoc.sections"
                :key="section.id"
                class="help-outline-link"
                :href="`#${section.id}`"
              >
                {{ section.title }}
              </a>
            </div>
          </aside>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import FormulaBlock from '../components/common/FormulaBlock.vue'
import CodeBlock from '../components/common/CodeBlock.vue'
import { analysisChildren } from '../data/helpAnalysisDocs'

function buildParagraphSections(helpText) {
  const parts = String(helpText || '')
    .split('\n')
    .map(text => text.trim())
    .filter(Boolean)

  const intro = parts[0] || ''
  const notice = parts.find(text => text.startsWith('注意：')) || ''

  return {
    intro,
    details: parts.filter(text => text !== intro && text !== notice),
    notice: notice.replace(/^注意：/, ''),
  }
}

function buildProcessingChild(id, title, helpText, extras = {}) {
  const parsed = buildParagraphSections(helpText)
  const sections = [
    {
      id: `${id}-purpose`,
      title: '1、作用',
      intro: parsed.intro || `${title}用于帮助你完成对应的数据整理任务。`,
      paragraphs: extras.purpose || parsed.details.slice(0, 1),
    },
    {
      id: `${id}-io`,
      title: '2、输入输出描述',
      paragraphs: extras.io || [
        extras.input || '输入：根据方法要求选择一个或多个变量，并完成必要参数设置。',
        extras.output || '输出：系统会在当前数据集中生成处理后的结果，或直接对原数据执行清洗与转换。',
      ],
    },
    {
      id: `${id}-usage`,
      title: '3、使用说明',
      points: extras.usage || [
        {
          title: '适用场景',
          text: parsed.details[0] || '适合在正式分析前先整理数据结构、提升数据质量或把变量转换成更适合建模的形式。',
        },
        {
          title: '操作建议',
          text: extras.tip || '先确认变量类型和缺失情况，再执行方法；处理完成后建议立即查看预览结果，确认变量是否按预期变化。',
        },
      ],
    },
  ]

  if (extras.formulas?.length) {
    sections.push({
      id: `${id}-formula`,
      title: '4、计算公式',
      formulas: extras.formulas,
    })
  }

  if (extras.codeBlocks?.length) {
    sections.push({
      id: `${id}-code`,
      title: extras.formulas?.length ? '5、程序实现' : '4、程序实现',
      codeBlocks: extras.codeBlocks,
    })
  }

  sections.push({
    id: `${id}-notice`,
    title: extras.formulas?.length || extras.codeBlocks?.length ? '6、注意事项' : '4、注意事项',
    paragraphs: [
      parsed.notice || extras.notice || '执行前请留意页面中的变量限制、参数范围和输出方式，避免处理结果与分析目标不一致。',
    ],
  })

  return {
    id,
    title,
    pageTitle: title,
    sections,
  }
}

const processingChildren = [
  buildProcessingChild('processing-label', '数据标签', '数据标签用于给分类编码绑定文字含义，适合性别、地区、学历、量表选项这类定类变量。它只影响展示，不改变原始数据和统计计算结果。\n定量变量本身已经有实际数值意义，比如年龄、收入、分数，因此不支持通过“数据标签”来处理。', {
    io: [
      '输入：1 个定类变量，以及每个编码值对应的文字标签。',
      '输出：变量本身数值不变，但在展示和结果阅读时可直接看到更易理解的标签文字。',
    ],
    tip: '如果你的分类变量当前是 1、2、3 这类编码，但希望结果显示为“男/女”“低/中/高”，就应该先做数据标签。',
    formulas: [
      {
        title: '标签映射',
        latex: `$$
f(v)=\\mathrm{label\\_map}(v)
$$
$$
v \\in \\{1,2,3,\\dots\\} \\mapsto \\{\\text{低},\\text{中},\\text{高},\\dots\\}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 算法片段',
        code: `def handle(df, variables, params):
    from backend.services.variable_metadata_service import infer_variable_type

    if not variables:
        return df, '处理完成'

    col = variables[0]
    if col not in df.columns:
        raise ValueError(f'变量 {col} 不存在')

    var_type = infer_variable_type(df[col], col)
    if var_type != 'categorical':
        raise ValueError('数据标签仅支持定类变量')

    label_map = {
        str(k): v for k, v in (params.get('label_map', {}) or {}).items()
        if v not in ('', None)
    }
    if not label_map:
        return df, '未设置标签，原数据保持不变'

    # 数据标签只更新展示层元数据，不修改底层原始数据
    return df, f'已为变量 {col} 保存数据标签'`,
      },
    ],
  }),
  buildProcessingChild('processing-encode', '数据编码', '将变量数值再次进行编码，可进一步浓缩或整合原始数据。支持新编码、范围编码和自动分组。新编码适合逐值重编码，范围编码适合按数值区间合并，自动分组适合按均值或分位数快速生成分组变量。输入为一项定量或定类变量，输出为对变量各取值重新编码后的结果。', {
    io: [
      '输入：1 个定量变量或定类变量，并选择新编码、范围编码或自动分组等方式。',
      '输出：生成重新编码后的变量结果，可用于后续分组比较、交叉分析或建模。',
    ],
    tip: '如果原始数据过细、不便分析，或你想把连续变量分成几个等级区间，通常可以先做数据编码。',
    formulas: [
      {
        title: '均值 2 组',
        latex: `$$
\\bar{x} = \\frac{1}{n}\\sum_{i=1}^{n}x_i,\\quad
\\mathrm{code}(x)=
\\begin{cases}
1, & x < \\bar{x} \\\\
2, & x \\ge \\bar{x}
\\end{cases}
$$`,
      },
      {
        title: '中位数 2 组',
        latex: `$$
Q_{0.5}=\\mathrm{median}(x),\\quad
\\mathrm{code}(x)=
\\begin{cases}
1, & x \\le Q_{0.5} \\\\
2, & x > Q_{0.5}
\\end{cases}
$$`,
      },
      {
        title: '区间编码',
        latex: `$$
\\mathrm{code}(x)=c_j,\\quad \\text{当 } x\\in [a_j,b_j)
$$`,
      },
      {
        title: '27% / 73% 三分组',
        latex: `$$
q_{27}=Q_{0.27}(x),\\quad q_{73}=Q_{0.73}(x)
$$
$$
\\mathrm{code}(x)=
\\begin{cases}
1, & x<q_{27} \\\\
2, & q_{27}\\le x\\le q_{73} \\\\
3, & x>q_{73}
\\end{cases}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 算法片段',
        code: `def handle(df, variables, params):
    col = variables[0]
    mode = params.get('mode', 'new')
    auto_strategy = params.get('auto_strategy', 'mean_2')

    series = df[col]
    numeric = pd.to_numeric(series, errors='coerce')
    valid = numeric.dropna()
    encoded = pd.Series(pd.NA, index=df.index, dtype='Int64')

    if mode == 'auto':
        if auto_strategy == 'mean_2':
            mean_val = valid.mean()
            encoded.loc[numeric < mean_val] = 1
            encoded.loc[numeric >= mean_val] = 2
        elif auto_strategy == 'median_2':
            median_val = valid.quantile(0.5)
            encoded.loc[numeric <= median_val] = 1
            encoded.loc[numeric > median_val] = 2
        elif auto_strategy == 'quantile_27_73':
            q27 = valid.quantile(0.27)
            q73 = valid.quantile(0.73)
            encoded.loc[numeric < q27] = 1
            encoded.loc[(numeric >= q27) & (numeric <= q73)] = 2
            encoded.loc[numeric > q73] = 3

    df[f'{col}_encoded'] = encoded
    return df, '数据编码完成'`,
      },
    ],
  }),
  buildProcessingChild('processing-outlier', '异常值处理', '异常值处理用于识别并排除偏离整体数据分布或超出合理范围的数据点。支持 3σ、IQR、MAD 三种自动识别方式，也支持自定义范围识别。输入为一项或多项定量变量，输出为将异常值置空，或将异常值填补为其它有效值。\n注意：异常值处理不支持含空值变量，请先完成缺失值处理；多列处理中各列独立判断、互不影响。', {
    io: [
      '输入：1 个或多个无空值定量变量，选择异常识别规则和处理动作。',
      '输出：异常值会被置空、替换，或按规则进行处理，帮助后续分析更稳健。',
    ],
    formulas: [
      {
        title: '3σ 规则',
        latex: `$$
\\mu = \\frac{1}{n}\\sum_{i=1}^{n}x_i,\\quad
\\sigma = \\sqrt{\\frac{1}{n-1}\\sum_{i=1}^{n}(x_i-\\mu)^2}
$$
$$
x \\text{ 为异常值 } \\iff x < \\mu - 3\\sigma \\;\\text{ 或 }\\; x > \\mu + 3\\sigma
$$`,
      },
      {
        title: 'IQR 规则',
        latex: `$$
IQR = Q_3 - Q_1
$$
$$
x \\text{ 为异常值 } \\iff x < Q_1 - 1.5IQR \\;\\text{ 或 }\\; x > Q_3 + 1.5IQR
$$`,
      },
      {
        title: 'MAD 规则',
        latex: `$$
\\mathrm{MAD} = 1.4826 \\cdot \\mathrm{median}(|x_i-\\mathrm{median}(x)|)
$$
$$
x \\text{ 为异常值 } \\iff |x-\\mathrm{median}(x)| > 3\\cdot \\mathrm{MAD}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 算法片段',
        code: `def handle(df, variables, params):
    detect = params.get("detect", "auto")
    outlier_method = params.get("method", "3sigma")
    action = params.get("action", "null")
    replace_with = params.get("replace_with", "")

    for col in variables:
        s = pd.to_numeric(df[col], errors="coerce")

        if detect == "auto":
            if outlier_method == "3sigma":
                mu, sigma = s.mean(), s.std()
                mask = (s < mu - 3 * sigma) | (s > mu + 3 * sigma)
            elif outlier_method == "iqr":
                q1, q3 = s.quantile(0.25), s.quantile(0.75)
                iqr = q3 - q1
                mask = (s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)
            elif outlier_method == "mad":
                med = s.median()
                mad = (s - med).abs().median() * 1.4826
                mask = (s - med).abs() > 3 * mad
            else:
                mask = pd.Series(False, index=s.index)
        else:
            lo = float(params.get("min_val"))
            hi = float(params.get("max_val"))
            mask = (s < lo) | (s > hi)

        if action == "null":
            df.loc[mask, col] = np.nan
        elif action == "replace":
            clean = s[~mask]
            rv = clean.mean() if replace_with == "mean" else clean.median()
            df.loc[mask, col] = rv

    return df, "异常值处理完成"`,
      },
    ],
  }),
  buildProcessingChild('processing-invalid-sample', '无效样本处理', '无效样本处理用于对整行样本进行识别与管理，目的是排除重复、无效样本，使分析数据更符合研究预期。支持“相同数据出现 XX% 及以上”与“缺失比例出现 XX% 及以上”两类规则。输入为两项或以上的定量或定类变量，输出为删除无效样本，或生成标记变量（1 有效，0 无效）。\n注意：对于“相同数据出现 XX% 及以上”的识别，若变量为定类变量，实际上识别的是相同编码出现的比例，通常不建议直接对定类变量使用此规则。', {
    io: [
      '输入：至少 2 个变量，并设置无效识别规则，如重复比例、缺失比例等。',
      '输出：系统会删除无效样本，或新增一列有效/无效标记变量。',
    ],
    formulas: [
      {
        title: '相同数据比例判定',
        latex: `$$
r_i = \\frac{\\max_c n_{ic}}{m_i}
$$
$$
\\text{样本 } i \\text{ 无效} \\iff r_i \\ge \\tau
$$`,
        text: '其中，$m_i$ 表示该样本当前参与判断的非空变量个数，$n_{ic}$ 表示样本中某一取值出现的次数，$\\tau$ 为阈值。',
      },
      {
        title: '缺失比例判定',
        latex: `$$
q_i = \\frac{\\#\\{x_{ij}\\text{ 为缺失}\\}}{p}
$$
$$
\\text{样本 } i \\text{ 无效} \\iff q_i \\ge \\eta
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 算法片段',
        code: `def handle(df, variables, params):
    cols = [col for col in variables if col in df.columns]
    subset = df[cols]
    invalid_mask = pd.Series(False, index=df.index)

    if params.get("same_digit", False):
        pct = params.get("same_digit_pct", 80) / 100.0
        for idx, row in subset.iterrows():
            vals = row.dropna()
            if len(vals) > 0:
                most_common_count = vals.value_counts().iloc[0]
                if most_common_count / len(vals) >= pct:
                    invalid_mask.loc[idx] = True

    if params.get("missing", False):
        mpct = params.get("missing_pct", 50) / 100.0
        missing_ratio = subset.isna().sum(axis=1) / len(cols)
        invalid_mask = invalid_mask | (missing_ratio >= mpct)

    if params.get("action", "mark") == "delete":
        df = df.loc[~invalid_mask].reset_index(drop=True)
    else:
        df.insert(0, "valid_flag", (~invalid_mask).astype(int))

    return df, "无效样本处理完成"`,
      },
    ],
  }),
  buildProcessingChild('processing-generate', '生成变量', '生成变量用于按照表达式或已有变量关系，快速构造一个新的分析变量。适合计算总分、均值、差值、比值或其他派生指标。', {
    io: [
      '输入：选择基础变量，填写新变量名称和生成表达式。',
      '输出：系统新增一个计算后的变量，供后续统计分析继续使用。',
    ],
    notice: '建议先确认公式逻辑和变量单位一致，再生成新变量，避免新指标含义错误。',
    formulas: [
      {
        title: '表达式生成',
        latex: `$$
y = g(x_1,x_2,\\dots,x_p)
$$`,
        text: '这里的 $g(\\cdot)$ 可以是四则运算，也可以是 log、sqrt、abs、mean、sum 等函数组合。',
      },
    ],
    codeBlocks: [
      {
        title: 'Python 算法片段',
        code: `def handle(df, variables, params):
    name = params.get('name', 'new_var')
    expr = params.get('expr', '')
    if not expr:
        return df, '处理完成'

    local_vars = {col: df[col] for col in df.columns}
    local_vars.update({
        'log': np.log,
        'sqrt': np.sqrt,
        'abs': np.abs,
        'mean': np.mean,
        'sum': np.sum,
        'np': np,
        'pd': pd,
    })

    try:
        df[name] = eval(expr, {"__builtins__": {}}, local_vars)
    except Exception as e:
        raise ValueError(f'公式计算错误: {str(e)}') from e

    return df, f'已生成新变量 {name}'`,
      },
    ],
  }),
  buildProcessingChild('processing-balance', '样本均衡', '样本均衡用于处理分类任务中因变量不同类别样本数量不均衡的问题。支持过采样、欠采样和组合采样三种方式，使不同类别样本数量尽量接近。\n注意：样本均衡不支持含空值变量，请先完成缺失值处理。', {
    io: [
      '输入：选择参与建模的变量，并指定一个定类目标变量作为均衡对象。',
      '输出：系统会按均衡策略调整不同类别样本数量，使训练数据分布更接近。',
    ],
    formulas: [
      {
        title: '过采样',
        latex: `$$
n_k' = \\max_j n_j
$$`,
      },
      {
        title: '欠采样',
        latex: `$$
n_k' = \\min_j n_j
$$`,
      },
      {
        title: '组合采样',
        latex: `$$
n_k' = \\mathrm{round}\\left(\\frac{1}{K}\\sum_{j=1}^{K} n_j\\right)
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 算法片段',
        code: `def _oversample_frame(df, target):
    counts = df[target].value_counts()
    max_count = counts.max()
    frames = []
    for val, count in counts.items():
        subset = df[df[target] == val]
        if count < max_count:
            frames.append(subset.sample(n=max_count, replace=True, random_state=42))
        else:
            frames.append(subset)
    return pd.concat(frames, ignore_index=True)

def _undersample_frame(df, target):
    counts = df[target].value_counts()
    min_count = counts.min()
    frames = [df[df[target] == val].sample(n=min_count, random_state=42) for val in counts.index]
    return pd.concat(frames, ignore_index=True)`,
      },
    ],
  }),
  buildProcessingChild('processing-winsorize', '缩尾/截尾处理', '缩尾/截尾处理用于对连续变量尾部极端值进行处理。缩尾会把超出指定百分位范围的值替换为对应分位数；截尾可选择仅将极端值置空，或删除极端值所在整行样本。\n注意：缩尾/截尾处理不支持含空值变量，请先完成缺失值处理；多列处理中各列独立处理、互不影响。', {
    io: [
      '输入：1 个或多个无空值定量变量，并设置百分位阈值和处理方式。',
      '输出：连续变量尾部的极端值会被缩尾、置空或整行删除。',
    ],
    formulas: [
      {
        title: '分位点阈值',
        latex: `$$
l = Q_p(x),\\quad h = Q_{1-p}(x)
$$`,
      },
      {
        title: '缩尾处理',
        latex: `$$
x'=
\\begin{cases}
l, & x<l \\\\
x, & l \\le x \\le h \\\\
h, & x>h
\\end{cases}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 算法片段',
        code: `def handle(df, variables, params):
    mode = params.get("mode", "winsorize")
    trim_action = params.get("trim_action", "null")
    pct = params.get("percent", 5) / 100.0
    row_delete_mask = pd.Series(False, index=df.index)

    for col in variables:
        s = pd.to_numeric(df[col], errors="coerce")
        lo = s.quantile(pct)
        hi = s.quantile(1 - pct)
        extreme_mask = (s < lo) | (s > hi)

        if mode == "winsorize":
            df[col] = s.clip(lo, hi)
        elif trim_action == "null":
            df.loc[extreme_mask, col] = pd.NA
        else:
            row_delete_mask = row_delete_mask | extreme_mask

    if mode == "trim" and trim_action == "row_delete":
        df = df.loc[~row_delete_mask].reset_index(drop=True)

    return df, "缩尾/截尾处理完成"`,
      },
    ],
  }),
  buildProcessingChild('processing-sliding-window', '时序数据滑窗转换', '时序数据滑窗转换用于将单一时间序列转换为可用于回归建模的数据。设定步阶后，系统会用前 N 个历史数据作为自变量 X1~XN，用当前值作为因变量 Y，从而将时间序列预测问题转换为监督学习问题。\n注意：时序数据滑窗转换仅支持 1 个无空值定量变量；转换后前几行会因凑不够前序窗口而为空，建模前不要直接对这些空行做数据填补。', {
    io: [
      '输入：1 个无空值定量时间序列变量，并设定滑窗步阶。',
      '输出：原时间序列会被转换为带有历史窗口特征的数据表，用于回归或预测建模。',
    ],
    formulas: [
      {
        title: '滑窗监督学习构造',
        latex: `$$
X_1(t)=y_{t-n},\\;X_2(t)=y_{t-n+1},\\;\\ldots,\\;X_n(t)=y_{t-1},\\;Y(t)=y_t
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 算法片段',
        code: `def handle(df, variables, params):
    window_size = int(params.get("window_size", 3))
    col = variables[0]
    s = pd.to_numeric(df[col], errors="coerce")
    result = df.copy()

    for step in range(1, window_size + 1):
        result[f"X{step}"] = s.shift(window_size - step + 1)

    result["Y"] = s
    return result, f"滑窗转换完成（步阶={window_size}）"`,
      },
    ],
  }),
  buildProcessingChild('processing-dummy', '虚拟变量转换', '虚拟变量转换用于将无序定类变量转换为可参与回归或机器学习建模的数值型变量。支持独热编码和哑变量化两种形式。\n注意：虚拟变量转换仅支持 1 个无空值定类变量。独热编码会为每个类别生成一个 0/1 变量；哑变量化会少一列，未生成的那一类作为参照项。', {
    io: [
      '输入：1 个无空值定类变量，并选择独热编码或哑变量化方式。',
      '输出：系统会生成若干列 0/1 变量，让原始分类信息可以进入回归或机器学习模型。',
    ],
    formulas: [
      {
        title: '独热编码',
        latex: `$$
d_{ik}=
\\begin{cases}
1, & x_i = c_k \\\\
0, & x_i \\ne c_k
\\end{cases}
$$`,
      },
      {
        title: '哑变量化',
        latex: `$$
\\{d_{i1},d_{i2},\\dots,d_{i(K-1)}\\}
$$`,
        text: '哑变量化会少保留一列，未生成的那一类作为参照组。',
      },
    ],
    codeBlocks: [
      {
        title: 'Python 算法片段',
        code: `def handle(df, variables, params):
    mode = params.get("mode", "dummy")
    col = variables[0]

    if mode == "dummy":
        dummies = pd.get_dummies(df[col], prefix=col, drop_first=True)
    else:
        dummies = pd.get_dummies(df[col], prefix=col, drop_first=False)

    df = df.drop(columns=[col])
    df = pd.concat([df, dummies.astype(int)], axis=1)
    return df, "虚拟变量转换完成"`,
      },
    ],
  }),
  buildProcessingChild('processing-feature-select', '特征筛选', '特征筛选用于从多个候选特征中识别更有效的变量。它会在变量名后标明“应保留”或“应剔除”，适合特征较多、希望减少噪声和过拟合风险的场景。', {
    io: [
      '输入：多个候选特征变量，并按不同筛选方法设置目标变量或阈值。',
      '输出：系统会给出保留/剔除建议，帮助你缩小特征集。',
    ],
    notice: '特征筛选结果更适合做辅助判断，不建议脱离业务背景或研究假设机械删除变量。',
    formulas: [
      {
        title: '方差筛选',
        latex: `$$
\\mathrm{Var}(X_j)=\\frac{1}{n-1}\\sum_{i=1}^{n}(x_{ij}-\\bar{x}_j)^2
$$`,
      },
      {
        title: 'Pearson 相关系数',
        latex: `$$
r_{X_j,Y}=\\frac{\\sum_{i=1}^{n}(x_{ij}-\\bar{x}_j)(y_i-\\bar{y})}
{\\sqrt{\\sum_{i=1}^{n}(x_{ij}-\\bar{x}_j)^2}\\sqrt{\\sum_{i=1}^{n}(y_i-\\bar{y})^2}}
$$`,
      },
      {
        title: 'VIF',
        latex: `$$
\\mathrm{VIF}_j = \\frac{1}{1-R_j^2}
$$`,
      },
      {
        title: '互信息',
        latex: `$$
I(X;Y)=\\sum_x\\sum_y p(x,y)\\log\\frac{p(x,y)}{p(x)p(y)}
$$`,
      },
      {
        title: '卡方值',
        latex: `$$
\\chi^2 = \\sum \\frac{(O-E)^2}{E}
$$`,
      },
      {
        title: '随机森林特征重要性',
        latex: `$$
\\mathrm{Importance}(A)=\\frac{1}{T}\\sum_{t=1}^{T}\\sum_{\\mathrm{node\\ using\\ }A}\\mathrm{Gain}(A)
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 算法片段',
        code: `def _variance_selection(df, feature_cols, threshold):
    variances = df[feature_cols].var()
    keep_cols = variances[variances >= threshold].index.tolist()
    drop_cols = [col for col in feature_cols if col not in keep_cols]
    return keep_cols, drop_cols, variances

def _pearson_selection(df, feature_cols, target):
    y = pd.to_numeric(df[target], errors="coerce")
    score_map = {}
    for col in feature_cols:
        score = abs(float(df[col].corr(y, method="pearson")))
        score_map[col] = 0.0 if np.isnan(score) else score
    return score_map

def _random_forest_selection(model, X):
    model.fit(X)
    return dict(zip(X.columns, map(float, model.feature_importances_)))`,
      },
    ],
  }),
  buildProcessingChild('processing-standardize', '数据标准化', '数据标准化用于消除不同指标的量纲差异，并在需要时统一指标方向。支持 Min-Max、Z-score、总和归一化、中心化、均值化、区间化、初值化、最小值化、最大值化以及正向/负向/中间型/区间型指标处理。\n注意：数据标准化仅支持无空值定量变量。', {
    io: [
      '输入：1 个或多个无空值定量变量，并选择标准化方法。',
      '输出：原始变量会被转换到统一尺度，便于综合评价、聚类、回归或机器学习建模。',
    ],
    formulas: [
      {
        title: 'Min-Max 标准化',
        latex: `$$
x' = \\frac{x - x_{\\min}}{x_{\\max} - x_{\\min}}
$$`,
      },
      {
        title: 'Z-score 标准化',
        latex: `$$
x' = \\frac{x - \\bar{x}}{\\sigma}
$$`,
      },
      {
        title: '区间化',
        latex: `$$
x' = a + \\frac{(b-a)(x-x_{\\min})}{x_{\\max}-x_{\\min}}
$$`,
      },
      {
        title: '总和归一化',
        latex: `$$
x' = \\frac{x}{\\sum_{i=1}^{n}x_i}
$$`,
      },
      {
        title: '中心化',
        latex: `$$
x' = x - \\bar{x}
$$`,
      },
      {
        title: '均值化',
        latex: `$$
x' = \\frac{x}{\\bar{x}}
$$`,
      },
      {
        title: '初值化',
        latex: `$$
x' = \\frac{x}{x_1}
$$`,
      },
      {
        title: '最小值化 / 最大值化',
        latex: `$$
x' = \\frac{x}{x_{\\min}},\\quad
x' = \\frac{x}{x_{\\max}}
$$`,
      },
      {
        title: '正向 / 负向指标',
        latex: `$$
x'_{\\text{positive}}=\\frac{x-x_{\\min}}{x_{\\max}-x_{\\min}},\\quad
x'_{\\text{negative}}=\\frac{x_{\\max}-x}{x_{\\max}-x_{\\min}}
$$`,
      },
      {
        title: '中间型指标',
        latex: `$$
x' = 1 - \\frac{|x-x^*|}{\\max_i |x_i-x^*|}
$$`,
      },
      {
        title: '区间型指标',
        latex: `$$
x'=
\\begin{cases}
1, & x\\in[a,b] \\\\
1-\\dfrac{a-x}{M}, & x<a \\\\
1-\\dfrac{x-b}{M}, & x>b
\\end{cases}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 算法片段',
        code: `def _minmax(series):
    smin, smax = series.min(), series.max()
    denom = smax - smin
    return (series - smin) / denom

def _zscore(series):
    sigma = series.std()
    return (series - series.mean()) / sigma

def _interval_scale(series, lower, upper):
    smin, smax = series.min(), series.max()
    denom = smax - smin
    return lower + ((upper - lower) * (series - smin) / denom)

def handle(df, variables, params):
    for col in variables:
        series = pd.to_numeric(df[col], errors="coerce")
        df[f"{col}_std"] = _zscore(series)
    return df, "数据标准化完成"`,
      },
    ],
  }),
  buildProcessingChild('processing-missing', '缺失值处理', '缺失值处理用于对空值进行剔除、标记或填补。支持按行列缺失比例/个数进行剔除标记，也支持统计量填充、规则填充、插值填充和模型填充。\n注意：定类变量与定量变量的填充方法不同。定类变量的统计量填充通常只适合众数；插值填充和模型填充通常仅支持定量变量。', {
    io: [
      '输入：1 个或多个变量，并选择删除、标记或填补等处理动作。',
      '输出：空值会被剔除、标注或按指定策略补齐，为后续分析提供更完整的数据。',
    ],
    formulas: [
      {
        title: '统计量填充',
        latex: `$$
x_{\\text{miss}}'=
\\begin{cases}
\\bar{x}, & \\text{均值填充} \\\\
\\mathrm{median}(x), & \\text{中位数填充} \\\\
\\mathrm{mode}(x), & \\text{众数填充}
\\end{cases}
$$`,
      },
      {
        title: '三倍标准差填充',
        latex: `$$
x_{\\text{miss}}' = \\bar{x} + 3\\sigma
\\quad \\text{或} \\quad
x_{\\text{miss}}' = \\bar{x} - 3\\sigma
$$`,
      },
      {
        title: '固定值填充',
        latex: `$$
x_{\\text{miss}}' = c
$$`,
      },
      {
        title: 'KNN 填充',
        latex: `$$
x_{\\text{miss}}' = \\frac{1}{k}\\sum_{j\\in\\mathcal{N}_k} x_j
$$`,
      },
      {
        title: '缺失比例删除',
        latex: `$$
r_i = \\frac{\\#\\{x_{ij}\\text{ 缺失}\\}}{p},\\quad
r_i\\ge \\tau \\Rightarrow \\text{删除或标记}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 算法片段',
        code: `def _fill_stat(df, cols, fill_method):
    for col in cols:
        series = df[col]
        numeric_series = pd.to_numeric(series, errors="coerce")
        if fill_method == "mean":
            df[col] = series.fillna(numeric_series.mean())
        elif fill_method == "median":
            df[col] = series.fillna(numeric_series.median())
        elif fill_method == "mode":
            df[col] = series.fillna(series.mode().iloc[0])
        elif fill_method == "plus_3sigma":
            df[col] = series.fillna(numeric_series.mean() + 3 * numeric_series.std())
        elif fill_method == "minus_3sigma":
            df[col] = series.fillna(numeric_series.mean() - 3 * numeric_series.std())
    return df`,
      },
    ],
  }),
  buildProcessingChild('processing-reduce', '数据降维', '数据降维用于将原始高维特征映射到更少维度的变量中，以减少冗余和噪声，同时尽量保留原始数据中的主要信息。支持 PCA、LDA、ISOMap、LLE、KPCA 和 t-SNE。\n注意：数据降维仅支持无空值定量变量；其中 LDA 需要额外选择一个无空值定类目标变量。', {
    io: [
      '输入：至少 2 个无空值定量变量，必要时再指定目标变量或维度数。',
      '输出：系统生成更少维度的新变量，用于可视化、建模或降低复杂度。',
    ],
    formulas: [
      {
        title: 'PCA 投影',
        latex: `$$
Z = XW,\\quad W = \\arg\\max_W \\mathrm{Var}(XW)
$$`,
      },
      {
        title: 'LDA 判别目标',
        latex: `$$
W = \\arg\\max_W \\frac{|W^TS_BW|}{|W^TS_WW|}
$$`,
      },
      {
        title: 'ISOMap',
        latex: `$$
\\min_Z \\sum_{i<j} (d_G(x_i,x_j)-\\|z_i-z_j\\|)^2
$$`,
      },
      {
        title: 'LLE',
        latex: `$$
\\min_W \\sum_i \\left\\|x_i-\\sum_j w_{ij}x_j\\right\\|^2
$$
$$
\\min_Z \\sum_i \\left\\|z_i-\\sum_j w_{ij}z_j\\right\\|^2
$$`,
      },
      {
        title: 'KPCA',
        latex: `$$
K_{ij}=k(x_i,x_j),\\quad Z = \\text{eig}(K)
$$`,
      },
      {
        title: 't-SNE',
        latex: `$$
\\min_Z \\mathrm{KL}(P\\|Q)=\\sum_{i\\ne j} p_{ij}\\log\\frac{p_{ij}}{q_{ij}}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 算法片段',
        code: `def handle(df, variables, params):
    X = df[variables]
    X_scaled = StandardScaler().fit_transform(X)
    method = params.get("method", "pca")

    if method == "pca":
        pca = PCA(n_components=params.get("variance_ratio", 0.8), random_state=42)
        transformed = pca.fit_transform(X_scaled)
    elif method == "lda":
        y = df[params.get("target")]
        model = LinearDiscriminantAnalysis(n_components=params.get("components", 2))
        transformed = model.fit_transform(X_scaled, y)

    return transformed`,
      },
    ],
  }),
  buildProcessingChild('processing-transform', '数据变换', '数据变换用于将原始定量变量转换为更适合分析的形式。支持傅里叶变换、傅里叶逆变换、Box-Cox、Box-Cox 逆变换、连续小波、离散小波、Johnson 和 Yeo-Johnson 变换。\n注意：数据变换仅支持 1 个无空值定量变量；Box-Cox 更适合正值数据，Yeo-Johnson 支持零值和负值。', {
    io: [
      '输入：1 个无空值定量变量，并选择变换方法及其参数。',
      '输出：变量分布、尺度或表示形式会被改变，以满足分析模型对数据的要求。',
    ],
    formulas: [
      {
        title: 'Box-Cox 变换',
        latex: `$$
y(\\lambda)=
\\begin{cases}
\\dfrac{x^\\lambda - 1}{\\lambda}, & \\lambda \\ne 0 \\\\
\\ln x, & \\lambda = 0
\\end{cases}
$$`,
      },
      {
        title: 'Box-Cox 逆变换',
        latex: `$$
x=
\\begin{cases}
(\\lambda y + 1)^{1/\\lambda}, & \\lambda \\ne 0 \\\\
e^y, & \\lambda = 0
\\end{cases}
$$`,
      },
      {
        title: '傅里叶变换',
        latex: `$$
X_k = \\sum_{n=0}^{N-1} x_n e^{-i2\\pi kn/N}
$$`,
      },
      {
        title: '傅里叶逆变换',
        latex: `$$
x_n = \\frac{1}{N}\\sum_{k=0}^{N-1} X_k e^{i2\\pi kn/N}
$$`,
      },
      {
        title: 'Yeo-Johnson 变换',
        latex: `$$
T(x;\\lambda)=
\\begin{cases}
\\dfrac{(x+1)^\\lambda-1}{\\lambda}, & x\\ge 0,\\lambda\\ne 0 \\\\
\\log(x+1), & x\\ge 0,\\lambda=0 \\\\
-\\dfrac{(-x+1)^{2-\\lambda}-1}{2-\\lambda}, & x<0,\\lambda\\ne 2 \\\\
-\\log(-x+1), & x<0,\\lambda=2
\\end{cases}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 算法片段',
        code: `def _transform_fourier(series):
    values = np.asarray(series, dtype=float)
    transformed = np.abs(np.fft.fft(values))
    return pd.Series(transformed, index=series.index)

def _transform_boxcox(series, lam):
    shift = 0.0
    if float(series.min()) <= 0:
        shift = abs(float(series.min())) + 1e-6
    shifted = series + shift
    transformed, used_lam = stats.boxcox(shifted) if lam in (None, "", np.nan) else (stats.boxcox(shifted, lmbda=float(lam)), float(lam))
    return pd.Series(transformed, index=series.index), used_lam, shift`,
      },
    ],
  }),
  buildProcessingChild('processing-downsample', '数据降采样', '数据降采样用于按固定规则减少样本数量，同时尽量保留原始数据中的关键趋势和模式。支持固定间隔的直接采样，以及基于分组统计量的稀释采样。\n注意：系统会按每 N 个样本分为一组，若最后一组样本数量不足 N，则该组会被直接剔除。', {
    io: [
      '输入：1 个或多个定量变量，并设置降采样因子、位置或聚合方式。',
      '输出：样本数量减少，但整体趋势会尽量被保留，适合长序列或高频数据预处理。',
    ],
    formulas: [
      {
        title: '直接采样',
        latex: `$$
G_j=\\{x_{(j-1)N+1},\\dots,x_{jN}\\},\\quad y_j = x_{(j-1)N+p}
$$`,
      },
      {
        title: '稀释采样',
        latex: `$$
y_j = \\mathrm{Agg}(G_j),\\quad \\mathrm{Agg}\\in\\{\\mathrm{mean},\\mathrm{median},\\mathrm{min},\\mathrm{max},\\mathrm{sum}\\}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 算法片段',
        code: `def _trimmed_groups(df, factor):
    usable_length = (len(df) // factor) * factor
    trimmed = df.iloc[:usable_length].copy()
    group_ids = trimmed.reset_index(drop=True).index // factor
    return trimmed, group_ids

def handle(df, variables, params):
    mode = params.get("mode", "direct")
    factor = int(params.get("factor", 10))
    trimmed, group_ids = _trimmed_groups(df, factor)

    if mode == "direct":
        position = int(params.get("position", 1))
        sampled = trimmed.reset_index(drop=True).groupby(group_ids, sort=False).nth(position - 1)
    else:
        subset = trimmed[variables].reset_index(drop=True)
        grouped = subset.groupby(group_ids, sort=False)
        sampled = getattr(grouped, params.get("aggregate", "mean"))()

    return sampled.reset_index(drop=True), "数据降采样完成"`,
      },
    ],
  }),
  buildProcessingChild('processing-weight', '样本加权', '样本加权用于按样本权重调整不同记录在分析中的影响程度。适合处理抽样概率不一致、样本结构偏差，或希望在汇总时突出重点样本的场景。', {
    io: [
      '输入：选择待分析变量，并指定一个权重变量作为加权依据。',
      '输出：后续统计中，不同样本会按权重值产生不同影响。',
    ],
    notice: '权重变量本身要有清晰含义，错误的权重设置会直接影响统计结果解释。',
    formulas: [
      {
        title: '样本加权',
        latex: `$$
x_i' = w_i x_i
$$`,
      },
      {
        title: '加权汇总均值',
        latex: `$$
\\bar{x}_w = \\frac{\\sum_{i=1}^{n} w_i x_i}{\\sum_{i=1}^{n} w_i}
$$`,
      },
    ],
    codeBlocks: [
      {
        title: 'Python 算法片段',
        code: `def handle(df, variables, params):
    weight_var = params.get('weight_var', '')
    if weight_var and weight_var in df.columns:
        w = pd.to_numeric(df[weight_var], errors='coerce').fillna(1)
        for col in variables:
            if col not in df.columns or col == weight_var:
                continue
            s = pd.to_numeric(df[col], errors='coerce')
            df[col] = s * w
        return df, f'已使用 {weight_var} 对选中变量加权'
    return df, '处理完成'`,
      },
    ],
  }),
]

const helpGroups = [
  {
    id: 'my-data',
    title: '我的数据',
    pageTitle: '我的数据',
    sections: [
      {
        id: 'upload-data',
        title: '一、如何上传数据？',
        intro: '第一次进入工作台后，先完成数据上传，系统才会开放后续变量配置与分析动作。',
        steps: [
          {
            title: '选择数据文件',
            text: '在工作台中点击上传区域，选择本地数据文件。建议优先使用结构清晰、字段命名规范的表格文件。',
          },
          {
            title: '等待系统解析',
            text: '系统会自动读取列名、样本记录与变量类型，并在左侧变量区域展示结果。',
          },
          {
            title: '核对变量信息',
            text: '上传完成后先检查变量名、类型和空值情况，确认没有错列、乱码或类型识别异常。',
          },
        ],
      },
      {
        id: 'data-check',
        title: '二、上传后先检查什么？',
        points: [
          {
            title: '变量名是否清晰',
            text: '变量名尽量避免重复、含义模糊或只有编号，这会直接影响后续变量选择与结果解读。',
          },
          {
            title: '变量类型是否合理',
            text: '定量变量、定类变量与文本变量的判断会影响方法可用性，发现不合理时建议先做数据处理。',
          },
          {
            title: '缺失和异常是否明显',
            text: '如果存在大量空值、极端值或无效样本，建议在正式统计分析前先完成清洗。',
          },
        ],
      },
      {
        id: 'data-faq',
        title: '三、常见问题',
        qa: [
          {
            q: '上传后为什么有些方法不可选？',
            a: '通常是因为变量类型、变量数量或缺失值状态不满足方法要求。先查看对应方法的变量限制和提示说明。',
          },
          {
            q: '为什么同一份数据换个方法后结果区为空？',
            a: '部分方法需要先完成变量拖拽或参数设置；如果条件不足，系统不会直接运行有效结果。',
          },
          {
            q: '数据上传后会不会改变原始文件？',
            a: '工作台内的处理是平台内部流程，不会直接修改你本地电脑里的原始文件。',
          },
        ],
      },
    ],
  },
  {
    id: 'charts',
    title: '可视化绘图',
    pageTitle: '可视化绘图',
    sections: [
      {
        id: 'chart-position',
        title: '一、可视化绘图适合什么场景？',
        paragraphs: [
          '可视化绘图适合把统计结果进一步转成更适合展示的图形，用于论文插图、答辩汇报、教学演示或业务复盘。',
          '如果你的目标是更直观地表达组间差异、趋势变化和分布特征，建议在完成分析后再进入图表能力进行补充。',
        ],
      },
      {
        id: 'chart-suggestions',
        title: '二、使用建议',
        points: [
          {
            title: '图先服务于结论',
            text: '先明确你要表达的是差异、趋势、结构还是分布，再决定图形类型，不要只追求图形复杂。',
          },
          {
            title: '命名要一致',
            text: '变量名、组名与图例建议保持一致，避免正文、表格和图形之间叫法不统一。',
          },
          {
            title: '避免视觉噪音',
            text: '过多颜色、边框和装饰会削弱重点，学术型输出通常更适合简洁风格。',
          },
        ],
      },
    ],
  },
  {
    id: 'processing',
    title: '数据处理',
    pageTitle: '数据处理',
    children: processingChildren,
    sections: [
      {
        id: 'processing-why',
        title: '一、为什么先做数据处理？',
        paragraphs: [
          '高质量分析的前提是高质量数据。缺失值、异常值、重复样本、编码混乱等问题，如果不先处理，后续统计结果会很容易失真。',
          'spssgo 把数据处理独立成单独模块，方便你按步骤完成清洗，再进入正式分析。',
        ],
      },
      {
        id: 'processing-workflow',
        title: '二、推荐处理顺序',
        steps: [
          {
            title: '先检查缺失值',
            text: '先确认哪些变量存在空值、空值比例如何，再决定删除、填补还是标记。',
          },
          {
            title: '再处理异常值',
            text: '对定量变量优先识别极端值，避免少量异常点过度影响均值、标准差和回归结果。',
          },
          {
            title: '最后做转换与编码',
            text: '如有需要，再进行标准化、重编码、虚拟变量转换、降维等操作，让数据更适合建模和分析。',
          },
        ],
      },
      {
        id: 'processing-notes',
        title: '三、使用提醒',
        points: [
          {
            title: '看清方法适用变量',
            text: '有些方法只支持定量变量，有些只支持定类变量，执行前先留意页面中的变量限制提示。',
          },
          {
            title: '一次只改清楚一件事',
            text: '如果连续进行多步处理，建议每一步都明确目的，避免在不知不觉中改变数据含义。',
          },
          {
            title: '重视结果解释',
            text: '数据处理不是机械操作，每一种处理都会影响后续分析含义，尤其在论文与正式报告中要说明理由。',
          },
        ],
      },
    ],
  },
  {
    id: 'analysis',
    title: '数据分析',
    pageTitle: '数据分析',
    children: analysisChildren,
    sections: [
      {
        id: 'analysis-start',
        title: '一、如何开始一次分析？',
        steps: [
          {
            title: '选定分析目标',
            text: '先确认你是想描述现状、比较差异、研究关系，还是做预测，这会决定方法方向。',
          },
          {
            title: '拖入正确变量',
            text: '根据页面要求把目标变量、自变量或分组变量放入对应区域，避免变量角色放错。',
          },
          {
            title: '设置必要参数',
            text: '如显著性水平、分组方式、检验方向等，建议理解含义后再修改默认值。',
          },
          {
            title: '查看并解释结果',
            text: '不要只盯着显著性结果，还要结合样本背景、效应方向和实际意义一起判断。',
          },
        ],
      },
      {
        id: 'analysis-reading',
        title: '二、怎么看分析结果？',
        points: [
          {
            title: '先看问题是否匹配',
            text: '结果是否回答了你一开始想解决的问题，比单纯“有没有显著”更重要。',
          },
          {
            title: '再看关键统计量',
            text: '均值、标准差、p 值、相关系数、回归系数等要结合具体方法来读，不能混用。',
          },
          {
            title: '最后写成解释语言',
            text: '尽量把统计结果翻译成业务语言、研究语言或论文表达，避免只复制表格而没有结论。',
          },
        ],
      },
      {
        id: 'analysis-faq',
        title: '三、常见误区',
        qa: [
          {
            q: 'p 值显著就说明研究结论一定成立吗？',
            a: '不是。显著性只是统计意义的一部分，还要看研究设计、样本质量、效应大小和实际背景。',
          },
          {
            q: '变量越多越好吗？',
            a: '不一定。变量过多可能带来噪声、共线性和解释困难，很多时候合适比堆砌更重要。',
          },
          {
            q: 'AI 解释能直接复制进论文吗？',
            a: '建议作为草稿参考，再结合你的研究背景进行人工核对、修改和定稿。',
          },
        ],
      },
    ],
  },
]

const activeDocId = ref('my-data')
const sidebarOpen = ref(false)
const expandedGroupId = ref(null)

const docIndex = helpGroups.reduce((acc, group) => {
  acc[group.id] = group
  for (const child of group.children || []) {
    acc[child.id] = { ...child, groupId: group.id }
  }
  return acc
}, {})

const activeDoc = computed(() => docIndex[activeDocId.value] || helpGroups[0])

const currentGroupId = computed(() => activeDoc.value.groupId || activeDoc.value.id)

const activeGroup = computed(() => {
  return helpGroups.find((group) => group.id === currentGroupId.value) || helpGroups[0]
})

const activeChildId = computed(() => activeDoc.value.groupId ? activeDoc.value.id : '')

function activateGroup(groupId, shouldCloseMobile = false) {
  const group = helpGroups.find((item) => item.id === groupId)

  if (expandedGroupId.value === groupId) {
    expandedGroupId.value = null
    activeDocId.value = groupId
  } else {
    expandedGroupId.value = groupId
    activeDocId.value = group?.children?.[0]?.id || groupId
  }

  if (typeof window !== 'undefined') {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
  if (shouldCloseMobile) {
    sidebarOpen.value = false
  }
}

function activateDoc(groupId, docId, shouldCloseMobile = false) {
  activeDocId.value = docId
  expandedGroupId.value = groupId
  if (typeof window !== 'undefined') {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
  if (shouldCloseMobile) {
    sidebarOpen.value = false
  }
}
</script>

<style scoped>
:global(html),
:global(body),
:global(#app) {
  min-height: 100%;
}

:global(body) {
  margin: 0;
  background: #f6f8fb;
  color: #1f2937;
  font-family: "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif;
  -webkit-font-smoothing: antialiased;
}

* {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

.help-page {
  min-height: 100vh;
  background: #fff;
}

.help-topbar {
  position: sticky;
  top: 0;
  z-index: 30;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  height: 76px;
  padding: 0 22px;
  background: #fff;
  border-bottom: 1px solid #edf1f5;
}

.help-brand {
  display: inline-flex;
  align-items: center;
  color: #1d4ed8;
  text-decoration: none;
}

.help-brand img {
  width: auto;
  height: 30px;
  object-fit: contain;
}

.help-topnav {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-right: auto;
  margin-left: 16px;
}

.help-topnav a {
  padding: 8px 12px;
  color: #4b5563;
  text-decoration: none;
  font-size: 15px;
  border-radius: 10px;
  transition: all 0.16s ease;
}

.help-topnav a:hover,
.help-topnav a.active {
  color: #1d4ed8;
  background: #f3f7ff;
}

.help-login-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 112px;
  height: 38px;
  padding: 0 18px;
  border-radius: 999px;
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: #fff;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  box-shadow: none;
}

.help-shell {
  display: grid;
  grid-template-columns: 248px minmax(0, 1fr);
  min-height: calc(100vh - 76px);
}

.help-sidebar {
  position: sticky;
  top: 76px;
  align-self: start;
  height: calc(100vh - 76px);
  padding: 18px 12px 20px 18px;
  background: #fff;
  border-right: 1px solid #f0f2f5;
  overflow-y: auto;
  overflow-x: hidden;
  overscroll-behavior: contain;
  scrollbar-gutter: stable;
  -webkit-overflow-scrolling: touch;
}

:global(.help-sidebar::-webkit-scrollbar) {
  width: 5px;
}

:global(.help-sidebar::-webkit-scrollbar-track) {
  background: transparent;
}

:global(.help-sidebar::-webkit-scrollbar-thumb) {
  background: #e2e5ea;
  border-radius: 8px;
}

:global(.help-sidebar::-webkit-scrollbar-thumb:hover) {
  background: #d1d5db;
}

.help-sidebar-title {
  margin-bottom: 16px;
  padding: 0 8px;
  font-size: 13px;
  font-weight: 700;
  color: #94a3b8;
  letter-spacing: 0.08em;
}

.help-sidebar-item,
.help-mobile-sidebar-item {
  width: 100%;
  border: none;
  background: transparent;
  cursor: pointer;
  font-family: inherit;
}

.help-sidebar-item {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 18px;
  align-items: center;
  gap: 12px;
  padding: 12px 12px;
  border-radius: 12px;
  color: #334155;
  font-size: 14px;
  font-weight: 500;
  text-align: left;
  transition: all 0.16s ease;
}

.help-sidebar-item:hover,
.help-sidebar-item.active {
  background: #f5f8ff;
  color: #1d4ed8;
}

.help-sidebar-arrow {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  font-size: 16px;
  color: #a0aec0;
  line-height: 1;
  flex-shrink: 0;
  pointer-events: none;
}

.help-sidebar-arrow--empty {
  visibility: hidden;
}

.help-sidebar-children {
  margin-top: 4px;
  margin-bottom: 8px;
  padding-left: 6px;
  border-left: 1px solid #eef2f6;
}

.help-sidebar-child {
  width: 100%;
  padding: 9px 10px 9px 14px;
  border: none;
  background: transparent;
  color: #475467;
  text-align: left;
  font-size: 14px;
  font-family: inherit;
  cursor: pointer;
  border-radius: 10px;
}

.help-sidebar-child:hover,
.help-sidebar-child.active {
  color: #1d4ed8;
  background: #f7faff;
}

.help-main {
  min-width: 0;
  padding: 22px 20px 48px;
}

.help-main-head {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 20px;
}

.help-menu-btn {
  display: none;
  width: 42px;
  height: 42px;
  border: 1px solid #d8e3f2;
  border-radius: 12px;
  background: #fff;
  color: #475569;
  font-size: 20px;
  cursor: pointer;
  flex-shrink: 0;
}

.help-breadcrumb {
  margin: 0 0 6px;
  font-size: 13px;
  color: #98a2b3;
}

.help-main-head h1 {
  margin: 0;
  font-size: 32px;
  line-height: 1.12;
  color: #101828;
  letter-spacing: -0.03em;
}

.help-mobile-sidebar {
  display: none;
  margin-bottom: 18px;
  padding: 8px;
  border: 1px solid #eef2f6;
  border-radius: 12px;
  background: #fff;
}

.help-content-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 210px;
  gap: 18px;
  align-items: start;
}

.help-article {
  min-width: 0;
  padding: 0 24px 36px;
  background: #fff;
  border: none;
  border-radius: 0;
  box-shadow: none;
}

.help-section + .help-section {
  margin-top: 34px;
}

.help-section-head {
  margin-bottom: 16px;
  padding-top: 18px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eef2f6;
}

.help-section-head h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  color: #1f2937;
}

.help-section-head p {
  margin: 10px 0 0;
  font-size: 14px;
  line-height: 1.8;
  color: #667085;
}

.help-paragraphs p {
  margin: 0 0 14px;
  font-size: 15px;
  line-height: 2;
  color: #344054;
}

.help-point-list,
.help-qa-list,
.help-formula-list,
.help-code-list {
  display: grid;
  gap: 8px;
}

.help-point-card,
.help-qa-card,
.help-formula-card,
.help-code-card {
  padding: 10px 0;
  border: none;
  border-radius: 0;
  background: transparent;
}

.help-point-card h3,
.help-qa-card h3,
.help-formula-card h3,
.help-code-card h3,
.help-step-card h3 {
  margin: 0 0 8px;
  font-size: 16px;
  color: #101828;
}

.help-point-card p,
.help-qa-card p,
.help-formula-card p,
.help-code-card p,
.help-step-card p {
  margin: 0;
  font-size: 15px;
  line-height: 1.9;
  color: #475467;
}

.help-formula-block,
.help-code-block {
  margin: 10px 0 0;
  padding: 0;
}

.help-code-card h3,
.help-code-card p {
  padding-left: 0;
  padding-right: 0;
}

.help-code-card h3 {
  margin-top: 0;
  margin-bottom: 6px;
}

.help-code-card p {
  margin-bottom: 10px;
  color: #667085;
}

.help-step-list {
  display: grid;
  gap: 10px;
}

.help-step-card {
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr);
  gap: 12px;
  padding: 8px 0;
  border: none;
  border-radius: 0;
  background: transparent;
}

.help-step-content {
  min-width: 0;
}

.help-step-shot {
  margin-top: 14px;
}

.help-step-shot-head {
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 700;
  color: #475467;
}

.help-step-shot-box {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 170px;
  padding: 18px;
  border: 1px dashed #cbd5e1;
  border-radius: 14px;
  background:
    linear-gradient(180deg, rgba(248, 250, 252, 0.96), rgba(241, 245, 249, 0.9));
  color: #94a3b8;
  font-size: 14px;
  font-weight: 600;
}

.help-step-shot-note {
  margin-top: 10px;
  font-size: 13px;
  line-height: 1.8;
  color: #667085;
}

.help-step-index {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  margin-top: 2px;
  border-radius: 50%;
  background: #f5f7fa;
  color: #667085;
  font-size: 13px;
  font-weight: 700;
}

.help-outline {
  position: sticky;
  top: 100px;
}

.help-feedback-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 52px;
  margin-bottom: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  background: #fff;
  color: #334155;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
}

.help-feedback-btn:hover {
  color: #1d4ed8;
  border-color: #cfe0ff;
}

.help-outline-card {
  display: grid;
  gap: 10px;
  padding: 4px 0 4px 16px;
  border-left: 1px solid #e4e7ec;
  background: transparent;
}

.help-outline-link {
  color: #667085;
  text-decoration: none;
  font-size: 14px;
  line-height: 1.6;
}

.help-outline-link:hover {
  color: #1d4ed8;
}

@media (max-width: 1100px) {
  .help-content-layout {
    grid-template-columns: 1fr;
  }

  .help-outline {
    position: static;
    order: -1;
  }

  .help-outline-card {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px 16px;
    padding: 0;
    border-left: none;
    margin-bottom: 18px;
  }
}

@media (max-width: 900px) {
  .help-shell {
    grid-template-columns: 1fr;
  }

  .help-sidebar {
    display: none;
  }

  .help-menu-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .help-mobile-sidebar {
    display: none;
  }

  .help-mobile-sidebar.open {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
    max-height: calc(100vh - 150px);
    overflow-y: auto;
    overscroll-behavior: contain;
    -webkit-overflow-scrolling: touch;
  }

  .help-mobile-sidebar-item {
    padding: 12px 10px;
    border-radius: 12px;
    color: #475569;
    font-size: 14px;
    text-align: center;
  }

  .help-mobile-sidebar-item--child {
    font-size: 13px;
    color: #667085;
  }

  .help-mobile-sidebar-item.active {
    background: #f5f8ff;
    color: #1d4ed8;
    font-weight: 700;
  }
}

@media (max-width: 768px) {
  .help-topbar {
    padding: 0 14px;
  }

  .help-topnav {
    display: none;
  }

  .help-main {
    padding: 16px 12px 30px;
  }

  .help-main-head h1 {
    font-size: 28px;
  }

  .help-article {
    padding: 0 10px 22px 6px;
  }

  .help-feedback-btn {
    height: 48px;
    margin-bottom: 14px;
  }

  .help-outline-card {
    grid-template-columns: 1fr;
  }

  .help-step-card {
    grid-template-columns: 1fr;
  }
}
</style>
