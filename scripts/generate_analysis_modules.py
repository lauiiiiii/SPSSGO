# -*- coding: utf-8 -*-
import ast
from pathlib import Path
from pprint import pformat
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = ROOT / "backend" / "analysis_templates.py"
METHODS_DIR = ROOT / "backend" / "analysis" / "methods"


EXISTING_METHODS = {
    "data_overview": {"function": "data_overview"},
    "descriptive": {"function": "descriptive"},
    "reliability": {"function": "reliability_analysis"},
    "factor_analysis": {"function": "factor_analysis_check"},
    "frequency": {"function": "frequency_table", "metadata_injector": "frequency_labels"},
    "cross_tabulation": {"function": "cross_tabulation_analysis", "metadata_injector": "cross_labels"},
    "category_summary": {"function": "category_summary", "metadata_injector": "group_labels"},
    "pearson_correlation": {"function": "pearson_correlation"},
    "multiple_choice": {"function": "multiple_choice_analysis", "metadata_injector": "multiple_choice_labels"},
    "survey_cross_tab": {"function": "survey_cross_tabulation", "metadata_injector": "cross_labels"},
    "correspondence_analysis": {"function": "correspondence_analysis", "metadata_injector": "cross_labels"},
    "confirmatory_factor_analysis": {"function": "confirmatory_factor_analysis"},
    "kano": {"function": "kano_analysis"},
    "independent_t_test": {"function": "independent_t_test", "metadata_injector": "group_labels"},
    "paired_t_test": {"function": "paired_t_test"},
    "anova_oneway": {"function": "anova_oneway", "metadata_injector": "group_labels"},
    "chi_square": {"function": "chi_square_test", "metadata_injector": "cross_labels"},
    "multiple_regression": {"function": "multiple_regression"},
    "mediation": {"function": "mediation_analysis"},
    "moderation": {"function": "moderation_analysis"},
    "vif": {"function": "vif_analysis"},
    "normality_test": {"function": "normality_test"},
    "spearman_correlation": {"function": "spearman_correlation"},
    "mds": {"function": "multidimensional_scaling_analysis"},
}


PREVIEW_METHODS = {
    "choice_multi_multi": {
        "label": "选择题【多选&多选】",
        "category": "高级问卷分析包",
        "description": "比较两组多选题之间的联合选择结构，适合研究题项组合与共现关系",
        "order": 100,
        "slots": [
            {"key": "variables_a", "label": "多选题A", "type": "multiple", "accept": "categorical", "min": 2, "hint": "放入第一组多选题变量"},
            {"key": "variables_b", "label": "多选题B", "type": "multiple", "accept": "categorical", "min": 2, "hint": "放入第二组多选题变量"},
        ],
        "options": [],
        "message": "当前版本已将该方法拆成独立模块并完成统一注册，后续可直接在本文件中接入多选题共现矩阵、交叉提升度和显著性分析。",
    },
    "choice_multi_single": {
        "label": "选择题【多选&单选】",
        "category": "高级问卷分析包",
        "description": "比较不同单选分组在多选题上的选择偏好差异",
        "order": 110,
        "slots": [
            {"key": "multiple_vars", "label": "多选题变量", "type": "multiple", "accept": "categorical", "min": 2, "hint": "放入同一题目的多选拆分变量"},
            {"key": "single_var", "label": "单选分组变量", "type": "single", "accept": "categorical", "hint": "放入用于分组的单选题变量"},
        ],
        "options": [],
        "message": "当前模块已独立，可继续扩展多选占比、组间差异和重点选项对比。",
    },
    "choice_single_multi": {
        "label": "选择题【单选&多选】",
        "category": "高级问卷分析包",
        "description": "从单选结果出发，分析不同单选人群在多选题上的偏好扩展",
        "order": 120,
        "slots": [
            {"key": "single_var", "label": "单选变量", "type": "single", "accept": "categorical", "hint": "放入单选题变量"},
            {"key": "multiple_vars", "label": "多选题变量", "type": "multiple", "accept": "categorical", "min": 2, "hint": "放入同一题目的多选拆分变量"},
        ],
        "options": [],
        "message": "当前模块已独立，可继续扩展单选分组下的多选偏好画像和显著性比较。",
    },
    "nps": {
        "label": "NPS净推荐值分析",
        "category": "高级问卷分析包",
        "description": "基于 0-10 推荐评分计算贬损者、被动者、推荐者及净推荐值",
        "order": 130,
        "slots": [
            {"key": "score_var", "label": "NPS评分变量", "type": "single", "accept": "numeric", "hint": "放入 0-10 推荐评分变量"},
        ],
        "options": [],
        "message": "当前模块已独立，可继续在本文件中扩展人群细分 NPS、趋势对比和标签映射。",
    },
    "discrimination": {
        "label": "区分度分析",
        "category": "高级问卷分析包",
        "description": "检验题项是否能够有效区分高水平与低水平样本",
        "order": 140,
        "slots": [
            {"key": "variables", "label": "题项变量", "type": "multiple", "accept": "numeric", "min": 2, "hint": "放入量表题项"},
        ],
        "options": [],
        "message": "当前模块已独立，可继续扩展 CRIT、高低组 t 检验和项目删除建议。",
    },
    "conjoint": {
        "label": "联合分析",
        "category": "高级问卷分析包",
        "description": "估计用户对多个属性水平的偏好权重",
        "order": 150,
        "slots": [
            {"key": "score_var", "label": "偏好评分变量", "type": "single", "accept": "numeric", "hint": "放入评分或偏好变量"},
            {"key": "attribute_vars", "label": "属性变量", "type": "multiple", "accept": "categorical", "min": 2, "hint": "放入属性水平变量"},
        ],
        "options": [],
        "message": "当前模块已独立，可继续接入 part-worth 效用、属性重要性和产品模拟。",
    },
    "path_analysis": {
        "label": "路径分析",
        "category": "高级回归&因果分析包",
        "description": "分析多个观测变量之间的直接路径与间接路径，输出直接效应、间接效应、总效应及修正指数",
        "order": 100,
        "slots": [
            {"key": "independent_vars", "label": "自变量(X)", "type": "multiple", "accept": "numeric", "min": 1, "hint": "放入外生自变量"},
            {"key": "dependent_vars", "label": "因变量(M/Y)", "type": "multiple", "accept": "numeric", "min": 2, "hint": "放入参与路径的因变量/中介变量（按因果顺序排列）"},
        ],
        "options": [],
        "message": "当前模块已独立，支持多方程模型、直接/间接/总效应分解、修正指数和路径图。",
    },
    "sem": {
        "label": "结构方程模型(SEM)",
        "category": "高级回归&因果分析包",
        "description": "同时估计测量模型和结构模型，适合潜变量与复杂理论检验",
        "order": 110,
        "slots": [
            {"key": "measurement_vars", "label": "测量题项", "type": "multiple", "accept": "numeric", "min": 3, "hint": "放入潜变量题项"},
        ],
        "options": [],
        "message": "当前模块已独立，可继续接入测量模型、路径模型和拟合指标输出。",
    },
    "entropy_weight": {
        "label": "权重分析",
        "category": "高级问卷分析包",
        "description": "支持 AHP 权重、熵值法和优序图法计算指标权重",
        "order": 160,
        "slots": [
            {"key": "variables", "label": "指标变量", "type": "multiple", "accept": "numeric", "min": 2, "hint": "放入综合评价指标"},
        ],
        "options": [
            {"key": "analysis_method", "label": "分析方法", "choices": [
                {"value": "ahp", "label": "AHP权重"},
                {"value": "entropy", "label": "熵值法"},
                {"value": "ranking", "label": "优序图法"},
            ], "default": "ranking"},
        ],
        "message": "当前模块已独立，可继续扩展 AHP 权重、熵值法、优序图法和综合得分。",
    },
    "maxdiff": {
        "label": "MaxDiff模型",
        "category": "高级问卷分析包",
        "description": "基于最好/最差选择结果恢复偏好强度与优先级排序",
        "order": 170,
        "slots": [
            {"key": "variables", "label": "MaxDiff任务变量", "type": "multiple", "accept": "categorical", "min": 2, "hint": "放入 MaxDiff 任务相关变量"},
        ],
        "options": [],
        "message": "当前模块已独立，可继续接入 best-worst 计分、HB 模型和分层偏好恢复。",
    },
    "price_breakpoint": {
        "label": "价格断裂点模型",
        "category": "高级问卷分析包",
        "description": "识别价格敏感度研究中的心理接受边界与关键交点",
        "order": 180,
        "slots": [
            {"key": "too_cheap", "label": "太便宜", "type": "single", "accept": "numeric", "hint": "放入“太便宜”价格变量"},
            {"key": "cheap", "label": "便宜", "type": "single", "accept": "numeric", "hint": "放入“便宜”价格变量"},
            {"key": "expensive", "label": "贵", "type": "single", "accept": "numeric", "hint": "放入“贵”价格变量"},
            {"key": "too_expensive", "label": "太贵", "type": "single", "accept": "numeric", "hint": "放入“太贵”价格变量"},
        ],
        "options": [],
        "message": "当前模块已独立，可继续扩展 PSM 曲线、交点求解和价格带建议。",
    },
    "parallel_mediation": {
        "label": "平行中介效应",
        "category": "高级回归&因果分析包",
        "description": "检验多个中介变量是否并行传递自变量对因变量的影响",
        "order": 120,
        "slots": [
            {"key": "x", "label": "自变量(X)", "type": "single", "accept": "numeric", "hint": "放入自变量"},
            {"key": "mediators", "label": "中介变量(M)", "type": "multiple", "accept": "numeric", "min": 2, "hint": "放入并行中介变量"},
            {"key": "y", "label": "因变量(Y)", "type": "single", "accept": "numeric", "hint": "放入因变量"},
        ],
        "options": [],
        "message": "当前模块已独立，可继续扩展并行路径系数、间接效应与 Bootstrap 区间。",
    },
    "serial_mediation": {
        "label": "链式中介效应",
        "category": "高级回归&因果分析包",
        "description": "检验多个中介变量按顺序传递影响的链式作用",
        "order": 130,
        "slots": [
            {"key": "x", "label": "自变量(X)", "type": "single", "accept": "numeric", "hint": "放入自变量"},
            {"key": "mediators", "label": "链式中介变量(M)", "type": "multiple", "accept": "numeric", "min": 2, "hint": "按顺序放入中介变量"},
            {"key": "y", "label": "因变量(Y)", "type": "single", "accept": "numeric", "hint": "放入因变量"},
        ],
        "options": [],
        "message": "当前模块已独立，可继续扩展链式路径系数、总间接效应与 Bootstrap 区间。",
    },
    "turf": {
        "label": "TURF分析",
        "category": "高级问卷分析包",
        "description": "寻找在给定数量约束下覆盖最多受众的最优选项组合",
        "order": 190,
        "slots": [
            {"key": "variables", "label": "覆盖项变量", "type": "multiple", "accept": "categorical", "min": 2, "hint": "放入 0/1 覆盖变量"},
        ],
        "options": [
            {"key": "combo_size", "label": "组合大小", "choices": ["2", "3", "4"], "default": "3"},
        ],
        "message": "当前模块已独立，可继续扩展覆盖率、增量覆盖和最优组合搜索。",
    },
    "penalty_analysis": {
        "label": "惩罚分析",
        "category": "高级问卷分析包",
        "description": "识别属性表现偏低时对总体满意度的拖累程度",
        "order": 200,
        "slots": [
            {"key": "satisfaction_var", "label": "总体满意度", "type": "single", "accept": "numeric", "hint": "放入总体满意度变量"},
            {"key": "attribute_vars", "label": "属性表现变量", "type": "multiple", "accept": "numeric", "min": 1, "hint": "放入属性评分变量"},
        ],
        "options": [],
        "message": "当前模块已独立，可继续扩展低分惩罚值、优先改进项和散点矩阵。",
    },
    "bpto": {
        "label": "品牌价格抵补模型BPTO",
        "category": "高级问卷分析包",
        "description": "评估品牌优势是否足以抵补价格劣势",
        "order": 210,
        "slots": [
            {"key": "choice_var", "label": "选择结果", "type": "single", "accept": "categorical", "hint": "放入选择结果变量"},
            {"key": "brand_var", "label": "品牌变量", "type": "single", "accept": "categorical", "hint": "放入品牌变量"},
            {"key": "price_var", "label": "价格变量", "type": "single", "accept": "numeric", "hint": "放入价格变量"},
        ],
        "options": [],
        "message": "当前模块已独立，可继续扩展品牌溢价区间、替代边界和竞争格局图。",
    },
    "cbc_conjoint": {
        "label": "联合分析CBC",
        "category": "高级问卷分析包",
        "description": "基于选择任务的联合分析，更贴近真实购买场景",
        "order": 220,
        "slots": [
            {"key": "choice_var", "label": "选择结果", "type": "single", "accept": "categorical", "hint": "放入选择任务结果变量"},
            {"key": "attribute_vars", "label": "属性变量", "type": "multiple", "accept": "categorical", "min": 2, "hint": "放入 CBC 属性变量"},
        ],
        "options": [],
        "message": "当前模块已独立，可继续接入 choice-based conjoint 效用估计和市场模拟。",
    },
    "maxdiff_pro": {
        "label": "MaxDiff Pro",
        "category": "高级问卷分析包",
        "description": "强调个体层效用恢复与高级模拟能力的 MaxDiff 扩展方法",
        "order": 230,
        "slots": [
            {"key": "variables", "label": "MaxDiff任务变量", "type": "multiple", "accept": "categorical", "min": 2, "hint": "放入 MaxDiff 任务变量"},
        ],
        "options": [],
        "message": "当前模块已独立，可继续扩展个体层效用恢复、细分人群偏好和模拟结果。",
    },
}


def extract_function_sources(source_text: str):
    tree = ast.parse(source_text)
    lines = source_text.splitlines()
    sources = {}
    method_meta = {}

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            start = node.lineno - 1
            end = node.end_lineno
            sources[node.name] = "\n".join(lines[start:end]) + "\n"
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "METHOD_META":
                    method_meta = ast.literal_eval(node.value)

    return sources, method_meta


def module_text_for_existing(method_key: str, function_name: str, meta: dict, metadata_injector: str | None):
    lines = [
        "# -*- coding: utf-8 -*-",
        "from backend.analysis.common import *",
        "",
        f'METHOD_KEY = "{method_key}"',
        f"METHOD_META = {pformat(meta, width=100, sort_dicts=False)}",
    ]
    if metadata_injector:
        lines.append(f'METADATA_INJECTOR = "{metadata_injector}"')
    lines.extend([
        "",
        FUNCTION_SOURCES[function_name].rstrip(),
        "",
        f"run = {function_name}",
        "",
    ])
    return "\n".join(lines)


def module_text_for_preview(method_key: str, config: dict):
    meta = {
        "label": config["label"],
        "category": config["category"],
        "description": config["description"],
        "order": config["order"],
        "slots": config["slots"],
        "options": config.get("options", []),
        "param_builder": "direct",
    }
    suggestions = [
        "当前文件已经从总模板中拆出，后续算法开发不会再影响其它方法。",
        "如果要继续落地算法，可直接在本模块中补充统计逻辑、图表和结果解释。",
    ]
    return "\n".join(
        [
            "# -*- coding: utf-8 -*-",
            "from backend.analysis.common import build_preview_result",
            "",
            f'METHOD_KEY = "{method_key}"',
            f"METHOD_META = {pformat(meta, width=100, sort_dicts=False)}",
            "",
            "",
            "def run(df, params):",
            "    return build_preview_result(",
            '        METHOD_META["label"],',
            "        params,",
            f"        {config['message']!r},",
            f"        suggestions={suggestions!r},",
            "    )",
            "",
        ]
    )


if __name__ == "__main__":
    source_text = SOURCE_FILE.read_text(encoding="utf-8")
    FUNCTION_SOURCES, method_meta_map = extract_function_sources(source_text)
    METHODS_DIR.mkdir(parents=True, exist_ok=True)

    init_file = METHODS_DIR / "__init__.py"
    if not init_file.exists():
        init_file.write_text("# -*- coding: utf-8 -*-\n", encoding="utf-8")

    for method_key, config in EXISTING_METHODS.items():
        module_path = METHODS_DIR / f"{method_key}.py"
        module_path.write_text(
            module_text_for_existing(
                method_key=method_key,
                function_name=config["function"],
                meta=method_meta_map[method_key],
                metadata_injector=config.get("metadata_injector"),
            ),
            encoding="utf-8",
        )

    for method_key, config in PREVIEW_METHODS.items():
        module_path = METHODS_DIR / f"{method_key}.py"
        module_path.write_text(module_text_for_preview(method_key, config), encoding="utf-8")
