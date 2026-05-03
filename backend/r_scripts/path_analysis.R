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
  cat(jsonlite::toJSON(list(success = FALSE, error = "缺少 R 包 lavaan，路径分析无法执行。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

input <- jsonlite::fromJSON(read_utf8(input_path), simplifyVector = FALSE)
input_dir <- dirname(normalizePath(input_path, winslash = "/", mustWork = TRUE))
data_file <- file.path(input_dir, input$data_file)
if (!file.exists(data_file)) stop("missing input data file")

raw_df <- read.csv(data_file, stringsAsFactors = FALSE, check.names = FALSE)
dependent <- input$dependent
predictors <- unlist(input$predictors)
variables <- unique(c(dependent, predictors))
missing <- variables[!(variables %in% names(raw_df))]
if (length(missing) > 0) {
  cat(jsonlite::toJSON(list(success = FALSE, error = paste0("以下变量不存在：", paste(missing, collapse = "、"), "。")), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

data <- raw_df[, variables, drop = FALSE]
for (col in variables) data[[col]] <- suppressWarnings(as.numeric(data[[col]]))
data <- stats::na.omit(data)
if (nrow(data) < 10) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "路径分析有效样本不足。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

model_desc <- paste0(dependent, " ~ ", paste(predictors, collapse = " + "))
fit <- tryCatch(lavaan::sem(model_desc, data = data, fixed.x = FALSE, missing = "listwise"), error = function(e) e)
if (inherits(fit, "error")) {
  cat(jsonlite::toJSON(list(success = FALSE, error = paste0("路径模型拟合失败：", fit$message)), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

param_est <- lavaan::parameterEstimates(fit, standardized = TRUE, ci = TRUE)
path_df <- param_est[param_est$op == "~" & param_est$lhs == dependent, ]

path_rows <- list()
for (i in seq_len(nrow(path_df))) {
  row <- path_df[i, ]
  path_rows[[length(path_rows) + 1]] <- list(
    as.character(row$rhs),
    fmt_num(row$est, 4),
    fmt_num(row$std.all, 4),
    fmt_num(row$se, 4),
    fmt_num(row$z, 4),
    fmt_num(row$pvalue, 4),
    fmt_num(row$ci.lower, 4),
    fmt_num(row$ci.upper, 4)
  )
}

fit_names <- c("chisq", "df", "pvalue", "cfi", "tli", "rmsea", "srmr", "aic", "bic")
fit_measure <- lavaan::fitMeasures(fit, fit_names)
r2_vals <- tryCatch(lavaan::inspect(fit, "r2"), error = function(e) NULL)
r2 <- if (!is.null(r2_vals) && dependent %in% names(r2_vals)) r2_vals[[dependent]] else NA
fit_rows <- list(
  list("有效样本量", as.character(nrow(data))),
  list("因变量", dependent),
  list("路径变量数", as.character(length(predictors))),
  list("R²", fmt_num(r2, 4)),
  list("Chi-square", fmt_num(unname(fit_measure["chisq"]), 4)),
  list("df", fmt_num(unname(fit_measure["df"]), 0)),
  list("p", fmt_num(unname(fit_measure["pvalue"]), 4)),
  list("CFI", fmt_num(unname(fit_measure["cfi"]), 4)),
  list("TLI", fmt_num(unname(fit_measure["tli"]), 4)),
  list("RMSEA", fmt_num(unname(fit_measure["rmsea"]), 4)),
  list("SRMR", fmt_num(unname(fit_measure["srmr"]), 4)),
  list("AIC", fmt_num(unname(fit_measure["aic"]), 4)),
  list("BIC", fmt_num(unname(fit_measure["bic"]), 4))
)

strongest <- ""
if (nrow(path_df) > 0) {
  idx <- which.max(abs(path_df$std.all))
  strongest <- paste0("，标准化路径最强的是 ", path_df$rhs[idx], "→", dependent, "（β=", fmt_num(path_df$std.all[idx], 3), "）")
}
smart <- paste0("路径分析使用 lavaan 完成，共纳入 ", nrow(data), " 条有效样本", strongest, "。")

sections <- list(
  sec_table("路径系数表", c("路径变量", "B", "标准化β", "Std. Err", "z", "p", "95% CI 下限", "95% CI 上限"), path_rows, "当前结果由 R/lavaan 估计，标准化路径更适合跨变量比较。"),
  sec_table("模型拟合概况", c("指标", "值"), fit_rows),
  sec_advice("路径分析适合检验多个观测变量对终点变量的直接影响。若需要潜变量测量模型和结构路径一起估计，应使用 SEM。"),
  sec_smart(smart),
  sec_refs(c("[1] Rosseel, Y. lavaan: An R Package for Structural Equation Modeling. Journal of Statistical Software, 2012."))
)

result <- list(
  success = TRUE,
  name = "路径分析",
  headers = c("路径变量", "B", "标准化β", "Std. Err", "z", "p", "95% CI 下限", "95% CI 上限"),
  rows = path_rows,
  description = smart,
  sections = sections
)
cat(jsonlite::toJSON(result, auto_unbox = TRUE, null = "null", force = TRUE, dataframe = "rows"))
