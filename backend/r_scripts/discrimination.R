# 区分度分析 R 脚本：检验题项是否能够有效区分高水平与低水平样本。
# 支持分位数选择（25/27/30），输出三组对比（低分组/中间组/高分组）。
# 包含分析步骤（正态性检验、方差齐性检验）、逐题项智能分析、三组均值折线图。
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
fmt_num <- function(x, digits = 3) {
  if (is.null(x) || length(x) == 0 || is.na(x) || is.infinite(x)) return("\u2014")
  if (abs(x - round(x)) < 1e-12) return(as.character(as.integer(round(x))))
  sprintf(paste0("%.", digits, "f"), x)
}
fmt_p <- function(p) {
  if (is.null(p) || is.na(p)) return("\u2014")
  if (p < 0.001) return("<0.001***")
  if (p < 0.01) return(paste0(fmt_num(p, 3), "**"))
  if (p < 0.05) return(paste0(fmt_num(p, 3), "*"))
  return(fmt_num(p, 3))
}
sec_table <- function(title, headers, rows, description = NULL, note = NULL) {
  item <- list(type = "table", title = title, headers = headers, rows = rows)
  if (!is.null(description)) item$description <- description
  if (!is.null(note)) item$note <- note
  item
}
sec_chart <- function(chart) list(type = "chart", chart = chart)
sec_smart <- function(content) list(type = "smart_analysis", title = "智能分析", content = content)
sec_advice <- function(content, title = "分析建议") list(type = "advice", title = title, content = content)
sec_refs <- function(items) list(type = "references", title = "参考文献", items = items)

input <- jsonlite::fromJSON(read_utf8(input_path), simplifyVector = FALSE)
input_dir <- dirname(normalizePath(input_path, winslash = "/", mustWork = TRUE))
data_file <- file.path(input_dir, input$data_file)
if (!file.exists(data_file)) stop("missing input data file")

variables <- unlist(input$variables)
percentile <- if (!is.null(input$percentile)) as.integer(input$percentile) else 27L
if (!(percentile %in% c(25L, 27L, 30L))) percentile <- 27L

raw_df <- read.csv(data_file, stringsAsFactors = FALSE, check.names = FALSE)
data <- raw_df[, variables, drop = FALSE]
for (col in variables) data[[col]] <- suppressWarnings(as.numeric(data[[col]]))
data <- stats::na.omit(data)
if (nrow(data) < 10) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "有效样本不足，至少建议保留 10 个完整样本。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

total_score <- rowSums(data)
group_size <- max(floor(nrow(data) * percentile / 100), 1)
sorted_idx <- order(total_score)
low_group <- data[sorted_idx[seq_len(group_size)], , drop = FALSE]
high_group <- data[sorted_idx[(nrow(data) - group_size + 1):nrow(data)], , drop = FALSE]
mid_start <- group_size + 1
mid_end <- nrow(data) - group_size
mid_group <- if (mid_end >= mid_start) data[sorted_idx[mid_start:mid_end], , drop = FALSE] else NULL

# ===== 分析步骤：正态性检验 + 方差齐性检验 =====
step_rows <- list()
step_normal <- TRUE
step_levene <- TRUE

# 正态性检验（Shapiro-Wilk，样本量>5000 时跳过）
if (nrow(data) <= 5000) {
  sw_result <- tryCatch(stats::shapiro.test(total_score), error = function(e) NULL)
  if (!is.null(sw_result)) {
    step_normal <- sw_result$p.value >= 0.05
    step_rows[[length(step_rows) + 1]] <- list("正态性检验", "Shapiro-Wilk", fmt_num(sw_result$statistic, 3), fmt_p(sw_result$p.value), ifelse(step_normal, "符合", "不符合"))
  }
} else {
  step_rows[[length(step_rows) + 1]] <- list("正态性检验", "\u2014", "\u2014", "\u2014", "样本量过大，跳过")
}

# 方差齐性检验（Levene 检验，使用 car 包或手动实现）
levene_result <- tryCatch({
  group_factor <- rep("middle", nrow(data))
  group_factor[sorted_idx[seq_len(group_size)]] <- "low"
  group_factor[sorted_idx[(nrow(data) - group_size + 1):nrow(data)]] <- "high"
  group_factor <- factor(group_factor, levels = c("low", "middle", "high"))
  abs_dev <- abs(total_score - stats::median(total_score))
  levene_model <- stats::aov(abs_dev ~ group_factor)
  summary(levene_model)[[1]]
}, error = function(e) NULL)

if (!is.null(levene_result) && nrow(levene_result) >= 1) {
  f_val <- levene_result[1, "F value"]
  p_val <- levene_result[1, "Pr(>F)"]
  step_levene <- p_val >= 0.05
  step_rows[[length(step_rows) + 1]] <- list("方差齐性检验", "Levene", fmt_num(f_val, 3), fmt_p(p_val), ifelse(step_levene, "符合", "不符合"))
}

step_description <- paste0(
  "1. 首先验证正态性分布，通常需满足符合正态性分布。\n",
  "2. 通过 t 检验判断高低组是否呈现出显著性(p<0.05)，若呈现显著，根据均值与标准差值进行差异分析，描述差异大小。如果高低组呈现显著则量表设计合适，反之则说明量表项无法区分出信息，设计不合理应该进行删除处理。\n",
  "3. 对分析进行总结。"
)

# ===== 区分度结果表 =====
rows <- list()
weak_items <- c()
strong_items <- c()
item_analyses <- c()

for (variable in variables) {
  corrected_total <- total_score - data[[variable]]
  corr <- suppressWarnings(stats::cor(data[[variable]], corrected_total))
  test <- tryCatch(stats::t.test(high_group[[variable]], low_group[[variable]]), error = function(e) NULL)

  mean_low <- mean(low_group[[variable]])
  sd_low <- stats::sd(low_group[[variable]])
  mean_mid <- if (!is.null(mid_group)) mean(mid_group[[variable]]) else NA
  sd_mid <- if (!is.null(mid_group)) stats::sd(mid_group[[variable]]) else NA
  mean_high <- mean(high_group[[variable]])
  sd_high <- stats::sd(high_group[[variable]])

  t_value <- if (!is.null(test)) unname(test$statistic) else NA
  p_value <- if (!is.null(test)) test$p.value else NA

  suggestion <- "保留"
  if (is.na(corr) || corr < 0.3 || is.na(p_value) || p_value >= 0.05) {
    suggestion <- "优先复核"
    weak_items <- c(weak_items, variable)
  } else {
    strong_items <- c(strong_items, variable)
  }

  rows[[length(rows) + 1]] <- list(
    variable,
    paste0(fmt_num(mean_low, 2), "\u00B1", fmt_num(sd_low, 2)),
    if (!is.na(mean_mid)) paste0(fmt_num(mean_mid, 2), "\u00B1", fmt_num(sd_mid, 2)) else "\u2014",
    paste0(fmt_num(mean_high, 2), "\u00B1", fmt_num(sd_high, 2)),
    fmt_num(t_value, 3),
    fmt_p(p_value),
    fmt_num(corr, 3),
    suggestion
  )

  # 逐题项智能分析
  sig_text <- if (!is.na(p_value) && p_value < 0.05) "显著" else "不显著"
  corr_text <- if (!is.na(corr) && corr >= 0.3) "良好" else "较弱"
  diff_dir <- if (!is.na(t_value) && t_value > 0) "高分组均值高于低分组" else "低分组均值高于高分组"
  item_analyses <- c(item_analyses, paste0(
    "对于变量", variable, "，显著性 p 值为", fmt_p(p_value), "，水平上呈现", sig_text, "性，",
    diff_dir, "，说明量表项设计区分度", ifelse(!is.na(p_value) && p_value < 0.05, "较好", "较差"), "，",
    "校正题总相关为", fmt_num(corr, 3), "，相关性", corr_text, "，设计较为", ifelse(!is.na(corr) && corr >= 0.3 && !is.na(p_value) && p_value < 0.05, "合理", "不合理")
  ))
}

# ===== 分组说明表 =====
group_rows <- list(
  list("有效样本量", as.character(nrow(data))),
  list("高分组样本", as.character(nrow(high_group))),
  list("中间组样本", if (!is.null(mid_group)) as.character(nrow(mid_group)) else "\u2014"),
  list("低分组样本", as.character(nrow(low_group))),
  list("分组比例", paste0("前后 ", percentile, "%"))
)

# ===== 结果描述（论文级别文字） =====
var_list_str <- paste(variables, collapse = "、")
n_vars <- length(variables)

# 显著性汇总
sig_items <- c()
ns_items <- c()
corr_good_items <- c()
corr_weak_items <- c()
for (variable in variables) {
  corrected_total <- total_score - data[[variable]]
  corr <- suppressWarnings(stats::cor(data[[variable]], corrected_total))
  test <- tryCatch(stats::t.test(high_group[[variable]], low_group[[variable]]), error = function(e) NULL)
  p_val <- if (!is.null(test)) test$p.value else NA
  if (!is.na(p_val) && p_val < 0.05) {
    sig_items <- c(sig_items, variable)
  } else {
    ns_items <- c(ns_items, variable)
  }
  if (!is.na(corr) && corr >= 0.3) {
    corr_good_items <- c(corr_good_items, variable)
  } else {
    corr_weak_items <- c(corr_weak_items, variable)
  }
}

sig_summary <- if (length(sig_items) == n_vars) {
  paste0(var_list_str, "共", n_vars, "项均呈现出显著性（p<0.05），意味着总共", n_vars, "项均具有良好的区分性，应予以保留")
} else if (length(sig_items) > 0) {
  paste0(paste(sig_items, collapse = "、"), "共", length(sig_items), "项呈现出显著性（p<0.05），具有良好的区分性，应予以保留；", paste(ns_items, collapse = "、"), "共", length(ns_items), "项未呈现出显著性（p>=0.05），区分性较差，建议修改或删除")
} else {
  paste0(var_list_str, "共", n_vars, "项均未呈现出显著性（p>=0.05），区分性较差，建议对量表进行修改或删除")
}

corr_summary <- if (length(corr_good_items) == n_vars) {
  paste0(var_list_str, "共", n_vars, "项的校正题总相关均大于 0.30，意味着总共", n_vars, "项均具有良好的区分性，应予以保留")
} else if (length(corr_good_items) > 0) {
  paste0(paste(corr_good_items, collapse = "、"), "共", length(corr_good_items), "项的校正题总相关大于 0.30，具有良好的区分性，应予以保留；", paste(corr_weak_items, collapse = "、"), "共", length(corr_weak_items), "项的校正题总相关小于 0.30，区分性较差，建议修改或删除")
} else {
  paste0(var_list_str, "共", n_vars, "项的校正题总相关均小于 0.30，区分性较差，建议对量表进行修改或删除")
}

result_text <- paste0(
  "从上表可知，针对", var_list_str, "共", n_vars, "项进行区分度分析，使用项目鉴别指数作为指标。",
  sig_summary, "。",
  corr_summary, "。"
)

# ===== 三组均值折线图 =====
chart_labels <- as.list(variables)
chart_metrics <- list(
  "低分组" = sapply(variables, function(v) mean(low_group[[v]])),
  "中间组" = sapply(variables, function(v) if (!is.null(mid_group)) mean(mid_group[[v]]) else NA),
  "高分组" = sapply(variables, function(v) mean(high_group[[v]]))
)
group_chart <- list(
  chartType = "metric_comparison",
  title = "各分组均值对比图",
  data = list(
    metric = "题项均值",
    labels = chart_labels,
    values = chart_metrics[["高分组"]],
    metrics = chart_metrics,
    multiSeries = TRUE,
    defaultMode = "line",
    displayTitle = "各分组均值对比图"
  )
)

# ===== 汇总智能分析 =====
if (length(weak_items) == 0) {
  smart <- paste0(
    "题项区分度检验结果表明，", length(strong_items), "个题项均达到良好标准，",
    "具有较强的鉴别能力，能够有效反映受测对象之间的差异，量表题项质量整体较好。"
  )
} else if (length(strong_items) > 0) {
  smart <- paste0(
    "题项区分度检验结果表明，", length(strong_items), "个题项达到良好标准，",
    "但", paste(weak_items, collapse = "、"), "共", length(weak_items), "项区分度较弱，",
    "建议对区分度较弱的题项进行修改或删除，以提升量表整体质量。"
  )
} else {
  smart <- paste0(
    "题项区分度检验结果表明，", length(weak_items), "个题项均未达到良好标准，",
    "区分度整体较弱，建议对量表进行修改或重新设计，确保题项能有效区分受测对象之间的差异。"
  )
}

# ===== 分析建议 =====
if (length(weak_items) > 0) {
  advice <- paste0(
    "建议重点复核以下题项：", paste(weak_items, collapse = "、"),
    "。可结合题意、反向计分和量表维度进一步判断。"
  )
} else {
  advice <- "当前量表题项整体区分效果较好，可继续结合信度和效度分析综合判断。"
}

# ===== 组装 sections =====
sections <- list(
  list(type = "text", title = "分析流程", content = step_description),
  sec_table("分析步骤", c("检验项", "方法", "统计量", "p", "结论"), step_rows),
  sec_table("区分度分析结果", c("题项", "低分组(均值\u00B1SD)", "中间组(均值\u00B1SD)", "高分组(均值\u00B1SD)", "t", "p", "校正题总相关", "建议"), rows, note = paste0("注：", percentile, "%、", 100 - percentile, "%分位数代表", percentile, "%、", 100 - percentile, "%的显著性水平")),
  list(type = "text", title = "结果描述", content = result_text),
  sec_chart(group_chart),
  sec_advice(advice),
  sec_smart(paste(smart, "\n\n", paste(item_analyses, collapse = "\n"))),
  sec_refs(c(
    "[1] Scientific Platform Serving for Statistics Professional 2021, SPSSPRO. (Version 1.0.11) [Online Application Software]. Retrieved from https://www.spsspro.com.",
    "[2] Joan, Fisher, Box, Guiness, Gosset, Fisher, and Small Samples[J]. Statistical Science, 1987."
  ))
)

result <- list(
  success = TRUE,
  name = "区分度分析",
  headers = c("题项", "低分组(均值\u00B1SD)", "中间组(均值\u00B1SD)", "高分组(均值\u00B1SD)", "t", "p", "校正题总相关", "建议"),
  rows = rows,
  description = smart,
  sections = sections
)
cat(jsonlite::toJSON(result, auto_unbox = TRUE, null = "null", force = TRUE, dataframe = "rows"))
