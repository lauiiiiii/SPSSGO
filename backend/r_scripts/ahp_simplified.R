# AHP 快速版：支持手填判断矩阵和按变量均值自动估权两种入口。
# 这里负责矩阵校验、权重计算、一致性检验和结果 JSON 输出；Python 只做 R bridge。
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

fmt_num <- function(x, digits = 4, trim = FALSE) {
  if (is.null(x) || length(x) == 0 || is.na(x) || is.infinite(x)) {
    return("\u2014")
  }
  text <- sprintf(paste0("%.", digits, "f"), as.numeric(x))
  if (isTRUE(trim)) {
    text <- sub("0+$", "", text)
    text <- sub("\\.$", "", text)
  }
  text
}

sec_table <- function(title, headers, rows, note = NULL, description = NULL) {
  section <- list(type = "table", title = title, headers = headers, rows = rows)
  if (!is.null(note)) section$note <- note
  if (!is.null(description)) section$description <- description
  section
}

sec_charts <- function(title, charts, description = NULL) {
  section <- list(type = "charts", title = title, charts = charts)
  if (!is.null(description)) section$description <- description
  section
}

sec_advice <- function(content, title = "分析建议") {
  list(type = "advice", title = title, content = content)
}

sec_smart <- function(content) {
  list(type = "smart_analysis", title = "智能分析", content = content)
}

sec_refs <- function(items) {
  list(type = "references", title = "参考文献", items = items)
}

output_error <- function(message) {
  cat(jsonlite::toJSON(
    list(success = FALSE, error = message),
    auto_unbox = TRUE,
    force = TRUE
  ))
}

ri_value <- function(n) {
  table <- c("1" = 0, "2" = 0, "3" = 0.58, "4" = 0.90, "5" = 1.12,
             "6" = 1.24, "7" = 1.32, "8" = 1.41, "9" = 1.45, "10" = 1.49)
  key <- as.character(n)
  if (key %in% names(table)) table[[key]] else 1.49
}

method_label <- function(method) {
  if (method == "root") return("方根法")
  if (method == "eigen") return("特征向量法")
  "和积法"
}

as_vector <- function(value) {
  if (is.null(value)) return(character(0))
  as.character(unlist(value, use.names = FALSE))
}

as_numeric_matrix <- function(value, n, name) {
  if (is.null(value)) {
    stop(paste0(name, "不能为空。"))
  }
  if (is.matrix(value) || is.data.frame(value)) {
    matrix_value <- suppressWarnings(matrix(as.numeric(as.matrix(value)), nrow = n))
  } else if (is.list(value)) {
    if (length(value) != n) {
      stop(paste0(name, "必须是 ", n, " 阶方阵。"))
    }
    rows <- lapply(value, function(row) suppressWarnings(as.numeric(unlist(row, use.names = FALSE))))
    if (any(vapply(rows, length, integer(1)) != n)) {
      stop(paste0(name, "必须是 ", n, " 阶方阵。"))
    }
    matrix_value <- do.call(rbind, rows)
  } else {
    flat <- suppressWarnings(as.numeric(unlist(value, use.names = FALSE)))
    if (length(flat) != n * n) {
      stop(paste0(name, "必须是 ", n, " 阶方阵。"))
    }
    matrix_value <- matrix(flat, nrow = n, byrow = TRUE)
  }
  if (any(!is.finite(matrix_value))) {
    stop(paste0(name, "只能填写有效数字。"))
  }
  matrix_value
}

validate_judgment_matrix <- function(matrix_value, labels, name) {
  n <- length(labels)
  if (!all(dim(matrix_value) == c(n, n))) {
    stop(paste0(name, "必须是 ", n, " 阶方阵。"))
  }
  if (any(matrix_value <= 0)) {
    stop(paste0(name, "所有判断值必须为正数。"))
  }
  for (i in seq_len(n)) {
    if (abs(matrix_value[i, i] - 1) > 1e-6) {
      stop(paste0(name, "对角线必须全部为 1。"))
    }
  }
  for (i in seq_len(n)) {
    for (j in seq_len(n)) {
      if (abs(matrix_value[i, j] * matrix_value[j, i] - 1) > 0.01) {
        stop(paste0(name, "必须满足互反关系 aij = 1/aji。"))
      }
    }
  }
}

calc_weights <- function(matrix_value, method) {
  n <- nrow(matrix_value)
  if (method == "root") {
    feature_vector <- apply(matrix_value, 1, function(row) prod(row) ^ (1 / n))
    weights <- feature_vector / sum(feature_vector)
  } else if (method == "eigen") {
    eig <- eigen(matrix_value)
    max_idx <- which.max(Re(eig$values))
    feature_vector <- abs(Re(eig$vectors[, max_idx]))
    weights <- feature_vector / sum(feature_vector)
  } else {
    col_sum <- colSums(matrix_value)
    normalized <- sweep(matrix_value, 2, col_sum, "/")
    feature_vector <- rowMeans(normalized)
    weights <- feature_vector / sum(feature_vector)
  }
  lambda_max <- mean(as.numeric(matrix_value %*% weights) / weights)
  ci <- if (n > 2) (lambda_max - n) / (n - 1) else 0
  ci <- max(ci, 0)
  ri <- ri_value(n)
  cr <- if (ri == 0) 0 else ci / ri
  list(
    weights = weights,
    feature_vector = feature_vector,
    lambda_max = lambda_max,
    ci = ci,
    ri = ri,
    cr = cr,
    passed = n <= 2 || cr < 0.1
  )
}

matrix_rows <- function(matrix_value, labels) {
  rows <- list()
  for (i in seq_along(labels)) {
    rows[[length(rows) + 1]] <- as.list(unname(c(
      labels[[i]],
      unname(vapply(matrix_value[i, ], fmt_num, character(1), digits = 4))
    )))
  }
  rows
}

weight_rows <- function(labels, weights) {
  order_idx <- order(weights, decreasing = TRUE)
  rows <- list()
  for (rank_idx in seq_along(order_idx)) {
    i <- order_idx[[rank_idx]]
    rows[[length(rows) + 1]] <- list(labels[[i]], fmt_num(weights[[i]], 4), as.character(rank_idx))
  }
  rows
}

ahp_result_rows <- function(labels, calc) {
  rows <- list()
  for (i in seq_along(labels)) {
    rows[[length(rows) + 1]] <- list(
      labels[[i]],
      fmt_num(calc$feature_vector[[i]], 4, TRUE),
      paste0(fmt_num(calc$weights[[i]] * 100, 3, TRUE), "%"),
      if (i == 1) fmt_num(calc$lambda_max, 4) else "",
      if (i == 1) fmt_num(calc$ci, 4) else ""
    )
  }
  rows
}

consistency_summary_rows <- function(calc) {
  list(
    list(
      fmt_num(calc$lambda_max, 4),
      fmt_num(calc$ci, 4),
      fmt_num(calc$ri, 4),
      fmt_num(calc$cr, 4),
      if (isTRUE(calc$passed)) "通过" else "不通过"
    )
  )
}

metric_chart <- function(title, metric, labels, values, mode = "horizontalBar") {
  list(
    chartType = "metric_comparison",
    title = title,
    data = list(
      metric = metric,
      labels = labels,
      values = as.numeric(values),
      defaultMode = mode,
      displayModes = list(list(value = "horizontalBar", label = "条形图"), list(value = "bar", label = "柱形图"))
    )
  )
}

build_matrix_from_means <- function(data) {
  means <- abs(colMeans(data, na.rm = TRUE))
  means[!is.finite(means) | means == 0] <- 1e-6
  outer(means, means, "/")
}

score_top_rows <- function(data, weights, row_numbers) {
  normalized <- data
  for (j in seq_len(ncol(normalized))) {
    values <- normalized[, j]
    min_value <- min(values)
    max_value <- max(values)
    range_value <- max_value - min_value
    if (!is.finite(range_value) || abs(range_value) < 1e-12) {
      normalized[, j] <- 1
    } else {
      normalized[, j] <- (values - min_value) / range_value + 1e-12
    }
  }
  scores <- as.numeric(as.matrix(normalized) %*% weights)
  order_idx <- order(scores, decreasing = TRUE)
  order_idx <- head(order_idx, 10)
  rows <- list()
  for (idx in order_idx) {
    rows[[length(rows) + 1]] <- list(as.character(row_numbers[[idx]]), fmt_num(scores[[idx]], 4))
  }
  rows
}

input <- jsonlite::fromJSON(read_utf8(input_path), simplifyVector = FALSE)
input_dir <- dirname(normalizePath(input_path, winslash = "/", mustWork = TRUE))
input_mode <- if (!is.null(input$input_mode) && input$input_mode == "data_auto") "data_auto" else "matrix"
weight_method <- if (!is.null(input$weight_method)) as.character(input$weight_method) else "sum_product"
if (!weight_method %in% c("sum_product", "root", "eigen")) {
  output_error("计算方法不支持。")
  quit(status = 0)
}

tryCatch({
  sample_note <- NULL
  score_rows <- NULL
  if (input_mode == "data_auto") {
    variables <- as_vector(input$variables)
    if (length(variables) < 2) {
      output_error("AHP 快速版数据自动估权至少需要 2 个准则变量。")
      quit(status = 0)
    }
    data_file <- file.path(input_dir, input$data_file)
    if (!file.exists(data_file)) {
      output_error("AHP 快速版缺少输入数据文件。")
      quit(status = 0)
    }
    raw_df <- read.csv(data_file, stringsAsFactors = FALSE, check.names = FALSE, fileEncoding = "UTF-8")
    missing_vars <- setdiff(variables, names(raw_df))
    if (length(missing_vars) > 0) {
      output_error("准则变量不存在。")
      quit(status = 0)
    }
    numeric_df <- raw_df[, variables, drop = FALSE]
    for (col in variables) {
      numeric_df[[col]] <- suppressWarnings(as.numeric(numeric_df[[col]]))
    }
    complete_mask <- stats::complete.cases(numeric_df)
    data <- numeric_df[complete_mask, , drop = FALSE]
    if (nrow(data) < 2) {
      output_error("有效样本不足。")
      quit(status = 0)
    }
    labels <- variables
    matrix_value <- build_matrix_from_means(data)
    sample_note <- paste0("有效样本量 N=", nrow(data), "；该模式按指标均值比值自动构造判断矩阵，只适合快速估权参考。")
    row_numbers <- which(complete_mask)
  } else {
    labels <- trimws(as_vector(input$criteria))
    labels <- labels[nzchar(labels)]
    if (length(labels) < 2 || length(labels) > 10) {
      output_error("AHP 快速版手填矩阵需要 2 到 10 个指标。")
      quit(status = 0)
    }
    if (any(duplicated(labels))) {
      output_error("指标名称不能重复。")
      quit(status = 0)
    }
    matrix_value <- as_numeric_matrix(input$matrix, length(labels), "判断矩阵")
    validate_judgment_matrix(matrix_value, labels, "判断矩阵")
  }

  calc <- calc_weights(matrix_value, weight_method)
  if (input_mode == "data_auto") {
    score_rows <- score_top_rows(data, calc$weights, row_numbers)
  }
  highest <- labels[[which.max(calc$weights)]]
  order_idx <- order(calc$weights, decreasing = TRUE)
  consistency_result <- if (isTRUE(calc$passed)) "通过" else "不通过"
  consistency_text <- paste0(
    "本次构建 ",
    length(labels),
    " 阶判断矩阵，最大特征根为 ",
    fmt_num(calc$lambda_max, 4),
    "，CI=",
    fmt_num(calc$ci, 4),
    "，对应 RI=",
    fmt_num(calc$ri, 4),
    "，CR=",
    fmt_num(calc$cr, 4),
    if (isTRUE(calc$passed)) " < 0.1，判断矩阵通过一致性检验。" else " >= 0.1，判断矩阵未通过一致性检验，建议重新调整两两比较。"
  )

  sections <- list(
    sec_advice(
      paste0(
        "AHP 快速版用于计算指标权重。分析流程为：填写判断矩阵，计算特征向量和权重值，再通过 CI、RI 和 CR 判断矩阵是否具有可接受一致性。",
        if (input_mode == "data_auto") " 当前结果由数据自动估权生成，不等同于专家两两比较判断，正式报告建议使用手填判断矩阵。" else ""
      ),
      "方法说明"
    ),
    sec_table("判断矩阵", c("项", labels), matrix_rows(matrix_value, labels)),
    sec_charts(
      "权重分布图",
      list(metric_chart("指标权重", "权重", labels[order_idx], calc$weights[order_idx])),
      "图中展示各指标的权重大小，条形越长表示该指标在本次 AHP 判断中越重要。"
    ),
    sec_table(
      "AHP层次分析结果",
      c("项", "特征向量", "权重值", "最大特征根", "CI值"),
      ahp_result_rows(labels, calc),
      description = paste0("权重值为归一化后的指标重要性百分比；本次计算方法为", method_label(weight_method), "。")
    ),
    sec_table(
      "一致性检验结果汇总",
      c("最大特征根", "CI值", "RI值", "CR值", "一致性检验结果"),
      consistency_summary_rows(calc),
      description = consistency_text
    ),
    sec_advice(
      paste0(
        "利用 AHP 层次分析法进行权重计算时，需要进行一致性检验。CI=(最大特征根-n)/(n-1)，RI 为 n 阶随机一致性指标，CR=CI/RI。",
        "通常 CR<0.1 认为判断矩阵满足一致性检验；若 CR>=0.1，应重新检查判断矩阵中逻辑冲突较大的两两比较。"
      )
    )
  )
  if (!is.null(sample_note)) {
    sections[[length(sections) + 1]] <- sec_table(
      "有效样本情况",
      c("项", "值"),
      list(list("有效样本量", as.character(nrow(data))), list("建模方式", "按指标均值比值自动构造判断矩阵")),
      description = sample_note
    )
    sections[[length(sections) + 1]] <- sec_table("综合得分 Top10", c("样本索引", "综合得分"), score_rows)
  }
  sections[[length(sections) + 1]] <- sec_smart(paste0(
    "AHP 快速版完成，权重最高的指标为 ",
    highest,
    "，权重值为 ",
    paste0(fmt_num(max(calc$weights) * 100, 3, TRUE), "%"),
    "；一致性检验结果为",
    consistency_result,
    "。"
  ))
  sections[[length(sections) + 1]] <- sec_refs(list(
    "[1] Saaty T L. The Analytic Hierarchy Process[M]. McGraw-Hill, 1980.",
    "[2] SPSSGO 团队. SPSSGO 在线数据分析平台[CP/OL]. https://www.spssgo.com."
  ))

  result <- list(
    success = TRUE,
    name = "层次分析法（AHP快速版）",
    headers = c("准则", "权重", "排序"),
    rows = weight_rows(labels, calc$weights),
    description = paste0(
      "AHP 快速版完成，共计算 ",
      length(labels),
      " 个准则权重；计算方法为",
      method_label(weight_method),
      "。"
    ),
    sections = sections
  )
  cat(jsonlite::toJSON(result, auto_unbox = TRUE, force = TRUE))
}, error = function(e) {
  output_error(conditionMessage(e))
})
