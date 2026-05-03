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

escape_json <- function(x) {
  value <- ifelse(is.na(x), "", as.character(x))
  value <- gsub("\\\\", "\\\\\\\\", value)
  value <- gsub("\"", "\\\\\"", value)
  value <- gsub("\n", "\\\\n", value)
  value <- gsub("\r", "\\\\r", value)
  value
}

fmt_num <- function(x, digits = 3) {
  if (is.null(x) || length(x) == 0 || is.na(x) || is.infinite(x)) {
    return("\u2014")
  }
  if (abs(x - round(x)) < 1e-12) {
    return(as.character(as.integer(round(x))))
  }
  sprintf(paste0("%.", digits, "f"), x)
}

sec_table <- function(title, headers, rows, description = NULL) {
  item <- list(type = "table", title = title, headers = headers, rows = rows)
  if (!is.null(description)) {
    item$description <- description
  }
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

input <- jsonlite::fromJSON(read_utf8(input_path), simplifyVector = FALSE)
input_dir <- dirname(normalizePath(input_path, winslash = "/", mustWork = TRUE))
data_file <- file.path(input_dir, input$data_file)
if (!file.exists(data_file)) {
  stop("missing input data file")
}

raw_df <- read.csv(data_file, stringsAsFactors = FALSE, check.names = FALSE)
sections <- list()
smart_parts <- c()
main_headers <- c()
main_rows <- list()

for (scale_name in names(input$items_groups)) {
  cols <- unlist(input$items_groups[[scale_name]])
  cols <- cols[cols %in% names(raw_df)]
  if (length(cols) < 2) {
    next
  }
  data <- raw_df[, cols, drop = FALSE]
  for (col in cols) {
    data[[col]] <- suppressWarnings(as.numeric(data[[col]]))
  }
  data <- stats::na.omit(data)
  k <- ncol(data)
  n <- nrow(data)
  if (k < 2 || n < 2) {
    next
  }

  item_vars <- apply(data, 2, stats::var)
  total_scores <- rowSums(data)
  total_var <- stats::var(total_scores)
  alpha <- (k / (k - 1)) * (1 - sum(item_vars) / total_var)

  corr_matrix <- stats::cor(data)
  mean_r <- (sum(corr_matrix) - k) / (k * (k - 1))
  std_alpha <- ifelse((1 + (k - 1) * mean_r) != 0, (k * mean_r) / (1 + (k - 1) * mean_r), alpha)

  item_stats <- list()
  for (col in cols) {
    rest_cols <- cols[cols != col]
    rest_sum <- rowSums(data[, rest_cols, drop = FALSE])
    del_corr <- suppressWarnings(stats::cor(data[[col]], rest_sum))
    del_mean <- mean(rest_sum)
    del_var <- stats::var(rest_sum)
    alpha_del <- NA
    if (length(rest_cols) >= 2) {
      rest_data <- data[, rest_cols, drop = FALSE]
      rest_item_vars <- apply(rest_data, 2, stats::var)
      rest_total_var <- stats::var(rowSums(rest_data))
      alpha_del <- (length(rest_cols) / (length(rest_cols) - 1)) * (1 - sum(rest_item_vars) / rest_total_var)
    }
    item_stats[[length(item_stats) + 1]] <- list(
      col = col,
      del_mean = del_mean,
      del_var = del_var,
      del_corr = del_corr,
      alpha_del = alpha_del
    )
  }

  t1_headers <- c("Cronbach's α系数", "标准化Cronbach's α系数", "项数", "样本数")
  t1_rows <- list(list(fmt_num(alpha), fmt_num(std_alpha), as.character(k), as.character(n)))
  sections[[length(sections) + 1]] <- sec_table(
    "输出结果1：Cronbach's α系数表",
    t1_headers,
    t1_rows,
    "用于衡量量表题项的内部一致性。"
  )

  smart1 <- paste0("量表“", scale_name, "”的 Cronbach's α 为", fmt_num(alpha), "。")
  if (!is.na(alpha) && alpha >= 0.8) {
    smart1 <- paste0(smart1, "整体信度较好。")
  } else if (!is.na(alpha) && alpha >= 0.7) {
    smart1 <- paste0(smart1, "整体信度可以接受。")
  } else {
    smart1 <- paste0(smart1, "建议检查题项设置与反向题编码。")
  }
  sections[[length(sections) + 1]] <- sec_smart(smart1)

  t2_headers <- c("", "删除项后的平均值", "删除项后的方差", "删除的项与删除项后的总体的相关性", "删除项后的Cronbach's α系数")
  t2_rows <- list()
  t3_rows <- list()
  weak_items <- c()
  idx <- 1
  for (stat in item_stats) {
    t2_rows[[length(t2_rows) + 1]] <- list(
      stat$col,
      fmt_num(stat$del_mean),
      fmt_num(stat$del_var),
      fmt_num(stat$del_corr),
      fmt_num(stat$alpha_del)
    )
    conclusion <- "较好"
    if (!is.na(stat$del_corr) && stat$del_corr < 0.3) {
      conclusion <- "需要检查"
      weak_items <- c(weak_items, stat$col)
    }
    t3_rows[[length(t3_rows) + 1]] <- list(
      as.character(idx),
      stat$col,
      fmt_num(stat$del_corr),
      fmt_num(stat$alpha_del),
      conclusion
    )
    idx <- idx + 1
  }

  sections[[length(sections) + 1]] <- sec_table(
    "输出结果2：删除分析项统计汇总",
    t2_headers,
    t2_rows,
    "可结合删除项后的相关性与 α 系数变化，辅助判断题项保留情况。"
  )
  sections[[length(sections) + 1]] <- sec_table(
    "输出结果3：信度分析总结图",
    c("序号", "分析项名", "删除的项与删除项后的总体的相关性", "删除项后的Cronbach's α系数", "参考结论"),
    t3_rows,
    "若题项删除后整体表现改善明显，可考虑复核题项设计。"
  )

  if (length(weak_items) > 0) {
    sections[[length(sections) + 1]] <- sec_advice(
      paste0("建议重点复核以下题项：", paste(weak_items, collapse = "、"), "。如果存在反向题，请确认是否已完成反向编码。")
    )
  } else {
    sections[[length(sections) + 1]] <- sec_advice("当前题项内部一致性整体稳定，可继续用于后续问卷分析。")
  }

  smart_parts <- c(smart_parts, smart1)
  main_headers <- t1_headers
  main_rows <- t1_rows
}

sections[[length(sections) + 1]] <- sec_refs(c(
  "[1] Cronbach, L. J. Coefficient alpha and the internal structure of tests. Psychometrika, 1951.",
  "[2] Eisinga R, Te Grotenhuis M, Pelzer B. The reliability of a two-item scale: Pearson, Cronbach, or Spearman-Brown? International Journal of Public Health, 2013."
))

result <- list(
  success = TRUE,
  name = "信度分析",
  headers = main_headers,
  rows = main_rows,
  description = ifelse(length(smart_parts) > 0, paste(smart_parts, collapse = " "), "信度分析完成。"),
  sections = sections
)

cat(jsonlite::toJSON(result, auto_unbox = TRUE, null = "null", force = TRUE, dataframe = "rows"))
