# -*- coding: UTF-8 -*-
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
  sprintf(paste0("%.", digits, "f"), as.numeric(x))
}
sig_mark <- function(p) {
  if (is.null(p) || length(p) == 0 || is.na(p) || is.infinite(p)) return("")
  if (p < 0.001) return("****")
  if (p < 0.01) return("***")
  if (p < 0.05) return("**")
  if (p < 0.1) return("*")
  ""
}
fmt_p <- function(p) {
  if (is.null(p) || length(p) == 0 || is.na(p) || is.infinite(p)) return("\u2014")
  paste0(fmt_num(p, 3), sig_mark(p))
}
fmt_ci <- function(low, high) paste0(fmt_num(low, 3), " ~ ", fmt_num(high, 3))
sec_table <- function(title, headers, rows, description = NULL, note = NULL, headerRows = NULL) {
  item <- list(type = "table", title = title, headers = headers, rows = rows)
  if (!is.null(description)) item$description <- description
  if (!is.null(note)) item$note <- note
  if (!is.null(headerRows)) item$headerRows <- headerRows
  item
}
sec_smart <- function(content) list(type = "smart_analysis", title = "\u667A\u80FD\u5206\u6790", content = content)
sec_advice <- function(content, title = "\u5206\u6790\u5EFA\u8BAE") list(type = "advice", title = title, content = content)
sec_refs <- function(items) list(type = "references", title = "\u53C2\u8003\u6587\u732E", items = items)
sec_charts <- function(title, charts, description = NULL) {
  item <- list(type = "charts", title = title, charts = charts)
  if (!is.null(description)) item$description <- description
  item
}

input <- jsonlite::fromJSON(read_utf8(input_path), simplifyVector = FALSE)
input_dir <- dirname(normalizePath(input_path, winslash = "/", mustWork = TRUE))
data_file <- file.path(input_dir, input$data_file)
if (!file.exists(data_file)) stop("missing input data file")

x <- input$x
w <- input$w
y <- input$y
controls <- input$controls
if (is.null(controls)) controls <- c()
controls <- unique(as.character(unlist(controls)))
moderation_type <- input$moderation_type
if (is.null(moderation_type) || moderation_type == "") moderation_type <- "X\u5B9A\u91CFW\u5B9A\u91CF(\u9ED8\u8BA4)"
data_process <- input$data_process
if (is.null(data_process) || data_process == "") data_process <- "\u4E2D\u5FC3\u5316(\u9ED8\u8BA4)"

raw_df <- read.csv(data_file, stringsAsFactors = FALSE, check.names = FALSE)
variables <- unique(c(y, x, w, controls))
missing_vars <- setdiff(variables, names(raw_df))
if (length(missing_vars) > 0) {
  cat(jsonlite::toJSON(list(success = FALSE, error = paste0("\u7F3A\u5C11\u53D8\u91CF\uFF1A", paste(missing_vars, collapse = "\u3001"))), auto_unbox = TRUE, force = TRUE, ascii = TRUE))
  quit(status = 0)
}

x_is_cat <- grepl("X\u5B9A\u7C7B", moderation_type)
w_is_cat <- grepl("W\u5B9A\u7C7B|Z\u5B9A\u7C7B", moderation_type)
if (x_is_cat && w_is_cat) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "\u8C03\u8282\u4F5C\u7528\u6682\u4E0D\u652F\u6301 X \u548C W \u540C\u65F6\u4E3A\u5B9A\u7C7B\u53D8\u91CF\u3002"), auto_unbox = TRUE, force = TRUE, ascii = TRUE))
  quit(status = 0)
}

source_df <- raw_df[, variables, drop = FALSE]
model_df <- data.frame(Y = suppressWarnings(as.numeric(source_df[[y]])))

process_numeric <- function(values) {
  numeric <- suppressWarnings(as.numeric(values))
  if (data_process == "\u6807\u51C6\u5316") {
    sd_value <- stats::sd(numeric, na.rm = TRUE)
    if (is.na(sd_value) || sd_value == 0) return(rep(NA_real_, length(numeric)))
    return((numeric - mean(numeric, na.rm = TRUE)) / sd_value)
  }
  if (data_process == "\u4E0D\u5904\u7406") return(numeric)
  numeric - mean(numeric, na.rm = TRUE)
}
make_factor <- function(values) {
  text <- trimws(as.character(values))
  text[text == "" | tolower(text) %in% c("nan", "na", "null", "none")] <- NA
  factor(text)
}

if (x_is_cat) {
  model_df$X <- make_factor(source_df[[x]])
} else {
  model_df$X <- process_numeric(source_df[[x]])
}
if (w_is_cat) {
  model_df$W <- make_factor(source_df[[w]])
} else {
  model_df$W <- process_numeric(source_df[[w]])
}
control_keys <- c()
control_labels <- list()
if (length(controls) > 0) {
  for (idx in seq_along(controls)) {
    key <- paste0("C", idx)
    control_keys <- c(control_keys, key)
    control_labels[[key]] <- controls[[idx]]
    model_df[[key]] <- suppressWarnings(as.numeric(source_df[[controls[[idx]]]]))
  }
}

model_df <- stats::na.omit(model_df)
if (nrow(model_df) < 10) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "\u8C03\u8282\u6548\u5E94\u5206\u6790\u6709\u6548\u6837\u672C\u4E0D\u8DB3\u3002"), auto_unbox = TRUE, force = TRUE, ascii = TRUE))
  quit(status = 0)
}
if (!x_is_cat && length(unique(model_df$X)) <= 1) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "\u81EA\u53D8\u91CF X \u5728\u6709\u6548\u6837\u672C\u4E2D\u6CA1\u6709\u53D8\u5F02\uFF0C\u65E0\u6CD5\u8FDB\u884C\u8C03\u8282\u4F5C\u7528\u5206\u6790\u3002"), auto_unbox = TRUE, force = TRUE, ascii = TRUE))
  quit(status = 0)
}
if (!w_is_cat && length(unique(model_df$W)) <= 1) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "\u8C03\u8282\u53D8\u91CF W \u5728\u6709\u6548\u6837\u672C\u4E2D\u6CA1\u6709\u53D8\u5F02\uFF0C\u65E0\u6CD5\u8FDB\u884C\u8C03\u8282\u4F5C\u7528\u5206\u6790\u3002"), auto_unbox = TRUE, force = TRUE, ascii = TRUE))
  quit(status = 0)
}

rhs <- function(terms) {
  if (!length(terms)) return("1")
  paste(terms, collapse = " + ")
}
base_terms <- control_keys
m1 <- stats::lm(stats::as.formula(paste("Y ~", rhs(c(base_terms, "X")))), data = model_df)
m2 <- stats::lm(stats::as.formula(paste("Y ~", rhs(c(base_terms, "X", "W")))), data = model_df)
m3 <- stats::lm(stats::as.formula(paste("Y ~", rhs(c(base_terms, "X", "W", "X:W")))), data = model_df)
models <- list("\u6A21\u578B1" = m1, "\u6A21\u578B2" = m2, "\u6A21\u578B3" = m3)

column_label_map <- function(model) {
  labels <- list("(Intercept)" = "\u5E38\u6570")
  mm_names <- colnames(stats::model.matrix(model))
  for (key in control_keys) labels[[key]] <- control_labels[[key]]
  if (!x_is_cat) labels[["X"]] <- x
  if (!w_is_cat) labels[["W"]] <- w
  if (!x_is_cat && !w_is_cat) labels[["X:W"]] <- paste0(x, "*", w)
  if (x_is_cat) {
    for (level in levels(model_df$X)[-1]) {
      labels[[paste0("X", make.names(level))]] <- paste0(x, "=", level)
      if (!w_is_cat) labels[[paste0("X", make.names(level), ":W")]] <- paste0(x, "=", level, "*", w)
    }
  }
  if (w_is_cat) {
    for (level in levels(model_df$W)[-1]) {
      labels[[paste0("W", make.names(level))]] <- paste0(w, "=", level)
      if (!x_is_cat) labels[[paste0("X:W", make.names(level))]] <- paste0(x, "*", w, "=", level)
    }
  }
  for (name in mm_names) {
    if (is.null(labels[[name]])) labels[[name]] <- name
  }
  labels
}
label_maps <- lapply(models, column_label_map)

ordered_terms <- function() {
  all_terms <- unique(unlist(lapply(models, function(model) names(stats::coef(model)))))
  labels <- label_maps[[length(label_maps)]]
  wanted_labels <- c("\u5E38\u6570", unlist(control_labels), x, w)
  if (x_is_cat) wanted_labels <- c(wanted_labels, paste0(x, "=", levels(model_df$X)[-1]))
  if (w_is_cat) wanted_labels <- c(wanted_labels, paste0(w, "=", levels(model_df$W)[-1]))
  wanted_labels <- c(wanted_labels, unname(unlist(labels[grep(":", names(labels), fixed = TRUE)])))
  ordered <- c()
  for (label in wanted_labels) {
    for (term in all_terms) {
      term_label <- labels[[term]]
      if (!is.null(term_label) && term_label == label && !(term %in% ordered)) ordered <- c(ordered, term)
    }
  }
  c(ordered, setdiff(all_terms, ordered))
}
terms_order <- ordered_terms()
term_label <- function(term) {
  label <- label_maps[[length(label_maps)]][[term]]
  if (is.null(label)) term else label
}

coef_cells <- function(model, term) {
  coefs <- summary(model)$coefficients
  if (!(term %in% rownames(coefs))) return(c("", "", "", "", ""))
  mm <- stats::model.matrix(model)
  beta <- "\u2014"
  if (term != "(Intercept)" && term %in% colnames(mm)) {
    beta_value <- stats::coef(model)[[term]] * stats::sd(mm[, term]) / stats::sd(model$model$Y)
    beta <- fmt_num(beta_value, 3)
  }
  c(
    fmt_num(coefs[term, "Estimate"], 3),
    fmt_num(coefs[term, "Std. Error"], 3),
    fmt_num(coefs[term, "t value"], 3),
    fmt_p(coefs[term, "Pr(>|t|)"]),
    beta
  )
}
model_p <- function(model) {
  f <- summary(model)$fstatistic
  if (is.null(f)) return(NA_real_)
  stats::pf(f[1], f[2], f[3], lower.tail = FALSE)
}
model_f_text <- function(model) {
  f <- summary(model)$fstatistic
  if (is.null(f)) return("\u2014")
  paste0("F(", as.integer(f[2]), ",", as.integer(f[3]), ")=", fmt_num(f[1], 3), ", p=", fmt_num(model_p(model), 3))
}
delta_text <- function(prev, current) {
  cmp <- if (is.null(prev)) stats::anova(current) else stats::anova(prev, current)
  row <- nrow(cmp)
  f_val <- cmp$F[row]
  p_val <- cmp$`Pr(>F)`[row]
  if (is.na(f_val)) return("\u2014")
  paste0("F(", as.integer(cmp$Df[row]), ",", as.integer(cmp$Res.Df[row]), ")=", fmt_num(f_val, 3), ", p=", fmt_num(p_val, 3))
}
delta_r2 <- function(prev, current) {
  current_r2 <- summary(current)$r.squared
  if (is.null(prev)) return(current_r2)
  current_r2 - summary(prev)$r.squared
}

header_rows <- list(
  c(list(list(text = "", rowspan = 2)), lapply(names(models), function(name) list(text = name, colspan = 5))),
  rep(c("B", "\u6807\u51C6\u8BEF", "t", "p", "\u03B2"), length(models))
)
full_header_rows <- list(
  list(
    list(text = "\u6A21\u578B", rowspan = 2),
    list(text = "\u9879", rowspan = 2),
    list(text = "\u975E\u6807\u51C6\u5316\u7CFB\u6570", colspan = 2),
    list(text = "\u6807\u51C6\u5316\u7CFB\u6570\u03B2", rowspan = 2),
    list(text = "t", rowspan = 2),
    list(text = "p", rowspan = 2),
    list(text = "95% CI", rowspan = 2),
    list(text = "\u5171\u7EBF\u6027\u8BCA\u65AD", colspan = 2)
  ),
  list("B", "\u6807\u51C6\u8BEF", "VIF", "\u5BB9\u5DEE")
)
main_rows <- list()
for (term in terms_order) {
  row <- c(term_label(term))
  for (model in models) row <- c(row, coef_cells(model, term))
  main_rows[[length(main_rows) + 1]] <- row
}
stat_row <- function(label, values) c(label, unlist(lapply(values, function(value) c(value, rep("", 4)))))
main_rows[[length(main_rows) + 1]] <- stat_row("\u6837\u672C\u91CF", lapply(models, function(model) as.character(stats::nobs(model))))
main_rows[[length(main_rows) + 1]] <- stat_row("R\u00B2", lapply(models, function(model) fmt_num(summary(model)$r.squared, 3)))
main_rows[[length(main_rows) + 1]] <- stat_row("\u8C03\u6574R\u00B2", lapply(models, function(model) fmt_num(summary(model)$adj.r.squared, 3)))
main_rows[[length(main_rows) + 1]] <- stat_row("F\u503C", lapply(models, model_f_text))
main_rows[[length(main_rows) + 1]] <- stat_row("\u25B3R\u00B2", list(fmt_num(delta_r2(NULL, m1), 3), fmt_num(delta_r2(m1, m2), 3), fmt_num(delta_r2(m2, m3), 3)))
main_rows[[length(main_rows) + 1]] <- stat_row("\u25B3F\u503C", list(delta_text(NULL, m1), delta_text(m1, m2), delta_text(m2, m3)))

vif_values <- function(model) {
  mm <- stats::model.matrix(model)
  cols <- setdiff(colnames(mm), "(Intercept)")
  result <- list()
  if (length(cols) < 2) return(result)
  for (col in cols) {
    others <- setdiff(cols, col)
    fit <- try(stats::lm(mm[, col] ~ mm[, others]), silent = TRUE)
    if (inherits(fit, "try-error")) next
    r2 <- summary(fit)$r.squared
    if (is.na(r2) || r2 >= 1) next
    result[[col]] <- 1 / (1 - r2)
  }
  result
}
coefs3 <- summary(m3)$coefficients
mark_model_divider <- function(row) {
  lapply(row, function(value) list(text = value, class = "tlt-cell--model-divider"))
}
full_model_rows <- function(model, model_label, prev_model = NULL, divider = FALSE) {
  coefs <- summary(model)$coefficients
  ci <- try(stats::confint(model), silent = TRUE)
  vifs <- vif_values(model)
  rows <- list()
  for (term in rownames(coefs)) {
    ci_low <- if (!inherits(ci, "try-error")) ci[term, 1] else NA_real_
    ci_high <- if (!inherits(ci, "try-error")) ci[term, 2] else NA_real_
    vif <- vifs[[term]]
    rows[[length(rows) + 1]] <- c(
      model_label,
      term_label(term),
      fmt_num(coefs[term, "Estimate"], 3),
      fmt_num(coefs[term, "Std. Error"], 3),
      coef_cells(model, term)[5],
      fmt_num(coefs[term, "t value"], 3),
      fmt_p(coefs[term, "Pr(>|t|)"]),
      fmt_ci(ci_low, ci_high),
      if (is.null(vif)) "\u2014" else fmt_num(vif, 3),
      if (is.null(vif)) "\u2014" else fmt_num(1 / vif, 3)
    )
  }
  if (divider && length(rows) > 0) rows[[1]] <- mark_model_divider(rows[[1]])
  rows[[length(rows) + 1]] <- c(model_label, "F\u68C0\u9A8C", "", "", "", model_f_text(model), "", "", "", "")
  rows[[length(rows) + 1]] <- c(model_label, "R\u65B9\u7B49", "", "", "", paste0("R\u00B2=", fmt_num(summary(model)$r.squared, 3), "\uFF0C\u8C03\u6574R\u00B2=", fmt_num(summary(model)$adj.r.squared, 3)), "", "", "", "")
  rows[[length(rows) + 1]] <- c(model_label, "\u25B3\u4FE1\u606F", "", "", "", paste0("\u25B3R\u00B2=", fmt_num(delta_r2(prev_model, model), 3), "\uFF0C\u25B3F=", delta_text(prev_model, model)), "", "", "", "")
  rows
}
full_rows <- c(
  full_model_rows(m1, "\u6A21\u578B1", NULL),
  full_model_rows(m2, "\u6A21\u578B2", m1, TRUE),
  full_model_rows(m3, "\u6A21\u578B3", m2, TRUE)
)

processing_rows <- list(
  c("\u56E0\u53D8\u91CF", y, "\u5B9A\u91CF", "\u4E0D\u5904\u7406"),
  c("\u81EA\u53D8\u91CF", x, if (x_is_cat) "\u5B9A\u7C7B" else "\u5B9A\u91CF", if (x_is_cat) "\u54D1\u53D8\u91CF" else data_process),
  c("\u8C03\u8282\u53D8\u91CF", w, if (w_is_cat) "\u5B9A\u7C7B" else "\u5B9A\u91CF", if (w_is_cat) "\u54D1\u53D8\u91CF" else data_process)
)
if (length(controls) > 0) {
  for (name in controls) processing_rows[[length(processing_rows) + 1]] <- c("\u63A7\u5236\u53D8\u91CF", name, "\u5B9A\u91CF", "\u4E0D\u5904\u7406")
}

predict_at <- function(x_value, w_value, x_level = NULL, w_level = NULL) {
  row <- data.frame(Y = 0, X = if (x_is_cat) factor(x_level, levels = levels(model_df$X)) else x_value, W = if (w_is_cat) factor(w_level, levels = levels(model_df$W)) else w_value)
  for (key in control_keys) row[[key]] <- mean(model_df[[key]], na.rm = TRUE)
  as.numeric(stats::predict(m3, newdata = row))
}
contrast <- function(row_a, row_b) {
  xmat <- stats::model.matrix(stats::delete.response(stats::terms(m3)), rbind(row_a, row_b))
  lvec <- xmat[2, ] - xmat[1, ]
  estimate <- sum(lvec * stats::coef(m3))
  variance <- as.numeric(t(lvec) %*% stats::vcov(m3) %*% lvec)
  se <- sqrt(max(variance, 0))
  t_value <- estimate / se
  p_value <- 2 * stats::pt(abs(t_value), df = stats::df.residual(m3), lower.tail = FALSE)
  crit <- stats::qt(0.975, df = stats::df.residual(m3))
  c(estimate, se, t_value, p_value, estimate - crit * se, estimate + crit * se)
}
make_new_row <- function(x_value = 0, w_value = 0, x_level = NULL, w_level = NULL) {
  row <- data.frame(Y = 0, X = if (x_is_cat) factor(x_level, levels = levels(model_df$X)) else x_value, W = if (w_is_cat) factor(w_level, levels = levels(model_df$W)) else w_value)
  for (key in control_keys) row[[key]] <- mean(model_df[[key]], na.rm = TRUE)
  row
}

simple_rows <- list()
simple_numeric <- list()
chart <- NULL
if (!x_is_cat) {
  x_mean <- mean(model_df$X)
  x_sd <- stats::sd(model_df$X)
  x_levels <- c("\u4F4E\u6C34\u5E73", "\u9AD8\u6C34\u5E73")
  x_values <- c(x_mean - x_sd, x_mean + x_sd)
  if (!w_is_cat) {
    w_mean <- mean(model_df$W)
    w_sd <- stats::sd(model_df$W)
    w_labels <- c("\u4F4E\u6C34\u5E73(-1SD)", "\u5E73\u5747\u6C34\u5E73", "\u9AD8\u6C34\u5E73(+1SD)")
    w_values <- c(w_mean - w_sd, w_mean, w_mean + w_sd)
    metrics <- list()
    for (idx in seq_along(w_labels)) {
      label <- w_labels[[idx]]
      w_value <- w_values[[idx]]
      c0 <- make_new_row(x_value = x_mean, w_value = w_value)
      c1 <- make_new_row(x_value = x_mean + 1, w_value = w_value)
      ct <- contrast(c0, c1)
      simple_rows[[length(simple_rows) + 1]] <- c(label, fmt_num(ct[1], 3), fmt_num(ct[2], 3), fmt_num(ct[3], 3), fmt_p(ct[4]), fmt_ci(ct[5], ct[6]))
      simple_numeric[[length(simple_numeric) + 1]] <- list(label = label, slope = ct[1], p = ct[4])
      metrics[[label]] <- c(predict_at(x_values[1], w_value), predict_at(x_values[2], w_value))
    }
    chart <- list(chartType = "metric_comparison", title = "\u7B80\u5355\u659C\u7387\u56FE", data = list(metric = y, labels = x_levels, values = metrics[[2]], metrics = metrics, multiSeries = TRUE, defaultMode = "line", displayTitle = "\u7B80\u5355\u659C\u7387\u56FE"))
  } else {
    metrics <- list()
    for (level in levels(model_df$W)) {
      c0 <- make_new_row(x_value = mean(model_df$X), w_level = level)
      c1 <- make_new_row(x_value = mean(model_df$X) + 1, w_level = level)
      ct <- contrast(c0, c1)
      simple_rows[[length(simple_rows) + 1]] <- c(paste0(w, "=", level), fmt_num(ct[1], 3), fmt_num(ct[2], 3), fmt_num(ct[3], 3), fmt_p(ct[4]), fmt_ci(ct[5], ct[6]))
      simple_numeric[[length(simple_numeric) + 1]] <- list(label = paste0(w, "=", level), slope = ct[1], p = ct[4])
      metrics[[paste0(w, "=", level)]] <- c(predict_at(x_values[1], 0, w_level = level), predict_at(x_values[2], 0, w_level = level))
    }
    chart <- list(chartType = "metric_comparison", title = "\u7B80\u5355\u659C\u7387\u56FE", data = list(metric = y, labels = x_levels, values = metrics[[1]], metrics = metrics, multiSeries = TRUE, defaultMode = "line", displayTitle = "\u7B80\u5355\u659C\u7387\u56FE"))
  }
} else {
  w_mean <- mean(model_df$W)
  w_sd <- stats::sd(model_df$W)
  w_labels <- c("\u4F4E\u6C34\u5E73(-1SD)", "\u5E73\u5747\u6C34\u5E73", "\u9AD8\u6C34\u5E73(+1SD)")
  w_values <- c(w_mean - w_sd, w_mean, w_mean + w_sd)
  metrics <- list()
  x_levels <- levels(model_df$X)
  for (idx in seq_along(w_labels)) {
    label <- w_labels[[idx]]
    w_value <- w_values[[idx]]
    metrics[[label]] <- sapply(x_levels, function(level) predict_at(0, w_value, x_level = level))
    simple_rows[[length(simple_rows) + 1]] <- c(label, paste(sapply(metrics[[label]], fmt_num, digits = 3), collapse = "\u3001"), "\u2014", "\u2014", "\u2014", "\u2014")
  }
  chart <- list(chartType = "metric_comparison", title = "\u7B80\u5355\u659C\u7387\u56FE", data = list(metric = y, labels = x_levels, values = metrics[[2]], metrics = metrics, multiSeries = TRUE, defaultMode = "line", displayTitle = "\u7B80\u5355\u659C\u7387\u56FE"))
}

interaction_terms <- rownames(coefs3)[grepl(":", rownames(coefs3), fixed = TRUE)]
interaction_ps <- sapply(interaction_terms, function(term) coefs3[term, "Pr(>|t|)"])
interaction_sig <- length(interaction_ps) > 0 && any(interaction_ps < 0.05, na.rm = TRUE)
delta_p <- stats::anova(m2, m3)$`Pr(>F)`[2]
interaction_names <- paste(unlist(lapply(interaction_terms, term_label)), collapse = "\u3001")
smart <- paste0(
  "\u8C03\u8282\u4F5C\u7528\u91C7\u7528\u5206\u5C42\u56DE\u5F52\u5B8C\u6210\uFF0C\u5171\u7EB3\u5165 ", nrow(model_df), " \u6761\u6709\u6548\u6837\u672C\u3002\u6A21\u578B1\u653E\u5165\u63A7\u5236\u53D8\u91CF\u548C\u81EA\u53D8\u91CF\uFF0C\u6A21\u578B2\u52A0\u5165\u8C03\u8282\u53D8\u91CF\uFF0C\u6A21\u578B3\u52A0\u5165\u4EA4\u4E92\u9879\u3002\u4EA4\u4E92\u9879 ",
  ifelse(interaction_names == "", paste0(x, "*", w), interaction_names),
  ifelse(interaction_sig, " \u8FBE\u5230\u663E\u8457", " \u672A\u8FBE\u5230\u663E\u8457"),
  "\uFF08\u6A21\u578B3\u76F8\u5BF9\u6A21\u578B2\uFF1A\u25B3R\u00B2=", fmt_num(delta_r2(m2, m3), 3), "\uFF0C\u25B3F\u68C0\u9A8Cp=", fmt_num(delta_p, 3), "\uFF09\u3002"
)

best_interaction <- if (length(interaction_terms) > 0) interaction_terms[[which.min(interaction_ps)]] else NA
best_interaction_label <- if (!is.na(best_interaction)) term_label(best_interaction) else paste0(x, "*", w)
best_interaction_b <- if (!is.na(best_interaction)) coefs3[best_interaction, "Estimate"] else NA_real_
best_interaction_p <- if (!is.na(best_interaction)) coefs3[best_interaction, "Pr(>|t|)"] else NA_real_
model_change_sig <- !is.na(delta_p) && delta_p < 0.05
moderation_supported <- interaction_sig && model_change_sig
result_interpretation <- paste(
  paste0("1. \u5148\u770B\u6A21\u578B\u53D8\u5316\uFF1A\u6A21\u578B3\u76F8\u6BD4\u6A21\u578B2\u7684\u25B3R\u00B2=", fmt_num(delta_r2(m2, m3), 3), "\uFF0C\u25B3F\u68C0\u9A8Cp=", fmt_num(delta_p, 3), ifelse(model_change_sig, "\uFF0C\u8BF4\u660E\u52A0\u5165\u4EA4\u4E92\u9879\u540E\u6A21\u578B\u89E3\u91CA\u529B\u663E\u8457\u63D0\u5347\u3002", "\uFF0C\u8BF4\u660E\u52A0\u5165\u4EA4\u4E92\u9879\u540E\u6A21\u578B\u89E3\u91CA\u529B\u6CA1\u6709\u663E\u8457\u63D0\u5347\u3002")),
  paste0("2. \u518D\u770B\u4EA4\u4E92\u9879\uFF1A", best_interaction_label, "\u7684\u7CFB\u6570B=", fmt_num(best_interaction_b, 3), "\uFF0Cp=", fmt_num(best_interaction_p, 3), ifelse(!is.na(best_interaction_p) && best_interaction_p < 0.05, "\uFF0C\u4EA4\u4E92\u9879\u663E\u8457\u3002", "\uFF0C\u4EA4\u4E92\u9879\u4E0D\u663E\u8457\u3002")),
  paste0("3. \u7ED3\u8BBA\uFF1A", ifelse(moderation_supported, paste0("\u672C\u6B21\u6570\u636E\u652F\u6301\u8C03\u8282\u6548\u5E94\u6210\u7ACB\uFF0C", w, "\u4F1A\u8C03\u8282", x, "\u5BF9", y, "\u7684\u5F71\u54CD\u3002"), paste0("\u672C\u6B21\u6570\u636E\u6682\u4E0D\u652F\u6301\u8C03\u8282\u6548\u5E94\u6210\u7ACB\uFF0C\u4E0D\u5EFA\u8BAE\u5C06", w, "\u89E3\u91CA\u4E3A", x, "\u4E0E", y, "\u4E4B\u95F4\u7684\u8C03\u8282\u53D8\u91CF\u3002"))),
  ifelse(moderation_supported, "4. \u89E3\u91CA\u65B9\u5411\u8981\u770B\u7B80\u5355\u659C\u7387\u8868\u548C\u7B80\u5355\u659C\u7387\u56FE\uFF1A\u4E0D\u540C\u8C03\u8282\u6C34\u5E73\u4E0B\u659C\u7387\u5DEE\u5F02\u8D8A\u660E\u663E\uFF0C\u8C03\u8282\u6548\u679C\u8D8A\u76F4\u89C2\u3002", "4. \u7B80\u5355\u659C\u7387\u56FE\u53EF\u4F5C\u4E3A\u8F85\u52A9\u89C2\u5BDF\uFF0C\u4F46\u4E0D\u8981\u5728\u4EA4\u4E92\u9879\u4E0D\u663E\u8457\u65F6\u8FC7\u5EA6\u89E3\u8BFB\u659C\u7387\u5DEE\u5F02\u3002"),
  sep = "\n"
)

if (length(simple_numeric) > 0) {
  slope_labels <- sapply(simple_numeric, function(item) item$label)
  slope_values <- sapply(simple_numeric, function(item) item$slope)
  slope_ps <- sapply(simple_numeric, function(item) item$p)
  sig_labels <- slope_labels[!is.na(slope_ps) & slope_ps < 0.05]
  strongest_index <- which.max(abs(slope_values))
  slope_interpretation <- paste(
    paste0("1. \u7B80\u5355\u659C\u7387\u7528\u6765\u770B\uFF1A\u5728\u4E0D\u540C", w, "\u6C34\u5E73\u4E0B\uFF0C", x, "\u5BF9", y, "\u7684\u5F71\u54CD\u662F\u5426\u4E00\u6837\u3002"),
    paste0("2. \u672C\u6B21\u7EDD\u5BF9\u659C\u7387\u6700\u5927\u7684\u6C34\u5E73\u662F\uFF1A", slope_labels[[strongest_index]], "\uFF08B=", fmt_num(slope_values[[strongest_index]], 3), "\uFF09\uFF0C\u8BF4\u660E\u8BE5\u6C34\u5E73\u4E0BX\u5BF9Y\u7684\u5F71\u54CD\u6700\u5F3A\u3002"),
    ifelse(length(sig_labels) > 0, paste0("3. \u5176\u4E2D", paste(sig_labels, collapse = "\u3001"), "\u7684\u7B80\u5355\u659C\u7387\u8FBE\u5230\u663E\u8457\uFF0C\u53EF\u4EE5\u91CD\u70B9\u89E3\u8BFB\u8FD9\u4E9B\u6C34\u5E73\u3002"), "3. \u5404\u6C34\u5E73\u7B80\u5355\u659C\u7387\u5747\u672A\u8FBE\u5230\u663E\u8457\uFF0C\u8BF4\u660E\u5206\u5C42\u540E\u7684X\u5BF9Y\u5F71\u54CD\u4ECD\u4E0D\u7A33\u5B9A\u3002"),
    sep = "\n"
  )
} else {
  slope_interpretation <- paste0("1. \u7B80\u5355\u659C\u7387\u56FE\u5C55\u793A\u4E0D\u540C", w, "\u6C34\u5E73\u4E0B", x, "\u5BF9", y, "\u7684\u9884\u6D4B\u503C\u53D8\u5316\u3002\n2. \u8BF7\u7ED3\u5408\u6A21\u578B3\u4EA4\u4E92\u9879\u662F\u5426\u663E\u8457\u6765\u5224\u65AD\u662F\u5426\u5B58\u5728\u8C03\u8282\u6548\u5E94\u3002")
}

advice <- paste(
  "\u8C03\u8282\u6548\u5E94\u7814\u7A76\u5171\u5206\u4E3A\u4E09\u4E2A\u6A21\u578B\uFF0C\u5206\u522B\u8BF4\u660E\u4E3A\uFF1A",
  "\u7B2C\u4E00\uFF1A\u6A21\u578B1\u5206\u6790\u81EA\u53D8\u91CFX\u5BF9\u4E8E\u56E0\u53D8\u91CFY\u7684\u5F71\u54CD\uFF0C\u63A7\u5236\u53D8\u91CF\u53EA\u7528\u4E8E\u6392\u9664\u5E72\u6270\uFF1B",
  "\u7B2C\u4E8C\uFF1A\u6A21\u578B2\u5728\u6A21\u578B1\u57FA\u7840\u4E0A\u52A0\u5165\u8C03\u8282\u53D8\u91CFW\uFF1B",
  "\u7B2C\u4E09\uFF1A\u6A21\u578B3\u5728\u6A21\u578B2\u57FA\u7840\u4E0A\u52A0\u5165X\u4E0EW\u7684\u4EA4\u4E92\u9879\uFF0C\u6838\u5FC3\u770B\u4EA4\u4E92\u9879\u53CA\u25B3F\u662F\u5426\u663E\u8457\uFF1B",
  "\u7B2C\u56DB\uFF1A\u5982\u679C\u4EA4\u4E92\u9879\u663E\u8457\uFF0C\u9700\u8981\u7ED3\u5408\u7B80\u5355\u659C\u7387\u8868\u548C\u7B80\u5355\u659C\u7387\u56FE\u89E3\u91CA\u4E0D\u540CW\u6C34\u5E73\u4E0BX\u5BF9Y\u7684\u5F71\u54CD\u3002",
  sep = "\n"
)

model_chart <- list(
  chartType = "model_path",
  title = "\u6A21\u578B\u7ED3\u679C\u56FE",
  data = list(
    target = y,
    nodes = c(unlist(control_labels), x, w, paste0(x, "*", w)),
    edges = lapply(c(setdiff(rownames(coefs3), "(Intercept)")), function(term) {
      p_value <- coefs3[term, "Pr(>|t|)"]
      list(label = term_label(term), value = paste0(fmt_num(coefs3[term, "Estimate"], 3), sig_mark(p_value)), p = fmt_num(p_value, 3), significant = !is.na(p_value) && p_value < 0.05)
    })
  )
)

sections <- list(
  sec_table("\u7814\u7A76\u53D8\u91CF\u5904\u7406\u8BF4\u660E", c("\u7C7B\u578B", "\u540D\u79F0", "\u6570\u636E\u7C7B\u578B", "\u6570\u636E\u5904\u7406"), processing_rows),
  sec_advice(advice),
  sec_table(
    paste0("\u8C03\u8282\u6548\u5E94\u5206\u6790\u7ED3\u679C (n=", nrow(model_df), ")"),
    c("\u9879", rep(c("B", "\u6807\u51C6\u8BEF", "t", "p", "\u03B2"), 3)),
    main_rows,
    note = paste0("\u5907\u6CE8\uFF1A\u56E0\u53D8\u91CF = ", y, "\uFF1B* p<0.1 ** p<0.05 *** p<0.01 **** p<0.001"),
    headerRows = header_rows
  ),
  sec_advice(result_interpretation, "\u7ED3\u679C\u89E3\u8BFB"),
  sec_smart(smart),
  sec_table("\u7B80\u5355\u659C\u7387\u8868", c("\u8C03\u8282\u53D8\u91CF\u6C34\u5E73", "\u56DE\u5F52\u7CFB\u6570", "\u6807\u51C6\u8BEF", "t", "p", "95% CI"), simple_rows),
  sec_advice(slope_interpretation, "\u7B80\u5355\u659C\u7387\u89E3\u8BFB"),
  sec_charts("简单斜率图", list(chart), "简单斜率图展示调节变量在不同水平时，自变量X对因变量Y的影响幅度差异。不同线条斜率差异越明显，说明调节变量改变X与Y关系的可能性越强；解释时应结合交互项p值和简单斜率表共同判断。"),
  sec_table("\u8C03\u8282\u4F5C\u7528\u5206\u6790\u7ED3\u679C\uFF08\u5B8C\u6574\u7ED3\u679C\uFF09", c("\u6A21\u578B", "\u9879", "B", "\u6807\u51C6\u8BEF", "\u03B2", "t", "p", "95% CI", "VIF", "\u5BB9\u5DEE"), full_rows, note = paste0("\u5907\u6CE8\uFF1A\u56E0\u53D8\u91CF = ", y, "\uFF1B\u62EC\u53F7\u661F\u53F7\u540C\u663E\u8457\u6027\u6C34\u5E73\u3002"), headerRows = full_header_rows),
  sec_charts("模型结果图", list(model_chart), "模型图基于模型3系数生成，箭头表示变量进入回归模型后的路径关系，路径标签显示对应系数和显著性标记；带星号的路径表示达到相应显著性水平。"),
  sec_refs(c(
    "[1] Hayes, A. F. Introduction to Mediation, Moderation, and Conditional Process Analysis.",
    "[2] \u6E29\u5FE0\u9E9F,\u4FAF\u6770\u6CF0,\u5F20\u96F7. \u8C03\u8282\u6548\u5E94\u4E0E\u4E2D\u4ECB\u6548\u5E94\u7684\u6BD4\u8F83\u548C\u5E94\u7528[J]. \u5FC3\u7406\u5B66\u62A5,2005(02):268-274."
  ))
)

result <- list(
  success = TRUE,
  name = paste0("\u8C03\u8282\u4F5C\u7528_", x, "_", y, "_", w),
  headers = c("\u9879", rep(c("B", "\u6807\u51C6\u8BEF", "t", "p", "\u03B2"), 3)),
  rows = main_rows,
  description = smart,
  sections = sections
)
cat(jsonlite::toJSON(result, auto_unbox = TRUE, null = "null", force = TRUE, dataframe = "rows", ascii = TRUE))
