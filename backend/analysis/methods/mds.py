# -*- coding: utf-8 -*-
# 多维尺度分析MDS：这里负责距离矩阵构造、经典 MDS 坐标求解和报告结构输出。
# 统计口径按 SPSSPRO 帮助页公式显式复现，别再退回相关系数近似距离。
from backend.analysis.common import *

METHOD_KEY = "mds"
METHOD_LABEL = "多维尺度分析MDS"

DATA_FROM_RAW = "根据数据创建距离矩阵"
DATA_IS_DISTANCE = "数据为距离矩阵"
DIM_BY_COLUMN = "按变量（列）"
DIM_BY_ROW = "按变量（行）"

METHOD_META = {
    "label": METHOD_LABEL,
    "category": "数据检验",
    "description": "基于距离矩阵把对象映射到低维空间，用于观察对象之间的相似与差异结构",
    "slots": [
        {
            "key": "variables",
            "label": "分析变量",
            "type": "multiple",
            "accept": "numeric",
            "min": 2,
            "hint": "放入需要构造距离矩阵或已经组成距离矩阵的变量",
        }
    ],
    "options": [
        {
            "key": "data_format",
            "label": "数据格式",
            "choices": [DATA_FROM_RAW, DATA_IS_DISTANCE],
            "default": DATA_FROM_RAW,
        },
        {
            "key": "analysis_dimension",
            "label": "分析维度",
            "choices": [DIM_BY_COLUMN, DIM_BY_ROW],
            "default": DIM_BY_COLUMN,
        },
    ],
    "param_builder": "direct",
}

_REFS_MDS = _REFS_GENERAL + [
    "[3] Torgerson W S. Multidimensional scaling: I. Theory and method[J]. Psychometrika, 1952, 17(4):401-419.",
    "[4] Borg I, Groenen P J F. Modern Multidimensional Scaling: Theory and Applications[M]. 2nd ed. New York: Springer, 2005.",
]


def _fail(message):
    return {"name": METHOD_LABEL, "headers": [], "rows": [], "description": message}


def _label_for_index(index, position):
    text = str(index).strip()
    if not text or text == str(position):
        return f"样本{position + 1}"
    return text


def _euclidean_distance_matrix(values):
    diff = values[:, None, :] - values[None, :, :]
    distances = np.sqrt(np.sum(diff ** 2, axis=2))
    np.fill_diagonal(distances, 0.0)
    return distances


def _normalize_distance_matrix(matrix):
    matrix = np.asarray(matrix, dtype=float)
    matrix = np.nan_to_num(matrix, nan=0.0, posinf=0.0, neginf=0.0)
    matrix = np.abs(matrix)
    n = matrix.shape[0]
    distances = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(i):
            left = matrix[i, j]
            right = matrix[j, i]
            if left > 0 and right > 0:
                value = (left + right) / 2
            else:
                value = max(left, right)
            distances[i, j] = distances[j, i] = value
    return distances


def _build_distance_from_raw(df, variables, dimension):
    data = df[variables].apply(pd.to_numeric, errors="coerce").dropna()
    if data.empty:
        return None, [], 0, "没有可用于构造距离矩阵的完整有效样本。"

    if dimension == DIM_BY_ROW:
        values = data.to_numpy(dtype=float)
        labels = [_label_for_index(index, pos) for pos, index in enumerate(data.index)]
        feature_count = len(variables)
    else:
        values = data.to_numpy(dtype=float).T
        labels = variables
        feature_count = len(data)

    if values.shape[0] < 2:
        return None, [], len(data), "MDS 至少需要 2 个可比较对象。"
    if values.shape[1] < 1:
        return None, [], len(data), "对象缺少可比较的数值特征。"
    return _euclidean_distance_matrix(values), labels, feature_count, ""


def _build_distance_from_matrix(df, variables):
    n = len(variables)
    matrix_frame = df[variables].apply(pd.to_numeric, errors="coerce")
    if len(matrix_frame) < n:
        return None, [], 0, f"距离矩阵模式需要至少 {n} 行数据，才能和已选 {n} 个变量组成方阵。"
    matrix = matrix_frame.iloc[:n, :n].to_numpy(dtype=float)
    return _normalize_distance_matrix(matrix), variables, n, ""


def _classical_mds(distances, dimensions=2):
    n = distances.shape[0]
    squared = distances ** 2
    centering = np.eye(n) - np.ones((n, n)) / n
    gram = -0.5 * centering @ squared @ centering
    eigvals, eigvecs = np.linalg.eigh(gram)
    order = np.argsort(eigvals)[::-1]
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]

    coords = np.zeros((n, dimensions), dtype=float)
    usable_dims = min(dimensions, n)
    for dim in range(usable_dims):
        if eigvals[dim] > 0:
            coords[:, dim] = eigvecs[:, dim] * np.sqrt(eigvals[dim])
    for dim in range(coords.shape[1]):
        pivot = int(np.argmax(np.abs(coords[:, dim])))
        if coords[pivot, dim] < 0:
            coords[:, dim] *= -1
    return coords, eigvals


def _fit_metrics(distances, coords):
    projected = _euclidean_distance_matrix(coords)
    upper = np.triu_indices_from(distances, k=1)
    raw = distances[upper]
    fitted = projected[upper]
    denominator = float(np.sum(raw ** 2))
    stress = np.sqrt(float(np.sum((raw - fitted) ** 2)) / denominator) if denominator > 0 else 0.0
    if len(raw) >= 2 and np.std(raw) > 0 and np.std(fitted) > 0:
        rsq = float(np.corrcoef(raw, fitted)[0, 1] ** 2)
    else:
        rsq = np.nan
    return stress, rsq


def _distance_table(labels, distances, limit=15):
    display_count = min(len(labels), limit)
    display_labels = labels[:display_count]
    headers = [""] + display_labels
    rows = []
    for i, label in enumerate(display_labels):
        row = [label]
        for j in range(display_count):
            value = distances[i, j] if i > j else 0
            row.append(_fmt(value, 3))
        rows.append(row)
    note = None
    if len(labels) > limit:
        note = "若变量（样本）超过15个，以上结果为预览结果，完整图形和坐标计算仍基于全部对象。"
    return headers, rows, note


def _coordinate_rows(labels, coords):
    return [
        [label, _fmt(coords[index, 0], 3), _fmt(coords[index, 1], 3)]
        for index, label in enumerate(labels)
    ]


def _space_chart(labels, coords):
    return {
        "chartType": "scatter_plot",
        "title": "空间感知图",
        "fullRow": True,
        "data": {
            "xLabel": "维1",
            "yLabel": "维2",
            "showLabels": True,
            "showZeroCross": True,
            "symmetricAxis": True,
            "purpose": "mds",
            "points": [
                {
                    "label": label,
                    "x": float(coords[index, 0]),
                    "y": float(coords[index, 1]),
                }
                for index, label in enumerate(labels)
            ],
        },
    }


def multidimensional_scaling_analysis(df, params):
    """
    执行多维尺度分析MDS。

    params:
        variables: 数值变量列表；原始数据模式下用于构造距离矩阵，距离矩阵模式下组成方阵。
        data_format: 根据数据创建距离矩阵 / 数据为距离矩阵。
        analysis_dimension: 按变量（列）/ 按变量（行），仅原始数据模式下影响对象方向。
    returns:
        统一分析结果字典，包含距离矩阵、空间感知图、坐标和拟合摘要。
    """
    variables = _resolve_cols(df, params.get("variables", []))
    if len(variables) < 2:
        return _fail("至少需要放入 2 个变量。")

    data_format = params.get("data_format") or DATA_FROM_RAW
    dimension = params.get("analysis_dimension") or DIM_BY_COLUMN
    if data_format == DATA_IS_DISTANCE:
        distances, labels, feature_count, error = _build_distance_from_matrix(df, variables)
        dimension_text = "距离矩阵"
    else:
        distances, labels, feature_count, error = _build_distance_from_raw(df, variables, dimension)
        dimension_text = dimension
    if error:
        return _fail(error)

    coords, eigenvalues = _classical_mds(distances, dimensions=2)
    stress, rsq = _fit_metrics(distances, coords)
    coord_headers = ["名称", "维1", "维2"]
    coord_rows = _coordinate_rows(labels, coords)
    distance_headers, distance_rows, distance_note = _distance_table(labels, distances)

    positive_eigenvalues = [value for value in eigenvalues if value > 0]
    summary_rows = [
        ["数据格式", data_format],
        ["分析维度", dimension_text],
        ["对象数", str(len(labels))],
        ["有效数据长度", str(feature_count)],
        ["Stress", _fmt(stress, 4)],
        ["RSQ", _fmt(rsq, 4)],
        ["正特征根个数", str(len(positive_eigenvalues))],
    ]

    sections = [
        _sec_table(
            "输出结果1：距离矩阵",
            distance_headers,
            distance_rows,
            note=distance_note,
            description="上表展示了对象之间的距离，值越大说明两个对象之间的差异性越大。",
        ),
        _sec_charts(
            "输出结果2：空间感知图",
            [_space_chart(labels, coords)],
            description="上图为根据距离矩阵在低维图形上绘制的对象位置，距离越近代表差异性越小。",
        ),
        _sec_table("坐标结果", coord_headers, coord_rows, description="坐标用于绘制空间感知图，解释时优先看点与点之间的相对远近。"),
        _sec_table("模型摘要", ["指标", "值"], summary_rows),
    ]

    if stress < 0.1:
        fit_text = "拟合效果较好"
    elif stress < 0.2:
        fit_text = "拟合效果可接受"
    else:
        fit_text = "拟合效果一般，二维图只能作为粗略结构参考"
    smart = (
        f"本次对{len(labels)}个对象进行{METHOD_LABEL}，Stress={_fmt(stress, 4)}，{fit_text}。"
        "图中点位越接近，表示对象之间的距离越小、结构越相似；点位越分散，表示差异越明显。"
    )
    sections.append(_sec_advice(
        "MDS 主要用于结构探索和定位图展示，不直接输出显著性检验结论。"
        "如果对象很多，先看空间感知图中的聚集和离群位置，再回到距离矩阵确认具体对象差异。"
    ))
    sections.append(_sec_smart(smart))
    sections.append(_sec_refs(_REFS_MDS))

    return {
        "name": METHOD_LABEL,
        "headers": coord_headers,
        "rows": coord_rows,
        "description": smart,
        "sections": sections,
        "charts": [_space_chart(labels, coords)],
    }


run = multidimensional_scaling_analysis
