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

if (is.null(input_path) || !file.exists(input_path)) {
  stop("missing --input json file")
}

read_utf8 <- function(path) {
  paste(readLines(path, warn = FALSE, encoding = "UTF-8"), collapse = "\n")
}

fmt_num <- function(x, digits = 3) {
  if (is.null(x) || length(x) == 0 || is.na(x) || is.infinite(x)) {
    return("\u2014")
  }
  sprintf(paste0("%.", digits, "f"), as.numeric(x))
}

fmt_trim <- function(x, digits = 3) {
  value <- fmt_num(x, digits)
  if (value == "\u2014") return(value)
  sub("\\.?0+$", "", value)
}

fmt_pct <- function(x, digits = 3) {
  if (is.null(x) || length(x) == 0 || is.na(x) || is.infinite(x)) {
    return("\u2014")
  }
  paste0(fmt_num(x, digits), "%")
}

fmt_p <- function(p, digits = 3, sig = FALSE) {
  if (is.null(p) || length(p) == 0 || is.na(p) || is.infinite(p)) {
    return("\u2014")
  }
  label <- fmt_num(p, digits)
  if (sig) {
    if (p < 0.001) return(paste0(label, "***"))
    if (p < 0.01) return(paste0(label, "**"))
    if (p < 0.05) return(paste0(label, "*"))
  }
  label
}

sec_table <- function(title, headers, rows, description = NULL, note = NULL) {
  item <- list(type = "table", title = title, headers = headers, rows = rows)
  if (!is.null(description)) item$description <- description
  if (!is.null(note)) item$note <- note
  item
}

sec_charts <- function(title, charts, description = NULL) {
  item <- list(type = "charts", title = title, charts = charts)
  if (!is.null(description)) item$description <- description
  item
}

sec_smart <- function(content) {
  list(type = "smart_analysis", title = "智能分析", content = content)
}

sec_advice <- function(content, title = "分析建议") {
  list(type = "advice", title = title, content = content)
}

sec_refs <- function(items) {
  list(type = "references", title = "参考文献", items = items)
}

compute_kmo <- function(corr_matrix) {
  inv_corr <- solve(corr_matrix)
  partial <- -cov2cor(inv_corr)
  diag(partial) <- 0
  corr_sq <- corr_matrix ^ 2
  partial_sq <- partial ^ 2
  diag(corr_sq) <- 0
  diag(partial_sq) <- 0
  kmo_per_item <- colSums(corr_sq) / (colSums(corr_sq) + colSums(partial_sq))
  kmo_total <- sum(corr_sq) / (sum(corr_sq) + sum(partial_sq))
  list(per_item = kmo_per_item, total = kmo_total)
}

compute_bartlett <- function(corr_matrix, n) {
  p <- ncol(corr_matrix)
  chi2 <- -(n - 1 - (2 * p + 5) / 6) * log(det(corr_matrix))
  dof <- p * (p - 1) / 2
  p_value <- stats::pchisq(chi2, df = dof, lower.tail = FALSE)
  list(chi2 = chi2, p = p_value, dof = dof)
}

normalize_loading_signs <- function(loadings_matrix) {
  for (col_idx in seq_len(ncol(loadings_matrix))) {
    column <- loadings_matrix[, col_idx]
    max_idx <- which.max(abs(column))
    if (length(max_idx) && !is.na(column[max_idx]) && column[max_idx] < 0) {
      loadings_matrix[, col_idx] <- -column
    }
  }
  loadings_matrix
}

fmt_table_cell <- function(text, class_name = NULL, colspan = NULL, rowspan = NULL) {
  cell <- list(text = text)
  if (!is.null(class_name)) cell$class <- class_name
  if (!is.null(colspan)) cell$colspan <- colspan
  if (!is.null(rowspan)) cell$rowspan <- rowspan
  cell
}

fmt_loading_cell <- function(value) {
  class_name <- if (!is.na(value) && abs(value) > 0.4) "tlt-cell--accent" else NULL
  fmt_table_cell(fmt_num(value, 3), class_name)
}

fmt_hidden_loading_cell <- function(value, threshold) {
  if (!is.na(value) && abs(value) < threshold) {
    return("")
  }
  fmt_loading_cell(value)
}

fmt_communality_cell <- function(value) {
  class_name <- if (!is.na(value) && value < 0.4) "tlt-cell--danger" else NULL
  fmt_table_cell(fmt_num(value, 3), class_name)
}

input <- jsonlite::fromJSON(read_utf8(input_path), simplifyVector = FALSE)
input_dir <- dirname(normalizePath(input_path, winslash = "/", mustWork = TRUE))
data_file <- file.path(input_dir, input$data_file)
if (!file.exists(data_file)) {
  stop("missing input data file")
}

raw_df <- read.csv(data_file, stringsAsFactors = FALSE, check.names = FALSE)
items <- unlist(input$items)
items <- items[items %in% names(raw_df)]
scale_name <- ifelse(is.null(input$scale_name) || !nzchar(input$scale_name), "量表", input$scale_name)
factor_count_setting <- ifelse(is.null(input$factor_count) || !nzchar(as.character(input$factor_count)), "auto", as.character(input$factor_count))

if (length(items) < 3) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "需要至少3个题目。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

data <- raw_df[, items, drop = FALSE]
for (col in items) {
  data[[col]] <- suppressWarnings(as.numeric(data[[col]]))
}
data <- stats::na.omit(data)

if (nrow(data) < 3) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "有效样本不足。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

corr_matrix <- stats::cor(data)
det_corr <- det(corr_matrix)
if (is.na(det_corr) || det_corr <= 0) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "相关矩阵不可逆，无法进行效度分析。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

item_count <- length(items)
total_rows <- nrow(raw_df)
valid_rows <- nrow(data)
excluded_rows <- total_rows - valid_rows
kmo_info <- compute_kmo(corr_matrix)
bartlett_info <- compute_bartlett(corr_matrix, valid_rows)
eigen_info <- eigen(corr_matrix)
eigen_values <- pmax(Re(eigen_info$values), 0)
eigen_vectors <- Re(eigen_info$vectors)
factor_count <- sum(eigen_values > 1)
factor_count <- max(1, min(factor_count, item_count))
factor_count_mode <- "自动抽取"
if (factor_count_setting != "auto") {
  fixed_factor_count <- suppressWarnings(as.integer(factor_count_setting))
  if (!is.na(fixed_factor_count)) {
    factor_count <- max(1, min(fixed_factor_count, item_count))
    factor_count_mode <- paste0("固定", factor_count, "个因子")
  } else {
    factor_count_setting <- "auto"
  }
}

unrotated_loadings_all <- eigen_vectors %*% diag(sqrt(eigen_values), nrow = item_count)
selected_loadings <- unrotated_loadings_all[, seq_len(factor_count), drop = FALSE]
if (factor_count >= 2) {
  rotated_loadings <- as.matrix(stats::varimax(selected_loadings)$loadings)
} else {
  rotated_loadings <- selected_loadings
}
rotated_loadings <- normalize_loading_signs(rotated_loadings)
rownames(rotated_loadings) <- items
colnames(rotated_loadings) <- paste0("因子", seq_len(factor_count))

communalities <- rowSums(rotated_loadings ^ 2)
rotated_ss <- colSums(rotated_loadings ^ 2)
rotated_var_pct <- rotated_ss / item_count * 100
rotated_cum_pct <- cumsum(rotated_var_pct)
initial_var_pct <- eigen_values / item_count * 100
initial_cum_pct <- cumsum(initial_var_pct)

kmo_desc <- "不太适合"
if (!is.na(kmo_info$total)) {
  if (kmo_info$total >= 0.9) {
    kmo_desc <- "非常适合"
  } else if (kmo_info$total >= 0.8) {
    kmo_desc <- "适合"
  } else if (kmo_info$total >= 0.7) {
    kmo_desc <- "较适合"
  } else if (kmo_info$total >= 0.6) {
    kmo_desc <- "勉强适合"
  }
}

headers <- c("指标", "值")
rows <- list(
  list("KMO值", fmt_num(kmo_info$total, 4)),
  list("相关矩阵行列式", fmt_num(det_corr, 6)),
  list("Bartlett球形检验 近似卡方", fmt_num(bartlett_info$chi2, 3)),
  list("Bartlett球形检验 df", as.character(bartlett_info$dof)),
  list("Bartlett球形检验 p值", fmt_p(bartlett_info$p, 3, TRUE)),
  list("维度个数设置", factor_count_mode),
  list("建议提取因子数", as.character(factor_count))
)

kmo_table_rows <- list(
  list(list(text = "KMO值", colspan = 2L), fmt_num(kmo_info$total, 3)),
  list(list(text = "Bartlett 球形度检验", rowspan = 3L), "近似卡方", fmt_num(bartlett_info$chi2, 3)),
  list("df", as.character(bartlett_info$dof)),
  list("p 值", fmt_p(bartlett_info$p, 3, FALSE))
)

variance_rows <- list()
for (i in seq_along(eigen_values)) {
  rotated_cells <- if (i <= factor_count) {
    list(fmt_num(rotated_ss[[i]], 3), fmt_pct(rotated_var_pct[[i]], 3), fmt_pct(rotated_cum_pct[[i]], 3))
  } else {
    list("", "", "")
  }
  variance_rows[[length(variance_rows) + 1]] <- c(
    list(as.character(i), fmt_num(eigen_values[[i]], 3), fmt_pct(initial_var_pct[[i]], 3), fmt_pct(initial_cum_pct[[i]], 3)),
    rotated_cells
  )
}

loading_headers <- c("名称", paste0("因子", seq_len(factor_count)), "共同度(公因子方差)")
build_loading_rows <- function(hide_threshold = NULL) {
  rows <- list()
  for (i in seq_along(items)) {
    loading_values <- lapply(seq_len(factor_count), function(j) {
      if (is.null(hide_threshold)) {
        fmt_loading_cell(rotated_loadings[i, j])
      } else {
        fmt_hidden_loading_cell(rotated_loadings[i, j], hide_threshold)
      }
    })
    rows[[length(rows) + 1]] <- c(list(items[[i]]), loading_values, list(fmt_communality_cell(communalities[[i]])))
  }
  rows
}

loading_rows <- build_loading_rows(0.4)

append_factor_summary_row <- function(rows, label, values) {
  rows[[length(rows) + 1]] <- c(
    list(label),
    lapply(seq_len(factor_count), function(i) values[[i]]),
    list("-")
  )
  rows
}

append_scalar_summary_row <- function(rows, label, value) {
  rows[[length(rows) + 1]] <- list(
    label,
    fmt_table_cell(value, colspan = factor_count),
    "-"
  )
  rows
}

append_loading_summary_rows <- function(rows) {
  rows <- append_factor_summary_row(rows, "特征根值(旋转前)", lapply(seq_len(factor_count), function(i) fmt_num(eigen_values[[i]], 3)))
  rows <- append_factor_summary_row(rows, "方差解释率%(旋转前)", lapply(seq_len(factor_count), function(i) fmt_pct(initial_var_pct[[i]], 3)))
  rows <- append_factor_summary_row(rows, "累积方差解释率%(旋转前)", lapply(seq_len(factor_count), function(i) fmt_pct(initial_cum_pct[[i]], 3)))
  rows <- append_factor_summary_row(rows, "特征根值(旋转后)", lapply(seq_len(factor_count), function(i) fmt_num(rotated_ss[[i]], 3)))
  rows <- append_factor_summary_row(rows, "方差解释率%(旋转后)", lapply(seq_len(factor_count), function(i) fmt_pct(rotated_var_pct[[i]], 3)))
  rows <- append_factor_summary_row(rows, "累积方差解释率%(旋转后)", lapply(seq_len(factor_count), function(i) fmt_pct(rotated_cum_pct[[i]], 3)))
  rows <- append_scalar_summary_row(rows, "KMO值", fmt_num(kmo_info$total, 3))
  rows <- append_scalar_summary_row(rows, "巴特球形值", fmt_num(bartlett_info$chi2, 3))
  rows <- append_scalar_summary_row(rows, "df", as.character(bartlett_info$dof))
  rows <- append_scalar_summary_row(rows, "p值", fmt_p(bartlett_info$p, 3, FALSE))
  rows
}

loading_rows <- append_loading_summary_rows(loading_rows)
loading_rows_none <- append_loading_summary_rows(build_loading_rows(NULL))
loading_display_modes <- list(
  list(key = "hide_default", label = "隐藏载荷系数", rows = loading_rows),
  list(key = "none", label = "不隐藏(默认)", rows = loading_rows_none),
  list(key = "hide_0_7", label = "小于0.7", rows = append_loading_summary_rows(build_loading_rows(0.7))),
  list(key = "hide_0_6", label = "小于0.6", rows = append_loading_summary_rows(build_loading_rows(0.6))),
  list(key = "hide_0_5", label = "小于0.5", rows = append_loading_summary_rows(build_loading_rows(0.5))),
  list(key = "hide_0_4", label = "小于0.4", rows = loading_rows),
  list(key = "hide_0_3", label = "小于0.3", rows = append_loading_summary_rows(build_loading_rows(0.3))),
  list(key = "hide_0_2", label = "小于0.2", rows = append_loading_summary_rows(build_loading_rows(0.2))),
  list(key = "hide_0_1", label = "小于0.1", rows = append_loading_summary_rows(build_loading_rows(0.1)))
)
loading_sort_values <- list()
for (i in seq_along(items)) {
  loading_sort_values[[length(loading_sort_values) + 1]] <- as.list(unname(round(rotated_loadings[i, seq_len(factor_count)], 6)))
}

kmo_rows <- lapply(seq_along(items), function(i) list(items[[i]], fmt_num(kmo_info$per_item[[i]], 4)))
missing_rows <- list(
  list("有效样本", as.character(valid_rows), paste0(fmt_num(valid_rows / total_rows * 100, 1), "%")),
  list("排除无效样本", as.character(excluded_rows), paste0(fmt_num(excluded_rows / total_rows * 100, 1), "%")),
  list("总计", as.character(total_rows), "100%")
)

scree_chart <- list(
  chartType = "metric_comparison",
  title = "碎石图",
  data = list(
    metric = "特征根",
    labels = as.list(as.character(seq_along(eigen_values))),
    values = as.list(round(eigen_values, 4)),
    defaultMode = "line",
    displayTitle = "碎石图"
  )
)

heatmap_values <- list()
for (i in seq_along(items)) {
  row <- list()
  for (j in seq_len(factor_count)) {
    row[[length(row) + 1]] <- round(rotated_loadings[i, j], 4)
  }
  row[[length(row) + 1]] <- round(communalities[[i]], 4)
  heatmap_values[[length(heatmap_values) + 1]] <- row
}
heatmap_chart <- list(
  chartType = "factor_loading_heatmap",
  title = "因子载荷矩阵热力图",
  data = list(
    rowLabels = as.list(items),
    colLabels = as.list(c(paste0("因子", seq_len(factor_count)), "共同度(公因子方差)")),
    values = heatmap_values
  )
)

advice <- paste(
  "效度分析用于研究定量数据（尤其是态度量表题）的结构合理性。",
  "第一：KMO值>0.9非常适合，0.8~0.9适合，0.7~0.8较适合，0.6~0.7勉强适合，<0.6不太适合。",
  "第二：Bartlett球形检验p<0.05说明变量间存在显著相关，适合继续做因子分析。",
  "第三：共同度通常希望高于0.4；因子载荷绝对值通常希望高于0.4，且题项应落在符合预期的因子上。",
  "第四：因子个数可结合特征根大于1、碎石图拐点和累计方差解释率综合判断。",
  sep = "\n"
)

description <- paste0(
  "对", scale_name, "进行效度分析。KMO值为", fmt_num(kmo_info$total, 3),
  "，", kmo_desc, "进行因子分析；Bartlett球形检验",
  ifelse(bartlett_info$p < 0.05, "显著", "不显著"),
  "（χ²=", fmt_num(bartlett_info$chi2, 3), "，df=", bartlett_info$dof, "，p=", fmt_p(bartlett_info$p, 3, TRUE), "）。",
  ifelse(factor_count_setting == "auto", "按特征根大于1自动提取", "按设置固定提取"), factor_count, "个因子，旋转后累计方差解释率为",
  fmt_pct(rotated_cum_pct[[factor_count]], 3), "。"
)

sections <- list()
section_kmo <- sec_table(
  "输出结果1：KMO检验和Bartlett的检验",
  c("检验", "指标", "值"),
  kmo_table_rows,
  "上表展示KMO检验和Bartlett球形检验的结果，用来判断是否可以进行因子分析。"
)
section_kmo$headerRows <- list(list(list(text = "KMO 和 Bartlett 的检验", colspan = 3L)))
section_kmo$bodyRowspanColumns <- 1L
sections[[length(sections) + 1]] <- section_kmo
sections[[length(sections) + 1]] <- sec_advice(advice)
sections[[length(sections) + 1]] <- sec_smart(description)
sections[[length(sections) + 1]] <- sec_table(
  "输出结果2：解释总方差",
  c("成分", "特征根", "方差解释率(%)", "累积百分比(%)", "旋转后特征根", "旋转后方差解释率(%)", "旋转后累积百分比(%)"),
  variance_rows,
  "该表用于查看各主成分对变量解释的贡献率。通常结合特征根大于1、累计解释率和碎石图确定因子个数。"
)
sections[[length(sections) + 1]] <- sec_charts(
  "输出结果3：碎石图",
  list(scree_chart),
  "碎石图用于观察特征根下降趋势，拐点前的成分通常更值得保留。"
)
section_loading <- sec_table(
  "输出结果4：因子载荷系数表",
  loading_headers,
  loading_rows_none,
  "上表展示因子载荷系数、共同度及因子提取相关汇总指标，用于判断题项与因子的对应关系。",
  "备注：表格中数字若有颜色：蓝色表示载荷系数绝对值大于0.4，红色表示共同度(公因子方差)小于0.4。"
)
section_loading$headerRows <- list(
  list(list(text = "效度分析结果", colspan = factor_count + 2L)),
  c(
    list(list(text = "名称", rowspan = 2L)),
    list(list(text = "因子载荷系数", colspan = factor_count)),
    list(list(text = "共同度(公因子方差)", rowspan = 2L))
  ),
  as.list(paste0("因子", seq_len(factor_count)))
)
section_loading$displayModeTitle <- ""
section_loading$displayModes <- loading_display_modes
section_loading$defaultDisplayMode <- "none"
section_loading$sortConfig <- list(
  type = "factor_loading",
  itemRowCount = length(items),
  factorCount = factor_count,
  values = loading_sort_values
)
sections[[length(sections) + 1]] <- section_loading
sections[[length(sections) + 1]] <- sec_charts(
  "输出结果5：因子载荷矩阵热力图",
  list(heatmap_chart),
  "热力图可快速查看题项与因子的对应关系，以及共同度是否偏低。"
)
sections[[length(sections) + 1]] <- sec_table(
  "各题项KMO",
  c("题项", "KMO"),
  kmo_rows
)
sections[[length(sections) + 1]] <- sec_table(
  "样本缺失情况汇总",
  c("项", "样本数", "占比"),
  missing_rows,
  "上表展示进入算法模型时有效样本和排除在外的无效样本情况。任一分析题项缺失都会导致该样本被排除。"
)
sections[[length(sections) + 1]] <- sec_refs(c(
  "[1] Kaiser, H. F. An index of factorial simplicity. Psychometrika, 1974.",
  "[2] Bartlett, M. S. A note on the multiplying factors for various chi square approximations. Journal of the Royal Statistical Society, 1954.",
  "[3] 周俊. 问卷数据分析破解SPSS的六类分析思路[M]. 电子工业出版社, 2017."
))

result <- list(
  success = TRUE,
  name = paste0("效度分析：", scale_name),
  headers = headers,
  rows = rows,
  description = description,
  sections = sections
)

cat(jsonlite::toJSON(result, auto_unbox = TRUE, null = "null", force = TRUE, dataframe = "rows"))
