# -*- coding: utf-8 -*-
# ISM 解释结构模型法，纯 Python 实现（布尔矩阵运算 + 图论层级划分）。
# 输入为邻接矩阵或可达矩阵，输出骨架矩阵、可达矩阵、可达集/先行集、层级分解和有向图。
from backend.analysis.common import *
import math

METHOD_KEY = "ism"

DATA_TYPE_CHOICES = [
    {"value": "adjacency", "label": "邻接矩阵"},
    {"value": "reachability", "label": "可达矩阵"},
]
DATA_TYPE_MAP = {item["value"]: item for item in DATA_TYPE_CHOICES}
DATA_TYPE_ALIAS = {
    "邻接矩阵": "adjacency",
    "adjacency": "adjacency",
    "可达矩阵": "reachability",
    "reachability": "reachability",
}

DECOMPOSITION_CHOICES = [
    {"value": "hierarchy", "label": "层次分解"},
    {"value": "up", "label": "结果优先-UP型"},
    {"value": "down", "label": "原因优先-DOWN型"},
]
DECOMPOSITION_MAP = {item["value"]: item for item in DECOMPOSITION_CHOICES}
DECOMPOSITION_ALIAS = {
    "层次分解": "hierarchy",
    "hierarchy": "hierarchy",
    "结果优先": "up",
    "结果优先-UP型": "up",
    "up": "up",
    "原因优先": "down",
    "原因优先-DOWN型": "down",
    "down": "down",
}

METHOD_META = {
    "label": "解释结构模型法(ISM)",
    "category": "综合评价",
    "description": "通过可达矩阵分析要素间的层级结构关系，支持邻接矩阵/可达矩阵输入和多种分解方式",
    "order": 135,
    "aliases": ["ISM", "解释结构模型", "Interpretive Structural Modeling"],
    "slots": [],
    "options": [
        {
            "key": "data_type",
            "label": "数据类型",
            "choices": DATA_TYPE_CHOICES,
            "default": "adjacency",
            "hint": "邻接矩阵为原始数据矩阵，后端自动计算可达矩阵；可达矩阵为已计算好的矩阵，直接使用。",
        },
        {
            "key": "decomposition_method",
            "label": "分解方式",
            "choices": DECOMPOSITION_CHOICES,
            "default": "up",
            "hint": "层次分解为标准层级划分；结果优先-UP型从结果要素向上追溯；原因优先-DOWN型从原因要素向下推导。",
        },
    ],
    "param_builder": "direct",
}


def _error(message):
    return {"name": METHOD_META["label"], "headers": [], "rows": [], "description": message}


def _clean_data_type(value):
    if value in (None, ""):
        return "adjacency"
    text = str(value).strip()
    if text in DATA_TYPE_ALIAS:
        return DATA_TYPE_ALIAS[text]
    return DATA_TYPE_ALIAS.get(text.lower(), "adjacency")


def _clean_decomposition(value):
    if value in (None, ""):
        return "up"
    text = str(value).strip()
    if text in DECOMPOSITION_ALIAS:
        return DECOMPOSITION_ALIAS[text]
    return DECOMPOSITION_ALIAS.get(text.lower(), "up")


def _coerce_to_numeric(cell):
    """将单元格内容强制转换为 0/1 数值，非 1 的值均视为 0。"""
    if cell in (0, 1):
        return cell
    if isinstance(cell, (int, float)):
        return 1 if cell == 1 else 0
    text = str(cell).strip().lower()
    return 1 if text in ('1', 'true', 'yes', '是', 'y') else 0


def _parse_matrix(value):
    """解析矩阵输入，支持字符串/数值混合的二维数组。"""
    if not isinstance(value, (list, tuple)):
        return None
    if not value:
        return None
    if isinstance(value[0], (list, tuple)):
        n = len(value)
        for row in value:
            if not isinstance(row, (list, tuple)):
                return None
        max_cols = max(len(row) for row in value)
        if max_cols != n:
            return None
        return [[_coerce_to_numeric(cell) for cell in row] for row in value]
    # 扁平数组（按行优先展开为 n×n 矩阵）
    total = len(value)
    n = int(total ** 0.5)
    if n * n != total:
        return None
    matrix = []
    for i in range(n):
        matrix.append([_coerce_to_numeric(value[i * n + j]) for j in range(n)])
    return matrix


def _validate_matrix(matrix, labels, name="矩阵"):
    """校验矩阵合法性。"""
    n = len(labels)
    if not matrix or len(matrix) != n:
        return f"{name}行数与要素数量不匹配（{len(matrix) if matrix else 0} vs {n}）。"
    for i, row in enumerate(matrix):
        if len(row) != n:
            return f"{name}第{i+1}行列数不匹配（{len(row)} vs {n}）。"
        for j, cell in enumerate(row):
            if cell not in (0, 1):
                return f"{name}[{i+1}][{j+1}] 的值必须为 0 或 1（当前为 {cell}）。"
    return ""


def _bool_matrix_multiply(a, b):
    """布尔矩阵乘法（OR-AND 半环）。"""
    n = len(a)
    result = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            result[i][j] = 1 if any(a[i][k] and b[k][j] for k in range(n)) else 0
    return result


def _bool_matrix_add(a, b):
    """布尔矩阵加法（逐元素 OR）。"""
    n = len(a)
    return [[a[i][j] | b[i][j] for j in range(n)] for i in range(n)]


def _identity_matrix(n):
    """n×n 单位矩阵。"""
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def _matrices_equal(a, b):
    """判断两个矩阵是否相等。"""
    n = len(a)
    for i in range(n):
        for j in range(n):
            if a[i][j] != b[i][j]:
                return False
    return True


def _compute_reachability(adjacency):
    """计算可达矩阵 M = (A + I)^k（布尔幂，直到收敛）。"""
    n = len(adjacency)
    identity = _identity_matrix(n)
    current = _bool_matrix_add(adjacency, identity)
    while True:
        next_matrix = _bool_matrix_multiply(current, current)
        if _matrices_equal(current, next_matrix):
            break
        current = next_matrix
    return current


def _compute_skeleton(reachability):
    """
    计算骨架矩阵：从可达矩阵中去除传递边。
    对每个 M[i][j]=1，若存在中间节点 k 使得 M[i][k]=1 且 M[k][j]=1，则 (i,j) 是传递边，去除。
    """
    n = len(reachability)
    skeleton = [row[:] for row in reachability]  # 深拷贝
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if skeleton[i][j] != 1:
                continue
            # 检查是否存在中间节点 k
            is_transitive = False
            for k in range(n):
                if k == i or k == j:
                    continue
                if reachability[i][k] == 1 and reachability[k][j] == 1:
                    is_transitive = True
                    break
            if is_transitive:
                skeleton[i][j] = 0
    return skeleton


def _compute_reachability_sets(reachability):
    """计算每个要素的可达集 R(i)、先行集 A(i)、交集 C(i)。"""
    n = len(reachability)
    sets = []
    for i in range(n):
        r = {j for j in range(n) if reachability[i][j] == 1}
        a = {j for j in range(n) if reachability[j][i] == 1}
        c = r & a
        sets.append({
            "index": i,
            "r": sorted(r),
            "a": sorted(a),
            "c": sorted(c),
        })
    return sets


def _decompose_levels(sets, labels, method):
    """层级划分算法。"""
    n = len(sets)
    remaining = set(range(n))
    levels = []
    level_num = 0

    while remaining:
        level_num += 1
        current_level = []
        for i in remaining:
            r_set = set(sets[i]["r"]) & remaining
            a_set = set(sets[i]["a"]) & remaining
            c_set = r_set & a_set
            if r_set == c_set:
                current_level.append(i)
        if not current_level:
            break
        levels.append(sorted(current_level))
        remaining -= set(current_level)

    # 根据分解方式调整层级顺序
    if method == "up":
        levels = levels[::-1]  # 结果优先：结果要素在上
    elif method == "down":
        pass  # 原因优先：原因要素在上（标准顺序）

    return levels


def _build_circular_graph(labels, edge_matrix):
    """构建圆形布局的有向图数据（对齐 SPSSAU 有向图）。"""
    n = len(labels)
    if n == 0:
        return {"nodes": [], "edges": [], "width": 400, "height": 400}

    # 根据节点数量动态调整半径，减少空白
    radius = max(120, n * 28)
    margin = 40
    cx = radius + margin
    cy = radius + margin
    width = cx + radius + margin
    height = cy + radius + margin

    nodes = []
    node_positions = {}

    for i in range(n):
        angle = 2 * math.pi * i / n - math.pi / 2
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        nodes.append({
            "index": i,
            "label": labels[i],
            "x": round(x, 1),
            "y": round(y, 1),
        })
        node_positions[i] = (x, y)

    edges = []
    for i in range(n):
        for j in range(n):
            if i != j and edge_matrix[i][j] == 1:
                edges.append({
                    "from": i,
                    "to": j,
                    "from_pos": [round(node_positions[i][0], 1), round(node_positions[i][1], 1)],
                    "to_pos": [round(node_positions[j][0], 1), round(node_positions[j][1], 1)],
                })

    return {
        "nodes": nodes,
        "edges": edges,
        "width": round(width),
        "height": round(height),
        "layout": "circular",
    }


def _build_hierarchical_graph(labels, levels, edge_matrix):
    """
    构建层次布局的有向图数据（对齐 SPSSAU 层次关系示意图）。
    节点按层级分行排列，同一层级的节点水平均匀分布。
    """
    n = len(labels)
    if n == 0:
        return {"nodes": [], "edges": [], "width": 400, "height": 400}

    node_w = 70
    node_h = 36
    h_gap = 20
    v_gap = 80
    margin = 60

    num_levels = len(levels)
    max_nodes_in_level = max(len(level) for level in levels) if levels else 1
    width = margin * 2 + max_nodes_in_level * (node_w + h_gap) - h_gap
    height = margin * 2 + num_levels * (node_h + v_gap) - v_gap

    nodes = []
    node_positions = {}

    for level_idx, level in enumerate(levels):
        level_node_count = len(level)
        level_width = level_node_count * node_w + (level_node_count - 1) * h_gap
        start_x = (width - level_width) / 2 + node_w / 2
        y = margin + level_idx * (node_h + v_gap) + node_h / 2

        for pos_in_level, node_idx in enumerate(level):
            x = start_x + pos_in_level * (node_w + h_gap)
            nodes.append({
                "index": node_idx,
                "label": labels[node_idx],
                "x": round(x, 1),
                "y": round(y, 1),
            })
            node_positions[node_idx] = (x, y)

    edges = []
    for i in range(n):
        for j in range(n):
            if i != j and edge_matrix[i][j] == 1:
                if i in node_positions and j in node_positions:
                    edges.append({
                        "from": i,
                        "to": j,
                        "from_pos": [round(node_positions[i][0], 1), round(node_positions[i][1], 1)],
                        "to_pos": [round(node_positions[j][0], 1), round(node_positions[j][1], 1)],
                    })

    return {
        "nodes": nodes,
        "edges": edges,
        "width": round(width),
        "height": round(height),
        "layout": "hierarchical",
    }


def _matrix_to_table(matrix, labels):
    """将矩阵转换为表格行。"""
    headers = [""] + labels
    rows = []
    for i, row in enumerate(matrix):
        rows.append([labels[i]] + [str(cell) for cell in row])
    return headers, rows


def _sets_to_table(sets, labels):
    """将可达集/先行集转换为表格行。"""
    headers = ["要素", "可达集合R", "先行集合Q", "交集A=R∩Q"]
    rows = []
    for s in sets:
        r_str = ",".join(str(labels[i]) for i in s["r"])
        a_str = ",".join(str(labels[i]) for i in s["a"])
        c_str = ",".join(str(labels[i]) for i in s["c"])
        rows.append([labels[s["index"]], r_str, a_str, c_str])
    return headers, rows


def _levels_to_table(levels, labels):
    """将层级分解转换为表格行。"""
    headers = ["层级", "要素"]
    rows = []
    for level_index, level in enumerate(levels):
        elements = ",".join(labels[i] for i in level)
        rows.append([f"L{level_index + 1}", elements])
    return headers, rows


def _directed_chart(graph):
    """生成有向图数据（用于 SVG 渲染）。"""
    return {
        "chartType": "directed_graph",
        "title": "有向图",
        "data": graph,
    }


def run(df, params):
    """
    执行 ISM 解释结构模型法。

    @param df: 当前数据集（未使用，ISM 使用矩阵输入）
    @param params: elements（要素名称数组）、matrix（邻接矩阵或可达矩阵）、data_type、decomposition_method
    @return: 对齐 SPSSAU 的结果 sections
    """
    params = params or {}
    elements = params.get("elements", [])
    matrix_data = params.get("matrix")
    data_type = _clean_data_type(params.get("data_type"))
    decomposition = _clean_decomposition(params.get("decomposition_method"))

    if not elements or len(elements) < 2:
        return _error("至少需要 2 个要素。")

    labels = [str(e).strip() for e in elements if str(e).strip()]
    if len(labels) < 2:
        return _error("至少需要 2 个有效要素名称。")

    matrix = _parse_matrix(matrix_data)
    if not matrix:
        return _error("矩阵数据格式错误，请提供 n×n 的 0/1 方阵。")

    error = _validate_matrix(matrix, labels, "输入矩阵")
    if error:
        return _error(error)

    n = len(labels)
    data_type_label = DATA_TYPE_MAP[data_type]["label"]
    decomposition_label = DECOMPOSITION_MAP[decomposition]["label"]

    # 计算可达矩阵
    if data_type == "adjacency":
        adjacency = matrix
        reachability = _compute_reachability(adjacency)
    else:
        adjacency = matrix
        reachability = matrix

    # 计算骨架矩阵（从可达矩阵去除传递边）
    skeleton = _compute_skeleton(reachability)

    # 计算可达集/先行集
    sets = _compute_reachability_sets(reachability)

    # 层级划分
    levels = _decompose_levels(sets, labels, decomposition)

    # 构建图数据
    circular_graph = _build_circular_graph(labels, adjacency)
    adjacency_graph = _build_hierarchical_graph(labels, levels, adjacency)
    skeleton_graph = _build_hierarchical_graph(labels, levels, skeleton)

    identity = _identity_matrix(n)
    adjacency_plus_identity = _bool_matrix_add(adjacency, identity)

    iteration_count = 0
    temp = _bool_matrix_add(adjacency, identity)
    while True:
        next_temp = _bool_matrix_multiply(temp, temp)
        iteration_count += 1
        if _matrices_equal(temp, next_temp):
            break
        temp = next_temp

    # 对齐 SPSSAU 完整输出顺序
    sections = [
        # 1. 邻接矩阵
        _sec_table(
            "邻接矩阵",
            *_matrix_to_table(adjacency, labels),
            description="'邻接矩阵'是原始数据矩阵，用于展示各要素之间的直接影响关系；"
            "\n第一：矩阵中数字 1 表示某要素对另一要素有直接影响，数字 0 表示无直接影响；"
            "\n第二：对角线元素通常为 0，表示要素对自身无直接影响。",
        ),
        _sec_advice(
            "'邻接矩阵'是 ISM 分析的起点，展示各要素之间的直接影响关系；"
            "\n第一：矩阵行表示影响源，列表示被影响对象；"
            "\n第二：基于邻接矩阵，后续将计算可达矩阵、骨架矩阵等。"
        ),
        # 2. 邻接矩阵与单位矩阵相加
        _sec_table(
            "邻接矩阵与单位矩阵相加",
            *_matrix_to_table(adjacency_plus_identity, labels),
            description="'邻接矩阵与单位矩阵相加'是指两个矩阵直接相加并得到新矩阵；"
            "\n第一：基于'邻接矩阵'基础上，计算'邻接矩阵'与'单位矩阵'之和，该矩阵用于计算下一步的'可达矩阵'。",
        ),
        _sec_advice(
            "'邻接矩阵与单位矩阵相加'是指两个矩阵直接相加并得到新矩阵；"
            "\n第一：基于'邻接矩阵'基础上，计算'邻接矩阵'与'单位矩阵'之和，该矩阵用于计算下一步的'可达矩阵'。"
        ),
        # 3. 可达矩阵
        _sec_table(
            "可达矩阵",
            *_matrix_to_table(reachability, labels),
            description="'可达矩阵'展示要素之间是否存在着连接路径；"
            "\n第一：如果数字为 1 则表示某要素到另一要素之间存在路径；"
            "\n第二：如果数字为 0 则表示某要素到另一要素之间不存在路径。",
        ),
        _sec_advice(
            "'可达矩阵'展示要素之间是否存在着连接路径；"
            "\n第一：如果数字为 1 则表示某要素到另一要素之间存在路径；"
            "\n第二：如果数字为 0 则表示某要素到另一要素之间不存在路径。"
        ),
        # 4. 可达集合与先行集合及其交集表
        _sec_table(
            "可达集合与先行集合及其交集表",
            *_sets_to_table(sets, labels),
            description="备注：数字代表某要素，比如 2 代表第 2 个要素",
        ),
        _sec_advice(
            f"针对上一步'可达矩阵'进行分解如上述表格；"
            f"\n第一：可达集合 R，其表示'可达矩阵'某要素对应行中，包含有 1 的元素集合；"
            f"\n第二：先行集合 Q，其表示'可达矩阵'某要素对应列中，包括有 1 的元素集合；"
            f"\n第三：交集 A，其表示可达集合 R 和先行集合 Q 的交集。"
            f"\n\n迭代次数为{iteration_count}次"
        ),
        # 5. 层次分解
        _sec_table(
            "层次分解",
            *_levels_to_table(levels, labels),
            description=f"基于：{decomposition_label}",
        ),
        _sec_advice(
            "层次分解表格展示各要素的层次分布情况；"
            "\n第一：层次分解目的在于了解各要素层次分布关系；"
            "\n第二：顶层表示系统最终目标，往下各层分别表示更上一层的原因；"
            "\n第三：底层表示系统最初点原因，往上各层分别受下一层的结果。"
        ),
        # 6. 有向图（圆形布局）
        _sec_charts("有向图", [_directed_chart(circular_graph)], ""),
        _sec_advice(
            "有向图展示各要素的关系情况；"
            "\n第一：有向图中'双向箭头'——此法，'邻接矩阵'中数字 1 表示有关系，数字 0 表示无关系；"
            "\n第二：有向图中，箭头指向代表因果关系方向，回环代表循环。"
        ),
        # 7. 层次关系示意图（层次布局，邻接矩阵）
        _sec_charts("层次关系示意图", [_directed_chart(adjacency_graph)], ""),
        # 8. 骨架矩阵
        _sec_table(
            "骨架矩阵",
            *_matrix_to_table(skeleton, labels),
            description="骨架矩阵是'缩边处理'后得到的最简逻辑图示；当 A→B 且 B→C 时，若 A→C 这条路径已经存在，则 A→C 是冗余路径（缩边处理）。",
        ),
        _sec_advice(
            "'骨架矩阵'是'邻接矩阵'进行缩边处理后的最简逻辑展示；"
            "\n第一：'骨架矩阵'简化'邻接矩阵'中不必要的路径，比如 A->B,B->C,A->C 这 3 条路径均存在时，A->C 是冗余路径可对其删除（即缩边处理）；"
            "\n第二：邻接矩阵通过缩边处理，删除了所有可以通过中间环节传递的间接路径，从而让系统层级结构一目了然；"
            "\n第三：'层次关系示意图（缩边处理后）'为缩边处理后的简化层次关系示意图。"
        ),
        # 9. 层次关系示意图（缩边处理后）
        _sec_charts("层次关系示意图（缩边处理后）", [_directed_chart(skeleton_graph)], ""),
        _sec_refs(_REFS_GENERAL),
    ]

    return {
        "name": METHOD_META["label"],
        "headers": ["要素", "层级"],
        "rows": [[labels[i], f"L{level_index + 1}"] for level_index, level in enumerate(levels) for i in level],
        "description": f"ISM 分析完成，{n} 个要素划分为 {len(levels)} 个层级。",
        "sections": sections,
    }
