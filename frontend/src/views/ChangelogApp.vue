<template>
  <div class="changelog-page">
    <header class="changelog-topbar">
      <a href="/" class="changelog-brand">
        <img src="/logo.png" alt="spssgo" />
      </a>
      <nav class="changelog-topnav" aria-label="顶部导航">
        <a href="/about">产品介绍</a>
        <a href="/help">帮助中心</a>
        <a href="/changelog" class="active">更新日志</a>
      </nav>
      <div class="changelog-topbar-actions">
        <a class="changelog-login-btn" href="/login?redirect=%2Fworkspace">进入工作台</a>
      </div>
    </header>

    <section class="changelog-hero">
      <div class="changelog-hero-bg" aria-hidden="true">
        <div class="changelog-hero-glow changelog-hero-glow--1" />
        <div class="changelog-hero-glow changelog-hero-glow--2" />
      </div>
      <div class="changelog-hero-body">
        <div class="changelog-hero-badge">更新日志</div>
        <h1 class="changelog-hero-title">版本发布记录</h1>
        <p class="changelog-hero-desc">
          SPSSGO 的每一次功能迭代与修复改进，都在这里记录。
        </p>
      </div>
    </section>

    <div class="changelog-shell">
      <aside class="changelog-sidebar">
        <div class="changelog-sidebar-title">版本目录</div>
        <button
          v-for="(entry, index) in changelogEntries"
          :key="index"
          class="changelog-sidebar-item"
          :class="{ active: activeEntryIndex === index }"
          type="button"
          @click="scrollToEntry(index)"
        >
          <span class="changelog-sidebar-date">{{ entry.date }}</span>
          <span class="changelog-sidebar-label">{{ entry.title }}</span>
        </button>
      </aside>

      <main class="changelog-timeline">
        <div
          v-for="(entry, index) in changelogEntries"
          :key="index"
          :ref="el => { if (el) entryRefs[index] = el }"
          :data-entry-index="index"
          class="changelog-entry"
        >
          <div class="changelog-entry-marker" />
          <div class="changelog-entry-card">
            <div class="changelog-entry-head">
              <time class="changelog-entry-date">{{ entry.date }}</time>
              <span class="changelog-entry-tag" :class="`changelog-entry-tag--${entry.type}`">
                {{ tagLabel(entry.type) }}
              </span>
            </div>
            <h2 class="changelog-entry-title">{{ entry.title }}</h2>
            <ul v-if="entry.items?.length" class="changelog-entry-list">
              <li v-for="(item, i) in entry.items" :key="i">{{ item }}</li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const changelogEntries = [
  {
    date: '2026-06-06',
    type: 'feat',
    title: '非参数检验全线重构与配置面板升级',
    items: [
      'Mann-Whitney U 检验全面重构，增强秩和计算、效应量输出与报告完整性',
      'Wilcoxon 符号秩检验重构，增强配对秩差分析与描述统计',
      '单样本 Wilcoxon 增强中位数偏离检验与置信区间报告',
      'Kruskal-Wallis 检验增强多组秩和比较、事后多重比较集成与效应量',
      'Friedman 检验重构多配对秩检验，增强 Kendall 和谐系数与事后比较',
      'Cochran\'s Q 检验与拟合优度卡方检验输出完整性增强',
      '配置面板升级：非参数检验参数联动与条件显示',
      '新增 7 个非参数检验方法的完整测试用例',
    ],
  },
  {
    date: '2026-06-05',
    type: 'feat',
    title: '中介效应全线 R 脚本升级与任务执行优化',
    items: [
      '有调节的中介效应 R 脚本大幅升级：增强调节效应交互项构造、条件间接效应置信区间估计及多水平调节输出',
      '中介效应 R 脚本全线优化输入输出协议，统一 Bootstrap 抽样与效应量报告格式',
      '链式中介效应 R 脚本一致性校准，与其他中介方法同步协议规范',
      '任务执行器增强：优化长时间 R 脚本任务的进程管理与超时控制',
      '图表组件与配置面板交互细节优化',
    ],
  },
  {
    date: '2026-06-04',
    type: 'feat',
    title: '有调节的中介效应上线与链式中介增强',
    items: [
      '全新上线的有调节的中介效应：R 引擎驱动，支持调节变量对中介路径的交互分析，Bootstrapped 置信区间与条件间接效应分解',
      '链式中介效应 R 脚本重构，增强路径系数输出与中介效应分解完整性',
      '可视化服务增强图表数据生成链路，优化多变量图表渲染性能',
      '分析配置面板参数联动与条件显示优化',
      '可视化工作台图表类型切换与变量选择体验增强',
      '更新中介效应全线 R 桥接测试',
    ],
  },
  {
    date: '2026-06-03',
    type: 'feat',
    title: '可视化工作台上线与全链路图表升级',
    items: [
      '可视化工作台模块上线：支持自由选择变量与图表类型创建探索性图表，散点图、箱线图、小提琴图等全覆盖',
      '新增可视化 API 与服务层，提供后端图表数据生成能力',
      '图表系统全链路升级：散点图、箱线图、小提琴图等复杂图表类型自适应渲染',
      '图标映射统一管理，ChartItem 支持动态图标类型识别',
      'TopBar 导航重构，新增可视化工作台入口',
      '共享报告页面集成图表渲染能力',
      '新增可视化服务测试用例',
    ],
  },
  {
    date: '2026-06-02',
    type: 'feat',
    title: '中介效应体系重构与方法导航增强',
    items: [
      '中介效应分析重构为 R 引擎驱动，支持 Bootstrap 置信区间估计、总效应/直接效应/间接效应完整输出',
      '平行中介效应 R 脚本架构重构，支持多条路径并行检验与效应量分解',
      '链式中介效应增强路径系数报告与多级间接效应汇总',
      '配置面板增强：统一参数布局与条件显示逻辑',
      '图表组件增强：中介路径示意图渲染',
      '方法导航优化：分类筛选与搜索体验提升',
      '更新中介效应 R 桥接测试',
    ],
  },
  {
    date: '2026-05-29',
    type: 'refactor',
    title: '前端目录结构重构 — 统一资源归集与路径规范',
    items: [
      '删除 src/entries/ 目录下 5 个废弃独立入口文件（admin-main.js、help-main.js、home-main.js、legal-main.js、login-main.js）',
      'AdminApp.vue 移至 src/views/admin/AdminHomeView.vue，统一 View 后缀命名',
      'src/admin/ 下全部组件移入 src/components/admin/，composables 移入 src/composables/admin/',
      '受影响文件的 import 路径改用 @/ 别名并在移动后修正路径，废弃 src/admin/api.js 中转文件',
      'src/styles/ 和 src/assets/ 合并为 src/assets/styles/，CSS 资源统一归集',
      'admin.css 改为 main.js 全局引入（原为组件内 import），并移至 assets/styles 目录',
      '删除已清空的 src/admin/ 目录',
    ],
  },
  {
    date: '2026-05-28',
    type: 'refactor',
    title: '首页全面重构 — 拆分为独立组件并迁移至 TailwindCSS',
    items: [
      '将 HomeApp.vue 各区块拆分为 9 个独立组件至 src/components/home/（NavBar、Hero、Generation、Workflow、TrustGuarantee、Deliverables、FAQ、CTA、Footer）',
      '全部改用 TailwindCSS 内置类，移除冗余自定义样式',
      '配置 @ 路径别名，统一 import 路径',
      '集成 @tailwindcss/vite 插件',
      'main.js 从 src/entries/ 移至 src/',
      'router.js 移至 src/router/index.js，移除冗余 route meta 字段',
      '移除 public/spssgo-config.js，改用 .env 管理 API 地址',
      '清理死代码：移除 * reset、useHomeHero composable 等',
    ],
  },
  {
    date: '2026-05-26',
    type: 'feat',
    title: '回归分析、调节效应与报告导出增强',
    items: [
      '多元线性回归全面重构：增强 R² 及调整 R² 报告、标准化/非标准化系数双输出、共线性诊断与 VIF 自动校验',
      '调节效应分析 R 脚本架构重构：增强交互项构造、简单斜率检验及 Johnson-Neyman 区间分析',
      '共线性诊断 VIF 计算链路优化，与多元回归结果自动联动',
      '图表系统大幅增强：散点图、拟合线、置信区间带自适应渲染，回归预测可视化',
      '报告导出增强：Word 导出支持图表嵌入与多章节排版',
      '报告页面新增回归预测可视化组件，支持任意 X 值预测 Y 及其置信区间',
      '更新调节效应与回归分析的 R 桥接测试',
    ],
  },
  {
    date: '2026-05-25',
    type: 'feat',
    title: '卡方检验、T 检验重构与报告系统增强',
    items: [
      '卡方检验全面重构：完善期望频数计算、残差分析与多种关联强度指标输出',
      '独立样本 T 检验重构：强化方差齐性检验、效应量计算及结果解读的完整链路',
      '配对 T 检验重构：增强配对相关系数、多重比较校正及描述统计输出',
      '图表系统增强：优化分类分布图与指标对比图的悬浮提示、图例及自适应渲染',
      '报告页面完善：表格式样、数据展开与引用标注统一规范',
      '新增卡方检验、独立 T 检验、配对 T 检验的完整测试用例',
    ],
  },
  {
    date: '2026-05-24',
    type: 'feat',
    title: '分析方法全面升级与配置面板重构',
    items: [
      '协方差分析与多元方差分析重构为统一槽位协议，增强统计输出完整性与可视化呈现',
      '单样本、配对及双样本等效性检验重构参数体系，统一结果结构与报告输出链路',
      '摘要单因素方差分析模块化重构，优化从参数输入到报告生成的完整链路',
      '分析配置面板重大重构：统一槽位渲染逻辑、条件显示控制与参数联动机制，显著提升分析流程的配置体验与可扩展性',
      '图表组件增强多变量溢出处理与自适应渲染能力',
      '新增协方差分析、多元方差分析、等效性检验及摘要方差分析共 6 个分析方法的完整测试覆盖',
    ],
  },
  {
    date: '2026-05-23',
    type: 'fix',
    title: '事后多重比较关键缺陷修正与 N 因素方差分析上线',
    items: [
      '修正 SNK 与 Duncan 事后检验的一项精度缺陷：rank_distance 参数此前未从调用方传入，导致逐步检验口径在任何均值间距下均固定为 k=2。修正后按实际排序间距动态确定 k 值，逐步收紧与逐步放宽逻辑恢复正常',
      'N 因素方差分析上线：解除传统软件对自变量数量的固定上限，接受任意数量的分类自变量与协变量，自动生成全部交互效应表，R 引擎执行确保计算精度',
      '发布 Python–R 双引擎接口规范文档：完整描述变量传递、矩阵转换与结果回传的映射关系',
      'N 因素方差分析全链路自动化测试就绪，核心路径纳入 CI 回归验证',
    ],
  },
  {
    date: '2026-05-18',
    type: 'feat',
    title: '方差分析重构与图表增强',
    items: [
      '事后多重比较全面重构：支持 LSD、Bonferroni、Tukey、Scheffe、SNK、Duncan、Games-Howell 七种比较方法，新增字母标记法、效应量、P 值标注，附带均值对比图',
      '双因素方差分析重构：统一 factors 参数，新增协变量支持、交互效应开关、事后多重比较集成，附带均值对比图',
      '三因素方差分析重构：统一 factors 参数，新增协变量支持、二阶/三阶交互控制、效应量选项、事后多重比较集成',
      '前端图表系统：指标对比图新增多系列折线图支持，展示多条数据序列对比，含图例和差异化配色',
      '变量拖拽：拖拽变量时显示拖拽数量预览标记，提升交互反馈',
      '配置面板：适配 factors（多选分类变量）槽位类型，支持协变量配置',
      '方法元数据：新增事后多重比较、双因素/三因素方差分析的前端槽位和选项配置',
      '新增事后多重比较、双因素/三因素方差分析完整测试覆盖',
      '更新分析方法参数文档，新增项目更新日志（CHANGELOG.md）',
    ],
  },
  {
    date: '2026-05-14',
    type: 'feat',
    title: '分析方法大幅增强，前端面板与测试全面升级',
    items: [
      '对应分析重构：增强 SVD 降维输出与可视化，补充惯量/卡方贡献/对称标准化等统计量',
      'Kano 模型增强：优化 Better-Worse 系数计算与类别判定逻辑，完善输出结构',
      '新增加权多选题-单选项交叉分析、多选题-多选题交叉分析、多选题-单选题交叉分析',
      '新增单样本 T 检验：检验样本均值是否显著偏离给定检验值，含描述统计与 Cohen\'s d',
      '新增摘要 T 检验：独立样本 T 检验的简化摘要封装，支持均值差与置信区间',
      '验证性因子分析 R 脚本重构：支持更多拟合指标与模型诊断输出',
      '分析配置面板（ConfigPanel）重构：支持变量拖拽排序、条件显示逻辑',
      '分析图表组件优化：图例、标签、悬浮提示交互增强',
      '样式系统增强：统一表格、按钮、卡片样式规范，补充缺失样式覆盖',
      '首页优化：更新文案展示与布局调整',
      '测试覆盖增强：新增对应分析、Kano、单样本 T 检验、摘要 T 检验、CFA R 桥接测试',
    ],
  },
  {
    date: '2026-05-13',
    type: 'feat',
    title: '新增更新日志页面，全面改版左侧目录',
    items: [
      '新增独立更新日志页面（/changelog），左侧目录 + 右侧时间线双栏布局',
      '目录侧边栏随滚动自动高亮当前条目，支持点击跳转',
      '移动端自适应折叠为横向标签布局',
      '产品介绍页、帮助中心、首页页脚统一添加「更新日志」入口',
    ],
  },
  {
    date: '2026-05-12',
    type: 'feat',
    title: '相关分析与报告展示优化',
    items: [
      '皮尔逊相关分析：优化结果输出与报告展示，增强可读性',
      '因子分析：增强结果解读与可视化呈现，完善输出结构',
      '图表组件：优化交互体验与视觉一致性',
      '报告页面：改进布局与数据展示效果',
      '公共分析层：完善通用处理逻辑',
    ],
  },
  {
    date: '2026-05-10',
    type: 'feat',
    title: '学术化报告升级 — 全线三线表与参考文献',
    items: [
      '频数分析：优化输出格式与图表展示，提升学术规范度',
      '卡方检验：完善结果呈现与报告排版',
      '信度分析（Cronbach\'s α）：增强结果解读与输出结构',
      '报告系统：全线升级为三线表样式，符合学术期刊/论文标准',
      '参考文献：更新引用格式，规范化文献列表',
      '前端图表组件：优化交互体验与视觉一致性',
    ],
  },
  {
    date: '2026-05-08',
    type: 'feat',
    title: '分类汇总增强与正态性检验上线',
    items: [
      '分类汇总功能增强，支持更多分组统计与输出格式',
      '优化 README 文档，添加界面预览截图并改进布局',
      '修复：文件夹删除时级联清理关联项，解决孤立数据问题',
      '新增正态性检验分析方法（Shapiro-Wilk、K-S、Jarque-Bera）',
      '新增全局悬浮提示组件（useGlobalTooltip），提升交互反馈',
    ],
  },
  {
    date: '2026-05-06',
    type: 'feat',
    title: '重构产品介绍页与帮助中心',
    items: [
      '全面重构产品介绍页（About），优化 UI 设计与交互体验',
      '重构帮助中心（Help），改进文档分类与内容呈现结构',
      '帮助文档支持段落、要点卡片、步骤引导、问答、公式块、代码块等多内容类型',
      '数据分析方法帮助文档补充，覆盖全部已有分析方法',
    ],
  },
  {
    date: '2026-05-03',
    type: 'feat',
    title: '多选题分析与判断题分析上线',
    items: [
      '新增多选分析：多选题选项频次统计、响应率与普及率计算',
      '支持多选题帕累托图展示，识别核心选择项',
      '新增区分度分析：基于 R 引擎检验题项对高/低分组样本的区分能力',
      '新增 NPS 净推荐值分析：贬损者/被动者/推荐者分类与 NPS 计算',
      '新增单选题-多选题、多选题-多选题交叉分析',
    ],
  },
  {
    date: '2026-04-28',
    type: 'feat',
    title: '高级问卷分析模块上线',
    items: [
      '新增联合分析（Conjoint Analysis）：通过 OLS 估计属性偏好权重',
      '新增 MaxDiff 模型：基于最好/最差选择恢复偏好强度排序',
      '新增 MaxDiff Pro：个体层效用恢复与高级模拟',
      '新增 CBC 联合分析：基于选择任务的离散选择模型',
      '新增 BPTO 品牌价格抵补模型：评估品牌与价格的权衡关系',
    ],
  },
  {
    date: '2026-04-25',
    type: 'feat',
    title: '可视化绘图模块上线',
    items: [
      '新增可视化绘图模块，支持柱状图、折线图、饼图、箱线图、散点图等常见图表类型',
      '图表配置面板支持数据列选择、颜色主题、标签格式等自定义选项',
      '分析结果图表支持独立保存、复制到剪贴板',
      '图表组件封装为统一协议：category_distribution / crosstab_distribution / metric_comparison',
      '分析结果图表复用公共渲染能力，新增方法无需重写图表',
    ],
  },
  {
    date: '2026-04-20',
    type: 'feat',
    title: 'TURF分析与惩罚分析上线',
    items: [
      '新增 TURF 分析：寻找在给定数量约束下覆盖最多受众的最优选项组合',
      '新增惩罚分析（Penalty Analysis）：识别属性表现偏低时对总体满意度的拖累程度',
      '新增价格断裂点模型：识别价格敏感度研究中的心理接受边界与关键交点',
    ],
  },
  {
    date: '2026-04-15',
    type: 'feat',
    title: '对应分析与 Kano 模型上线',
    items: [
      '新增对应分析（Correspondence Analysis）：对分类变量列联表做 SVD 降维，观察类别间接近关系',
      '新增 Kano 模型：基于正向题与反向题的配对回答，识别题项的 Kano 类别（A/O/M/I/R/Q）',
      '新增交叉表（调研专项）：输出交叉频数、行百分比和列百分比',
    ],
  },
  {
    date: '2026-04-10',
    type: 'feat',
    title: '结构方程模型 SEM 上线',
    items: [
      '基于 R/lavaan 实现结构方程模型（SEM），同时估计测量模型和结构模型',
      '新增路径分析（Path Analysis）：分析观测变量之间的直接与间接路径',
      '新增验证性因子分析（CFA）：支持多因子测量模型的 CFA',
      '新增探索性因子分析（EFA）：识别潜在结构与指标归类',
    ],
  },
  {
    date: '2026-04-05',
    type: 'feat',
    title: '效度分析与中介调节效应上线',
    items: [
      '基于 R 引擎实现效度分析：KMO 检验、Bartlett 球形检验和因子载荷',
      '新增中介效应分析（Mediation）：检验单中介模型',
      '新增平行中介效应：多个中介变量并行传递影响',
      '新增链式中介效应：多个中介变量按顺序传递影响',
    ],
  },
  {
    date: '2026-03-28',
    type: 'feat',
    title: '调节效应与 ICC 一致性分析上线',
    items: [
      '新增调节作用分析（Moderation）：分层回归检验调节效应',
      '新增组内相关系数 ICC：基于 R 引擎评估评价者间可靠性',
      '新增多维尺度分析 MDS：基于变量间距离关系建立二维空间坐标',
      '新增 Spearman 等级相关分析：非参数等级相关分析',
    ],
  },
  {
    date: '2026-03-20',
    type: 'feat',
    title: '报告系统升级 — Word 导出与共享',
    items: [
      '分析报告支持导出为 Word 文档（.docx），含标题、表格、图表、说明文字',
      '报告支持生成分享链接，匿名用户可查看',
      '新增报告历史记录管理',
      '报告导出支持三线表样式与学术格式',
    ],
  },
  {
    date: '2026-03-15',
    type: 'feat',
    title: '非参数检验模块上线',
    items: [
      '新增 Mann-Whitney U 检验：比较两个独立组秩次分布',
      '新增 Wilcoxon 符号秩检验：配对样本中位数差异',
      '新增单样本 Wilcoxon 符号秩检验：检验样本中位数是否偏离给定值',
      '新增 Kruskal-Wallis 检验：比较 3 组以上独立样本秩次分布',
      '新增 Friedman 检验：多配对样本秩次差异检验',
    ],
  },
  {
    date: '2026-03-10',
    type: 'feat',
    title: '信度分析与正态性检验上线',
    items: [
      '基于 R 引擎实现 Cronbach\'s α 信度分析',
      '支持折半系数（Split-half）、McDonald Omega、Theta 系数',
      '支持删除项后的信度变化预览',
      '新增正态性检验：Shapiro-Wilk、K-S、Jarque-Bera 综合输出',
      '支持直方图、P-P 图和 Q-Q 图辅助判断正态性',
    ],
  },
  {
    date: '2026-03-05',
    type: 'feat',
    title: '卡方检验与一致性分析上线',
    items: [
      '新增卡方检验：含 Cramer\'s V 效应量，2x2 表自动输出连续性校正',
      '新增卡方拟合优度检验：检验样本分布是否符合理论分布',
      '新增 Cochran\'s Q 检验：比较 3 个以上相关二分类变量比例差异',
      '新增 Kappa 一致性检验：评估两个评价者分类结果的一致性',
      '新增 Kendall 一致性检验：评估多个评价对象排序的一致性（Kendall\'s W）',
    ],
  },
  {
    date: '2026-02-28',
    type: 'feat',
    title: '等价性检验上线',
    items: [
      '新增单样本等价性检验：使用 TOST 检验均值是否落在等价区间内',
      '新增双样本等价性检验：使用 TOST 检验两个独立样本均值的等价性',
      '新增配对样本等价性检验：使用 TOST 检验配对差值的等价性',
    ],
  },
  {
    date: '2026-02-25',
    type: 'feat',
    title: '数据处理功能上线',
    items: [
      '新增数据标签（值标签）管理：支持为分类变量设置标签',
      '新增数据编码：支持反向计分、连续变量离散化',
      '新增异常值处理：Z-Score 法、IQR 法识别异常值',
      '新增无效样本处理：按缺失比例、异常值标记剔除样本',
      '新增缺失值处理：删除、均值/中位数/众数填充、多重插补',
      '新增数据标准化：Z-Score 标准化、Min-Max 归一化',
      '新增数据变换与虚拟变量转换',
    ],
  },
  {
    date: '2026-02-20',
    type: 'feat',
    title: '相关性分析自动求解器上线',
    items: [
      '新增相关性分析自动求解器：自动识别变量特征并推荐合适方法',
      '实现 Pearson / Spearman / Kendall 三种相关系数矩阵',
      '支持显著性检验与星号标注',
      '输出相关矩阵热力图，直观展示变量间关系',
    ],
  },
  {
    date: '2026-02-15',
    type: 'feat',
    title: '多元回归与共线性分析上线',
    items: [
      '新增多元线性回归：模型摘要、B/Beta 系数、VIF 共线性诊断',
      '支持 95% 置信区间输出',
      '新增共线性分析：检测自变量之间的共线性，含 VIF 与容忍度',
      '新增单样本 T 检验：检验样本均值是否显著偏离给定检验值',
    ],
  },
  {
    date: '2026-02-10',
    type: 'feat',
    title: '多维方差分析与协方差分析上线',
    items: [
      '新增多变量方差分析 MANOVA：同时检验多个因变量在组间的总体差异',
      '新增协方差分析 ANCOVA：在控制协变量影响后比较组间均值差异',
    ],
  },
  {
    date: '2026-02-05',
    type: 'feat',
    title: '双因素/三因素方差分析上线',
    items: [
      '新增双因素方差分析：检验两个分类因素及其交互作用',
      '新增三因素方差分析：检验三个分类因素及其交互作用',
      '新增多因素方差分析 N-Way ANOVA：两个以上因素的通用入口',
    ],
  },
  {
    date: '2026-01-25',
    type: 'feat',
    title: '方差分析与事后多重比较上线',
    items: [
      '新增单因素方差分析 One-Way ANOVA：SS/MS/F/eta-squared',
      '支持事后多重比较：LSD / Bonferroni / Tukey 三种方法',
      '新增摘要 T 检验与摘要单因素方差分析：简化封装的快速输出',
    ],
  },
  {
    date: '2026-01-20',
    type: 'feat',
    title: 'T 检验系列上线',
    items: [
      '新增独立样本 T 检验：含 Levene 方差齐性检验和 Cohen\'s d 效应量',
      '新增配对样本 T 检验：含 Cohen\'s d 和配对相关系数',
      '新增摘要 T 检验：独立样本 T 检验的简化摘要封装',
    ],
  },
  {
    date: '2026-01-15',
    type: 'feat',
    title: '综合评价方法（三）上线',
    items: [
      '新增 DEA 数据包络分析：使用 CCR 模型计算各决策单元相对效率',
      '新增 CRITIC 权重法：综合考虑指标对比强度与冲突性客观赋权',
      '新增独立性权系数法：依据指标独立性和离散度构造综合客观权重',
      '新增灰色关联分析：通过比较序列与参考序列接近程度评估关联强弱',
    ],
  },
  {
    date: '2026-01-10',
    type: 'feat',
    title: '综合评价方法（二）上线',
    items: [
      '新增 AHP 层次分析法简化版：基于指标均值近似构造判断矩阵',
      '新增 AHP 层次分析法专业版：补充一致性检验和综合得分',
      '新增耦合协调度：衡量 2-3 个子系统的耦合关系与协调发展水平',
      '新增模糊综合评价：通过模糊隶属度和加权合成得到综合得分',
    ],
  },
  {
    date: '2026-01-05',
    type: 'feat',
    title: '数据管理模块上线',
    items: [
      '支持 CSV、Excel、SPSS（.sav）格式数据文件导入',
      '数据预览：变量列表、前 N 行预览、数据类型推断',
      '数据集管理：新建、重命名、删除、文件夹分类',
      '变量管理：设置测量尺度（名义/有序/连续）、变量类型转换',
    ],
  },
  {
    date: '2025-12-28',
    type: 'feat',
    title: '综合评价方法（一）上线',
    items: [
      '新增 TOPSIS 优劣解距离法：基于与正负理想解的距离排序',
      '新增 RSR 秩和比综合评价法：通过排序后秩和比值排序',
      '新增熵值法（Entropy Method）：依据指标离散程度自动分配客观权重',
      '新增变异系数法：使用变异系数衡量指标离散程度并客观赋权',
    ],
  },
  {
    date: '2025-12-20',
    type: 'feat',
    title: '综合决策与结构模型上线',
    items: [
      '新增 VIKOR 多准则妥协排序法：群体效用与个体遗憾构建折中排序',
      '新增 ISM 解释结构模型：基于变量间相关关系构建多层级的解释结构',
      '新增数据探查功能：数据集规模、变量类型分布、缺失与异常概览',
      '新增交叉分析功能：支持 1 个分组变量对应多个 X 变量',
    ],
  },
  {
    date: '2025-12-15',
    type: 'feat',
    title: '频数分析与描述性统计分析上线',
    items: [
      '频数分析：频数表、百分比、累计百分比、条形图、饼图',
      '描述性统计：均值、中位数、众数、标准差、方差、偏度、峰度',
      '支持按分组输出统计量',
      '支持输出百分位数（四分位数、自定义分位点）',
    ],
  },
  {
    date: '2025-12-10',
    type: 'feat',
    title: '熵权法与权重分析上线',
    items: [
      '新增熵权法权重分析：依据指标离散程度自动分配客观权重',
      '支持问卷分析包中的权重计算场景',
    ],
  },
  {
    date: '2025-12-05',
    type: 'feat',
    title: '变量管理与数据预览功能上线',
    items: [
      '新增变量管理面板：变量列表排序、筛选、搜索',
      '变量行组件支持类型图标与测量尺度标识',
      '新增变量批量重命名功能',
      '新增数据预览工作表组件：支持横向滚动查看全部变量',
    ],
  },
  {
    date: '2025-12-01',
    type: 'feat',
    title: '用户系统与工作台上线',
    items: [
      '用户注册、登录、退出功能',
      'JWT 身份认证与会话管理',
      '工作台主页：数据集列表、分析方法导航、快捷入口',
      '个人中心：密码修改、账户设置',
      'AI 助手侧边栏：智能问答辅助数据分析',
    ],
  },
  {
    date: '2025-11-25',
    type: 'feat',
    title: '数据处理面板与任务中心上线',
    items: [
      '数据处理面板上线，集中管理数据前处理/后处理流程',
      '任务中心：分析任务执行状态实时跟踪',
      '新增实时任务日志查看与中断操作',
      '新增历史记录管理：分析记录保存、筛选、删除',
    ],
  },
  {
    date: '2025-11-20',
    type: 'feat',
    title: '管理后台上线',
    items: [
      '新增管理后台路由与前端页面（AdminApp）',
      '仪表盘概览：系统运行数据统计',
      '用户管理：用户列表、创建、编辑、启用/禁用、重置密码',
      '会话管理：查看/清理活跃会话',
      '任务管理：任务列表与状态筛选',
      '系统信息查看与 AI 配置管理',
    ],
  },
  {
    date: '2025-11-15',
    type: 'feat',
    title: 'R 脚本集成引擎完成',
    items: [
      '搭建 Python 调用 R 脚本的桥接层（rpy2 接口封装）',
      'R 运行时环境检测与自动配置',
      '标准化 R 脚本接口协议：输入输出参数规范',
      '13 个 R 分析脚本开发：信度、效度、因子分析、ICC、中介、调节、路径、SEM、CFA、EFA、区分度',
    ],
  },
  {
    date: '2025-11-10',
    type: 'feat',
    title: '任务调度与异步处理系统上线',
    items: [
      '新增异步任务调度引擎：计划执行与辅助执行双模式',
      '新增任务提交与调度服务：支持长时间分析任务',
      '新增任务容错与故障注入测试',
      '新增运行时控制与沙箱服务：确保分析任务安全隔离',
      '新增任务事件机制：实时监控任务状态变更',
    ],
  },
  {
    date: '2025-11-05',
    type: 'feat',
    title: '数据上传与文件系统上线',
    items: [
      '新增数据上传服务：支持 CSV、Excel、SPSS（.sav）格式',
      '新增上传拖拽组件（UploadDropCard）',
      '新增文件存储抽象层：支持本地文件系统与 S3 云存储',
      '新增文件上传进度追踪与校验',
    ],
  },
  {
    date: '2025-10-28',
    type: 'feat',
    title: '分析方法注册与元数据系统上线',
    items: [
      '搭建分析方法自动注册系统（registry.py），扫描 methods/ 目录自动注册',
      '定义分析方法元数据规范：METHOD_KEY、METHOD_META、run 函数',
      '分析方法分类系统上线：8 大分类、80+ 方法自动归类',
      '新增通用参数构造器与元数据注入器注册表',
    ],
  },
  {
    date: '2025-10-20',
    type: 'feat',
    title: '后端 API 框架搭建完成',
    items: [
      '基于 FastAPI 搭建 RESTful API 层，11 个路由模块',
      '数据访问与业务服务分层：Service 模式',
      '文件存储层：本地文件系统 / 云存储适配',
      '统一的错误处理与请求验证机制',
      '会话管理与数据集版本管理服务',
    ],
  },
  {
    date: '2025-10-15',
    type: 'feat',
    title: '账号体系与权限控制上线',
    items: [
      '用户注册、登录 API，JWT Token 签发与验证',
      '路由守卫机制：公开路由、需登录路由、仅游客路由三级隔离',
      '登录页与注册流程开发',
      '密码重置与账户安全管理',
    ],
  },
  {
    date: '2025-10-10',
    type: 'feat',
    title: '共享报告与法律声明页面上线',
    items: [
      '新增共享报告页面（/share/report/:shareToken）：匿名用户可查看分析报告',
      '新增法律声明页面（/legal）',
      '共享报告支持独立渲染，不依赖用户登录状态',
    ],
  },
  {
    date: '2025-10-05',
    type: 'feat',
    title: '我的数据模块上线',
    items: [
      '新增数据集管理面板：列表/卡片双视图',
      '支持数据文件夹分类管理',
      '数据集上下文菜单：重命名、删除、下载、查看详情',
      '数据集结果展开组件：预览分析输出',
    ],
  },
  {
    date: '2025-09-28',
    type: 'feat',
    title: '分析配置面板与执行引擎上线',
    items: [
      '新增分析配置面板：变量拖拽选择、参数配置',
      '新增分析执行引擎：同步/异步双模式执行',
      '新增分析执行遮罩层：执行过程中的状态反馈',
      '新增分析报告页面：分节展示结果表格、图表、建议、参考文献',
    ],
  },
  {
    date: '2025-09-20',
    type: 'feat',
    title: '图表组件系统搭建',
    items: [
      '通用图表组件封装：柱状图、条形图、饼图、环形图、折线图、雷达图',
      '图表悬浮提示组件（AnalysisChartTooltip）',
      '图表独立保存与复制功能',
      '图表数据展开：查看原始数据明细',
      '分类分布图、交叉分布图、指标对比图三种统一图表协议',
    ],
  },
  {
    date: '2025-09-15',
    type: 'feat',
    title: '前端基础框架搭建完成',
    items: [
      '基于 Vue 3 + Vite 搭建前端工程',
      'Vue Router 路由系统：9 条路由，公共/认证页面隔离',
      'Pinia 状态管理：用户状态、数据集状态、分析任务状态',
      '全局样式系统：统一色彩、排版、间距规范',
      'Axios HTTP 客户端封装，请求/响应拦截器',
      '前端入口文件完成（RootApp/App 分层架构）',
    ],
  },
  {
    date: '2025-09-10',
    type: 'feat',
    title: '结果展示与报告工具链上线',
    items: [
      '新增结果展示组件：表格渲染、指标高亮、显著性星号标注',
      '新增分析建议段落组件（AnalysisAdviceSection）',
      '新增智能分析段落组件（AnalysisSmartSection）',
      '新增参考文献段落组件（AnalysisReferencesSection）',
      '新增报告工具栏：导出、分享、打印',
    ],
  },
  {
    date: '2025-09-05',
    type: 'feat',
    title: 'Composable 组合式函数架构搭建',
    items: [
      '分析相关：useAnalysisConfig / useAnalysisExecution / useAnalysisReport / useAnalysisCharts / useAnalysisShare',
      '数据相关：useDataUpload / useDatasetLibrary / useExpandedResults / useTaskJobs',
      '工作区相关：useAppBootstrap / useWorkspaceNavigation / useWorkspaceDialogs / useWorkspaceExport',
      '通用工具：useClipboardCopy / useScrollReveal / useProfileAccount',
    ],
  },
  {
    date: '2025-08-25',
    type: 'feat',
    title: 'AI 智能分析与预览面板上线',
    items: [
      'AI 助手侧边栏组件（AiAssistant）：智能问答辅助数据分析',
      '新增 AI 配置服务与接口（ai_settings_service）',
      '新增分析结果 AI 解读功能（useAiInterpretation）',
      '新增研究流程面板（ResearchForm）与计划审查面板（PlanReview）',
      '新增数据预览面板（PreviewPane）',
    ],
  },
  {
    date: '2025-08-15',
    type: 'feat',
    title: '数据集版本管理与导入引擎开发',
    items: [
      '新增数据集版本管理服务：版本创建、追溯、回滚',
      '新增上传导入服务（upload_ingest_service）：文件解析与数据入库',
      '新增数据集健康检查与测试',
      '新增数据集生命周期测试覆盖',
    ],
  },
  {
    date: '2025-08-05',
    type: 'feat',
    title: '公式渲染与代码块组件开发',
    items: [
      '新增 FormulaBlock 公式渲染组件：LaTeX 公式实时渲染',
      '新增 CodeBlock 代码块组件：语法高亮与复制',
      '新增通用对话框组件：ConfirmDialog、RenameDialog、UploadDataDialog',
    ],
  },
  {
    date: '2025-07-25',
    type: 'feat',
    title: '工作台交互框架开发',
    items: [
      '新增工作台 TopBar 与侧边栏 AppSidebar',
      '新增步骤导航组件 StepNav：引导用户完成分析流程',
      '新增分析方法导航组件 MethodNav：按分类浏览分析方法',
      '新增首页登录弹窗组件 HomeLoginModal',
    ],
  },
  {
    date: '2025-07-20',
    type: 'feat',
    title: '技术选型与项目立项',
    items: [
      '确定前端技术栈：Vue 3 + Vite + Pinia + Vue Router',
      '确定后端技术栈：Python FastAPI + MySQL + Redis',
      '确定统计分析引擎：Python（SciPy/Statsmodels）+ R 脚本桥接',
      '项目仓库初始化，CI/CD 流水线搭建',
      '产品原型设计与交互方案评审',
    ],
  },
  {
    date: '2025-07-10',
    type: 'feat',
    title: '首页与产品介绍页开发',
    items: [
      '首页（HomeApp）开发：Hero 区域、核心能力展示、产品优势、Footer',
      '首页内容配置化：homePageContent.js 管理页面内容',
      '产品介绍页（AboutApp）初版开发',
      '页面滚动动画效果（useScrollReveal）',
    ],
  },
  {
    date: '2025-06-25',
    type: 'feat',
    title: '赞助与技术支持页面上线',
    items: [
      '新增赞助页面组件（SponsorSection）',
      '新增首页 Footer：GitHub/Gitee 源码链接',
      '首页 FAQ 区上线',
    ],
  },
  {
    date: '2025-06-15',
    type: 'feat',
    title: '测试框架搭建与基础测试覆盖',
    items: [
      '搭建 pytest 测试框架',
      '添加配置文件路径测试、数据库连接池测试',
      '添加数据集服务单元测试',
      '添加 R 引擎桥接测试（因子分析、信度分析）',
      '添加报告导出测试',
    ],
  },
  {
    date: '2025-06-05',
    type: 'feat',
    title: '数据库模型与基础设施搭建',
    items: [
      '数据库模型设计与建表',
      'Redis 缓存集成',
      '基础设施配置：环境配置、日志系统、监控接入',
      '健康检查接口与脚本',
    ],
  },
  {
    date: '2025-05-20',
    type: 'feat',
    title: '项目初始化 — 前后端脚手架',
    items: [
      '前端项目初始化：Vue 3 + Vite 模板搭建',
      '后端项目初始化：FastAPI 项目结构与依赖管理',
      '项目目录结构与编码规范确立',
      'Git 仓库初始化与分支策略定义',
    ],
  },
  {
    date: '2025-05-01',
    type: 'init',
    title: 'SPSSGO 项目诞生',
    items: [
      '产品愿景确立：打造面向科研与教学的在线统计分析平台',
      '核心团队组建：前后端开发、统计分析专家、UI 设计',
      '市场调研与竞品分析：对标 SPSSAU、SPSSPRO 等产品',
      '产品需求文档（PRD）初稿完成',
      '项目代号：SPSSGO（Smart Processing Statistical System Guided Operations）',
    ],
  },
]

const activeEntryIndex = ref(0)
const entryRefs = ref({})

function tagLabel(type) {
  const map = { feat: '功能更新', fix: '问题修复', refactor: '代码重构', docs: '文档改进', init: '初始版本' }
  return map[type] || type
}

function scrollToEntry(index) {
  const el = entryRefs.value[index]
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

let scrollObserver = null
onMounted(() => {
  scrollObserver = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          const idx = Number(entry.target.dataset.entryIndex)
          if (!isNaN(idx)) {
            activeEntryIndex.value = idx
          }
        }
      }
    },
    { rootMargin: '-20% 0px -60% 0px' }
  )

  for (const key of Object.keys(entryRefs.value)) {
    const el = entryRefs.value[key]
    if (el) scrollObserver.observe(el)
  }
})

onUnmounted(() => {
  if (scrollObserver) scrollObserver.disconnect()
})
</script>

<style scoped>
.changelog-page {
  min-height: 100vh;
  background: #f8fafc;
}

/* ===== Top Bar ===== */
.changelog-topbar {
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

.changelog-brand {
  display: inline-flex;
  align-items: center;
  color: #1d4ed8;
  text-decoration: none;
}

.changelog-brand img {
  width: auto;
  height: 30px;
  object-fit: contain;
}

.changelog-topnav {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-right: auto;
  margin-left: 16px;
}

.changelog-topnav a {
  padding: 8px 12px;
  color: #4b5563;
  text-decoration: none;
  font-size: 15px;
  border-radius: 10px;
  transition: all 0.16s ease;
}

.changelog-topnav a:hover,
.changelog-topnav a.active {
  color: #1d4ed8;
  background: #f3f7ff;
}

.changelog-login-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 112px;
  height: 38px;
  padding: 0 18px;
  background: #1d4ed8;
  color: #fff;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  border-radius: 8px;
  transition: background 0.2s ease;
}

.changelog-login-btn:hover {
  background: #1e40af;
}

/* ===== Hero ===== */
.changelog-hero {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 22px 50px;
  overflow: hidden;
}

.changelog-hero-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.changelog-hero-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.35;
}

.changelog-hero-glow--1 {
  width: 420px;
  height: 420px;
  top: -140px;
  left: -60px;
  background: #3b82f6;
}

.changelog-hero-glow--2 {
  width: 360px;
  height: 360px;
  bottom: -120px;
  right: -40px;
  background: #8b5cf6;
}

.changelog-hero-body {
  position: relative;
  text-align: center;
  max-width: 680px;
}

.changelog-hero-badge {
  display: inline-flex;
  padding: 6px 18px;
  background: #eef2ff;
  color: #4f46e5;
  font-size: 13px;
  font-weight: 600;
  border-radius: 999px;
  margin-bottom: 18px;
}

.changelog-hero-title {
  font-size: 42px;
  font-weight: 800;
  color: #111827;
  line-height: 1.2;
  margin: 0 0 14px;
}

.changelog-hero-desc {
  font-size: 16px;
  color: #6b7280;
  line-height: 1.7;
  margin: 0;
}

/* ===== Shell (Sidebar + Content) ===== */
.changelog-shell {
  display: flex;
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 22px 80px;
  gap: 40px;
}

/* ===== Sidebar ===== */
.changelog-sidebar {
  position: sticky;
  top: 100px;
  flex-shrink: 0;
  width: 220px;
  max-height: calc(100vh - 120px);
  overflow-y: auto;
  overflow-x: hidden;
  overscroll-behavior: contain;
  scrollbar-gutter: stable;
  align-self: flex-start;
}

:global(.changelog-sidebar::-webkit-scrollbar) {
  width: 5px;
}

:global(.changelog-sidebar::-webkit-scrollbar-track) {
  background: transparent;
}

:global(.changelog-sidebar::-webkit-scrollbar-thumb) {
  background: #e2e5ea;
  border-radius: 8px;
}

:global(.changelog-sidebar::-webkit-scrollbar-thumb:hover) {
  background: #d1d5db;
}

.changelog-sidebar-title {
  font-size: 13px;
  font-weight: 700;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
  padding-left: 4px;
}

.changelog-sidebar-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
  width: 100%;
  padding: 8px 10px;
  margin-bottom: 4px;
  background: none;
  border: none;
  border-radius: 8px;
  text-align: left;
  cursor: pointer;
  transition: all 0.15s ease;
}

.changelog-sidebar-item:hover {
  background: #f3f4f6;
}

.changelog-sidebar-item.active {
  background: #eef2ff;
}

.changelog-sidebar-date {
  font-size: 11px;
  color: #9ca3af;
  font-weight: 500;
}

.changelog-sidebar-item.active .changelog-sidebar-date {
  color: #4f46e5;
}

.changelog-sidebar-label {
  font-size: 13px;
  color: #374151;
  font-weight: 500;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.changelog-sidebar-item.active .changelog-sidebar-label {
  color: #4f46e5;
  font-weight: 600;
}

/* ===== Timeline ===== */
.changelog-timeline {
  flex: 1;
  min-width: 0;
  position: relative;
  padding-left: 32px;
}

.changelog-timeline::before {
  content: '';
  position: absolute;
  left: 0;
  top: 8px;
  bottom: 8px;
  width: 2px;
  background: #e5e7eb;
}

.changelog-entry {
  position: relative;
  padding-left: 20px;
  margin-bottom: 32px;
  scroll-margin-top: 100px;
}

.changelog-entry:last-child {
  margin-bottom: 0;
}

.changelog-entry-marker {
  position: absolute;
  left: -7px;
  top: 6px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #fff;
  border: 3px solid #3b82f6;
  z-index: 1;
}

.changelog-entry-card {
  background: #fff;
  border: 1px solid #edf1f5;
  border-radius: 12px;
  padding: 20px 24px;
  transition: box-shadow 0.2s ease;
}

.changelog-entry-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

.changelog-entry-head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.changelog-entry-date {
  font-size: 13px;
  color: #9ca3af;
  font-weight: 500;
  white-space: nowrap;
}

.changelog-entry-tag {
  display: inline-flex;
  padding: 2px 10px;
  font-size: 11px;
  font-weight: 600;
  border-radius: 999px;
  white-space: nowrap;
}

.changelog-entry-tag--feat {
  background: #eef2ff;
  color: #4f46e5;
}

.changelog-entry-tag--fix {
  background: #fef2f2;
  color: #dc2626;
}

.changelog-entry-tag--docs {
  background: #f0fdf4;
  color: #16a34a;
}

.changelog-entry-tag--init {
  background: #f5f3ff;
  color: #7c3aed;
}

.changelog-entry-tag--refactor {
  background: #fff7ed;
  color: #c2410c;
}

.changelog-entry-title {
  font-size: 17px;
  font-weight: 700;
  color: #111827;
  margin: 0 0 10px;
}

.changelog-entry-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.changelog-entry-list li {
  position: relative;
  padding-left: 16px;
  font-size: 14px;
  color: #4b5563;
  line-height: 1.7;
}

.changelog-entry-list li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 10px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #d1d5db;
}

/* ===== Responsive ===== */
@media (max-width: 900px) {
  .changelog-shell {
    flex-direction: column;
    padding: 0 14px 60px;
    gap: 0;
  }

  .changelog-sidebar {
    position: relative;
    top: auto;
    width: 100%;
    max-height: none;
    overflow-y: visible;
    margin-bottom: 32px;
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  .changelog-sidebar-title {
    width: 100%;
    margin-bottom: 8px;
  }

  .changelog-sidebar-item {
    width: auto;
    padding: 6px 12px;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
  }

  .changelog-sidebar-label {
    -webkit-line-clamp: 1;
  }

  .changelog-timeline {
    padding-left: 24px;
  }
}

@media (max-width: 768px) {
  .changelog-topbar {
    padding: 0 14px;
  }

  .changelog-topnav {
    display: none;
  }

  .changelog-hero {
    padding: 40px 14px 30px;
  }

  .changelog-hero-title {
    font-size: 28px;
  }

  .changelog-entry-card {
    padding: 16px 18px;
  }
}
</style>
