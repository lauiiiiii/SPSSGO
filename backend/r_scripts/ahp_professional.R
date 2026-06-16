# AHP 专业版：固定处理“目标-指标-方案”三层决策模型。
# 这里负责指标矩阵、方案矩阵、综合得分和一致性检验；暂不支持任意多级树。
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
  table <- c(
    "1" = 0, "2" = 0, "3" = 0.58, "4" = 0.90, "5" = 1.12,
    "6" = 1.24, "7" = 1.32, "8" = 1.41, "9" = 1.45, "10" = 1.49,
    "11" = 1.52, "12" = 1.54, "13" = 1.56, "14" = 1.58, "15" = 1.59,
    "16" = 1.5943, "17" = 1.6064, "18" = 1.6133, "19" = 1.6207, "20" = 1.6292
  )
  key <- as.character(n)
  if (key %in% names(table)) table[[key]] else table[["20"]]
}

method_label <- function(method) {
  if (method == "root") return("方根法")
  if (method == "eigen") return("特征向量法")
  "和积法"
}

parse_items <- function(items, prefix, fallback_label) {
  if (is.null(items) || length(items) == 0) {
    return(list(ids = character(0), labels = character(0)))
  }
  ids <- character(0)
  labels <- character(0)
  if (is.list(items) && length(items) > 0 && is.list(items[[1]])) {
    for (i in seq_along(items)) {
      item <- items[[i]]
      item_id <- if (!is.null(item$id) && nzchar(trimws(as.character(item$id)))) {
        trimws(as.character(item$id))
      } else {
        paste0(prefix, i)
      }
      item_label <- if (!is.null(item$label) && nzchar(trimws(as.character(item$label)))) {
        trimws(as.character(item$label))
      } else {
        paste0(fallback_label, i)
      }
      ids <- c(ids, item_id)
      labels <- c(labels, item_label)
    }
  } else {
    labels <- trimws(as.character(unlist(items, use.names = FALSE)))
    labels <- labels[nzchar(labels)]
    ids <- paste0(prefix, seq_along(labels))
  }
  list(ids = ids, labels = labels)
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
    rows[[length(rows) + 1]] <- list(labels[[i]], fmt_num(weights[[i]], 4), paste0(fmt_num(weights[[i]] * 100, 3, TRUE), "%"), as.character(rank_idx))
  }
  rows
}

consistency_line <- function(name, calc) {
  list(
    name,
    fmt_num(calc$lambda_max, 4),
    fmt_num(calc$ci, 4),
    fmt_num(calc$ri, 4),
    fmt_num(calc$cr, 4),
    if (isTRUE(calc$passed)) "通过" else "不通过"
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

get_alt_matrix <- function(matrices, criterion_id, index) {
  if (is.null(matrices)) return(NULL)
  if (!is.null(names(matrices)) && criterion_id %in% names(matrices)) {
    return(matrices[[criterion_id]])
  }
  if (length(matrices) >= index) {
    return(matrices[[index]])
  }
  NULL
}

input <- jsonlite::fromJSON(read_utf8(input_path), simplifyVector = FALSE)
goal <- if (!is.null(input$goal) && nzchar(trimws(as.character(input$goal)))) trimws(as.character(input$goal)) else "中心主题"
weight_method <- if (!is.null(input$weight_method)) as.character(input$weight_method) else "sum_product"
if (!weight_method %in% c("sum_product", "root", "eigen")) {
  output_error("计算方法不支持。")
  quit(status = 0)
}

tryCatch({
  criteria <- parse_items(input$criteria, "c", "指标")
  alternatives <- parse_items(input$alternatives, "a", "方案")
  criterion_ids <- criteria$ids
  criterion_labels <- criteria$labels
  alternative_labels <- alternatives$labels

  if (length(criterion_labels) < 2 || length(criterion_labels) > 20) {
    output_error("AHP 专业版需要 2 到 20 个指标。")
    quit(status = 0)
  }
  if (length(alternative_labels) < 2 || length(alternative_labels) > 20) {
    output_error("AHP 专业版需要 2 到 20 个方案。")
    quit(status = 0)
  }
  if (any(duplicated(criterion_ids)) || any(duplicated(criterion_labels))) {
    output_error("指标 ID 和名称不能重复。")
    quit(status = 0)
  }
  if (any(duplicated(alternatives$ids)) || any(duplicated(alternative_labels))) {
    output_error("方案 ID 和名称不能重复。")
    quit(status = 0)
  }

  criteria_matrix <- as_numeric_matrix(input$criteria_matrix, length(criterion_labels), "指标判断矩阵")
  validate_judgment_matrix(criteria_matrix, criterion_labels, "指标判断矩阵")
  criteria_calc <- calc_weights(criteria_matrix, weight_method)

  local_weights <- matrix(0, nrow = length(criterion_labels), ncol = length(alternative_labels))
  consistency_rows <- list(consistency_line("指标权重", criteria_calc))
  alt_matrix_sections <- list()
  for (i in seq_along(criterion_labels)) {
    matrix_input <- get_alt_matrix(input$alternative_matrices, criterion_ids[[i]], i)
    matrix_name <- paste0("方案判断矩阵-", criterion_labels[[i]])
    alt_matrix <- as_numeric_matrix(matrix_input, length(alternative_labels), matrix_name)
    validate_judgment_matrix(alt_matrix, alternative_labels, matrix_name)
    alt_calc <- calc_weights(alt_matrix, weight_method)
    local_weights[i, ] <- alt_calc$weights
    consistency_rows[[length(consistency_rows) + 1]] <- consistency_line(criterion_labels[[i]], alt_calc)
    alt_matrix_sections[[length(alt_matrix_sections) + 1]] <- sec_table(
      matrix_name,
      c("方案", alternative_labels),
      matrix_rows(alt_matrix, alternative_labels)
    )
  }

  final_scores <- as.numeric(t(local_weights) %*% criteria_calc$weights)
  score_order <- order(final_scores, decreasing = TRUE)
  score_rows <- list()
  for (rank_idx in seq_along(score_order)) {
    j <- score_order[[rank_idx]]
    score_rows[[length(score_rows) + 1]] <- list(as.character(rank_idx), alternative_labels[[j]], fmt_num(final_scores[[j]], 4))
  }

  local_rows <- list()
  for (i in seq_along(criterion_labels)) {
    local_rows[[length(local_rows) + 1]] <- as.list(c(
      criterion_labels[[i]],
      vapply(local_weights[i, ], fmt_num, character(1), digits = 4)
    ))
  }

  failed_items <- vapply(consistency_rows, function(row) row[[6]] != "通过", logical(1))
  best_alt <- alternative_labels[[score_order[[1]]]]
  best_score <- final_scores[[score_order[[1]]]]
  score_labels <- alternative_labels[score_order]
  score_values <- final_scores[score_order]
  criteria_order <- order(criteria_calc$weights, decreasing = TRUE)
  flow_text <- paste0(
    "专业版按“目标-指标-方案”三层结构计算：先由指标判断矩阵得到指标权重，再分别计算各指标下方案局部权重，最后汇总为方案综合得分。",
    "本次目标为“",
    goal,
    "”，共评价 ",
    length(alternative_labels),
    " 个方案和 ",
    length(criterion_labels),
    " 个指标。"
  )

  sections <- list(
    sec_advice(flow_text, "分析流程"),
    sec_charts(
      "方案得分",
      list(metric_chart("方案综合得分", "综合得分", score_labels, score_values)),
      "图中展示各方案的综合得分，条形越长表示该方案在当前 AHP 模型下的综合评价越高。"
    ),
    sec_table("方案综合得分排名", c("排名", "方案", "综合得分"), score_rows),
    sec_table(
      "指标权重",
      c("指标", "权重", "权重值", "排序"),
      weight_rows(criterion_labels, criteria_calc$weights)
    ),
    sec_charts(
      "指标权重分布图",
      list(metric_chart("指标权重", "权重", criterion_labels[criteria_order], criteria_calc$weights[criteria_order])),
      "图中展示各指标对目标的权重大小。"
    ),
    sec_table(
      "决策模型摘要",
      c("项", "值"),
      list(
        list("目标", goal),
        list("指标数", as.character(length(criterion_labels))),
        list("方案数", as.character(length(alternative_labels))),
        list("计算方法", method_label(weight_method))
      )
    ),
    sec_table(
      "一致性检验汇总",
      c("对象", "最大特征根", "CI值", "RI值", "CR值", "一致性检验结果"),
      consistency_rows,
      description = if (any(failed_items)) {
        "存在至少一个判断矩阵 CR>=0.1，建议重新检查相关指标或方案两两比较。"
      } else {
        "所有判断矩阵均通过一致性检验。通常 CR<0.1 认为判断矩阵具有可接受一致性。"
      }
    ),
    sec_table("各指标下方案局部权重", c("指标", alternative_labels), local_rows),
    sec_table("指标判断矩阵", c("指标", criterion_labels), matrix_rows(criteria_matrix, criterion_labels))
  )
  for (section in alt_matrix_sections) {
    sections[[length(sections) + 1]] <- section
  }
  sections[[length(sections) + 1]] <- sec_smart(paste0(
    "AHP 专业版完成，综合得分最高的方案为 ",
    best_alt,
    "，得分为 ",
    fmt_num(best_score, 4),
    "。一致性检验",
    if (any(failed_items)) "存在未通过项，建议重新检查相关判断矩阵。" else "全部通过。"
  ))
  sections[[length(sections) + 1]] <- sec_refs(list(
    "[1] Saaty T L. The Analytic Hierarchy Process[M]. McGraw-Hill, 1980.",
    "[2] SPSSGO 团队. SPSSGO 在线数据分析平台[CP/OL]. https://www.spssgo.com."
  ))

  result <- list(
    success = TRUE,
    name = "层次分析法（AHP专业版）",
    headers = c("排名", "方案", "综合得分"),
    rows = score_rows,
    description = paste0(
      "AHP 专业版完成，共评价 ",
      length(alternative_labels),
      " 个方案、",
      length(criterion_labels),
      " 个指标；综合得分最高的方案为 ",
      best_alt,
      "。"
    ),
    sections = sections
  )
  cat(jsonlite::toJSON(result, auto_unbox = TRUE, force = TRUE))
}, error = function(e) {
  output_error(conditionMessage(e))
})
