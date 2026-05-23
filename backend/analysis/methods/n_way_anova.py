# -*- coding: utf-8 -*-
# 多因素方差分析主流程：这里只做参数整理和 R 引擎桥接，统计口径放在 R 脚本里。
# 默认使用无交互主效应模型；交互模型走双因素/三因素专门入口，别在这里混。
from io import StringIO

from backend.analysis.common import *
from backend.analysis.methods.two_way_anova import _as_list
from backend.r_runner import RExecutionError, is_r_runtime_available, run_r_script

METHOD_KEY = "n_way_anova"
METHOD_META = {'label': '多因素方差分析',
 'category': '差异对比分析包',
 'description': '检验多个分类因素对因变量的影响',
 'order': 50,
 'slots': [{'key': 'dependent', 'label': 'Y', 'type': 'single', 'accept': 'numeric', 'hint': '放入因变量'},
           {'key': 'factors', 'label': 'X', 'type': 'multiple', 'accept': 'categorical', 'min': 2, 'hint': '放入2个及以上分组因素'}],
 'options': [{'key': 'do_post_hoc', 'label': '事后多重比较', 'type': 'checkbox', 'default': False},
             {'key': 'post_hoc_method', 'label': '方法选择', 'choices': ['LSD', 'Tukey法', 'Bonferroni校正', 'Sidak法'], 'default': 'LSD',
              'hint': '默认不进行事后多重比较，可选比如LSD等事后多重比较检验方法。'},
             {'key': 'include_effect_size', 'label': '效应量', 'type': 'checkbox', 'default': False,
              'hint': '选中后结果表格中会输出效应量。'}],
 'param_builder': 'direct'}


def _truthy(value, default=False):
    if value is None:
        return default
    return value in (True, "true", "1", 1, "是", "yes", "on")


def run(df, params):
    factors = _resolve_cols(df, _as_list(params.get("factors", [])))
    dependent = params.get("dependent", "")
    covariates = _resolve_cols(df, _as_list(params.get("covariates", [])))
    do_post_hoc = _truthy(params.get("do_post_hoc"), False)
    include_effect_size = _truthy(params.get("include_effect_size"), False)
    post_hoc_method = str(params.get("post_hoc_method", "LSD") or "LSD")

    if len(factors) < 2:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "分组变量X需要放入至少2个定类变量。"}
    needed = factors + [dependent] + covariates
    if any(not col or col not in df.columns for col in needed):
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "因素变量、因变量或协变量不存在。"}

    csv_buffer = StringIO()
    df[needed].to_csv(csv_buffer, index=False)
    payload = {
        "factors": factors,
        "dependent": dependent,
        "covariates": covariates,
        "do_post_hoc": do_post_hoc,
        "post_hoc_method": post_hoc_method,
        "include_effect_size": include_effect_size,
        "data_file": "n_way_anova_input.csv",
    }
    if not is_r_runtime_available():
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "R 运行环境不可用，多因素方差分析需要 R 引擎执行。"}
    try:
        result = run_r_script("n_way_anova.R", payload=payload, temp_files={"n_way_anova_input.csv": csv_buffer.getvalue()})
    except RExecutionError as exc:
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": f"R 多因素方差分析执行失败：{str(exc)}"}
    if isinstance(result, dict) and result.get("success"):
        return {
            "name": result.get("name") or METHOD_META["label"],
            "headers": result.get("headers") or [],
            "rows": result.get("rows") or [],
            "description": result.get("description") or "多因素方差分析完成。",
            "sections": result.get("sections") or [],
        }
    if isinstance(result, dict) and result.get("error"):
        return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": str(result["error"])}
    return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": "R 多因素方差分析未返回有效结果。"}
