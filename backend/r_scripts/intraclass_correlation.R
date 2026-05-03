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
sec_table <- function(title, headers, rows, description = NULL) {
  item <- list(type = "table", title = title, headers = headers, rows = rows)
  if (!is.null(description)) item$description <- description
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
if (nrow(data) < 3 || ncol(data) < 2) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "ICC 有效样本不足。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
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
ms_rows <- ss_rows / (n - 1)
ms_cols <- ss_cols / (k - 1)
ms_error <- ss_error / ((n - 1) * (k - 1))
ms_within <- (ss_cols + ss_error) / (n * (k - 1))

icc1 <- (ms_rows - ms_within) / (ms_rows + (k - 1) * ms_within)
icc2 <- (ms_rows - ms_error) / (ms_rows + (k - 1) * ms_error + k * (ms_cols - ms_error) / n)
icc3 <- (ms_rows - ms_error) / (ms_rows + (k - 1) * ms_error)
icc1k <- (ms_rows - ms_within) / ms_rows
icc2k <- (ms_rows - ms_error) / (ms_rows + (ms_cols - ms_error) / n)
icc3k <- (ms_rows - ms_error) / ms_rows
f_value <- ms_rows / ms_error
p_value <- stats::pf(f_value, n - 1, (n - 1) * (k - 1), lower.tail = FALSE)

rows <- list(
  list("ICC(1,1)", "单向随机/单个测量", fmt_num(icc1, 4), fmt_num(f_value, 4), fmt_num(p_value, 4)),
  list("ICC(2,1)", "双向随机/绝对一致/单个测量", fmt_num(icc2, 4), fmt_num(f_value, 4), fmt_num(p_value, 4)),
  list("ICC(3,1)", "双向混合/一致性/单个测量", fmt_num(icc3, 4), fmt_num(f_value, 4), fmt_num(p_value, 4)),
  list("ICC(1,k)", "单向随机/平均测量", fmt_num(icc1k, 4), fmt_num(f_value, 4), fmt_num(p_value, 4)),
  list("ICC(2,k)", "双向随机/绝对一致/平均测量", fmt_num(icc2k, 4), fmt_num(f_value, 4), fmt_num(p_value, 4)),
  list("ICC(3,k)", "双向混合/一致性/平均测量", fmt_num(icc3k, 4), fmt_num(f_value, 4), fmt_num(p_value, 4))
)
anova_rows <- list(
  list("被评对象", fmt_num(ss_rows, 4), as.character(n - 1), fmt_num(ms_rows, 4)),
  list("评价者/测量", fmt_num(ss_cols, 4), as.character(k - 1), fmt_num(ms_cols, 4)),
  list("误差", fmt_num(ss_error, 4), as.character((n - 1) * (k - 1)), fmt_num(ms_error, 4))
)
smart <- paste0("组内相关系数使用 R 完成，共纳入 ", n, " 个对象、", k, " 个评价变量。ICC(2,1)=", fmt_num(icc2, 4), "，ICC(3,1)=", fmt_num(icc3, 4), "。")

sections <- list(
  sec_table("ICC 多口径结果", c("指标", "口径", "ICC", "F", "p"), rows, "ICC(2,1)更适合多个评价者随机抽样且关注绝对一致的场景；ICC(3,1)更适合固定评价者且关注一致性。"),
  sec_table("方差分解", c("来源", "SS", "df", "MS"), anova_rows),
  sec_advice("选择 ICC 口径前先确认评价者是否固定、是否关注绝对一致、以及最终使用单个测量还是平均测量。"),
  sec_smart(smart),
  sec_refs(c("[1] Shrout, P. E., & Fleiss, J. L. Intraclass correlations: Uses in assessing rater reliability.", "[2] McGraw, K. O., & Wong, S. P. Forming inferences about some intraclass correlation coefficients."))
)

result <- list(success = TRUE, name = "组内相关系数", headers = c("指标", "口径", "ICC", "F", "p"), rows = rows, description = smart, sections = sections)
cat(jsonlite::toJSON(result, auto_unbox = TRUE, null = "null", force = TRUE, dataframe = "rows"))
