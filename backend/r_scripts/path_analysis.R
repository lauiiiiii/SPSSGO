# -*- coding: utf-8 -*-
# spssgo - 路径分析 R 脚本
# 基于 lavaan 拟合路径模型，输出路径系数、直接/间接/总效应、修正指数。
# 用户在前端逐条定义路径，每条路径包含 from 和 to 两个变量。

args <- commandArgs(trailingOnly = TRUE)

input_path <- NULL
if (length(args) >= 2) {
  for (i in seq(1, length(args) - 1, by = 1)) {
    if (args[i] == "--input") {
      input_path <- args[i + 1]
      break
    }
  }
}
if (is.null(input_path) || !file.exists(input_path)) stop("missing --input json file")

read_utf8 <- function(path) paste(readLines(path, warn = FALSE, encoding = "UTF-8"), collapse = "\n")
fmt_num <- function(x, digits = 4) {
  if (is.null(x) || length(x) == 0 || is.na(x) || is.infinite(x)) return("\u2014")
  if (abs(x - round(x)) < 1e-12) return(as.character(as.integer(round(x))))
  sprintf(paste0("%.", digits, "f"), x)
}
fmt_p <- function(p) {
  if (is.null(p) || length(p) == 0 || is.na(p) || is.infinite(p)) return("\u2014")
  if (p < 0.001) return("0.000")
  sprintf("%.3f", p)
}
sig_mark <- function(p) {
  if (is.null(p) || length(p) == 0 || is.na(p) || is.infinite(p)) return("")
  if (p < 0.001) return("****")
  if (p < 0.01) return("***")
  if (p < 0.05) return("**")
  if (p < 0.1) return("*")
  ""
}
fmt_coef <- function(value, p = NA_real_) paste0(fmt_num(value, 3), sig_mark(p))

sec_table <- function(title, headers, rows, description = NULL, note = NULL, headerRows = NULL, tableClass = NULL) {
  item <- list(type = "table", title = title, headers = headers, rows = rows)
  if (!is.null(description)) item$description <- description
  if (!is.null(note)) item$note <- note
  if (!is.null(headerRows)) item$headerRows <- headerRows
  if (!is.null(tableClass)) item$tableClass <- tableClass
  item
}
sec_smart <- function(content) list(type = "smart_analysis", title = "智能分析", content = content)
sec_advice <- function(content, title = "分析建议") list(type = "advice", title = title, content = content)
sec_refs <- function(items) list(type = "references", title = "参考文献", items = items)
sec_charts <- function(title, charts) list(type = "charts", title = title, charts = charts)

as_chars <- function(value) {
  if (is.null(value)) return(character(0))
  result <- as.character(unlist(value, use.names = FALSE))
  result[nzchar(result)]
}

if (!requireNamespace("lavaan", quietly = TRUE)) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "缺少 R 包 lavaan，路径分析无法执行。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

input <- jsonlite::fromJSON(read_utf8(input_path), simplifyVector = FALSE)
input_dir <- dirname(normalizePath(input_path, winslash = "/", mustWork = TRUE))
data_file <- file.path(input_dir, input$data_file)
if (!file.exists(data_file)) stop("missing input data file")

# 解析路径列表
paths_input <- input$paths
if (is.null(paths_input) || length(paths_input) == 0) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "至少需要定义 1 条路径。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

# 提取所有变量
all_vars_set <- c()
for (p in paths_input) {
  all_vars_set <- c(all_vars_set, p$from, p$to)
}
all_vars <- unique(all_vars_set)

if (length(all_vars) < 2) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "路径分析至少需要 2 个不同的变量。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

raw_df <- read.csv(data_file, stringsAsFactors = FALSE, check.names = FALSE)
missing_cols <- setdiff(all_vars, colnames(raw_df))
if (length(missing_cols) > 0) {
  cat(jsonlite::toJSON(list(success = FALSE, error = paste0("以下变量不存在：", paste(missing_cols, collapse = "、"), "。")), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

data <- raw_df[, all_vars, drop = FALSE]
for (col in all_vars) data[[col]] <- suppressWarnings(as.numeric(data[[col]]))
n_before <- nrow(data)
data <- stats::na.omit(data)
n_after <- nrow(data)
min_n <- max(5, length(all_vars))
if (n_after < min_n) {
  cat(jsonlite::toJSON(list(
    success = FALSE,
    error = paste0("路径分析有效样本不足。完整数据仅 ", n_after, " 条（原始 ", n_before, " 条，缺失删除 ", n_before - n_after, " 条），至少需要 ", min_n, " 条。")
  ), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

# ── 构建路径方程 ──
# 每条路径定义一个回归关系：to ~ from
# 如果同一个因变量有多个自变量，合并为一条方程
equation_map <- list()
for (p in paths_input) {
  from_var <- p$from
  to_var <- p$to
  if (is.null(equation_map[[to_var]])) {
    equation_map[[to_var]] <- c()
  }
  equation_map[[to_var]] <- c(equation_map[[to_var]], from_var)
}

equation_lines <- c()
dependent_vars <- names(equation_map)
for (dv in dependent_vars) {
  predictors <- unique(equation_map[[dv]])
  equation_lines <- c(equation_lines, paste0(dv, " ~ ", paste(predictors, collapse = " + ")))
}
model_desc <- paste(equation_lines, collapse = "\n")

# 识别外生变量（只作为 from，不作为 to）
as_to_vars <- unique(unlist(lapply(paths_input, function(p) p$to)))
as_from_vars <- unique(unlist(lapply(paths_input, function(p) p$from)))
independent_vars <- setdiff(as_from_vars, as_to_vars)

fit <- tryCatch(
  lavaan::sem(model_desc, data = data, fixed.x = FALSE, missing = "listwise"),
  error = function(e) e
)
if (inherits(fit, "error")) {
  cat(jsonlite::toJSON(list(success = FALSE, error = paste0("路径模型拟合失败：", fit$message)), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

# ── 路径系数表（按方程分组） ──
param_est <- lavaan::parameterEstimates(fit, standardized = TRUE, ci = TRUE)
path_df <- param_est[param_est$op == "~", ]

# 构建带方程分组的路径系数表
path_rows <- list()
for (dv in dependent_vars) {
  eq_rows <- path_df[path_df$lhs == dv, ]
  for (i in seq_len(nrow(eq_rows))) {
    row <- eq_rows[i, ]
    path_rows[[length(path_rows) + 1]] <- list(
      dv,
      as.character(row$rhs),
      fmt_num(row$est, 4),
      fmt_num(row$std.all, 4),
      fmt_num(row$se, 4),
      fmt_num(row$z, 4),
      fmt_p(row$pvalue),
      fmt_num(row$ci.lower, 4),
      fmt_num(row$ci.upper, 4)
    )
  }
}

# ── 模型拟合指标 ──
fit_names <- c("chisq", "df", "pvalue", "cfi", "tli", "rmsea", "srmr", "aic", "bic")
fit_measure <- lavaan::fitMeasures(fit, fit_names)
chi2 <- unname(fit_measure["chisq"])
dof <- unname(fit_measure["df"])
cmin_df <- ifelse(!is.na(chi2) && !is.na(dof) && dof != 0, chi2 / dof, NA)

r2_vals <- tryCatch(lavaan::inspect(fit, "r2"), error = function(e) NULL)

fit_rows <- list(
  list("有效样本量", as.character(nrow(data))),
  list("变量总数", as.character(length(all_vars))),
  list("外生变量数", as.character(length(independent_vars))),
  list("内生变量数", as.character(length(dependent_vars))),
  list("路径方程数", as.character(length(dependent_vars))),
  list("Chi-square", fmt_num(chi2, 4)),
  list("df", fmt_num(dof, 0)),
  list("CMIN/DF", fmt_num(cmin_df, 4)),
  list("p", fmt_p(unname(fit_measure["pvalue"]))),
  list("CFI", fmt_num(unname(fit_measure["cfi"]), 4)),
  list("TLI", fmt_num(unname(fit_measure["tli"]), 4)),
  list("RMSEA", fmt_num(unname(fit_measure["rmsea"]), 4)),
  list("SRMR", fmt_num(unname(fit_measure["srmr"]), 4)),
  list("AIC", fmt_num(unname(fit_measure["aic"]), 4)),
  list("BIC", fmt_num(unname(fit_measure["bic"]), 4))
)

# R² 表
r2_rows <- list()
if (!is.null(r2_vals)) {
  for (dv in dependent_vars) {
    if (dv %in% names(r2_vals)) {
      r2_rows[[length(r2_rows) + 1]] <- list(dv, fmt_num(r2_vals[[dv]], 4))
    }
  }
}

# ── 直接效应 / 间接效应 / 总效应 ──
# 用矩阵方法计算：构建标准化系数矩阵，通过矩阵幂级数求总效应
all_path_vars <- all_vars
n_vars <- length(all_path_vars)
# 直接效应矩阵 direct[i,j] = j→i 的标准化路径系数
direct_mat <- matrix(0, nrow = n_vars, ncol = n_vars, dimnames = list(all_path_vars, all_path_vars))
for (i in seq_len(nrow(path_df))) {
  row <- path_df[i, ]
  lhs <- as.character(row$lhs)
  rhs <- as.character(row$rhs)
  if (lhs %in% all_path_vars && rhs %in% all_path_vars && !is.na(row$std.all)) {
    direct_mat[lhs, rhs] <- row$std.all
  }
}

# 总效应 = (I - B)^{-1} - I，其中 B 是直接效应矩阵
# 用幂级数：total = B + B^2 + B^3 + ... 直到收敛
total_mat <- direct_mat
current <- direct_mat
for (iter in seq_len(max(n_vars, 10))) {
  current <- current %*% direct_mat
  total_mat <- total_mat + current
  if (all(abs(current) < 1e-10)) break
}
indirect_mat <- total_mat - direct_mat

# 输出效应表
effect_rows <- list()
for (pred in all_path_vars) {
  for (dep in all_path_vars) {
    if (pred == dep) next
    d_val <- direct_mat[dep, pred]
    ind_val <- indirect_mat[dep, pred]
    t_val <- total_mat[dep, pred]
    if (abs(d_val) < 1e-10 && abs(ind_val) < 1e-10 && abs(t_val) < 1e-10) next
    effect_rows[[length(effect_rows) + 1]] <- list(
      pred, dep,
      fmt_num(d_val, 4),
      fmt_num(ind_val, 4),
      fmt_num(t_val, 4)
    )
  }
}

# ── 修正指数（MI） ──
mi <- tryCatch(lavaan::modindices(fit), error = function(e) NULL)
mi_rows <- list()
if (!is.null(mi) && nrow(mi) > 0) {
  # 只保留 ~ 类型的修正（路径类）
  mi_path <- mi[mi$op == "~", ]
  if (nrow(mi_path) > 0) {
    mi_path <- mi_path[order(-mi_path$mi), ]
    top_n <- min(10, nrow(mi_path))
    for (i in seq_len(top_n)) {
      row <- mi_path[i, ]
      mi_rows[[length(mi_rows) + 1]] <- list(
        paste0(as.character(row$lhs), " ~ ", as.character(row$rhs)),
        fmt_num(row$mi, 3),
        fmt_num(row$epc, 4),
        "可结合理论判断是否增加该路径"
      )
    }
  }
}

# ── 路径图数据（用于前端渲染） ──
path_edges <- list()
for (i in seq_len(nrow(path_df))) {
  row <- path_df[i, ]
  path_edges[[length(path_edges) + 1]] <- list(
    from = as.character(row$rhs),
    to = as.character(row$lhs),
    value = paste0("β=", fmt_num(row$std.all, 3)),
    significant = !is.na(row$pvalue) && row$pvalue < 0.05
  )
}

# 构建节点位置 - 按列分层布局
# 第 1 列：外生变量（只作为起点）
# 第 2 列：中介变量（既是起点又是终点）
# 第 3 列：内生变量（只作为终点）
node_x <- list()
node_col <- list()

# 识别每个变量的角色
for (v in all_vars) {
  is_from <- any(path_df$rhs == v)
  is_to <- any(path_df$lhs == v)
  if (is_from && !is_to) {
    node_col[[v]] <- 1  # 外生变量
  } else if (is_from && is_to) {
    node_col[[v]] <- 2  # 中介变量
  } else {
    node_col[[v]] <- 3  # 内生变量
  }
}

# 按列分组
col1_vars <- all_vars[sapply(all_vars, function(v) node_col[[v]] == 1)]
col2_vars <- all_vars[sapply(all_vars, function(v) node_col[[v]] == 2)]
col3_vars <- all_vars[sapply(all_vars, function(v) node_col[[v]] == 3)]

# 计算每列的 x 坐标
col_x <- c(60, 240, 420)

# 计算 y 坐标 - 每列内均匀分布
node_y <- list()
max_rows <- max(length(col1_vars), length(col2_vars), length(col3_vars), 1)
chart_h <- max(260, 50 + max_rows * 60)

for (col_idx in 1:3) {
  col_vars <- switch(col_idx, col1_vars, col2_vars, col3_vars)
  n <- length(col_vars)
  if (n == 0) next
  # 垂直居中
  total_height <- (n - 1) * 60
  start_y <- (chart_h - total_height) / 2 - 30
  for (i in seq_along(col_vars)) {
    v <- col_vars[i]
    node_x[[v]] <- col_x[col_idx]
    node_y[[v]] <- start_y + (i - 1) * 60
  }
}

nodes <- list()
for (v in all_vars) {
  nodes[[length(nodes) + 1]] <- list(
    key = v,
    label = v,
    x = node_x[[v]],
    y = node_y[[v]]
  )
}

chart_w <- max(560, max(sapply(all_vars, function(v) node_x[[v]])) + 180)

path_chart <- list(
  chartType = "model_path",
  title = "模型路径图",
  data = list(
    width = chart_w,
    height = chart_h,
    nodes = nodes,
    edges = path_edges,
    defaultShowDataLabels = TRUE
  )
)

# ── 智能分析文本 ──
sig_paths <- c()
for (i in seq_len(nrow(path_df))) {
  row <- path_df[i, ]
  if (!is.na(row$pvalue) && row$pvalue < 0.05) {
    sig_paths <- c(sig_paths, paste0(as.character(row$rhs), "→", as.character(row$lhs)))
  }
}

strongest <- ""
if (nrow(path_df) > 0) {
  idx <- which.max(abs(path_df$std.all))
  strongest <- paste0("，标准化路径最强的是 ", path_df$rhs[idx], "→", path_df$lhs[idx], "（β=", fmt_num(path_df$std.all[idx], 3), "）")
}

smart <- paste0(
  "路径分析使用 lavaan 完成，共纳入 ", nrow(data), " 条有效样本，",
  "定义 ", length(paths_input), " 条路径，生成 ", length(dependent_vars), " 条路径方程", strongest, "。"
)

# 模型拟合评价
fit_issues <- c()
if (!is.na(cmin_df) && cmin_df >= 3) fit_issues <- c(fit_issues, "卡方自由度比偏高")
cfi_val <- unname(fit_measure["cfi"])
if (!is.na(cfi_val) && cfi_val < 0.9) fit_issues <- c(fit_issues, "CFI 偏低")
rmsea_val <- unname(fit_measure["rmsea"])
if (!is.na(rmsea_val) && rmsea_val >= 0.08) fit_issues <- c(fit_issues, "RMSEA 偏高")
srmr_val <- unname(fit_measure["srmr"])
if (!is.na(srmr_val) && srmr_val >= 0.08) fit_issues <- c(fit_issues, "SRMR 偏高")

if (length(fit_issues) > 0) {
  smart <- paste0(smart, " 当前需要重点关注：", paste(fit_issues, collapse = "、"), "。")
} else {
  smart <- paste0(smart, " 主要拟合指标整体较为稳定。")
}

if (length(sig_paths) > 0) {
  smart <- paste0(smart, " 显著路径包括：", paste(sig_paths, collapse = "、"), "。")
}

# ── 组装输出 ──
sections <- list(
  sec_table("路径系数表",
    c("因变量", "自变量", "B", "标准化β", "Std. Err", "z", "p", "95% CI 下限", "95% CI 上限"),
    path_rows,
    "当前结果由 R/lavaan 估计，标准化路径更适合跨变量比较。",
    tableClass = "tlt--spssau"
  ),
  sec_table("模型拟合概况",
    c("指标", "值"),
    fit_rows,
    "路径分析基于线性回归方法，用于分析多个变量之间的路径关系。",
    tableClass = "tlt--spssau"
  )
)

if (length(r2_rows) > 0) {
  sections[[length(sections) + 1]] <- sec_table("内生变量解释力(R²)",
    c("因变量", "R²"),
    r2_rows,
    "R² 表示该因变量被模型中预测变量解释的方差比例。",
    tableClass = "tlt--spssau"
  )
}

if (length(effect_rows) > 0) {
  sections[[length(sections) + 1]] <- sec_table("直接效应 / 间接效应 / 总效应",
    c("起点变量", "终点变量", "直接效应", "间接效应", "总效应"),
    effect_rows,
    "直接效应是两变量间的直接路径系数；间接效应是通过中间变量传递的效应；总效应 = 直接效应 + 间接效应。",
    tableClass = "tlt--spssau"
  )
}

if (length(mi_rows) > 0) {
  sections[[length(sections) + 1]] <- sec_table("模型修正建议（MI）",
    c("建议路径", "MI", "EPC", "建议"),
    mi_rows,
    "修正指数越高，说明增加该路径可能显著改善模型拟合；但必须结合理论判断，不可纯数据驱动。",
    tableClass = "tlt--spssau"
  )
}

sections[[length(sections) + 1]] <- sec_charts("模型路径图", list(path_chart))

sections[[length(sections) + 1]] <- sec_advice(
  paste(
    "路径分析结果建议从三层解读：",
    "第一：先看模型拟合指标是否达到常用阈值（CFI>0.9, RMSEA<0.08, SRMR<0.08）；",
    "第二：再看各路径系数是否显著，识别关键路径；",
    "第三：结合直接效应、间接效应和总效应，理解变量间影响是如何层层传递的。",
    sep = "\n"
  )
)

sections[[length(sections) + 1]] <- sec_smart(smart)

sections[[length(sections) + 1]] <- sec_refs(c(
  "[1] Rosseel, Y. lavaan: An R Package for Structural Equation Modeling. Journal of Statistical Software, 2012.",
  "[2] Kline, R. B. Principles and Practice of Structural Equation Modeling. Guilford Press."
))

result <- list(
  success = TRUE,
  name = "路径分析",
  headers = c("因变量", "自变量", "B", "标准化β", "Std. Err", "z", "p", "95% CI 下限", "95% CI 上限"),
  rows = path_rows,
  description = smart,
  sections = sections
)

cat(jsonlite::toJSON(result, auto_unbox = TRUE, null = "null", force = TRUE, dataframe = "rows"))
