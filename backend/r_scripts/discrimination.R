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
sec_table <- function(title, headers, rows, description = NULL, note = NULL) {
  item <- list(type = "table", title = title, headers = headers, rows = rows)
  if (!is.null(description)) item$description <- description
  if (!is.null(note)) item$note <- note
  item
}
sec_smart <- function(content) list(type = "smart_analysis", title = "智能分析", content = content)
sec_advice <- function(content, title = "分析建议") list(type = "advice", title = title, content = content)
sec_refs <- function(items) list(type = "references", title = "参考文献", items = items)

input <- jsonlite::fromJSON(read_utf8(input_path), simplifyVector = FALSE)
input_dir <- dirname(normalizePath(input_path, winslash = "/", mustWork = TRUE))
data_file <- file.path(input_dir, input$data_file)
if (!file.exists(data_file)) stop("missing input data file")

variables <- unlist(input$variables)
raw_df <- read.csv(data_file, stringsAsFactors = FALSE, check.names = FALSE)
data <- raw_df[, variables, drop = FALSE]
for (col in variables) data[[col]] <- suppressWarnings(as.numeric(data[[col]]))
data <- stats::na.omit(data)
if (nrow(data) < 10) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "有效样本不足，至少建议保留 10 个完整样本。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

total_score <- rowSums(data)
group_size <- max(floor(nrow(data) * 0.27), 1)
sorted_idx <- order(total_score)
low_group <- data[sorted_idx[seq_len(group_size)], , drop = FALSE]
high_group <- data[sorted_idx[(nrow(data) - group_size + 1):nrow(data)], , drop = FALSE]

rows <- list()
weak_items <- c()
strong_items <- c()
for (variable in variables) {
  corrected_total <- total_score - data[[variable]]
  corr <- suppressWarnings(stats::cor(data[[variable]], corrected_total))
  test <- tryCatch(stats::t.test(high_group[[variable]], low_group[[variable]]), error = function(e) NULL)
  mean_high <- mean(high_group[[variable]])
  mean_low <- mean(low_group[[variable]])
  diff <- mean_high - mean_low
  t_value <- if (!is.null(test)) unname(test$statistic) else NA
  p_value <- if (!is.null(test)) test$p.value else NA
  suggestion <- "保留"
  if (is.na(corr) || corr < 0.3 || is.na(p_value) || p_value >= 0.05) {
    suggestion <- "优先复核"
    weak_items <- c(weak_items, variable)
  } else {
    strong_items <- c(strong_items, variable)
  }
  rows[[length(rows) + 1]] <- list(variable, fmt_num(mean_high, 3), fmt_num(mean_low, 3), fmt_num(diff, 3), fmt_num(t_value, 3), fmt_num(p_value, 3), fmt_num(corr, 3), suggestion)
}

group_rows <- list(
  list("有效样本量", as.character(nrow(data))),
  list("高分组样本", as.character(nrow(high_group))),
  list("低分组样本", as.character(nrow(low_group))),
  list("分组比例", "前后 27%")
)
advice <- if (length(weak_items) > 0) paste0("建议优先复核以下题项：", paste(weak_items, collapse = "、"), "。可结合题意、反向计分和量表维度进一步判断。") else "当前题项整体区分效果较好，可继续结合信度和效度分析综合判断。"
smart <- paste0("区分度分析使用 R 完成，共检验 ", length(variables), " 个题项，其中区分表现较好的题项有 ", length(strong_items), " 个，", ifelse(length(weak_items) > 0, paste0("需要重点复核的题项为 ", paste(weak_items, collapse = "、")), "暂未发现明显弱区分题项"), "。")

sections <- list(
  sec_table("区分度结果", c("题项", "高分组均值", "低分组均值", "均值差", "t", "p", "校正题总相关", "建议"), rows, note = "通常校正题总相关 >= 0.30 且高低组差异显著时，题项区分效果更稳。"),
  sec_table("分组说明", c("项", "值"), group_rows),
  sec_advice(advice),
  sec_smart(smart),
  sec_refs(c("[1] DeVellis, R. F. Scale Development: Theory and Applications.", "[2] Nunnally, J. C., & Bernstein, I. H. Psychometric Theory."))
)

result <- list(success = TRUE, name = "区分度分析", headers = c("题项", "高分组均值", "低分组均值", "均值差", "t", "p", "校正题总相关", "建议"), rows = rows, description = smart, sections = sections)
cat(jsonlite::toJSON(result, auto_unbox = TRUE, null = "null", force = TRUE, dataframe = "rows"))
