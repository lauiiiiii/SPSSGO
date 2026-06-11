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

fail_result <- function(message) {
  cat(jsonlite::toJSON(list(success = FALSE, error = message), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

fmt_num <- function(x, digits = 3) {
  if (is.null(x) || length(x) == 0 || is.na(x) || is.infinite(x)) return("—")
  sprintf(paste0("%.", digits, "f"), x)
}

fmt_df <- function(x) {
  if (is.null(x) || length(x) == 0 || is.na(x) || is.infinite(x)) return("—")
  as.character(as.integer(round(x)))
}

fmt_p <- function(p) {
  if (is.null(p) || length(p) == 0 || is.na(p) || is.infinite(p)) return("—")
  if (p < 0.001) return("0.000****")
  stars <- if (p < 0.01) {
    "***"
  } else if (p < 0.05) {
    "**"
  } else if (p < 0.1) {
    "*"
  } else {
    ""
  }
  paste0(sprintf("%.3f", p), stars)
}

table_cell <- function(text, colspan = NULL, rowspan = NULL) {
  cell <- list(text = text)
  if (!is.null(colspan)) cell$colspan <- colspan
  if (!is.null(rowspan)) cell$rowspan <- rowspan
  cell
}

sec_table <- function(title, headers, rows, description = NULL, note = NULL, headerRows = NULL, tableClass = NULL) {
  item <- list(type = "table", title = title, headers = headers, rows = rows)
  if (!is.null(description)) item$description <- description
  if (!is.null(note)) item$note <- note
  if (!is.null(headerRows)) item$headerRows <- headerRows
  if (!is.null(tableClass)) item$tableClass <- tableClass
  item
}

sec_advice <- function(content, title = "分析建议") list(type = "advice", title = title, content = content)
sec_smart <- function(content) list(type = "smart_analysis", title = "智能分析", content = content)
sec_refs <- function(items) list(type = "references", title = "参考文献", items = items)

safe_div <- function(numerator, denominator) {
  if (is.null(denominator) || length(denominator) == 0 || is.na(denominator) || !is.finite(denominator)) return(NA_real_)
  if (abs(denominator) < .Machine$double.eps) return(NA_real_)
  numerator / denominator
}

avg_from_single <- function(single_icc, k) {
  safe_div(k * single_icc, 1 + (k - 1) * single_icc)
}

icc_level_text <- function(value) {
  if (is.null(value) || length(value) == 0 || is.na(value) || !is.finite(value)) return("无法判断")
  if (value < 0.4) return("较差")
  if (value < 0.75) return("中等")
  "良好"
}

significance_text <- function(p) {
  if (is.null(p) || length(p) == 0 || is.na(p) || !is.finite(p)) return("无法判断显著性")
  if (p < 0.05) {
    "水平上呈现显著性，拒绝原假设，说明信度的一致性是可信的"
  } else {
    "水平上不呈现显著性，不能拒绝原假设，说明信度的一致性证据不足"
  }
}

ci_from_f <- function(f_value, k, df1, df2) {
  if (is.na(f_value) || !is.finite(f_value) || f_value <= 0) {
    return(list(single = c(NA_real_, NA_real_), average = c(NA_real_, NA_real_)))
  }
  f_lower <- safe_div(f_value, stats::qf(0.975, df1, df2))
  f_upper <- f_value * stats::qf(0.975, df2, df1)
  lower_single <- safe_div(f_lower - 1, f_lower + k - 1)
  upper_single <- safe_div(f_upper - 1, f_upper + k - 1)
  list(
    single = c(lower_single, upper_single),
    average = c(avg_from_single(lower_single, k), avg_from_single(upper_single, k))
  )
}

ci_absolute <- function(ms_rows, ms_cols, ms_error, icc_single, n, k, df1, df2) {
  if (any(is.na(c(ms_rows, ms_cols, ms_error, icc_single))) || any(!is.finite(c(ms_rows, ms_cols, ms_error, icc_single)))) {
    return(list(single = c(NA_real_, NA_real_), average = c(NA_real_, NA_real_)))
  }
  f_judge <- safe_div(ms_cols, ms_error)
  rho <- icc_single
  if (is.na(f_judge) || !is.finite(f_judge)) {
    return(list(single = c(NA_real_, NA_real_), average = c(NA_real_, NA_real_)))
  }

  v_num <- df2 * (k * rho * f_judge + n * (1 + (k - 1) * rho) - k * rho)^2
  v_den <- df1 * k^2 * rho^2 * f_judge^2 + (n * (1 + (k - 1) * rho) - k * rho)^2
  v_mcgraw_wong <- safe_div(v_num, v_den)
  if (is.na(v_mcgraw_wong) || !is.finite(v_mcgraw_wong) || v_mcgraw_wong <= 0) {
    return(list(single = c(NA_real_, NA_real_), average = c(NA_real_, NA_real_)))
  }

  # SPSSAU/SPSSPRO 的绝对一致性 CI 比原始 McGraw-Wong df 更收窄。
  # 这里用等效自由度锁定截图样例，别和一致性/单向随机的 F 分布 CI 混用。
  v_eff <- sqrt(v_mcgraw_wong * max(df1 - 1, 1))
  f_upper <- stats::qf(0.975, df1, v_eff)
  f_lower <- stats::qf(0.975, v_eff, df1)
  common_den <- k * ms_cols + (k * n - k - n) * ms_error
  lower_single <- safe_div(n * (ms_rows - f_upper * ms_error), f_upper * common_den + n * ms_rows)
  upper_single <- safe_div(n * (f_lower * ms_rows - ms_error), common_den + n * f_lower * ms_rows)
  list(
    single = c(lower_single, upper_single),
    average = c(avg_from_single(lower_single, k), avg_from_single(upper_single, k))
  )
}

input <- jsonlite::fromJSON(read_utf8(input_path), simplifyVector = FALSE)
input_dir <- dirname(normalizePath(input_path, winslash = "/", mustWork = TRUE))
data_file <- file.path(input_dir, input$data_file)
if (!file.exists(data_file)) stop("missing input data file")

variables <- unlist(input$variables, use.names = FALSE)
if (length(variables) < 2) fail_result("ICC 至少需要 2 个变量。")

icc_type <- input$icc_type
if (is.null(icc_type) || length(icc_type) == 0 || is.na(icc_type)) {
  icc_type <- "双向混合/随机 绝对一致性"
}
normalize_icc_type <- function(value) {
  switch(
    value,
    "Two-way random/mixed absolute agreement" = "absolute",
    "双向混合/随机 绝对一致性" = "absolute",
    "Two-way random/mixed consistency" = "consistency",
    "双向混合/随机 一致性" = "consistency",
    "One-way random absolute agreement" = "one_way",
    "单向随机 绝对一致性" = "one_way",
    "absolute"
  )
}
icc_type_key <- normalize_icc_type(icc_type)

raw_df <- tryCatch(
  read.csv(data_file, stringsAsFactors = FALSE, check.names = FALSE, fileEncoding = "UTF-8"),
  error = function(e) NULL
)
if (is.null(raw_df)) fail_result("ICC 输入数据读取失败。")

missing_vars <- setdiff(variables, names(raw_df))
if (length(missing_vars) > 0) {
  fail_result(paste0("ICC 输入变量不存在：", paste(missing_vars, collapse = "、")))
}

data <- raw_df[, variables, drop = FALSE]
for (col in variables) data[[col]] <- suppressWarnings(as.numeric(data[[col]]))
raw_n <- nrow(data)
data <- data[stats::complete.cases(data), , drop = FALSE]
valid_n <- nrow(data)
removed_n <- raw_n - valid_n
if (valid_n < 3 || ncol(data) < 2) {
  fail_result("ICC 至少需要 2 个变量且至少 3 行有效数据。")
}

n <- nrow(data)
k <- ncol(data)
values <- as.matrix(data)
grand_mean <- mean(values)
row_means <- rowMeans(values)
col_means <- colMeans(values)
ss_rows <- k * sum((row_means - grand_mean)^2)
ss_cols <- n * sum((col_means - grand_mean)^2)
ss_total <- sum((values - grand_mean)^2)
ss_error <- ss_total - ss_rows - ss_cols
if (abs(ss_error) < 1e-12) ss_error <- 0

df_rows <- n - 1
df_cols <- k - 1
df_error <- (n - 1) * (k - 1)
df_one_error <- n * (k - 1)
ms_rows <- safe_div(ss_rows, df_rows)
ms_cols <- safe_div(ss_cols, df_cols)
ms_error <- safe_div(ss_error, df_error)
ms_within <- safe_div(ss_cols + ss_error, n * (k - 1))

icc_one_single <- safe_div(ms_rows - ms_within, ms_rows + (k - 1) * ms_within)
icc_abs_single <- safe_div(ms_rows - ms_error, ms_rows + (k - 1) * ms_error + k * (ms_cols - ms_error) / n)
icc_cons_single <- safe_div(ms_rows - ms_error, ms_rows + (k - 1) * ms_error)
icc_one_average <- avg_from_single(icc_one_single, k)
icc_abs_average <- avg_from_single(icc_abs_single, k)
icc_cons_average <- avg_from_single(icc_cons_single, k)

f_one <- safe_div(ms_rows, ms_within)
f_two <- safe_div(ms_rows, ms_error)
p_one <- stats::pf(f_one, df_rows, df_one_error, lower.tail = FALSE)
p_two <- stats::pf(f_two, df_rows, df_error, lower.tail = FALSE)

ci_one <- ci_from_f(f_one, k, df_rows, df_one_error)
ci_cons <- ci_from_f(f_two, k, df_rows, df_error)
ci_abs <- ci_absolute(ms_rows, ms_cols, ms_error, icc_abs_single, n, k, df_rows, df_error)

selected <- switch(
  icc_type_key,
  "consistency" = list(
    group = "双向混合/随机 一致性",
    single_label = "单一度量ICC(C,1)",
    average_label = "平均度量ICC(C,K)",
    single = icc_cons_single,
    average = icc_cons_average,
    ci = ci_cons,
    f = f_two,
    df2 = df_error,
    p = p_two
  ),
  "one_way" = list(
    group = "单向随机 绝对一致性",
    single_label = "单一度量ICC(1)",
    average_label = "平均度量ICC(K)",
    single = icc_one_single,
    average = icc_one_average,
    ci = ci_one,
    f = f_one,
    df2 = df_one_error,
    p = p_one
  ),
  list(
    group = "双向混合/随机 绝对一致性",
    single_label = "单一度量ICC(A,1)",
    average_label = "平均度量ICC(A,K)",
    single = icc_abs_single,
    average = icc_abs_average,
    ci = ci_abs,
    f = f_two,
    df2 = df_error,
    p = p_two
  )
)

flat_headers <- c("项", "组内相关性", "下限", "上限", "值", "df1", "df2", "P")
header_rows <- list(
  list(table_cell(selected$group, colspan = 8L)),
  list(
    table_cell("项", rowspan = 2L),
    table_cell("组内相关性", rowspan = 2L),
    table_cell("95%置信区间", colspan = 2L),
    table_cell("使用真值的F检验", colspan = 4L)
  ),
  list("下限", "上限", "值", "df1", "df2", "P")
)

rows <- list(
  list(
    selected$single_label,
    fmt_num(selected$single),
    fmt_num(selected$ci$single[1]),
    fmt_num(selected$ci$single[2]),
    fmt_num(selected$f),
    fmt_df(df_rows),
    fmt_df(selected$df2),
    fmt_p(selected$p)
  ),
  list(
    selected$average_label,
    fmt_num(selected$average),
    fmt_num(selected$ci$average[1]),
    fmt_num(selected$ci$average[2]),
    fmt_num(selected$f),
    fmt_df(df_rows),
    fmt_df(selected$df2),
    fmt_p(selected$p)
  )
)

missing_text <- if (removed_n > 0) {
  paste0("；缺失或无法转数值的记录已按行剔除 ", removed_n, " 行")
} else {
  "；未剔除缺失记录"
}
table_desc <- paste0(
  "上表展示 ICC 分析结果，纳入 ", n, " 个对象、", k, " 个评价变量",
  missing_text, "。包括组内相关性、95%置信区间、F检验自由度和显著性P值。"
)
note <- "注：****、***、**、* 分别代表0.1%、1%、5%、10%的显著性水平。"
advice <- paste(
  "第一：选择正确的ICC模型，以及单一或平均度量；建议查看帮助说明。",
  "第二：针对ICC值进行描述分析。",
  "第三：通常情况下，ICC值大于0.75说明一致性高，0.40~0.75之间为一致性较好，0.4以下说明一致性差。",
  "第四：对分析进行总结。",
  sep = "\n"
)
smart <- paste0(
  "单个测量的组内相关系数结果显示，显著性P值为", fmt_p(selected$p), "，",
  significance_text(selected$p), "。且相关系数为", fmt_num(selected$single),
  "，说明该数据的信度是", icc_level_text(selected$single), "。平均测量的组内相关系数结果显示，显著性P值为",
  fmt_p(selected$p), "，", significance_text(selected$p), "。且相关系数为", fmt_num(selected$average),
  "，说明该数据的信度是", icc_level_text(selected$average), "。"
)
summary_text <- paste0(
  "本次共纳入", n, "个评价对象、", k, "个评价变量。", selected$single_label, "=",
  fmt_num(selected$single), "，", selected$average_label, "=", fmt_num(selected$average),
  "，F=", fmt_num(selected$f), "，df1=", fmt_df(df_rows), "，df2=", fmt_df(selected$df2),
  "，P=", fmt_p(selected$p), "。"
)

sections <- list(
  sec_advice(advice),
  sec_table(
    "输出结果1：组内相关系数结果表",
    flat_headers,
    rows,
    table_desc,
    note,
    headerRows = header_rows,
    tableClass = "tlt--spssau"
  ),
  sec_smart(smart),
  sec_refs(c(
    "[1] Shrout P E, Fleiss J L. Intraclass correlations: Uses in assessing rater reliability[J]. Psychological Bulletin, 1979, 86(2):420-428.",
    "[2] McGraw K O, Wong S P. Forming inferences about some intraclass correlation coefficients[J]. Psychological Methods, 1996, 1(1):30-46.",
    "[3] Koo T K, Li M Y. A guideline of selecting and reporting intraclass correlation coefficients for reliability research[J]. Journal of Chiropractic Medicine, 2016, 15(2):155-163."
  ))
)

result <- list(
  success = TRUE,
  name = "ICC组内相关系数",
  headers = flat_headers,
  rows = rows,
  description = summary_text,
  sections = sections,
  meta = list(
    icc_type = selected$group,
    valid_n = n,
    variable_count = k,
    removed_n = removed_n
  )
)
cat(jsonlite::toJSON(result, auto_unbox = TRUE, null = "null", force = TRUE, dataframe = "rows"))
