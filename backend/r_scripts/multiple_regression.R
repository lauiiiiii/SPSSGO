# -*- coding: UTF-8 -*-
# 线性回归（最小二乘法）统计计算层；Python 只负责校验、打包和 R 调用。
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
if (!requireNamespace("jsonlite", quietly = TRUE)) stop("缺少 R 包 jsonlite，线性回归无法执行。")

read_utf8 <- function(path) paste(readLines(path, warn = FALSE, encoding = "UTF-8"), collapse = "\n")
emit_json <- function(value) {
  cat(jsonlite::toJSON(value, auto_unbox = TRUE, null = "null", na = "null", force = TRUE, dataframe = "rows", ascii = TRUE))
}
emit_error <- function(message) {
  emit_json(list(success = FALSE, error = message))
  quit(status = 0)
}
fmt_num <- function(x, digits = 3, inf_text = "\u2014") {
  if (is.null(x) || length(x) == 0 || is.na(x)) return("\u2014")
  x <- suppressWarnings(as.numeric(x))
  if (!is.finite(x)) return(inf_text)
  sprintf(paste0("%.", digits, "f"), x)
}
fmt_p <- function(p) {
  if (is.null(p) || length(p) == 0 || is.na(p) || !is.finite(p)) return("\u2014")
  if (p < 0.001) return("<0.001")
  fmt_num(p, 3)
}
p_compare <- function(p) {
  if (is.null(p) || length(p) == 0 || is.na(p) || !is.finite(p)) return("p=\u2014")
  if (p < 0.001) return("p<0.001")
  if (p < 0.05) return(paste0("p=", fmt_num(p, 3), "<0.05"))
  paste0("p=", fmt_num(p, 3), ">0.05")
}
sig_mark <- function(p) {
  if (is.null(p) || length(p) == 0 || is.na(p) || !is.finite(p)) return("")
  if (p < 0.001) return("***")
  if (p < 0.01) return("**")
  if (p < 0.05) return("*")
  ""
}
fmt_ci <- function(low, high) paste0("[", fmt_num(low, 3), ", ", fmt_num(high, 3), "]")
safe_number <- function(x) {
  x <- suppressWarnings(as.numeric(x))
  if (length(x) == 0 || is.na(x) || !is.finite(x)) return(NA_real_)
  x
}
number_or_zero <- function(x) {
  x <- safe_number(x)
  if (is.na(x)) 0 else x
}
sec_table <- function(title, headers, rows, description = NULL, note = NULL, headerRows = NULL, bodyRowspanColumns = NULL, tableClass = NULL) {
  item <- list(type = "table", title = title, headers = headers, rows = rows)
  if (!is.null(description)) item$description <- description
  if (!is.null(note)) item$note <- note
  if (!is.null(headerRows)) item$headerRows <- headerRows
  if (!is.null(bodyRowspanColumns)) item$bodyRowspanColumns <- bodyRowspanColumns
  if (!is.null(tableClass)) item$tableClass <- tableClass
  item
}
table_cell <- function(text, colspan = NULL, class_name = NULL) {
  cell <- list(text = as.character(text))
  if (!is.null(colspan)) cell$colspan <- colspan
  if (!is.null(class_name)) cell$class <- class_name
  cell
}
sec_charts <- function(title, charts, description = NULL) {
  item <- list(type = "charts", title = title, charts = charts)
  if (!is.null(description)) item$description <- description
  item
}
sec_advice <- function(content, title = "\u5206\u6790\u5EFA\u8BAE") list(type = "advice", title = title, content = content)
sec_smart <- function(content) list(type = "smart_analysis", title = "\u667A\u80FD\u5206\u6790", content = content)
sec_refs <- function(items) list(type = "references", title = "\u53C2\u8003\u6587\u732E", items = items)
clean_missing <- function(values) {
  text <- trimws(as.character(values))
  text[tolower(text) %in% c("", "nan", "na", "null", "none", "<na>")] <- NA
  text
}
is_categorical_type <- function(value) {
  type <- tolower(trimws(as.character(value %||% "")))
  type %in% c("categorical", "category", "nominal", "ordinal", "\u5B9A\u7C7B", "\u5206\u7C7B")
}
`%||%` <- function(a, b) if (is.null(a) || length(a) == 0) b else a

input <- jsonlite::fromJSON(read_utf8(input_path), simplifyVector = FALSE)
input_dir <- dirname(normalizePath(input_path, winslash = "/", mustWork = TRUE))
data_file <- file.path(input_dir, input$data_file)
if (!file.exists(data_file)) stop("missing input data file")

raw_df <- read.csv(data_file, stringsAsFactors = FALSE, check.names = FALSE)
dependent <- input$dependent
predictors <- unique(as.character(unlist(input$predictors %||% c())))
if (is.null(dependent) || dependent == "" || length(predictors) == 0) emit_error("\u7F3A\u5C11\u56E0\u53D8\u91CF\u6216\u81EA\u53D8\u91CF\u3002")
variables <- unique(c(dependent, predictors))
missing_vars <- setdiff(variables, names(raw_df))
if (length(missing_vars) > 0) emit_error(paste0("\u4EE5\u4E0B\u53D8\u91CF\u4E0D\u5B58\u5728\uFF1A", paste(missing_vars, collapse = "\u3001"), "\u3002"))

variable_meta <- input$variable_meta %||% list()
meta_for <- function(variable) variable_meta[[variable]] %||% list()
display_name <- function(variable) {
  meta <- meta_for(variable)
  label <- meta$display_name %||% variable
  if (is.null(label) || label == "") variable else as.character(label)
}
apply_value_labels <- function(variable, values) {
  meta <- meta_for(variable)
  labels <- meta$value_labels %||% list()
  text <- clean_missing(values)
  if (length(labels) == 0) return(text)
  for (i in seq_along(text)) {
    if (is.na(text[[i]])) next
    mapped <- labels[[as.character(text[[i]])]]
    if (!is.null(mapped) && mapped != "") text[[i]] <- as.character(mapped)
  }
  text
}
predictor_type <- function(variable, values) {
  meta <- meta_for(variable)
  if (is_categorical_type(meta$var_type) || length(meta$value_labels %||% list()) > 0) return("categorical")
  numeric <- suppressWarnings(as.numeric(values))
  non_empty <- clean_missing(values)
  if (sum(!is.na(non_empty)) > 0 && sum(!is.na(numeric)) < sum(!is.na(non_empty))) return("categorical")
  "numeric"
}

model_df <- data.frame(Y = suppressWarnings(as.numeric(raw_df[[dependent]])))
predictor_info <- list()
predictor_order <- c()
for (idx in seq_along(predictors)) {
  variable <- predictors[[idx]]
  key <- paste0("X", idx)
  raw_values <- raw_df[[variable]]
  type <- predictor_type(variable, raw_values)
  predictor_order <- c(predictor_order, key)
  if (type == "categorical") {
    values <- apply_value_labels(variable, raw_values)
    levels_used <- unique(values[!is.na(values)])
    if (length(levels_used) == 0) emit_error(paste0("\u81EA\u53D8\u91CF ", display_name(variable), " \u6CA1\u6709\u6709\u6548\u7C7B\u522B\u3002"))
    model_df[[key]] <- factor(values, levels = levels_used)
    predictor_info[[key]] <- list(original = variable, label = display_name(variable), type = "categorical", levels = levels_used, reference = levels_used[[1]])
  } else {
    model_df[[key]] <- suppressWarnings(as.numeric(raw_values))
    predictor_info[[key]] <- list(original = variable, label = display_name(variable), type = "numeric")
  }
}

valid_mask <- stats::complete.cases(model_df)
model_df <- model_df[valid_mask, , drop = FALSE]
for (key in predictor_order) {
  if (predictor_info[[key]]$type == "categorical") {
    model_df[[key]] <- droplevels(model_df[[key]])
    predictor_info[[key]]$levels <- levels(model_df[[key]])
    predictor_info[[key]]$reference <- levels(model_df[[key]])[[1]]
  }
}
valid_n <- nrow(model_df)
if (valid_n < max(3, length(predictors) + 2)) emit_error("\u7EBF\u6027\u56DE\u5F52\u6709\u6548\u6837\u672C\u4E0D\u8DB3\u3002")
if (length(unique(model_df$Y)) <= 1) emit_error("\u56E0\u53D8\u91CF\u5728\u6709\u6548\u6837\u672C\u4E2D\u6CA1\u6709\u53D8\u5F02\uFF0C\u65E0\u6CD5\u8FDB\u884C\u7EBF\u6027\u56DE\u5F52\u3002")
for (key in predictor_order) {
  info <- predictor_info[[key]]
  unique_count <- if (info$type == "categorical") length(levels(model_df[[key]])) else length(unique(model_df[[key]]))
  if (unique_count <= 1) emit_error(paste0("\u81EA\u53D8\u91CF ", info$label, " \u5728\u6709\u6548\u6837\u672C\u4E2D\u6CA1\u6709\u53D8\u5F02\uFF0C\u65E0\u6CD5\u8FDB\u884C\u7EBF\u6027\u56DE\u5F52\u3002"))
}

formula_text <- paste("Y ~", paste(predictor_order, collapse = " + "))
model <- tryCatch(stats::lm(stats::as.formula(formula_text), data = model_df, na.action = stats::na.omit), error = function(e) e)
if (inherits(model, "error")) emit_error(paste0("\u7EBF\u6027\u56DE\u5F52\u62DF\u5408\u5931\u8D25\uFF1A", model$message))
if (stats::df.residual(model) <= 0) emit_error("\u6709\u6548\u6837\u672C\u91CF\u4E0D\u8DB3\uFF0C\u65E0\u6CD5\u4F30\u8BA1\u56DE\u5F52\u6A21\u578B\u3002")

model_summary <- summary(model)
coef_values <- stats::coef(model)
coef_summary <- model_summary$coefficients
ci_matrix <- tryCatch(stats::confint(model), error = function(e) NULL)
mm <- stats::model.matrix(model)
mm_cols <- colnames(mm)
assign_vec <- attr(mm, "assign")
term_labels <- attr(stats::terms(model), "term.labels")
sd_y <- stats::sd(model_df$Y)

design_terms <- list()
level_counters <- list()
if (ncol(mm) > 1) {
  for (col_index in seq(2, ncol(mm))) {
    term <- mm_cols[[col_index]]
    predictor_key <- term_labels[[assign_vec[[col_index]]]]
    info <- predictor_info[[predictor_key]]
    if (is.null(info)) next
    if (info$type == "categorical") {
      level_counters[[predictor_key]] <- (level_counters[[predictor_key]] %||% 0) + 1
      level <- info$levels[-1][[level_counters[[predictor_key]]]]
      label <- paste0(info$label, "=", level)
      design_terms[[term]] <- list(input_key = predictor_key, original = info$original, label = label, type = "categorical", level = level, reference = info$reference)
    } else {
      design_terms[[term]] <- list(input_key = predictor_key, original = info$original, label = info$label, type = "numeric")
    }
  }
}

coef_value <- function(term) if (term %in% names(coef_values)) coef_values[[term]] else NA_real_
coef_stat <- function(term, column) {
  if (!is.null(coef_summary) && term %in% rownames(coef_summary) && column %in% colnames(coef_summary)) return(coef_summary[term, column])
  NA_real_
}
coef_ci <- function(term, bound) {
  if (!is.null(ci_matrix) && term %in% rownames(ci_matrix)) return(ci_matrix[term, bound])
  NA_real_
}
beta_value <- function(term) {
  b <- coef_value(term)
  if (!(term %in% colnames(mm)) || is.na(b) || !is.finite(b) || is.na(sd_y) || sd_y == 0) return(NA_real_)
  sx <- stats::sd(mm[, term])
  if (is.na(sx) || sx == 0) return(NA_real_)
  b * sx / sd_y
}
vif_values <- function() {
  cols <- setdiff(colnames(mm), "(Intercept)")
  result <- list()
  if (length(predictors) < 2 || length(cols) < 2) return(result)
  design <- as.data.frame(mm[, cols, drop = FALSE], check.names = FALSE)
  for (term in cols) {
    others <- setdiff(cols, term)
    fit <- tryCatch(stats::lm(design[[term]] ~ ., data = design[, others, drop = FALSE]), error = function(e) NULL)
    if (is.null(fit)) {
      result[[term]] <- Inf
      next
    }
    r2 <- tryCatch(summary(fit)$r.squared, error = function(e) NA_real_)
    if (is.na(r2) || !is.finite(r2)) result[[term]] <- NA_real_
    else if (r2 >= 1 - 1e-10) result[[term]] <- Inf
    else result[[term]] <- 1 / (1 - r2)
  }
  result
}
vifs <- vif_values()
fmt_vif <- function(term) {
  value <- vifs[[term]]
  if (is.null(value)) return("\u2014")
  fmt_num(value, 3, inf_text = "inf")
}
fmt_tol <- function(term) {
  value <- vifs[[term]]
  if (is.null(value) || is.na(value) || !is.finite(value) || value == 0) return("\u2014")
  fmt_num(1 / value, 3)
}

main_coef_headers <- c("\u9879", "B", "\u6807\u51C6\u8BEF", "Beta", "t", "p", "VIF", "\u5BB9\u5FCD\u5EA6")
main_coef_header_rows <- list(
  list(
    list(text = "", rowspan = 2),
    list(text = "\u975E\u6807\u51C6\u5316\u7CFB\u6570", colspan = 2),
    list(text = "\u6807\u51C6\u5316\u7CFB\u6570", class = "tlt-head-group"),
    list(text = "t", rowspan = 2),
    list(text = "p", rowspan = 2),
    list(text = "\u5171\u7EBF\u6027\u8BCA\u65AD", colspan = 2)
  ),
  list("B", "\u6807\u51C6\u8BEF", "Beta", "VIF", "\u5BB9\u5FCD\u5EA6")
)
coef_headers <- c("\u9879", "\u975E\u6807\u51C6\u5316\u7CFB\u6570B", "\u6807\u51C6\u8BEF", "\u6807\u51C6\u5316\u7CFB\u6570Beta", "t", "p", "\u663E\u8457\u6027", "95% CI", "VIF", "\u5BB9\u5FCD\u5EA6")
coef_row <- function(term, label, include_beta = TRUE) {
  p_value <- coef_stat(term, "Pr(>|t|)")
  beta <- if (include_beta) beta_value(term) else NA_real_
  c(
    label,
    fmt_num(coef_value(term), 3),
    fmt_num(coef_stat(term, "Std. Error"), 3),
    if (include_beta) fmt_num(beta, 3) else "\u2014",
    fmt_num(coef_stat(term, "t value"), 3),
    fmt_p(p_value),
    sig_mark(p_value),
    fmt_ci(coef_ci(term, 1), coef_ci(term, 2)),
    if (term == "(Intercept)") "\u2014" else fmt_vif(term),
    if (term == "(Intercept)") "\u2014" else fmt_tol(term)
  )
}
main_coef_row <- function(term, label, include_beta = TRUE) {
  p_value <- coef_stat(term, "Pr(>|t|)")
  beta <- if (include_beta) beta_value(term) else NA_real_
  c(
    label,
    fmt_num(coef_value(term), 3),
    fmt_num(coef_stat(term, "Std. Error"), 3),
    if (include_beta) fmt_num(beta, 3) else "\u2014",
    fmt_num(coef_stat(term, "t value"), 3),
    paste0(fmt_p(p_value), sig_mark(p_value)),
    if (term == "(Intercept)") "\u2014" else fmt_vif(term),
    if (term == "(Intercept)") "\u2014" else fmt_tol(term)
  )
}
coef_rows <- list(coef_row("(Intercept)", "\u5E38\u6570", FALSE))
for (term in names(design_terms)) {
  coef_rows[[length(coef_rows) + 1]] <- coef_row(term, design_terms[[term]]$label, TRUE)
}

fstat <- model_summary$fstatistic
f_value <- if (!is.null(fstat)) as.numeric(fstat[[1]]) else NA_real_
df1 <- if (!is.null(fstat)) as.numeric(fstat[[2]]) else NA_real_
df2 <- if (!is.null(fstat)) as.numeric(fstat[[3]]) else NA_real_
f_p <- if (!is.null(fstat)) stats::pf(f_value, df1, df2, lower.tail = FALSE) else NA_real_
r2 <- model_summary$r.squared
adj_r2 <- model_summary$adj.r.squared
r_value <- sqrt(max(r2, 0))
residuals <- stats::residuals(model)
rmse <- sqrt(mean(residuals^2))
dw <- sum(diff(residuals)^2) / sum(residuals^2)
aic <- stats::AIC(model)
bic <- stats::BIC(model)

summary_rows <- list(
  c("\u6709\u6548\u6837\u672C\u91CF N", as.character(valid_n)),
  c("R", fmt_num(r_value, 3)),
  c("R\u00B2", fmt_num(r2, 3)),
  c("\u8C03\u6574R\u00B2", fmt_num(adj_r2, 3)),
  c("F", fmt_num(f_value, 3)),
  c("df1", fmt_num(df1, 0)),
  c("df2", fmt_num(df2, 0)),
  c("p", fmt_p(f_p)),
  c("Durbin-Watson", fmt_num(dw, 3)),
  c("RMSE", fmt_num(rmse, 3)),
  c("AIC", fmt_num(aic, 3)),
  c("BIC", fmt_num(bic, 3))
)

main_coef_rows <- list(main_coef_row("(Intercept)", "\u5E38\u6570", FALSE))
for (term in names(design_terms)) {
  main_coef_rows[[length(main_coef_rows) + 1]] <- main_coef_row(term, design_terms[[term]]$label, TRUE)
}
main_coef_rows[[length(main_coef_rows) + 1]] <- list("R\u00B2", table_cell("", colspan = 3), table_cell(fmt_num(r2, 3), colspan = 4))
main_coef_rows[[length(main_coef_rows) + 1]] <- list("\u8C03\u6574R\u00B2", table_cell("", colspan = 3), table_cell(fmt_num(adj_r2, 3), colspan = 4))
main_coef_rows[[length(main_coef_rows) + 1]] <- list("F", table_cell("", colspan = 3), table_cell(paste0("F(", fmt_num(df1, 0), ",", fmt_num(df2, 0), ")=", fmt_num(f_value, 3), ", p=", fmt_p(f_p)), colspan = 4))
main_coef_rows[[length(main_coef_rows) + 1]] <- list("D-W\u503C", table_cell("", colspan = 3), table_cell(fmt_num(dw, 3), colspan = 4))

tss <- sum((model_df$Y - mean(model_df$Y))^2)
rss <- sum(residuals^2)
ssr <- tss - rss
msr <- ssr / df1
mse <- rss / df2
anova_rows <- list(
  c("\u56DE\u5F52", fmt_num(ssr, 3), fmt_num(df1, 0), fmt_num(msr, 3), fmt_num(f_value, 3), fmt_p(f_p)),
  c("\u6B8B\u5DEE", fmt_num(rss, 3), fmt_num(df2, 0), fmt_num(mse, 3), "\u2014", "\u2014"),
  c("\u603B\u8BA1", fmt_num(tss, 3), fmt_num(df1 + df2, 0), "\u2014", "\u2014", "\u2014")
)

simplified_rows <- list()
for (term in names(design_terms)) {
  p_value <- coef_stat(term, "Pr(>|t|)")
  b <- coef_value(term)
  direction <- if (!is.na(b) && b < 0) "\u8D1F\u5411" else "\u6B63\u5411"
  conclusion <- if (!is.na(p_value) && p_value < 0.05) paste0("\u663E\u8457", direction, "\u5F71\u54CD") else "\u672A\u8FBE\u663E\u8457"
  simplified_rows[[length(simplified_rows) + 1]] <- c(design_terms[[term]]$label, fmt_num(b, 3), fmt_num(beta_value(term), 3), paste0(fmt_p(p_value), sig_mark(p_value)), conclusion)
}

ref_notes <- c()
for (key in predictor_order) {
  info <- predictor_info[[key]]
  if (info$type == "categorical") ref_notes <- c(ref_notes, paste0(info$label, "\u7684\u53C2\u7167\u7C7B\u522B\u4E3A", info$reference))
}
reference_note <- if (length(ref_notes) > 0) paste0("\u5B9A\u7C7B\u81EA\u53D8\u91CF\u5DF2\u81EA\u52A8\u54D1\u53D8\u91CF\u5316\uFF1B", paste(ref_notes, collapse = "\uFF1B"), "\u3002") else "\u672C\u6A21\u578B\u672A\u7EB3\u5165\u5B9A\u7C7B\u81EA\u53D8\u91CF\u3002"

fitted_values <- stats::fitted(model)
plot_n <- min(length(fitted_values), 100)
fit_chart <- list(
  chartType = "metric_comparison",
  title = "\u62DF\u5408\u6548\u679C\u56FE",
  data = list(
    metric = display_name(dependent),
    labels = as.character(seq_len(plot_n)),
    values = as.numeric(model_df$Y[seq_len(plot_n)]),
    metrics = list("\u771F\u5B9E\u503C" = as.numeric(model_df$Y[seq_len(plot_n)]), "\u9884\u6D4B\u503C" = as.numeric(fitted_values[seq_len(plot_n)])),
    multiSeries = TRUE,
    defaultMode = "line",
    displayTitle = "\u62DF\u5408\u6548\u679C\u56FE"
  )
)
path_edges <- list()
for (term in names(design_terms)) {
  p_value <- coef_stat(term, "Pr(>|t|)")
  path_edges[[length(path_edges) + 1]] <- list(
    label = design_terms[[term]]$label,
    value = paste0(fmt_num(beta_value(term), 3), sig_mark(p_value)),
    p = fmt_p(p_value),
    significant = !is.na(p_value) && p_value < 0.05
  )
}
path_chart <- list(
  chartType = "model_path",
  title = "\u6A21\u578B\u8DEF\u5F84\u56FE",
  data = list(target = display_name(dependent), edges = path_edges)
)
ci_terms <- names(design_terms)
ci_chart <- list(
  chartType = "coefficient_interval",
  title = "\u56DE\u5F52\u7CFB\u657095% CI",
  data = list(
    metric = "\u975E\u6807\u51C6\u5316\u7CFB\u6570B",
    labels = unname(sapply(ci_terms, function(term) design_terms[[term]]$label)),
    estimates = as.numeric(sapply(ci_terms, coef_value)),
    lower = as.numeric(sapply(ci_terms, function(term) coef_ci(term, 1))),
    upper = as.numeric(sapply(ci_terms, function(term) coef_ci(term, 2))),
    displayTitle = "\u56DE\u5F52\u7CFB\u657095% CI"
  )
)

prediction_inputs <- list()
prediction_rows <- list(c("\u5E38\u6570", "\u2014", fmt_num(coef_value("(Intercept)"), 3), "\u9ED8\u8BA4\u9884\u6D4B\u503C"))
for (key in predictor_order) {
  info <- predictor_info[[key]]
  matching_terms <- names(Filter(function(item) item$input_key == key, design_terms))
  if (info$type == "numeric") {
    term <- matching_terms[[1]]
    coefficient <- number_or_zero(coef_value(term))
    prediction_inputs[[length(prediction_inputs) + 1]] <- list(
      key = info$original,
      label = info$label,
      type = "numeric",
      coefficient = coefficient,
      defaultValue = 0
    )
    prediction_rows[[length(prediction_rows) + 1]] <- c(info$label, "0", fmt_num(coefficient, 3), "\u5B9A\u91CF\u8F93\u5165")
  } else {
    options <- list(list(label = info$reference, value = info$reference, coefficient = 0, reference = TRUE))
    for (term in matching_terms) {
      item <- design_terms[[term]]
      coefficient <- number_or_zero(coef_value(term))
      options[[length(options) + 1]] <- list(label = item$level, value = item$level, coefficient = coefficient, reference = FALSE)
      prediction_rows[[length(prediction_rows) + 1]] <- c(paste0(info$label, "=", item$level), info$reference, fmt_num(coefficient, 3), "\u76F8\u5BF9\u53C2\u7167\u7C7B\u522B")
    }
    prediction_inputs[[length(prediction_inputs) + 1]] <- list(
      key = info$original,
      label = info$label,
      type = "categorical",
      reference = info$reference,
      defaultValue = info$reference,
      options = options
    )
  }
}
equation_parts <- c(fmt_num(coef_value("(Intercept)"), 3))
for (term in names(design_terms)) {
  b <- coef_value(term)
  if (is.na(b) || !is.finite(b)) next
  sign <- if (b < 0) " - " else " + "
  equation_parts <- c(equation_parts, paste0(sign, fmt_num(abs(b), 3), "\u00D7", design_terms[[term]]$label))
}
prediction_section <- list(
  type = "regression_prediction",
  title = "\u8F93\u51FA\u7ED3\u679C4\uFF1A\u6A21\u578B\u7ED3\u679C\u9884\u6D4B",
  dependent = display_name(dependent),
  intercept = number_or_zero(coef_value("(Intercept)")),
  defaultPrediction = number_or_zero(coef_value("(Intercept)")),
  description = paste0("预测值就是模型按公式算出来的“预计得分”，它能帮你看趋势和模拟情况，但不能当成确定结论。", "\u672C\u8868\u628A\u56DE\u5F52\u65B9\u7A0B\u8F6C\u6362\u4E3A\u53EF\u8C03\u9884\u6D4B\u5668\uFF1A\u5728\u201C\u6D4B\u8BD5\u503C\u201D\u4E2D\u8F93\u5165\u5404\u81EA\u53D8\u91CF\u53D6\u503C\uFF0C\u7CFB\u7EDF\u4F1A\u6309\u5E38\u6570\u9879\u548C\u5404\u53D8\u91CF\u7CFB\u6570\u8BA1\u7B97", display_name(dependent), "\u7684\u9884\u6D4B\u503C\u3002\u9884\u6D4B\u662F\u5426\u53EF\u9760\u4ECD\u9700\u7ED3\u5408\u6A21\u578BR\u00B2\u3001F\u68C0\u9A8C\u3001\u6B8B\u5DEE\u60C5\u51B5\u548C\u6837\u672C\u9002\u7528\u8303\u56F4\u5224\u65AD\u3002"),
  equation = paste0(display_name(dependent), " = ", paste(equation_parts, collapse = "")),
  inputs = prediction_inputs,
  coefficientRows = prediction_rows
)

model_kind <- if (length(predictors) == 1) "\u4E00\u5143\u7EBF\u6027\u56DE\u5F52" else "\u591A\u5143\u7EBF\u6027\u56DE\u5F52"
significant_labels <- c()
for (term in names(design_terms)) {
  p_value <- coef_stat(term, "Pr(>|t|)")
  if (!is.na(p_value) && p_value < 0.05) significant_labels <- c(significant_labels, design_terms[[term]]$label)
}
beta_values <- sapply(names(design_terms), beta_value)
strongest <- if (length(beta_values) && any(!is.na(beta_values))) names(design_terms)[which.max(abs(beta_values))] else NA
strongest_text <- if (!is.na(strongest)) paste0("\u6807\u51C6\u5316\u5F71\u54CD\u6700\u5927\u7684\u9879\u662F ", design_terms[[strongest]]$label, "\uFF08Beta=", fmt_num(beta_value(strongest), 3), "\uFF09") else "\u6682\u65E0\u53EF\u6BD4\u8F83\u7684\u6807\u51C6\u5316\u7CFB\u6570"
overall_text <- paste0(
  model_kind, "\u91C7\u7528\u6700\u5C0F\u4E8C\u4E58\u6CD5\u548C\u5F3A\u5236\u8FDB\u5165\u6CD5\u5B8C\u6210\uFF0C\u5171\u7EB3\u5165 ", valid_n, " \u6761\u6709\u6548\u6837\u672C\u3002",
  "\u6A21\u578B\u6574\u4F53", ifelse(!is.na(f_p) && f_p < 0.05, "\u8FBE\u5230\u663E\u8457", "\u672A\u8FBE\u5230\u663E\u8457"),
  "\uFF08F=", fmt_num(f_value, 3), "\uFF0Cp=", fmt_p(f_p), "\uFF09\uFF0CR\u00B2=", fmt_num(r2, 3), "\uFF0C\u8C03\u6574R\u00B2=", fmt_num(adj_r2, 3), "\u3002"
)
detail_text <- paste0(
  overall_text, "\n",
  strongest_text, "\u3002",
  if (length(significant_labels) > 0) paste0("\u663E\u8457\u81EA\u53D8\u91CF\u4E3A\uFF1A", paste(significant_labels, collapse = "\u3001"), "\u3002") else "\u5404\u81EA\u53D8\u91CF\u5747\u672A\u8FBE\u52300.05\u663E\u8457\u6027\u6C34\u5E73\u3002"
)
high_vif <- names(Filter(function(value) !is.null(value) && is.finite(value) && value > 10, vifs))
inf_vif <- names(Filter(function(value) !is.null(value) && is.infinite(value), vifs))
term_interpretation <- function(term) {
  label <- design_terms[[term]]$label
  b <- coef_value(term)
  beta <- beta_value(term)
  p_value <- coef_stat(term, "Pr(>|t|)")
  direction <- if (!is.na(b) && b < 0) "\u8D1F\u5411" else "\u6B63\u5411"
  if (!is.na(p_value) && p_value < 0.05) {
    paste0(label, "\u5BF9", display_name(dependent), "\u5448\u663E\u8457", direction, "\u5F71\u54CD\uFF08B=", fmt_num(b, 3), "\uFF0CBeta=", fmt_num(beta, 3), "\uFF0C", p_compare(p_value), "\uFF09")
  } else {
    paste0(label, "\u672A\u5448\u73B0\u663E\u8457\u5F71\u54CD\uFF08", p_compare(p_value), "\uFF09")
  }
}
sig_terms <- Filter(function(term) {
  p_value <- coef_stat(term, "Pr(>|t|)")
  !is.na(p_value) && p_value < 0.05
}, names(design_terms))
non_sig_terms <- setdiff(names(design_terms), sig_terms)
sig_text <- if (length(sig_terms) > 0) {
  paste(sapply(sig_terms, term_interpretation), collapse = "\uFF1B")
} else {
  "\u5404\u81EA\u53D8\u91CF\u5747\u672A\u5448\u73B0\u663E\u8457\u5F71\u54CD"
}
non_sig_text <- if (length(non_sig_terms) > 0) {
  paste0("\u672A\u8FBE\u663E\u8457\u7684\u53D8\u91CF\u4E3A\uFF1A", paste(sapply(non_sig_terms, function(term) design_terms[[term]]$label), collapse = "\u3001"), "\u3002")
} else {
  "\u5176\u4F59\u81EA\u53D8\u91CF\u5747\u8FBE\u52300.05\u663E\u8457\u6027\u6C34\u5E73\u3002"
}
collinearity_text <- if (length(inf_vif) > 0) {
  paste0("\u5171\u7EBF\u6027\u65B9\u9762\uFF0C", paste(sapply(inf_vif, function(term) design_terms[[term]]$label), collapse = "\u3001"), "\u5B58\u5728\u5B8C\u5168\u5171\u7EBF\u6216\u5F02\u5E38\u5171\u7EBF\uFF0CVIF\u8BB0\u4E3Ainf\u3002")
} else if (length(high_vif) > 0) {
  paste0("\u5171\u7EBF\u6027\u65B9\u9762\uFF0C", paste(sapply(high_vif, function(term) design_terms[[term]]$label), collapse = "\u3001"), "\u7684VIF>10\uFF0C\u9700\u8B66\u60D5\u591A\u91CD\u5171\u7EBF\u6027\u3002")
} else {
  "\u5171\u7EBF\u6027\u65B9\u9762\uFF0C\u5404\u9879VIF\u5747\u672A\u8D85\u8FC710\uFF0C\u6682\u672A\u53D1\u73B0\u4E25\u91CD\u591A\u91CD\u5171\u7EBF\u6027\u95EE\u9898\u3002"
}
dw_text <- if (!is.na(dw) && dw >= 1.5 && dw <= 2.5) {
  paste0("D-W\u503C\u4E3A", fmt_num(dw, 3), "\uFF0C\u63A5\u8FD12\uFF0C\u6B8B\u5DEE\u81EA\u76F8\u5173\u98CE\u9669\u8F83\u4F4E\u3002")
} else {
  paste0("D-W\u503C\u4E3A", fmt_num(dw, 3), "\uFF0C\u5EFA\u8BAE\u7ED3\u5408\u6B8B\u5DEE\u56FE\u68C0\u67E5\u6B8B\u5DEE\u72EC\u7ACB\u6027\u3002")
}
table_interpretation <- paste0(
  "\u4ECE\u4E0A\u8868\u53EF\u77E5\uFF1A\n",
  "1. \u6A21\u578B\u6574\u4F53", ifelse(!is.na(f_p) && f_p < 0.05, "\u663E\u8457", "\u4E0D\u663E\u8457"),
  "\uFF08F(", fmt_num(df1, 0), ",", fmt_num(df2, 0), ")=", fmt_num(f_value, 3), "\uFF0C", p_compare(f_p), "\uFF09\uFF0CR\u00B2=", fmt_num(r2, 3), "\uFF0C\u8C03\u6574R\u00B2=", fmt_num(adj_r2, 3), "\u3002\n",
  "2. \u5177\u4F53\u53D8\u91CF\u4E2D\uFF0C", sig_text, "\u3002", non_sig_text, "\n",
  "3. ", collinearity_text,
  dw_text
)
smart <- detail_text
if (length(high_vif) > 0) smart <- paste0(smart, "\n\u6CE8\u610F\uFF1A", paste(sapply(high_vif, function(term) design_terms[[term]]$label), collapse = "\u3001"), "\u7684VIF>10\uFF0C\u5B58\u5728\u8F83\u5F3A\u591A\u91CD\u5171\u7EBF\u6027\u3002")
if (length(inf_vif) > 0) smart <- paste0(smart, "\n\u6CE8\u610F\uFF1A", paste(sapply(inf_vif, function(term) design_terms[[term]]$label), collapse = "\u3001"), "\u5B58\u5728\u5B8C\u5168\u5171\u7EBF\u6216\u5F02\u5E38\u5171\u7EBF\uFF0CVIF\u8BB0\u4E3Ainf\u3002")

steps <- paste(
  paste0("1. \u56E0\u53D8\u91CFY\uFF1A", display_name(dependent), "\u3002"),
  paste0("2. \u81EA\u53D8\u91CFX\uFF1A", paste(sapply(predictors, display_name), collapse = "\u3001"), "\u3002"),
  "3. \u6A21\u578B\u4F30\u8BA1\uFF1A\u91C7\u7528lm()\u6700\u5C0F\u4E8C\u4E58\u6CD5\uFF0C\u6240\u6709X\u540C\u65F6\u8FDB\u5165\u6A21\u578B\u3002",
  "4. \u7F3A\u5931\u5904\u7406\uFF1A\u5BF9Y\u548C\u6240\u6709X\u8FDB\u884C\u5217\u8868\u5220\u9664\uFF0C\u4EFB\u4E00\u5EFA\u6A21\u53D8\u91CF\u7F3A\u5931\u7684\u6837\u672C\u4E0D\u8FDB\u5165\u6A21\u578B\u3002",
  ifelse(length(ref_notes) > 0, paste0("5. \u5B9A\u7C7B\u5904\u7406\uFF1A", paste(ref_notes, collapse = "\uFF1B"), "\u3002"), "5. \u672C\u6B21X\u5747\u6309\u5B9A\u91CF\u53D8\u91CF\u8FDB\u5165\u6A21\u578B\u3002"),
  sep = "\n"
)
advice <- paste(
  "\u7B2C\u4E00\uFF1A\u5148\u770B\u6A21\u578B\u6C47\u603B\uFF0CR\u00B2\u548C\u8C03\u6574R\u00B2\u8868\u793A\u89E3\u91CA\u5EA6\uFF0C\u4E0D\u5E94\u53EA\u770Bp\u503C\u3002",
  "\u7B2C\u4E8C\uFF1AF\u68C0\u9A8C\u7528\u4E8E\u5224\u65AD\u56DE\u5F52\u65B9\u7A0B\u6574\u4F53\u662F\u5426\u6709\u6548\u3002",
  "\u7B2C\u4E09\uFF1A\u56DE\u5F52\u7CFB\u6570B\u53CD\u6620\u975E\u6807\u51C6\u5316\u5F71\u54CD\uFF0CBeta\u66F4\u9002\u5408\u6BD4\u8F83\u4E0D\u540CX\u7684\u76F8\u5BF9\u5F71\u54CD\u3002",
  "\u7B2C\u56DB\uFF1AVIF>10\u6216VIF=inf\u65F6\u9700\u8B66\u60D5\u5171\u7EBF\u6027\uFF0C\u4E0D\u8981\u76F4\u63A5\u673A\u68B0\u89E3\u91CA\u5355\u4E2A\u7CFB\u6570\u3002",
  sep = "\n"
)

sections <- list(
  sec_advice(steps, "\u5206\u6790\u6B65\u9AA4"),
  sec_advice(detail_text, "\u8BE6\u7EC6\u7ED3\u8BBA"),
  sec_table(
    paste0("\u8F93\u51FA\u7ED3\u679C1\uFF1A\u7EBF\u6027\u56DE\u5F52\u5206\u6790\u7ED3\u679C\u8868 (n=", valid_n, ")"),
    main_coef_headers,
    main_coef_rows,
    description = table_interpretation,
    note = paste0("\u5907\u6CE8\uFF1A\u56E0\u53D8\u91CF = ", display_name(dependent), "\u3002* p<0.05 ** p<0.01 *** p<0.001\u3002", reference_note),
    headerRows = main_coef_header_rows,
    bodyRowspanColumns = 1
  ),
  sec_charts("输出结果2：拟合效果图", list(fit_chart), paste0("图中展示前 ", plot_n, " 条有效样本的真实值和预测值。两条线越接近，说明模型对样本的拟合越好；若某些位置真实值和预测值偏离较大，说明这些样本的误差较高，需要结合残差、异常值和业务背景继续判断。")),
  sec_charts("输出结果3：模型路径图", list(path_chart), paste0("图中箭头表示各自变量对因变量 ", display_name(dependent), " 的影响路径，路径标签为标准化Beta，便于比较不同自变量的相对影响强弱。带星号的路径表示p<0.05，未带星号的路径表示该变量在当前模型中未达到0.05显著性水平。")),
  prediction_section,
  sec_table("\u7EBF\u6027\u56DE\u5F52\u5206\u6790\u7ED3\u679C-\u7B80\u5316\u683C\u5F0F", c("\u81EA\u53D8\u91CF", "B", "Beta", "p", "\u7ED3\u8BBA"), simplified_rows),
  sec_table("\u6A21\u578B\u6C47\u603B\uFF08\u4E2D\u95F4\u8FC7\u7A0B\uFF09", c("\u6307\u6807", "\u503C"), summary_rows),
  sec_table("ANOVA\u8868\u683C\uFF08\u4E2D\u95F4\u8FC7\u7A0B\uFF09", c("\u6765\u6E90", "SS", "df", "MS", "F", "p"), anova_rows),
  sec_table("\u56DE\u5F52\u7CFB\u6570\uFF08\u4E2D\u95F4\u8FC7\u7A0B\uFF09", coef_headers, coef_rows, note = reference_note),
  sec_charts("回归系数95% CI", list(ci_chart), "图中黑色横线表示回归系数B的95%置信区间，蓝点表示系数估计值。若区间整体位于0的一侧，说明该系数方向相对稳定；若区间跨过0，说明该系数方向和显著性需要谨慎解释。"),
  sec_advice(advice),
  sec_smart(smart),
  sec_refs(c(
    "[1] SPSSGO \u56E2\u961F. SPSSGO \u5728\u7EBF\u6570\u636E\u5206\u6790\u5E73\u53F0[CP/OL]. https://www.spssgo.com.",
    "[2] Cohen J, Cohen P, West S G, Aiken L S. Applied Multiple Regression/Correlation Analysis for the Behavioral Sciences. 3rd ed. Routledge, 2003.",
    "[3] Kutner M H, Nachtsheim C J, Neter J, Li W. Applied Linear Statistical Models. 5th ed. McGraw-Hill, 2005."
  ))
)

result <- list(
  success = TRUE,
  name = "\u7EBF\u6027\u56DE\u5F52\uFF08\u6700\u5C0F\u4E8C\u4E58\u6CD5\uFF09",
  headers = coef_headers,
  rows = coef_rows,
  description = smart,
  sections = sections
)
emit_json(result)
