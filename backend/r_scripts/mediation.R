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

if (!requireNamespace("lavaan", quietly = TRUE)) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "缺少 R 包 lavaan，中介效应分析无法执行。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

input <- jsonlite::fromJSON(read_utf8(input_path), simplifyVector = FALSE)
input_dir <- dirname(normalizePath(input_path, winslash = "/", mustWork = TRUE))
data_file <- file.path(input_dir, input$data_file)
if (!file.exists(data_file)) stop("missing input data file")

x <- input$x
m <- input$m
y <- input$y
raw_df <- read.csv(data_file, stringsAsFactors = FALSE, check.names = FALSE)
variables <- c(x, m, y)
data <- raw_df[, variables, drop = FALSE]
for (col in variables) data[[col]] <- suppressWarnings(as.numeric(data[[col]]))
data <- stats::na.omit(data)
if (nrow(data) < 10) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "中介效应分析有效样本不足。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

model_desc <- paste(
  paste0(m, " ~ a*", x),
  paste0(y, " ~ cprime*", x, " + b*", m),
  "indirect := a*b",
  "total := cprime + indirect",
  sep = "\n"
)
fit <- tryCatch(lavaan::sem(model_desc, data = data, se = "bootstrap", bootstrap = 2000, fixed.x = FALSE), error = function(e) e)
if (inherits(fit, "error")) {
  cat(jsonlite::toJSON(list(success = FALSE, error = paste0("中介模型拟合失败：", fit$message)), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

pe <- lavaan::parameterEstimates(fit, standardized = TRUE, ci = TRUE, boot.ci.type = "perc")
path_df <- pe[pe$op == "~", ]
effect_df <- pe[pe$op == ":=", ]

path_rows <- list()
for (i in seq_len(nrow(path_df))) {
  row <- path_df[i, ]
  label <- ifelse(row$lhs == m, paste0("a: ", x, "→", m), ifelse(row$rhs == m, paste0("b: ", m, "→", y), paste0("c': ", x, "→", y)))
  path_rows[[length(path_rows) + 1]] <- list(label, fmt_num(row$est, 4), fmt_num(row$std.all, 4), fmt_num(row$se, 4), fmt_num(row$z, 4), fmt_num(row$pvalue, 4))
}
effect_rows <- list()
for (i in seq_len(nrow(effect_df))) {
  row <- effect_df[i, ]
  effect_rows[[length(effect_rows) + 1]] <- list(row$lhs, fmt_num(row$est, 4), fmt_num(row$ci.lower, 4), fmt_num(row$ci.upper, 4), fmt_num(row$pvalue, 4))
}

indirect <- effect_df$est[effect_df$lhs == "indirect"]
lower <- effect_df$ci.lower[effect_df$lhs == "indirect"]
upper <- effect_df$ci.upper[effect_df$lhs == "indirect"]
sig <- ifelse(length(lower) > 0 && !is.na(lower) && !is.na(upper) && lower * upper > 0, "不包含 0", "包含 0")
smart <- paste0("中介效应分析使用 lavaan Bootstrap 完成，共纳入 ", nrow(data), " 条有效样本。间接效应 a×b=", fmt_num(indirect, 4), "，Bootstrap 95%CI=[", fmt_num(lower, 4), ", ", fmt_num(upper, 4), "]，区间", sig, "。")

sections <- list(
  sec_table("路径系数表", c("路径", "B", "标准化β", "Std. Err", "z", "p"), path_rows),
  sec_table("Bootstrap 效应分解", c("效应", "估计值", "Bootstrap 下限", "Bootstrap 上限", "p"), effect_rows, "优先依据 Bootstrap 置信区间判断间接效应是否显著。"),
  sec_advice("若间接效应 Bootstrap 区间不含 0，可认为中介路径成立；再结合直接效应 c' 判断完全中介或部分中介。"),
  sec_smart(smart),
  sec_refs(c(
    "[1] 温忠麟, 张雷, 侯杰泰, 刘红云. (2004). 中介效应检验程序及其应用. 心理学报, 36(5), 614-620.",
    "[2] 温忠麟, 叶宝娟. (2014). 中介效应分析：方法和模型发展. 心理科学进展, 22(5), 731-745.",
    "[3] Baron, R. M., & Kenny, D. A. (1986). The moderator-mediator variable distinction in social psychological research: Conceptual, strategic, and statistical considerations. Journal of Personality and Social Psychology, 51(6), 1173-1182.",
    "[4] MacKinnon, D. P. (2008). Introduction to Statistical Mediation Analysis. Routledge."
  ))
)

result <- list(success = TRUE, name = paste0("中介效应检验：", x, "→", m, "→", y), headers = c("路径", "B", "标准化β", "Std. Err", "z", "p"), rows = path_rows, description = smart, sections = sections)
cat(jsonlite::toJSON(result, auto_unbox = TRUE, null = "null", force = TRUE, dataframe = "rows"))
