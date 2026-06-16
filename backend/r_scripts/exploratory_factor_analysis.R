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

fmt_pct <- function(x, digits = 3) {
  if (is.null(x) || length(x) == 0 || is.na(x) || is.infinite(x)) {
    return("\u2014")
  }
  paste0(fmt_num(x, digits), "%")
}

fmt_p <- function(p, digits = 3) {
  if (is.null(p) || length(p) == 0 || is.na(p) || is.infinite(p)) {
    return("\u2014")
  }
  fmt_num(p, digits)
}

as_flag <- function(value) {
  if (is.null(value) || length(value) == 0) return(FALSE)
  if (is.logical(value)) return(isTRUE(value[[1]]))
  normalized <- tolower(trimws(as.character(value[[1]])))
  normalized %in% c("1", "true", "yes", "y", "on", "是")
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

normalize_loading_signs <- function(loadings_matrix, score_coefficients, phi_matrix = NULL) {
  sign_vector <- rep(1, ncol(loadings_matrix))
  for (col_idx in seq_len(ncol(loadings_matrix))) {
    column <- loadings_matrix[, col_idx]
    max_idx <- which.max(abs(column))
    if (length(max_idx) && !is.na(column[max_idx]) && column[max_idx] < 0) {
      sign_vector[col_idx] <- -1
    }
  }
  loadings_matrix <- sweep(loadings_matrix, 2, sign_vector, `*`)
  score_coefficients <- sweep(score_coefficients, 2, sign_vector, `*`)
  if (!is.null(phi_matrix) && ncol(phi_matrix) == length(sign_vector)) {
    diag_sign <- diag(sign_vector, nrow = length(sign_vector))
    phi_matrix <- diag_sign %*% phi_matrix %*% diag_sign
  }
  list(loadings = loadings_matrix, scores = score_coefficients, phi = phi_matrix)
}

rotation_label <- function(method, factor_count) {
  if (factor_count <= 1) {
    return("因子数为1，未执行旋转")
  }
  if (identical(method, "promax")) {
    return("最优斜交法Promax")
  }
  "最大方差法Varimax"
}

build_rotation <- function(unrotated_loadings, method) {
  factor_count <- ncol(unrotated_loadings)
  base_transform <- diag(factor_count)
  if (factor_count <= 1) {
    return(list(
      loadings = unrotated_loadings,
      transform = base_transform,
      phi = diag(1),
      label = rotation_label(method, factor_count)
    ))
  }

  varimax_result <- stats::varimax(unrotated_loadings)
  if (!identical(method, "promax")) {
    return(list(
      loadings = as.matrix(varimax_result$loadings),
      transform = varimax_result$rotmat,
      phi = diag(factor_count),
      label = rotation_label("varimax", factor_count)
    ))
  }

  promax_result <- stats::promax(varimax_result$loadings)
  combined_transform <- varimax_result$rotmat %*% promax_result$rotmat
  phi_matrix <- promax_result$Phi
  if (is.null(phi_matrix)) {
    phi_matrix <- diag(factor_count)
  }
  list(
    loadings = as.matrix(promax_result$loadings),
    transform = combined_transform,
    phi = phi_matrix,
    label = rotation_label("promax", factor_count)
  )
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
rotation_method <- tolower(ifelse(is.null(input$rotation_method) || !nzchar(as.character(input$rotation_method)), "varimax", as.character(input$rotation_method)))
if (!rotation_method %in% c("varimax", "promax")) {
  rotation_method <- "varimax"
}
output_correlation_matrix <- as_flag(input$output_correlation_matrix)
save_factor_scores <- as_flag(input$save_factor_scores)
save_composite_score <- as_flag(input$save_composite_score)
row_id_column <- ifelse(is.null(input$row_id_column) || !nzchar(as.character(input$row_id_column)), "__row_id__", as.character(input$row_id_column))

if (length(items) < 3) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "需要至少3个题目。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}
if (!row_id_column %in% names(raw_df)) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "缺少原始行号信息，无法进行探索性因子分析。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

data_numeric <- raw_df[, items, drop = FALSE]
for (col in items) {
  data_numeric[[col]] <- suppressWarnings(as.numeric(data_numeric[[col]]))
}

row_ids <- suppressWarnings(as.integer(raw_df[[row_id_column]]))
complete_mask <- stats::complete.cases(data_numeric)
valid_data <- data_numeric[complete_mask, , drop = FALSE]
valid_row_ids <- row_ids[complete_mask]

if (nrow(valid_data) < 5) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "有效样本不足。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

corr_matrix <- stats::cor(valid_data)
det_corr <- det(corr_matrix)
if (is.na(det_corr) || det_corr <= 0) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "相关矩阵不可逆，无法进行探索性因子分析。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

item_count <- length(items)
total_rows <- nrow(raw_df)
valid_rows <- nrow(valid_data)
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
  }
}

selected_eigen_values <- eigen_values[seq_len(factor_count)]
selected_vectors <- eigen_vectors[, seq_len(factor_count), drop = FALSE]
unrotated_loadings <- selected_vectors %*% diag(sqrt(selected_eigen_values), nrow = factor_count)
rotation_result <- build_rotation(unrotated_loadings, rotation_method)
rotated_loadings <- rotation_result$loadings
score_coefficients <- selected_vectors %*% rotation_result$transform
normalized_result <- normalize_loading_signs(rotated_loadings, score_coefficients, rotation_result$phi)
rotated_loadings <- normalized_result$loadings
score_coefficients <- normalized_result$scores
phi_matrix <- normalized_result$phi

rownames(rotated_loadings) <- items
colnames(rotated_loadings) <- paste0("因子", seq_len(factor_count))
rownames(score_coefficients) <- items
colnames(score_coefficients) <- paste0("成分", seq_len(factor_count))
if (is.null(phi_matrix)) {
  phi_matrix <- diag(factor_count)
}

structure_loadings <- rotated_loadings %*% phi_matrix
communalities <- pmax(rowSums(rotated_loadings * structure_loadings), 0)
rotated_ss <- pmax(colSums(rotated_loadings * structure_loadings), 0)
rotated_var_pct <- rotated_ss / item_count * 100
rotated_cum_pct <- cumsum(rotated_var_pct)
initial_var_pct <- eigen_values / item_count * 100
initial_cum_pct <- cumsum(initial_var_pct)

standardized_valid <- scale(valid_data)
factor_scores_valid <- standardized_valid %*% score_coefficients
colnames(factor_scores_valid) <- paste0("成分", seq_len(factor_count))

score_columns <- list()
if (save_factor_scores || save_composite_score) {
  score_matrix_full <- matrix(NA_real_, nrow = total_rows, ncol = factor_count)
  valid_positions <- valid_row_ids + 1L
  for (idx in seq_along(valid_positions)) {
    pos <- valid_positions[[idx]]
    if (!is.na(pos) && pos >= 1 && pos <= total_rows) {
      score_matrix_full[pos, ] <- factor_scores_valid[idx, ]
    }
  }

  if (save_factor_scores) {
    for (col_idx in seq_len(factor_count)) {
      score_columns[[length(score_columns) + 1]] <- list(
        base_name = paste0("FactorScore_", col_idx),
        values = as.list(round(score_matrix_full[, col_idx], 6))
      )
    }
  }

  if (save_composite_score) {
    weight_sum <- sum(rotated_var_pct)
    if (weight_sum > 0) {
      composite_valid <- as.numeric(factor_scores_valid %*% (rotated_var_pct / weight_sum))
    } else {
      composite_valid <- rowMeans(factor_scores_valid)
    }
    composite_full <- rep(NA_real_, total_rows)
    for (idx in seq_along(valid_positions)) {
      pos <- valid_positions[[idx]]
      if (!is.na(pos) && pos >= 1 && pos <= total_rows) {
        composite_full[pos] <- composite_valid[[idx]]
      }
    }
    score_columns[[length(score_columns) + 1]] <- list(
      base_name = "CompScore_1",
      values = as.list(round(composite_full, 6))
    )
  }
}

kmo_desc <- "不适合"
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
  list("KMO值", fmt_num(kmo_info$total, 3)),
  list("Bartlett球形检验 近似卡方", fmt_num(bartlett_info$chi2, 3)),
  list("Bartlett球形检验 df", as.character(bartlett_info$dof)),
  list("Bartlett球形检验 p值", fmt_p(bartlett_info$p, 3)),
  list("因子提取方式", factor_count_mode),
  list("旋转方法", rotation_result$label),
  list("有效样本量", as.character(valid_rows))
)

kmo_table_rows <- list(
  list(list(text = "KMO值", colspan = 2L), fmt_num(kmo_info$total, 3)),
  list(list(text = "Bartlett 球形度检验", rowspan = 3L), "近似卡方", fmt_num(bartlett_info$chi2, 3)),
  list("df", as.character(bartlett_info$dof)),
  list("p 值", fmt_p(bartlett_info$p, 3))
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

loading_rows_none <- build_loading_rows(NULL)
loading_rows_hide_default <- build_loading_rows(0.4)
loading_display_modes <- list(
  list(key = "hide_default", label = "隐藏载荷系数", rows = loading_rows_hide_default),
  list(key = "none", label = "不隐藏", rows = loading_rows_none),
  list(key = "hide_0_7", label = "小于0.7", rows = build_loading_rows(0.7)),
  list(key = "hide_0_6", label = "小于0.6", rows = build_loading_rows(0.6)),
  list(key = "hide_0_5", label = "小于0.5", rows = build_loading_rows(0.5)),
  list(key = "hide_0_4", label = "小于0.4", rows = loading_rows_hide_default),
  list(key = "hide_0_3", label = "小于0.3", rows = build_loading_rows(0.3)),
  list(key = "hide_0_2", label = "小于0.2", rows = build_loading_rows(0.2)),
  list(key = "hide_0_1", label = "小于0.1", rows = build_loading_rows(0.1))
)

loading_sort_values <- list()
for (i in seq_along(items)) {
  loading_sort_values[[length(loading_sort_values) + 1]] <- as.list(unname(round(rotated_loadings[i, seq_len(factor_count)], 6)))
}

score_headers <- c("名称", paste0("成分", seq_len(factor_count)))
score_rows <- list()
for (i in seq_along(items)) {
  score_rows[[length(score_rows) + 1]] <- c(
    list(items[[i]]),
    lapply(seq_len(factor_count), function(j) fmt_num(score_coefficients[i, j], 3))
  )
}

correlation_rows <- list()
if (output_correlation_matrix) {
  for (i in seq_along(items)) {
    correlation_rows[[length(correlation_rows) + 1]] <- c(
      list(items[[i]]),
      lapply(seq_along(items), function(j) fmt_num(corr_matrix[i, j], 3))
    )
  }
}

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

quadrant_points <- list()
if (factor_count >= 2) {
  for (i in seq_along(items)) {
    point <- list(
      label = items[[i]],
      x = round(rotated_loadings[i, 1], 4),
      y = round(rotated_loadings[i, 2], 4)
    )
    if (factor_count >= 3) {
      point$z <- round(rotated_loadings[i, 3], 4)
    }
    quadrant_points[[length(quadrant_points) + 1]] <- point
  }
}
quadrant_chart_2d <- if (factor_count >= 2) {
  list(
    chartType = "factor_loading_quadrant",
    title = "二维因子载荷图",
    data = list(
      points = quadrant_points,
      xLabel = "维度1",
      yLabel = "维度2",
      showThreeDim = FALSE,
      viewMode = "2d"
    )
  )
} else {
  NULL
}

quadrant_chart_3d <- if (factor_count >= 3) {
  list(
    chartType = "factor_loading_quadrant",
    title = "三维因子载荷图",
    data = list(
      points = quadrant_points,
      xLabel = "维度1",
      yLabel = "维度2",
      zLabel = "维度3",
      showThreeDim = TRUE,
      viewMode = "3d"
    )
  )
} else {
  NULL
}

low_communality_items <- items[communalities < 0.4]
cross_loading_items <- c()
if (factor_count >= 2) {
  for (i in seq_along(items)) {
    if (sum(abs(rotated_loadings[i, ]) >= 0.4, na.rm = TRUE) >= 2) {
      cross_loading_items <- c(cross_loading_items, items[[i]])
    }
  }
}

score_formula <- if (save_factor_scores || save_composite_score) {
  formula_lines <- c()
  for (factor_idx in seq_len(factor_count)) {
    terms <- c()
    for (item_idx in seq_along(items)) {
      terms[[length(terms) + 1]] <- paste0(fmt_num(score_coefficients[item_idx, factor_idx], 3), "*", items[[item_idx]])
    }
    formula_lines[[length(formula_lines) + 1]] <- paste0("因子得分", factor_idx, "=", paste(terms, collapse = "+"))
  }
  if (save_composite_score) {
    weight_terms <- paste0("F", seq_len(factor_count), "*", fmt_num(rotated_var_pct, 3))
    formula_lines[[length(formula_lines) + 1]] <- paste0(
      "综合得分=(",
      paste(weight_terms, collapse = "+"),
      ")/",
      fmt_num(sum(rotated_var_pct), 3)
    )
  }
  paste(formula_lines, collapse = "\n")
} else {
  "本次未勾选保存因子得分或保存综合得分，因此不会生成新的得分变量。"
}

description <- paste0(
  "对", scale_name, "进行探索性因子分析。KMO值为", fmt_num(kmo_info$total, 3),
  "，", kmo_desc, "进行因子分析；Bartlett球形检验",
  ifelse(bartlett_info$p < 0.05, "显著", "不显著"),
  "（χ²=", fmt_num(bartlett_info$chi2, 3), "，df=", bartlett_info$dof, "，p=", fmt_p(bartlett_info$p, 3), "）。",
  ifelse(factor_count_setting == "auto", "按特征根大于1自动提取", "按设置固定提取"), factor_count,
  "个因子，采用", rotation_result$label, "，旋转后累计方差解释率为",
  fmt_pct(rotated_cum_pct[[factor_count]], 3), "。算法采用整行剔除处理缺失值，有效样本量为",
  valid_rows, "，剔除样本量为", excluded_rows, "。"
)

sections <- list()

section_kmo <- sec_table(
  "KMO 和 Bartlett 的检验",
  c("检验", "指标", "值"),
  kmo_table_rows,
  "上表展示 KMO 检验和 Bartlett 球形检验结果，用于判断是否适合继续进行探索性因子分析。"
)
section_kmo$headerRows <- list(list(list(text = "KMO 和 Bartlett 的检验", colspan = 3L)))
section_kmo$bodyRowspanColumns <- 1L
sections[[length(sections) + 1]] <- section_kmo
sections[[length(sections) + 1]] <- sec_advice(paste(
  "第一：分析探索性因子分析前，可以先观察 KMO 和 Bartlett 球形检验结果；",
  "第二：若 KMO 值高于 0.8，说明非常适合进行因子分析；若 KMO 值高于 0.7~0.8 之间，则说明比较适合进行因子分析；若 KMO 值高于 0.6~0.7，则说明可以进行因子分析；若 KMO 值小于 0.6，说明不太适合进行因子分析；",
  "第三：如果 Bartlett 检验对应 p 值小于 0.05，说明适合进行因子分析；",
  "第四：如果仅两个分析项，则 KMO 无论如何均为 0.5。",
  sep = "\n"
))
sections[[length(sections) + 1]] <- sec_smart(paste0(
  "使用因子分析进行信息浓缩研究，首先分析研究数据是否适合进行因子分析。从上表可以看出：KMO为",
  fmt_num(kmo_info$total, 3), "，", ifelse(kmo_info$total >= 0.6, "大于0.6，满足因子分析的前提要求", "未达到0.6，说明不太适合继续进行因子分析"),
  "；同时数据通过Bartlett球形度检验（p=", fmt_p(bartlett_info$p, 3), "），说明研究数据适合进行因子分析。"
))

sections[[length(sections) + 1]] <- sec_table(
  "方差解释率表格",
  c("因子编号", "特征根", "方差解释率%", "累积%", "旋转后特征根", "旋转后方差解释率%", "旋转后累积%"),
  variance_rows,
  "上表格对应因子提取情况，以及因子提取信息总情况进行分析。"
)
# 方差解释率智能分析
total_cum <- rotated_cum_pct[[factor_count]]
first_initial_var <- initial_var_pct[[1]]

# 提取方式说明
if (factor_count_setting == "auto") {
  extraction_note <- paste0(
    "依据特征根大于1的Kaiser准则，从", item_count, "个题项中提取出", factor_count, "个因子。",
    if (factor_count < item_count && item_count - factor_count == 1) {
      paste0("第", factor_count + 1, "个因子特征根为", fmt_num(eigen_values[[factor_count + 1]], 3), "，未达到1.0的提取门槛。")
    } else if (factor_count < item_count) {
      paste0("从第", factor_count + 1, "个因子起特征根均低于1.0，因此不予提取。")
    } else {
      ""
    }
  )
} else {
  note_extra <- ""
  if (factor_count < item_count) {
    note_extra <- paste0("（第", factor_count + 1, "个因子特征根为", fmt_num(eigen_values[[factor_count + 1]], 3), "，已低于1.0）")
  }
  extraction_note <- paste0("按手动设置提取", factor_count, "个因子。", note_extra)
}

# 旋转效果评价
redistribution_note <- ""
if (factor_count >= 2 && first_initial_var > 0) {
  first_post_var <- rotated_var_pct[[1]]
  redistribution <- first_initial_var - first_post_var
  if (redistribution > 8) {
    redistribution_note <- paste0(
      "旋转前第一个因子方差解释率达", fmt_pct(first_initial_var, 1),
      "，存在较明显的载荷集中；经", rotation_result$label, "旋转后第一个因子方差解释率降至",
      fmt_pct(first_post_var, 1), "，方差被重新分配至其他因子，因子结构更加均衡清晰。"
    )
  } else if (redistribution > 3) {
    redistribution_note <- paste0(
      "经", rotation_result$label, "旋转后，第一个因子方差解释率由",
      fmt_pct(first_initial_var, 1), "调整为", fmt_pct(first_post_var, 1),
      "，各因子方差分布更趋合理。"
    )
  } else {
    redistribution_note <- paste0(
      rotation_result$label, "旋转后各因子方差分布较为均衡。"
    )
  }
}

# 总解释力评价（阈值参考 Hair et al. 2014 及 Merenda 1997）
if (total_cum >= 70) {
  adequacy <- paste0(
    "旋转后累计方差解释率达", fmt_pct(total_cum, 1),
    "，高于社会科学研究常用良好水平（Hair et al. 建议≥60%），提取的因子能够充分概括原始变量的变异信息。"
  )
} else if (total_cum >= 60) {
  adequacy <- paste0(
    "旋转后累计方差解释率为", fmt_pct(total_cum, 1),
    "，达到社会科学研究满意水平（Hair et al. 建议≥60%），提取的因子对原始变量具有较好的代表性。"
  )
} else if (total_cum >= 50) {
  adequacy <- paste0(
    "旋转后累计方差解释率为", fmt_pct(total_cum, 1),
    "，虽低于60%的经验满意线，但仍高于Merenda建议的50%最低要求，且在社科研究中此类解释水平并不少见（Peterson, 2000）。",
    "建议结合因子载荷系数表关注共同度较低的题项，评估是否需要删除部分题项以改善解释力。"
  )
} else {
  adequacy <- paste0(
    "旋转后累计方差解释率仅为", fmt_pct(total_cum, 1),
    "，低于Merenda（1997）建议的50%最低要求，解释力不足。",
    "提示题项间共同变异偏低或题项质量有待提升，建议结合载荷表和共同度排查异常题项，必要时调整变量组合重新分析。"
  )
}

variance_smart <- paste0(extraction_note, redistribution_note, adequacy)
sections[[length(sections) + 1]] <- sec_smart(variance_smart)

section_loading <- sec_table(
  "旋转后因子载荷系数表",
  loading_headers,
  loading_rows_hide_default,
  "上表展示因子项对于研究项的信息提取情况，以及因子和研究项对应关系。",
  paste0(
    "备注：表格中数字若有颜色：蓝色表示载荷系数绝对值大于0.4，红色表示共同度(公因子方差)小于0.4。\n",
    "旋转方法：", rotation_result$label, "。"
  )
)
section_loading$headerRows <- list(
  list(
    list(text = "名称", rowspan = 2L),
    list(text = "因子载荷系数", colspan = factor_count),
    list(text = "共同度(公因子方差)", rowspan = 2L)
  ),
  as.list(paste0("因子", seq_len(factor_count)))
)
section_loading$displayModeTitle <- ""
section_loading$displayModes <- loading_display_modes
section_loading$defaultDisplayMode <- "hide_default"
section_loading$sortConfig <- list(
  type = "factor_loading",
  itemRowCount = length(items),
  factorCount = factor_count,
  values = loading_sort_values
)
sections[[length(sections) + 1]] <- section_loading
sections[[length(sections) + 1]] <- sec_advice(paste(
  "第一：通过因子载荷系数值，分析出每个因子与题项对应关系；",
  "第二：结合因子与题项对应关系，对各个因子进行命名。",
  sep = "\n"
))

loading_summary_lines <- c(
  paste0("本次研究使用", rotation_result$label, "进行旋转，以便找出因子和研究项的对应关系。"),
  paste0("共涉及", length(items), "个研究项；其中共同度小于0.4的题项有", length(low_communality_items), "个。")
)
if (length(low_communality_items) > 0) {
  loading_summary_lines[[length(loading_summary_lines) + 1]] <- paste0("共同度偏低题项：", paste(low_communality_items, collapse = "、"), "。")
}
if (length(cross_loading_items) > 0) {
  loading_summary_lines[[length(loading_summary_lines) + 1]] <- paste0("存在跨因子载荷偏高题项：", paste(cross_loading_items, collapse = "、"), "。")
}
sections[[length(sections) + 1]] <- sec_smart(paste(loading_summary_lines, collapse = "\n"))
sections[[length(sections) + 1]] <- sec_charts(
  "因子载荷矩阵热力图",
  list(heatmap_chart),
  "热力图通过颜色深浅展示各题项在不同因子上的载荷大小，以及共同度是否偏低，可快速定位高载荷或低共同度题项。"
)
if (!is.null(quadrant_chart_2d)) {
  quadrant_charts <- list(quadrant_chart_2d)
  if (!is.null(quadrant_chart_3d)) {
    quadrant_charts[[length(quadrant_charts) + 1]] <- quadrant_chart_3d
  }
  sections[[length(sections) + 1]] <- sec_charts(
    "因子载荷象限分析",
    quadrant_charts,
    ifelse(
      factor_count >= 3,
      "因子载荷图通过将多因子降维成双因子或者三因子，展示题项在因子空间中的分布情况。二维图用于观察前两个因子的题项聚类，三维图用于观察前三个因子的空间分布。",
      "因子载荷图通过将多因子降维成双因子，展示题项在前两个因子空间中的分布情况，可辅助判断题项聚类和跨因子载荷情况。"
    )
  )
}

sections[[length(sections) + 1]] <- sec_table(
  "成份得分系数矩阵",
  score_headers,
  score_rows,
  "使用因子分析目的在于信息浓缩，如需使用因子分析法进行权重计算，则需要使用成份得分系数矩阵建立因子和研究项之间的关系公式。"
)
sections[[length(sections) + 1]] <- sec_smart(paste(
  "使用因子分析目的在于信息浓缩，如需使用因子分析法进行权重计算，则需要使用成份得分系数矩阵建立因子和研究项之间的关系等式。",
  "得分基于标准化后数据计算，缺失行得分留空。",
  score_formula,
  sep = "\n"
))

sections[[length(sections) + 1]] <- sec_charts(
  "碎石图",
  list(scree_chart),
  "碎石图用于辅助判断因子提取个数，当折线由陡峭变为平缓时，陡峭前平稳对应的因子个数可作为参考提取因子个数。"
)

if (output_correlation_matrix) {
  sections[[length(sections) + 1]] <- sec_table(
    "相关系数矩阵",
    c("名称", items),
    correlation_rows,
    "该表展示题项两两之间的相关关系，可辅助判断题项结构是否适合继续做因子分析。"
  )
}

sections[[length(sections) + 1]] <- sec_refs(c(
  "[1] Kaiser, H. F. An index of factorial simplicity. Psychometrika, 1974.",
  "[2] Bartlett, M. S. A note on the multiplying factors for various chi square approximations. Journal of the Royal Statistical Society, 1954.",
  "[3] Hair, J. F., Black, W. C., Babin, B. J., & Anderson, R. E. Multivariate data analysis (7th ed.). Pearson, 2014.",
  "[4] Merenda, P. F. Factor analysis in international encyclopedia of the social and behavioral sciences. Elsevier, 1997.",
  "[5] Peterson, R. A. A meta-analysis of variance accounted for and factor loadings in exploratory factor analysis. Marketing Letters, 2000.",
  "[6] 周俊. 问卷数据分析破解SPSS的六类分析思路[M]. 电子工业出版社, 2017."
))

result <- list(
  success = TRUE,
  name = "探索性因子分析（EFA）",
  headers = headers,
  rows = rows,
  description = description,
  sections = sections
)
if (length(score_columns) > 0) {
  result$score_columns <- score_columns
}

cat(jsonlite::toJSON(result, auto_unbox = TRUE, null = "null", na = "null", force = TRUE, dataframe = "rows"))
