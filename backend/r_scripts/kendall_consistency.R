# Kendall一致性检验：行是评价者/专家，列是被评价对象，输出 Kendall's W 结果表。
# 并列分数按平均秩处理，并启用 tie correction；别改成列内排名。
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

fmt_num <- function(x, digits = 3, trim = TRUE) {
  if (is.null(x) || length(x) == 0 || is.na(x) || is.infinite(x)) {
    return("\u2014")
  }
  if (abs(x - round(x)) < 1e-12) {
    return(as.character(as.integer(round(x))))
  }
  text <- sprintf(paste0("%.", digits, "f"), x)
  if (isTRUE(trim)) {
    text <- sub("0+$", "", text)
    text <- sub("\\.$", "", text)
  }
  text
}

p_mark <- function(p) {
  if (is.null(p) || length(p) == 0 || is.na(p) || is.infinite(p)) {
    return("")
  }
  if (p < 0.001) {
    "****"
  } else if (p < 0.01) {
    "***"
  } else if (p < 0.05) {
    "**"
  } else if (p < 0.1) {
    "*"
  } else {
    ""
  }
}

fmt_p <- function(p) {
  if (is.null(p) || length(p) == 0 || is.na(p) || is.infinite(p)) {
    return("\u2014")
  }
  paste0(sprintf("%.3f", p), p_mark(p))
}

sec_table <- function(title, headers, rows, note = NULL, description = NULL) {
  item <- list(type = "table", title = title, headers = headers, rows = rows)
  if (!is.null(note)) item$note <- note
  if (!is.null(description)) item$description <- description
  item
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

strength_text <- function(w) {
  if (is.null(w) || length(w) == 0 || is.na(w) || is.infinite(w)) {
    return("无法判断")
  }
  if (w < 0.2) {
    "极低的一致性"
  } else if (w < 0.4) {
    "较低的一致性"
  } else if (w < 0.6) {
    "一般的一致性"
  } else if (w < 0.8) {
    "较高的一致性"
  } else {
    "极高的一致性"
  }
}

output_error <- function(message) {
  cat(jsonlite::toJSON(
    list(success = FALSE, error = message),
    auto_unbox = TRUE,
    force = TRUE
  ))
}

input <- jsonlite::fromJSON(read_utf8(input_path), simplifyVector = FALSE)
input_dir <- dirname(normalizePath(input_path, winslash = "/", mustWork = TRUE))
data_file <- file.path(input_dir, input$data_file)
if (!file.exists(data_file)) {
  stop("missing input data file")
}

variables <- unlist(input$variables)
if (is.null(variables) || length(variables) < 2) {
  output_error("Kendall一致性检验至少需要 2 个评价对象变量。")
  quit(status = 0)
}

raw_df <- read.csv(
  data_file,
  stringsAsFactors = FALSE,
  check.names = FALSE,
  fileEncoding = "UTF-8"
)
missing_vars <- setdiff(variables, names(raw_df))
if (length(missing_vars) > 0) {
  output_error("评价对象变量不存在。")
  quit(status = 0)
}

data <- raw_df[, variables, drop = FALSE]
for (col in variables) {
  data[[col]] <- suppressWarnings(as.numeric(data[[col]]))
}
data <- stats::na.omit(data)
if (nrow(data) < 2) {
  output_error("有效样本不足，至少需要 2 行完整评价者数据。")
  quit(status = 0)
}
if (ncol(data) < 2) {
  output_error("Kendall一致性检验至少需要 2 个评价对象变量。")
  quit(status = 0)
}

values <- as.matrix(data)
rank_matrix <- t(apply(values, 1, rank, ties.method = "average"))
if (is.null(dim(rank_matrix))) {
  rank_matrix <- matrix(rank_matrix, nrow = nrow(values), byrow = TRUE)
}

n_raters <- nrow(values)
n_objects <- ncol(values)
rank_sums <- colSums(rank_matrix)
s_value <- sum((rank_sums - mean(rank_sums)) ^ 2)

tie_total <- 0
for (i in seq_len(n_raters)) {
  counts <- as.numeric(table(values[i, ]))
  tie_total <- tie_total + sum(counts ^ 3 - counts)
}

denominator <- n_raters ^ 2 * (n_objects ^ 3 - n_objects) - n_raters * tie_total
if (!is.finite(denominator) || denominator <= 0) {
  output_error("所有评价对象在评价者内部均为并列分数，无法计算 Kendall协调系数。")
  quit(status = 0)
}

w_value <- 12 * s_value / denominator
chi_square <- n_raters * (n_objects - 1) * w_value
df_value <- n_objects - 1
p_value <- stats::pchisq(chi_square, df = df_value, lower.tail = FALSE)

rank_means <- colMeans(rank_matrix)
medians <- vapply(data, stats::median, numeric(1), na.rm = TRUE)
w_text <- fmt_num(w_value, 3, trim = FALSE)
chi_text <- fmt_num(chi_square, 3, trim = FALSE)
p_text <- fmt_p(p_value)

rows <- list()
for (j in seq_along(variables)) {
  base_row <- list(
    variables[[j]],
    fmt_num(rank_means[[j]], 3),
    fmt_num(medians[[j]], 3)
  )
  if (j == 1) {
    base_row <- c(
      base_row,
      list(
        list(text = w_text, rowspan = n_objects),
        list(text = chi_text, rowspan = n_objects),
        list(text = p_text, rowspan = n_objects)
      )
    )
  }
  rows[[length(rows) + 1]] <- base_row
}

headers <- c("名称", "秩平均值", "中位数", "Kendall's W系数", "\u03c7\u00b2", "P")
sig <- is.finite(p_value) && p_value < 0.05
sig_text <- if (sig) "呈现显著性" else "不呈现显著性"
reject_text <- if (sig) "拒绝" else "不能拒绝"
consistent_text <- if (sig) "呈现一致性" else "不能呈现一致性"

smart <- paste0(
  "Kendall系数一致性检验的结果显示，总体数据的显著性P值为",
  p_text,
  "，水平上",
  sig_text,
  "，",
  reject_text,
  "原假设，因此数据",
  consistent_text,
  "，同时模型的Kendall协调系数W值为",
  w_text,
  "，因此相关性的程度为",
  strength_text(w_value),
  "。"
)

analysis_steps <- paste(
  "1. 将每一行视为一位评价者或专家，对其给出的多个评价对象分数做行内排名。",
  "2. 并列分数使用平均秩，并在 Kendall's W 分母中做并列修正。",
  "3. 汇总各评价对象的秩和，计算 Kendall's W、\u03c7\u00b2 和显著性P值。",
  "4. 先看P值是否显著，再结合 Kendall's W 判断整体一致性强弱。",
  sep = "\n"
)

detail_text <- paste0(
  "本次共纳入",
  n_raters,
  "位评价者、",
  n_objects,
  "个评价对象。Kendall's W=",
  w_text,
  "，\u03c7\u00b2=",
  chi_text,
  "，df=",
  df_value,
  "，P=",
  p_text,
  "；结果",
  sig_text,
  "，",
  reject_text,
  "原假设，说明评价结果",
  consistent_text,
  "。"
)

config_rows <- list(
  list("算法", "Kendall一致性检验（Kendall's W）"),
  list("统计口径", "行内平均秩 + 并列秩修正"),
  list("评价对象变量", paste(variables, collapse = "、")),
  list("评价者数量", as.character(n_raters)),
  list("评价对象数量", as.character(n_objects)),
  list(
    "并列秩修正",
    if (tie_total > 0) {
      paste0("已启用（T=", fmt_num(tie_total, 0), "）")
    } else {
      "未触发"
    }
  ),
  list("缺失值处理", "任一评价对象变量缺失或无法转为数值时剔除整行评价者数据")
)

result_section <- sec_table(
  "输出结果1：Kendall's W分析结果",
  headers,
  rows,
  note = "注：****、***、**、* 分别代表0.1%、1%、5%、10%的显著性水平。",
  description = "上表展示 Kendall一致性检验结果，包括秩平均值、中位数、Kendall协调系数W、卡方值和显著性P值。"
)

sections <- list(
  sec_table("分析配置", c("项目", "内容"), config_rows),
  sec_advice(analysis_steps, title = "分析步骤"),
  result_section,
  sec_advice(detail_text, title = "详细结论"),
  sec_smart(smart),
  sec_refs(c(
    "[1] 李蜀生,李江红,刘小宁,申希平,米友军. Kendall's W分析方法在医学数据处理中的应用及在SPSS中的实现方法[J].现代预防医学,2008(01):33-42.",
    "[2] Kendall M G, Smith B B. The problem of m rankings[J]. The Annals of Mathematical Statistics, 1939, 10(3):275-287."
  ))
)

result <- list(
  success = TRUE,
  name = paste0("Kendall一致性检验_", paste(head(variables, 3), collapse = "_")),
  headers = headers,
  rows = rows,
  description = smart,
  sections = sections
)
cat(jsonlite::toJSON(
  result,
  auto_unbox = TRUE,
  null = "null",
  force = TRUE,
  dataframe = "rows"
))
