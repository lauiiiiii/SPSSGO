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
  if (is.null(x) || length(x) == 0 || is.na(x) || is.infinite(x)) return("")
  if (abs(x - round(x)) < 1e-12) return(as.character(as.integer(round(x))))
  sprintf(paste0("%.", digits, "f"), x)
}
fmt_p <- function(p) {
  if (is.null(p) || length(p) == 0 || is.na(p) || is.infinite(p)) return("")
  if (p < 0.001) return("0.000")
  sprintf("%.3f", p)
}
pct_fmt <- function(value) {
  if (is.null(value) || length(value) == 0 || is.na(value) || is.infinite(value)) return("")
  paste0(sprintf("%.3f", value), "%")
}
sig_mark <- function(p) {
  if (is.null(p) || length(p) == 0 || is.na(p) || is.infinite(p)) return("")
  if (p < 0.001) return("****")
  if (p < 0.01) return("***")
  if (p < 0.05) return("**")
  if (p < 0.1) return("*")
  ""
}
fmt_coef <- function(value, p = NA_real_) paste0(fmt_num(value, 3), sig_mark(p))
fmt_ci <- function(low, high) paste0(fmt_num(low, 3), " ~ ", fmt_num(high, 3))
is_sig <- function(p) !is.null(p) && length(p) > 0 && !is.na(p) && is.finite(p) && p < 0.05
`%||%` <- function(a, b) if (is.null(a)) b else a

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
sec_charts <- function(title, charts) list(type = "charts", title = title, charts = charts)
sec_refs <- function(items) list(type = "references", title = "参考文献", items = items)
sanitize_json <- function(value) {
  if (is.list(value)) return(lapply(value, sanitize_json))
  if (is.atomic(value)) {
    if (is.logical(value)) {
      if (any(is.na(value))) value[is.na(value)] <- FALSE
      return(value)
    }
    missing <- is.na(value)
    if (!any(missing)) return(value)
    text <- as.character(value)
    text[missing] <- ""
    return(text)
  }
  value
}

as_chars <- function(value) {
  if (is.null(value)) return(character(0))
  result <- as.character(unlist(value, use.names = FALSE))
  result[nzchar(result)]
}
truthy <- function(value) {
  if (is.null(value)) return(FALSE)
  text <- tolower(as.character(value)[1])
  isTRUE(value) || text %in% c("1", "true", "yes", "on", "是")
}
auto_reps <- function(n) {
  if (n <= 500) return(5000L)
  if (n <= 2000) return(1000L)
  50L
}
parse_reps <- function(value, n) {
  if (is.null(value)) return(auto_reps(n))
  text <- as.character(value)[1]
  if (!nzchar(text) || text %in% c("auto", "default", "自动")) return(auto_reps(n))
  reps <- suppressWarnings(as.integer(text))
  if (!is.finite(reps) || reps < 50L) return(auto_reps(n))
  reps
}
parse_bootstrap_method <- function(value) {
  text <- tolower(as.character(value %||% "percentile")[1])
  if (text %in% c("bias_corrected", "bc", "偏差校正bootstrap法")) return("bias_corrected")
  "percentile"
}
parse_moderator_levels <- function(value) {
  text <- tolower(as.character(value %||% "mean_sd")[1])
  if (text %in% c("quantile", "quantiles", "分位数")) return("quantile")
  "mean_sd"
}
bootstrap_ci <- function(dist, estimate, method) {
  dist <- dist[is.finite(dist)]
  if (length(dist) < 20) return(c(NA_real_, NA_real_))
  if (method == "bias_corrected" && is.finite(estimate)) {
    prop <- mean(dist < estimate)
    prop <- min(max(prop, 1 / (2 * length(dist))), 1 - 1 / (2 * length(dist)))
    z0 <- stats::qnorm(prop)
    probs <- stats::pnorm(2 * z0 + stats::qnorm(c(0.025, 0.975)))
    probs <- c(min(max(probs[1], 0), 1), min(max(probs[2], 0), 1))
    if (length(probs) == 2 && all(is.finite(probs))) {
      return(as.numeric(stats::quantile(dist, probs, na.rm = TRUE, names = FALSE, type = 6)))
    }
  }
  as.numeric(stats::quantile(dist, c(0.025, 0.975), na.rm = TRUE, names = FALSE, type = 6))
}

input <- jsonlite::fromJSON(read_utf8(input_path), simplifyVector = FALSE)
input_dir <- dirname(normalizePath(input_path, winslash = "/", mustWork = TRUE))
data_file <- file.path(input_dir, input$data_file)
if (!file.exists(data_file)) stop("missing input data file")

x_label <- as_chars(input$x)[1]
y_label <- as_chars(input$y)[1]
z_label <- as_chars(input$z)[1]
mediator_labels <- as_chars(input$mediators)
control_labels <- as_chars(input$controls)
model <- gsub("^Model", "", as.character(input$model %||% "7")[1], ignore.case = TRUE)
paths <- input$moderated_paths %||% list()
moderate_x_m <- truthy(paths$x_m)
moderate_m_y <- truthy(paths$m_y)
moderate_x_y <- truthy(paths$x_y)
bootstrap_method <- parse_bootstrap_method(input$bootstrap_method)
bootstrap_method_label <- if (bootstrap_method == "bias_corrected") "偏差校正bootstrap法" else "百分位bootstrap法"
moderator_levels_method <- parse_moderator_levels(input$moderator_levels)

raw_df <- read.csv(data_file, stringsAsFactors = FALSE, check.names = FALSE)
variables <- unique(c(x_label, y_label, z_label, mediator_labels, control_labels))
missing_cols <- setdiff(variables, colnames(raw_df))
if (length(missing_cols) > 0) {
  cat(jsonlite::toJSON(list(success = FALSE, error = paste0("以下变量不存在：", paste(missing_cols, collapse = "，"))), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

mediator_labels <- mediator_labels[order(match(mediator_labels, colnames(raw_df)))]
control_labels <- control_labels[order(match(control_labels, colnames(raw_df)))]
variables <- unique(c(x_label, y_label, z_label, mediator_labels, control_labels))
data <- raw_df[, variables, drop = FALSE]
for (col in variables) data[[col]] <- suppressWarnings(as.numeric(data[[col]]))
valid_mask <- stats::complete.cases(data)
valid_n <- sum(valid_mask)
invalid_n <- nrow(data) - valid_n
data <- data[valid_mask, , drop = FALSE]
if (nrow(data) < max(10, length(variables) + 2)) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "调节中介有效样本不足。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}
bootstrap_reps <- parse_reps(input$bootstrap_reps, nrow(data))

safe_names <- paste0("v", seq_along(variables))
names(safe_names) <- variables
safe_df <- data
colnames(safe_df) <- unname(safe_names[colnames(data)])
x <- safe_names[[x_label]]
y <- safe_names[[y_label]]
z <- safe_names[[z_label]]
mediators <- unname(safe_names[mediator_labels])
controls <- unname(safe_names[control_labels])
xz <- paste0(x, "_x_", z)
safe_df[[xz]] <- safe_df[[x]] * safe_df[[z]]
for (m in mediators) safe_df[[paste0(m, "_x_", z)]] <- safe_df[[m]] * safe_df[[z]]

z_mean <- mean(safe_df[[z]], na.rm = TRUE)
z_sd <- stats::sd(safe_df[[z]], na.rm = TRUE)
if (!is.finite(z_sd) || z_sd == 0) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "调节变量 Z 在有效样本中没有变异，无法进行调节中介。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}
if (moderator_levels_method == "quantile") {
  z_quantiles <- as.numeric(stats::quantile(safe_df[[z]], probs = c(0.25, 0.5, 0.75), na.rm = TRUE, names = FALSE, type = 7))
  z_levels <- list(
    list(key = "low", label = paste0("低分位(P25)：", fmt_num(z_quantiles[1], 3)), value = z_quantiles[1]),
    list(key = "mean", label = paste0("中位数(P50)：", fmt_num(z_quantiles[2], 3)), value = z_quantiles[2]),
    list(key = "high", label = paste0("高分位(P75)：", fmt_num(z_quantiles[3], 3)), value = z_quantiles[3])
  )
} else {
  z_levels <- list(
    list(key = "low", label = paste0("低水平(-1SD)：", fmt_num(z_mean - z_sd, 3)), value = z_mean - z_sd),
    list(key = "mean", label = paste0("平均值：", fmt_num(z_mean, 3)), value = z_mean),
    list(key = "high", label = paste0("高水平(+1SD)：", fmt_num(z_mean + z_sd, 3)), value = z_mean + z_sd)
  )
}

make_formula <- function(response, predictors) stats::reformulate(predictors, response = response)
mediator_predictors <- function() c(x, if (moderate_x_m) c(z, xz) else character(0), controls)
outcome_predictors <- function() c(
  x,
  mediators,
  if (moderate_x_y || moderate_m_y) z else character(0),
  if (moderate_x_y) xz else character(0),
  if (moderate_m_y) paste0(mediators, "_x_", z) else character(0),
  controls
)
fit_all <- function(frame) {
  med_models <- lapply(mediators, function(m) stats::lm(make_formula(m, mediator_predictors()), data = frame))
  out_model <- stats::lm(make_formula(y, outcome_predictors()), data = frame)
  list(mediators = med_models, outcome = out_model)
}
coef_value <- function(model, term) {
  if (!term %in% names(stats::coef(model))) return(NA_real_)
  value <- stats::coef(model)[[term]]
  if (is.null(value) || !is.finite(value)) return(NA_real_)
  value
}
coef_p <- function(model, term) {
  table <- coef(summary(model))
  if (!term %in% rownames(table)) return(NA_real_)
  table[term, "Pr(>|t|)"]
}
coef_se <- function(model, term) {
  table <- coef(summary(model))
  if (!term %in% rownames(table)) return(NA_real_)
  table[term, "Std. Error"]
}
coef_t <- function(model, term) {
  table <- coef(summary(model))
  if (!term %in% rownames(table)) return(NA_real_)
  table[term, "t value"]
}
beta_value <- function(model, term) {
  if (term == "(Intercept)") return(NA_real_)
  mf <- stats::model.frame(model)
  response <- names(mf)[1]
  if (!term %in% names(mf)) return(NA_real_)
  y_sd <- stats::sd(mf[[response]], na.rm = TRUE)
  x_sd <- stats::sd(mf[[term]], na.rm = TRUE)
  if (!is.finite(y_sd) || !is.finite(x_sd) || y_sd == 0) return(NA_real_)
  coef_value(model, term) * x_sd / y_sd
}
model_f <- function(model) {
  f <- summary(model)$fstatistic
  if (is.null(f)) return("")
  p <- stats::pf(f[["value"]], f[["numdf"]], f[["dendf"]], lower.tail = FALSE)
  paste0("F(", as.integer(f[["numdf"]]), ",", as.integer(f[["dendf"]]), ")=", fmt_num(f[["value"]], 3), ", p=", fmt_p(p))
}
equation_term <- function(term, value, is_first = FALSE) {
  if (!is.finite(value)) return("")
  if (term == "(Intercept)") return(fmt_num(value, 3))
  sign_text <- if (value < 0) "-" else if (is_first) "" else "+"
  paste0(sign_text, fmt_num(abs(value), 3), "*", label_for(term))
}
equation_for_model <- function(title, model_obj, terms_order = names(stats::coef(model_obj))) {
  terms <- terms_order[terms_order %in% names(stats::coef(model_obj))]
  terms <- unique(c("(Intercept)", terms[terms != "(Intercept)"]))
  parts <- character(0)
  for (term in terms) {
    value <- coef_value(model_obj, term)
    piece <- equation_term(term, value, length(parts) == 0)
    if (nzchar(piece)) parts <- c(parts, piece)
  }
  paste0(title, "=", paste(parts, collapse = ""))
}

fits <- fit_all(safe_df)
all_models <- c(list(fits$outcome), fits$mediators)
model_titles <- c(y_label, mediator_labels)
label_for <- function(term) {
  if (term == "(Intercept)") return("常数")
  if (term == x) return(x_label)
  if (term == y) return(y_label)
  if (term == z) return(z_label)
  if (term == xz) return(paste0(x_label, "*", z_label))
  for (i in seq_along(mediators)) {
    if (term == mediators[i]) return(mediator_labels[i])
    if (term == paste0(mediators[i], "_x_", z)) return(paste0(mediator_labels[i], "*", z_label))
  }
  for (i in seq_along(controls)) if (term == controls[i]) return(control_labels[i])
  term
}

direct_effect <- function(fits, z_value) {
  effect <- coef_value(fits$outcome, x)
  if (moderate_x_y) effect <- effect + coef_value(fits$outcome, xz) * z_value
  effect
}
direct_effect_stat <- function(fits, z_value) {
  model_obj <- fits$outcome
  effect <- direct_effect(fits, z_value)
  cov_mat <- tryCatch(stats::vcov(model_obj), error = function(e) NULL)
  se <- coef_se(model_obj, x)
  if (moderate_x_y && !is.null(cov_mat) && x %in% rownames(cov_mat) && xz %in% rownames(cov_mat)) {
    variance <- cov_mat[x, x] + z_value * z_value * cov_mat[xz, xz] + 2 * z_value * cov_mat[x, xz]
    se <- if (is.finite(variance) && variance >= 0) sqrt(variance) else NA_real_
  }
  t_value <- if (!is.na(se) && se > 0) effect / se else NA_real_
  df <- stats::df.residual(model_obj)
  p_value <- if (!is.na(t_value) && is.finite(df) && df > 0) 2 * stats::pt(-abs(t_value), df = df) else NA_real_
  t_crit <- if (is.finite(df) && df > 0) stats::qt(0.975, df = df) else NA_real_
  list(
    est = effect,
    se = se,
    t = t_value,
    p = p_value,
    lower = if (!is.na(t_crit) && !is.na(se)) effect - t_crit * se else NA_real_,
    upper = if (!is.na(t_crit) && !is.na(se)) effect + t_crit * se else NA_real_
  )
}
indirect_effect <- function(fits, mediator_index, z_value) {
  a <- coef_value(fits$mediators[[mediator_index]], x)
  if (moderate_x_m) a <- a + coef_value(fits$mediators[[mediator_index]], xz) * z_value
  b <- coef_value(fits$outcome, mediators[mediator_index])
  if (moderate_m_y) b <- b + coef_value(fits$outcome, paste0(mediators[mediator_index], "_x_", z)) * z_value
  a * b
}
total_indirect_effect <- function(fits, z_value) {
  values <- vapply(seq_along(mediators), function(index) indirect_effect(fits, index, z_value), numeric(1))
  sum(values, na.rm = TRUE)
}
has_conditional_direct <- moderate_x_y
has_conditional_indirect <- moderate_x_m || moderate_m_y
effect_keys <- c("ind_total_avg")
for (m_index in seq_along(mediators)) effect_keys <- c(effect_keys, paste0("ind_m", m_index, "_avg"))
if (has_conditional_indirect) {
  for (m_index in seq_along(mediators)) {
    for (level in z_levels) effect_keys <- c(effect_keys, paste0("ind_m", m_index, "_", level$key))
  }
}

build_design_matrix <- function(predictors, frame) {
  if (length(predictors) > 0) {
    matrix_x <- cbind(`(Intercept)` = 1, as.matrix(frame[, predictors, drop = FALSE]))
  } else {
    matrix_x <- matrix(1, nrow = nrow(frame), ncol = 1)
    colnames(matrix_x) <- "(Intercept)"
  }
  matrix_x
}
fast_mediator_predictors <- mediator_predictors()
fast_outcome_predictors <- outcome_predictors()
fast_designs <- list(
  mediators = lapply(mediators, function(m) build_design_matrix(fast_mediator_predictors, safe_df)),
  outcome = build_design_matrix(fast_outcome_predictors, safe_df)
)
fast_responses <- list(
  mediators = lapply(mediators, function(m) safe_df[[m]]),
  outcome = safe_df[[y]]
)
fast_coef_from_matrix <- function(matrix_x, response_y, index = NULL) {
  if (is.null(index)) index <- seq_len(nrow(matrix_x))
  fit <- stats::lm.fit(matrix_x[index, , drop = FALSE], response_y[index])
  coefs <- fit$coefficients
  names(coefs) <- colnames(matrix_x)
  coefs[!is.finite(coefs)] <- NA_real_
  coefs
}
fast_fit_all <- function(index = NULL) {
  list(
    mediators = lapply(seq_along(mediators), function(i) fast_coef_from_matrix(fast_designs$mediators[[i]], fast_responses$mediators[[i]], index)),
    outcome = fast_coef_from_matrix(fast_designs$outcome, fast_responses$outcome, index)
  )
}
coef_fast <- function(coefs, term) {
  if (!term %in% names(coefs)) return(NA_real_)
  value <- coefs[[term]]
  if (is.null(value) || !is.finite(value)) return(NA_real_)
  value
}
direct_effect_fast <- function(fast_fit, z_value) {
  effect <- coef_fast(fast_fit$outcome, x)
  if (moderate_x_y) effect <- effect + coef_fast(fast_fit$outcome, xz) * z_value
  effect
}
indirect_effect_fast <- function(fast_fit, mediator_index, z_value) {
  a <- coef_fast(fast_fit$mediators[[mediator_index]], x)
  if (moderate_x_m) a <- a + coef_fast(fast_fit$mediators[[mediator_index]], xz) * z_value
  b <- coef_fast(fast_fit$outcome, mediators[mediator_index])
  if (moderate_m_y) b <- b + coef_fast(fast_fit$outcome, paste0(mediators[mediator_index], "_x_", z)) * z_value
  a * b
}
compute_effects_fast <- function(fast_fit) {
  values <- rep(NA_real_, length(effect_keys))
  names(values) <- effect_keys
  values["ind_total_avg"] <- sum(vapply(seq_along(mediators), function(index) indirect_effect_fast(fast_fit, index, z_mean), numeric(1)), na.rm = TRUE)
  for (m_index in seq_along(mediators)) values[paste0("ind_m", m_index, "_avg")] <- indirect_effect_fast(fast_fit, m_index, z_mean)
  if (has_conditional_indirect) {
    for (m_index in seq_along(mediators)) {
      for (level in z_levels) values[paste0("ind_m", m_index, "_", level$key)] <- indirect_effect_fast(fast_fit, m_index, level$value)
    }
  }
  values
}
observed_effects <- compute_effects_fast(fast_fit_all())

set.seed(42)
bootstrap_effects <- matrix(NA_real_, nrow = bootstrap_reps, ncol = length(effect_keys))
colnames(bootstrap_effects) <- effect_keys
for (rep_index in seq_len(bootstrap_reps)) {
  sample_index <- sample.int(nrow(safe_df), nrow(safe_df), replace = TRUE)
  values <- tryCatch(compute_effects_fast(fast_fit_all(sample_index)), error = function(e) NULL)
  if (!is.null(values)) bootstrap_effects[rep_index, names(values)] <- values
}
effect_stats <- function(key) {
  effect <- observed_effects[[key]]
  dist <- bootstrap_effects[, key]
  dist <- dist[is.finite(dist)]
  se <- stats::sd(dist, na.rm = TRUE)
  ci <- bootstrap_ci(dist, effect, bootstrap_method)
  z_value <- if (!is.na(se) && se > 0) effect / se else NA_real_
  p_value <- if (!is.na(z_value)) 2 * stats::pnorm(-abs(z_value)) else NA_real_
  list(est = effect, se = se, z = z_value, p = p_value, lower = ci[1], upper = ci[2])
}

row_terms <- unique(c(
  "(Intercept)",
  x,
  if (moderate_x_m || moderate_x_y || moderate_m_y) z else character(0),
  if (moderate_x_m || moderate_x_y) xz else character(0),
  mediators,
  if (moderate_m_y) paste0(mediators, "_x_", z) else character(0),
  controls
))
reg_headers <- c("项", rep(c("β", "SE", "t值", "p值"), length(all_models)))
reg_header_rows <- list(
  c(list(list(text = "项", rowspan = 2L)), lapply(model_titles, function(title) list(text = title, colspan = 4L))),
  rep(list("β", "SE", "t值", "p值"), length(all_models))
)
regression_rows <- list()
for (term in row_terms) {
  row <- c(label_for(term))
  for (model_obj in all_models) {
    p <- coef_p(model_obj, term)
    row <- c(row, fmt_coef(coef_value(model_obj, term), p), fmt_num(coef_se(model_obj, term), 3), fmt_num(coef_t(model_obj, term), 3), paste0(fmt_p(p), sig_mark(p)))
  }
  regression_rows[[length(regression_rows) + 1]] <- row
}
regression_rows[[length(regression_rows) + 1]] <- c("样本量", unlist(lapply(all_models, function(model_obj) c(as.character(nobs(model_obj)), "", "", ""))))
regression_rows[[length(regression_rows) + 1]] <- c("R²", unlist(lapply(all_models, function(model_obj) c(fmt_num(summary(model_obj)$r.squared, 3), "", "", ""))))
regression_rows[[length(regression_rows) + 1]] <- c("调整R²", unlist(lapply(all_models, function(model_obj) c(fmt_num(summary(model_obj)$adj.r.squared, 3), "", "", ""))))
regression_rows[[length(regression_rows) + 1]] <- c("F值", unlist(lapply(all_models, function(model_obj) c(model_f(model_obj), "", "", ""))))

direct_rows <- list()
level_title <- function(level) sub("：.*$", "", level$label)
level_value_text <- function(level) fmt_num(level$value, 3)
if (has_conditional_direct) {
  for (level in z_levels) {
    stat <- direct_effect_stat(fits, level$value)
    direct_rows[[length(direct_rows) + 1]] <- c(level_title(level), level_value_text(level), fmt_num(stat$est, 3), fmt_num(stat$se, 3), fmt_num(stat$t, 3), fmt_p(stat$p), fmt_num(stat$lower, 3), fmt_num(stat$upper, 3))
  }
} else {
  stat <- direct_effect_stat(fits, z_mean)
  direct_rows[[length(direct_rows) + 1]] <- c("平均值", fmt_num(z_mean, 3), fmt_num(stat$est, 3), fmt_num(stat$se, 3), fmt_num(stat$t, 3), fmt_p(stat$p), fmt_num(stat$lower, 3), fmt_num(stat$upper, 3))
}

indirect_rows <- list()
total_indirect <- effect_stats("ind_total_avg")
indirect_rows[[length(indirect_rows) + 1]] <- c("Total", fmt_num(total_indirect$est, 3), fmt_num(total_indirect$se, 3), fmt_num(total_indirect$lower, 3), fmt_num(total_indirect$upper, 3))
for (m_index in seq_along(mediators)) {
  stat <- effect_stats(paste0("ind_m", m_index, "_avg"))
  indirect_rows[[length(indirect_rows) + 1]] <- c(mediator_labels[m_index], fmt_num(stat$est, 3), fmt_num(stat$se, 3), fmt_num(stat$lower, 3), fmt_num(stat$upper, 3))
}

conditional_rows <- list()
conditional_text <- c()
if (has_conditional_indirect) {
  for (m_index in seq_along(mediators)) {
    level_sigs <- c()
    for (level in z_levels) {
      key <- paste0("ind_m", m_index, "_", level$key)
      stat <- effect_stats(key)
      sig <- !is.na(stat$lower) && !is.na(stat$upper) && ((stat$lower > 0 && stat$upper > 0) || (stat$lower < 0 && stat$upper < 0))
      level_sigs <- c(level_sigs, sig)
      conditional_rows[[length(conditional_rows) + 1]] <- c(
        mediator_labels[m_index],
        level$label,
        fmt_num(stat$est, 3),
        fmt_num(stat$se, 3),
        fmt_num(stat$lower, 3),
        fmt_num(stat$upper, 3)
      )
      conditional_text <- c(conditional_text, paste0(
        "针对", x_label, "->", mediator_labels[m_index], "->", y_label, "路径，在", z_label, "取", level$label,
        "时，Bootstrap 95%CI为", fmt_num(stat$lower, 3), "~", fmt_num(stat$upper, 3),
        if (sig) "，不包括0，说明该水平下中介效应存在。" else "，包括0，说明该水平下中介效应不显著。"
      ))
    }
    if (length(unique(level_sigs)) > 1) {
      conditional_text <- c(conditional_text, paste0("综合可知，", mediator_labels[m_index], "在不同", z_label, "水平下的中介作用显著性并不一致，提示存在调节中介作用。"))
    }
  }
}

simplified_rows <- list()
for (term in row_terms) {
  row <- c(label_for(term))
  for (model_obj in all_models) {
    p <- coef_p(model_obj, term)
    cell <- if (term %in% names(coef(model_obj))) paste0(fmt_coef(coef_value(model_obj, term), p), "\n(", fmt_num(coef_t(model_obj, term), 3), ")") else ""
    row <- c(row, cell)
  }
  simplified_rows[[length(simplified_rows) + 1]] <- row
}
simplified_rows[[length(simplified_rows) + 1]] <- c("样本量", rep(as.character(valid_n), length(all_models)))
simplified_rows[[length(simplified_rows) + 1]] <- c("R²", unlist(lapply(all_models, function(model_obj) fmt_num(summary(model_obj)$r.squared, 3))))
simplified_rows[[length(simplified_rows) + 1]] <- c("调整R²", unlist(lapply(all_models, function(model_obj) fmt_num(summary(model_obj)$adj.r.squared, 3))))
simplified_rows[[length(simplified_rows) + 1]] <- c("F值", unlist(lapply(all_models, model_f)))

path_desc <- paste(c(
  if (moderate_x_m) paste0(z_label, "调节", x_label, "->M") else NULL,
  if (moderate_m_y) paste0(z_label, "调节M->", y_label) else NULL,
  if (moderate_x_y) paste0(z_label, "调节", x_label, "->", y_label) else NULL
), collapse = "，")
note_sig <- "备注：* p<0.1 ** p<0.05 *** p<0.01 **** p<0.001"
note_simplified <- "备注：* p<0.1 ** p<0.05 *** p<0.01 **** p<0.001 括号里面为t值"
note_boot <- paste0("备注：BootLLCI指Bootstrap抽样95%区间下限，BootULCI指Bootstrap抽样95%区间上限，bootstrap类型：", bootstrap_method_label)
moderator_levels_label <- if (moderator_levels_method == "quantile") "P25、P50、P75分位数" else "低水平(-1SD)、平均值、高水平(+1SD)"
equations <- vapply(seq_along(all_models), function(index) equation_for_model(model_titles[index], all_models[[index]], row_terms), character(1))
smart <- paste(c(
  "从上表可知：调节中介效应分析共涉及多个模型，分别如下：",
  equations
), collapse = "\n")
regression_advice <- paste(c(
  "调节中介效应模型共分为两类回归模型；",
  "第一：第1类回归模型为因变量Y时的回归模型构建；",
  "第二：第2类回归模型为因变量为中介变量M的回归模型构建（如果多个中介变量则多个模型）；",
  "第三：调节中介效应模型有多个，具体请参阅帮助手册。"
), collapse = "\n")
chart_w <- 840
chart_h <- max(330, 170 + length(mediators) * 70)
mid_y <- chart_h / 2 - 19
m_top <- max(110, mid_y - (length(mediators) - 1) * 42)
nodes <- list(
  list(key = "x", label = x_label, x = 70, y = mid_y),
  list(key = "z", label = z_label, x = 370, y = 42)
)
for (m_index in seq_along(mediators)) {
  nodes[[length(nodes) + 1]] <- list(key = paste0("m", m_index), label = mediator_labels[m_index], x = 340, y = m_top + (m_index - 1) * 84)
}
nodes[[length(nodes) + 1]] <- list(key = "y", label = y_label, x = 680, y = mid_y)
path_edges <- list()
for (m_index in seq_along(mediators)) {
  m_key <- paste0("m", m_index)
  a_p <- coef_p(fits$mediators[[m_index]], x)
  b_p <- coef_p(fits$outcome, mediators[m_index])
  path_edges[[length(path_edges) + 1]] <- list(
    from = "x",
    to = m_key,
    value = fmt_coef(coef_value(fits$mediators[[m_index]], x), a_p),
    significant = is_sig(a_p)
  )
  path_edges[[length(path_edges) + 1]] <- list(
    from = m_key,
    to = "y",
    value = fmt_coef(coef_value(fits$outcome, mediators[m_index]), b_p),
    significant = is_sig(b_p)
  )
  if (moderate_x_m) {
    xz_p <- coef_p(fits$mediators[[m_index]], xz)
    path_edges[[length(path_edges) + 1]] <- list(
      from = "z",
      to = m_key,
      value = paste0(label_for(xz), " ", fmt_coef(coef_value(fits$mediators[[m_index]], xz), xz_p)),
      significant = is_sig(xz_p)
    )
  }
  if (moderate_m_y) {
    mz <- paste0(mediators[m_index], "_x_", z)
    mz_p <- coef_p(fits$outcome, mz)
    path_edges[[length(path_edges) + 1]] <- list(
      from = "z",
      to = "y",
      value = paste0(label_for(mz), " ", fmt_coef(coef_value(fits$outcome, mz), mz_p)),
      significant = is_sig(mz_p),
      labelY = m_top + (m_index - 1) * 34 + 16
    )
  }
}
xy_p <- coef_p(fits$outcome, x)
path_edges[[length(path_edges) + 1]] <- list(
  from = "x",
  to = "y",
  value = fmt_coef(coef_value(fits$outcome, x), xy_p),
  significant = is_sig(xy_p),
  labelY = mid_y + 44
)
if (moderate_x_y) {
  xy_z_p <- coef_p(fits$outcome, xz)
  path_edges[[length(path_edges) + 1]] <- list(
    from = "z",
    to = "y",
    value = paste0(label_for(xz), " ", fmt_coef(coef_value(fits$outcome, xz), xy_z_p)),
    significant = is_sig(xy_z_p),
    labelY = 96
  )
}
path_chart <- list(
  chartType = "model_path",
  title = "模型图",
  data = list(width = chart_w, height = chart_h, target = y_label, nodes = nodes, edges = path_edges, defaultShowDataLabels = TRUE, defaultShowSignificantOnly = FALSE)
)
missing_rows <- list(
  c("有效样本", as.character(valid_n), pct_fmt(if (nrow(raw_df) > 0) valid_n / nrow(raw_df) * 100 else NA_real_)),
  c("排除无效样本", as.character(invalid_n), pct_fmt(if (nrow(raw_df) > 0) invalid_n / nrow(raw_df) * 100 else NA_real_)),
  c("总计", as.character(nrow(raw_df)), "100%")
)
missing_advice <- paste(c(
  "上表格展示算法模型时有效样本和排除在外的无效样本情况等。",
  "第一：上表格中有效样本指所有分析项均有数据的样本总数，排除无效样本指任意一个分析项出现缺失的样本总数；",
  "第二：如果某样本在任意一个分析项上出现缺失数据（即排除无效样本），该类样本无法进入模型分析，模型只能针对有效样本进行分析；",
  "第三：可通过通用方法里面的描述分析检查各分析项样本情况，也可在右上角查看数据查看具体数据。"
), collapse = "\n")
indirect_smart <- paste(c(
  paste0("针对", y_label, "总中介效应，模型boot 95% CI", if (!is.na(total_indirect$lower) && !is.na(total_indirect$upper) && ((total_indirect$lower > 0 && total_indirect$upper > 0) || (total_indirect$lower < 0 && total_indirect$upper < 0))) "并不包括数字0，意味着具有中介作用。" else "包括数字0，意味着不具有中介作用。"),
  vapply(seq_along(mediators), function(index) {
    stat <- effect_stats(paste0("ind_m", index, "_avg"))
    paste0("针对", mediator_labels[index], "这一中介变量，模型boot 95% CI", if (!is.na(stat$lower) && !is.na(stat$upper) && ((stat$lower > 0 && stat$upper > 0) || (stat$lower < 0 && stat$upper < 0))) "并不包括数字0，意味着具有中介作用。" else "包括数字0，意味着不具有中介作用。")
  }, character(1))
), collapse = "\n")

sections <- list(
  sec_table("回归模型汇总表格", reg_headers, regression_rows, "上表将调节中介涉及的回归模型结果全部列出。", note_sig, headerRows = reg_header_rows, tableClass = "tlt--spssau"),
  sec_advice(regression_advice),
  sec_smart(smart),
  sec_charts("模型图", list(path_chart))
)
sections[[length(sections) + 1]] <- sec_table(
  if (has_conditional_direct) "条件直接效应（Conditional Direct Effect）结果" else "直接效应（Direct Effect）结果",
  c("水平", "水平值", "Effect", "SE", "t值", "p值", "LLCI", "ULCI"),
  direct_rows,
  if (has_conditional_direct) "条件直接效应表示调节变量在不同水平时，X对于Y的效应情况。" else "直接效应表示X对于Y的效应情况。",
  "备注：LLCI指估计值95%区间下限，ULCI指估计值95%区间上限。",
  tableClass = "tlt--spssau"
)
sections[[length(sections) + 1]] <- sec_advice(
  if (has_conditional_direct) {
    "直接效应/条件直接效应为X对于Y的效应情况；如果某项的p值小于0.05，则说明呈现出显著性。"
  } else {
    "直接效应为X对于Y的效应情况；如果p值小于0.05，则说明呈现出显著性。"
  }
)
if (has_conditional_indirect) {
  sections[[length(sections) + 1]] <- sec_table("条件间接效应（Conditional Indirect Effect）结果", c("中介变量", paste0(z_label, "水平"), "Effect", "BootSE", "BootLLCI", "BootULCI"), conditional_rows, "该表为调节中介的核心表格，展示调节变量在不同水平时的间接效应。", note_boot, tableClass = "tlt--spssau")
  sections[[length(sections) + 1]] <- sec_advice("如果某一水平下 Bootstrap 95%CI 不包括0，说明该水平下存在中介效应；不同水平下显著性或方向不同，可作为调节中介存在的证据。")
  sections[[length(sections) + 1]] <- sec_smart(paste(conditional_text, collapse = "\n"))
} else {
  sections[[length(sections) + 1]] <- sec_table("间接效应（Indirect Effect）结果", c("项", "Effect", "BootSE", "BootLLCI", "BootULCI"), indirect_rows, "间接效应为中介效应分析结果。", note_boot, tableClass = "tlt--spssau")
  sections[[length(sections) + 1]] <- sec_advice("如果间接效应值的95%区间(BootCI)值不包括数字0，则说明具有中介效应；如果包括数字0，则说明不具有中介效应。")
  sections[[length(sections) + 1]] <- sec_smart(indirect_smart)
}
sections[[length(sections) + 1]] <- sec_table("回归模型汇总表格-简化格式", c("项", model_titles), simplified_rows, "上表为回归模型汇总表格的横向简化格式，括号中为t值。", note_simplified, tableClass = "tlt--spssau")
sections[[length(sections) + 1]] <- sec_table("样本缺失情况汇总", c("项", "样本数", "占比"), missing_rows, NULL, NULL, tableClass = "tlt--spssau")
sections[[length(sections) + 1]] <- sec_advice(missing_advice)
sections[[length(sections) + 1]] <- sec_refs(c(
  "[1] 温忠麟, 张雷, 侯杰泰. (2006). 有中介的调节变量和有调节的中介变量. 心理学报, 38(3), 448-452.",
  "[2] 方杰, 张敏强, 顾红磊, 梁东梅. (2014). 基于不对称区间估计的有调节的中介模型检验. 心理科学进展, 22(10), 1660-1668.",
  "[3] Preacher, K. J., Rucker, D. D., & Hayes, A. F. (2007). Addressing moderated mediation hypotheses: Theory, methods, and prescriptions. Multivariate Behavioral Research, 42(1), 185-227.",
  "[4] Hayes, A. F. (2015). An index and test of linear moderated mediation. Multivariate Behavioral Research, 50(1), 1-22."
))

result <- list(
  success = TRUE,
  name = "调节中介",
  headers = if (has_conditional_indirect) c("中介变量", "Z水平", "Effect", "BootSE", "BootLLCI", "BootULCI") else c("项", "Effect", "BootSE", "BootLLCI", "BootULCI"),
  rows = if (has_conditional_indirect) conditional_rows else indirect_rows,
  description = smart,
  sections = sections
)
cat(jsonlite::toJSON(sanitize_json(result), auto_unbox = TRUE, null = "null", force = TRUE, dataframe = "rows"))
