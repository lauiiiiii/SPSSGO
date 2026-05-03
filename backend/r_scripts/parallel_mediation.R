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
  cat(jsonlite::toJSON(list(success = FALSE, error = "缺少 R 包 lavaan，平行中介效应无法执行。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

input <- jsonlite::fromJSON(read_utf8(input_path), simplifyVector = FALSE)
input_dir <- dirname(normalizePath(input_path, winslash = "/", mustWork = TRUE))
data_file <- file.path(input_dir, input$data_file)
if (!file.exists(data_file)) stop("missing input data file")

x <- input$x
y <- input$y
mediators <- unlist(input$mediators)
raw_df <- read.csv(data_file, stringsAsFactors = FALSE, check.names = FALSE)
variables <- unique(c(x, y, mediators))
data <- raw_df[, variables, drop = FALSE]
for (col in variables) data[[col]] <- suppressWarnings(as.numeric(data[[col]]))
data <- stats::na.omit(data)
if (nrow(data) < 10) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "平行中介有效样本不足。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

model_lines <- c()
for (i in seq_along(mediators)) {
  model_lines <- c(model_lines, paste0(mediators[i], " ~ a", i, "*", x))
}
b_terms <- paste(paste0("b", seq_along(mediators), "*", mediators), collapse = " + ")
model_lines <- c(model_lines, paste0(y, " ~ cprime*", x, " + ", b_terms))
ind_names <- c()
for (i in seq_along(mediators)) {
  ind_name <- paste0("ind", i)
  ind_names <- c(ind_names, ind_name)
  model_lines <- c(model_lines, paste0(ind_name, " := a", i, "*b", i))
}
model_lines <- c(model_lines, paste0("total_indirect := ", paste(ind_names, collapse = " + ")))
model_lines <- c(model_lines, "total := cprime + total_indirect")
model_desc <- paste(model_lines, collapse = "\n")

fit <- tryCatch(lavaan::sem(model_desc, data = data, se = "bootstrap", bootstrap = 2000, fixed.x = FALSE), error = function(e) e)
if (inherits(fit, "error")) {
  cat(jsonlite::toJSON(list(success = FALSE, error = paste0("平行中介模型拟合失败：", fit$message)), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

pe <- lavaan::parameterEstimates(fit, standardized = TRUE, ci = TRUE, boot.ci.type = "perc")
path_df <- pe[pe$op == "~", ]
effect_df <- pe[pe$op == ":=", ]

path_rows <- list()
for (i in seq_len(nrow(path_df))) {
  row <- path_df[i, ]
  path_rows[[length(path_rows) + 1]] <- list(paste0(row$rhs, "→", row$lhs), fmt_num(row$est, 4), fmt_num(row$std.all, 4), fmt_num(row$se, 4), fmt_num(row$z, 4), fmt_num(row$pvalue, 4))
}

effect_rows <- list()
for (i in seq_len(nrow(effect_df))) {
  row <- effect_df[i, ]
  label <- row$lhs
  if (grepl("^ind[0-9]+$", label)) {
    idx <- as.integer(sub("^ind", "", label))
    if (!is.na(idx) && idx <= length(mediators)) label <- paste0(x, "→", mediators[idx], "→", y)
  }
  sig <- ifelse(!is.na(row$ci.lower) && !is.na(row$ci.upper) && row$ci.lower * row$ci.upper > 0, "显著", "不显著")
  effect_rows[[length(effect_rows) + 1]] <- list(label, fmt_num(row$est, 4), fmt_num(row$ci.lower, 4), fmt_num(row$ci.upper, 4), sig)
}

total_indirect <- effect_df$est[effect_df$lhs == "total_indirect"]
lower <- effect_df$ci.lower[effect_df$lhs == "total_indirect"]
upper <- effect_df$ci.upper[effect_df$lhs == "total_indirect"]
smart <- paste0("平行中介效应使用 lavaan Bootstrap 完成，共纳入 ", nrow(data), " 条有效样本。总间接效应=", fmt_num(total_indirect, 4), "，Bootstrap 95%CI=[", fmt_num(lower, 4), ", ", fmt_num(upper, 4), "]。")

sections <- list(
  sec_table("平行中介路径系数", c("路径", "B", "标准化β", "Std. Err", "z", "p"), path_rows),
  sec_table("Bootstrap 特定间接效应", c("效应", "估计值", "Bootstrap 下限", "Bootstrap 上限", "结论"), effect_rows, "该表对应 PROCESS 并行中介中的 specific indirect effects 输出。"),
  sec_advice("平行中介建议优先依据各特定间接效应的 Bootstrap 区间判断对应中介路径是否成立。"),
  sec_smart(smart),
  sec_refs(c("[1] Hayes, A. F. Introduction to Mediation, Moderation, and Conditional Process Analysis.", "[2] Rosseel, Y. lavaan: An R Package for Structural Equation Modeling."))
)

result <- list(success = TRUE, name = "平行中介效应", headers = c("路径", "B", "标准化β", "Std. Err", "z", "p"), rows = path_rows, description = smart, sections = sections)
cat(jsonlite::toJSON(result, auto_unbox = TRUE, null = "null", force = TRUE, dataframe = "rows"))
