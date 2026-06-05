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
sig_bool <- function(p) !is.na(p) && is.finite(p) && p < 0.05
same_sign <- function(a, b) !is.na(a) && !is.na(b) && is.finite(a) && is.finite(b) && a * b > 0
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
parse_reps <- function(value) {
  if (is.null(value)) return(1000L)
  text <- as.character(value)[1]
  if (!nzchar(text) || text %in% c("auto", "default", "自动")) return(1000L)
  reps <- suppressWarnings(as.integer(text))
  if (!is.finite(reps) || reps < 100L) return(1000L)
  reps
}
is_auto_reps <- function(value) {
  if (is.null(value)) return(TRUE)
  text <- as.character(value)[1]
  !nzchar(text) || text %in% c("auto", "default", "自动")
}
parse_bootstrap_enabled <- function(value) {
  if (is.null(value)) return(TRUE)
  text <- tolower(as.character(value)[1])
  !(isFALSE(value) || text %in% c("false", "0", "no", "off"))
}
parse_bootstrap_method <- function(value) {
  text <- tolower(as.character(value %||% "percentile")[1])
  if (text %in% c("bias_corrected", "bc", "偏差校正bootstrap法")) return("bias_corrected")
  "percentile"
}

input <- jsonlite::fromJSON(read_utf8(input_path), simplifyVector = FALSE)
input_dir <- dirname(normalizePath(input_path, winslash = "/", mustWork = TRUE))
data_file <- file.path(input_dir, input$data_file)
if (!file.exists(data_file)) stop("missing input data file")

x_labels <- as_chars(input$x)
y_label <- as_chars(input$y)[1]
mediator_labels <- as_chars(input$mediators)
control_labels <- as_chars(input$controls)
display_name <- if (!is.null(input$display_name) && nzchar(input$display_name)) input$display_name else "链式中介"
bootstrap_enabled <- parse_bootstrap_enabled(input$bootstrap)
bootstrap_reps <- parse_reps(input$bootstrap_reps)
bootstrap_reps_is_auto <- is_auto_reps(input$bootstrap_reps)
bootstrap_method <- parse_bootstrap_method(input$bootstrap_method)
bootstrap_method_label <- if (bootstrap_method == "bias_corrected") "偏差校正bootstrap法" else "百分位bootstrap法"

if (length(x_labels) < 1 || is.na(y_label) || !nzchar(y_label) || length(mediator_labels) < 2) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "链式中介需要至少 1 个X、2 个顺序M、1 个Y。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

raw_df <- read.csv(data_file, stringsAsFactors = FALSE, check.names = FALSE)
variables <- unique(c(x_labels, y_label, mediator_labels, control_labels))
missing_cols <- setdiff(variables, colnames(raw_df))
if (length(missing_cols) > 0) {
  cat(jsonlite::toJSON(list(success = FALSE, error = paste0("以下变量不存在：", paste(missing_cols, collapse = "，"))), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

data <- raw_df[, variables, drop = FALSE]
for (col in variables) data[[col]] <- suppressWarnings(as.numeric(data[[col]]))
valid_mask <- stats::complete.cases(data)
valid_n <- sum(valid_mask)
excluded_n <- nrow(data) - valid_n
data <- data[valid_mask, , drop = FALSE]
if (nrow(data) < max(10, length(variables) + 2)) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "链式中介有效样本不足。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

# R 公式对中文和特殊字符列名比较挑，这里内部换安全名，输出仍用原始变量名。
safe_names <- paste0("v", seq_along(variables))
names(safe_names) <- variables
safe_df <- data
colnames(safe_df) <- unname(safe_names[colnames(data)])
xs <- unname(safe_names[x_labels])
y <- safe_names[[y_label]]
mediators <- unname(safe_names[mediator_labels])
controls <- unname(safe_names[control_labels])

make_formula <- function(response, predictors) {
  if (!length(predictors)) return(stats::as.formula(paste(response, "~ 1")))
  stats::reformulate(predictors, response = response)
}
make_lm_data <- function(response, predictors, frame) stats::lm(make_formula(response, predictors), data = frame)
make_lm <- function(response, predictors) make_lm_data(response, predictors, safe_df)
mediator_predictors <- function(index) c(xs, if (index > 1) mediators[seq_len(index - 1)] else character(0), controls)

total_model <- make_lm(y, c(xs, controls))
mediator_models <- lapply(seq_along(mediators), function(i) make_lm(mediators[i], mediator_predictors(i)))
outcome_model <- make_lm(y, c(xs, mediators, controls))
all_models <- c(mediator_models, list(total_model), list(outcome_model))
model_titles <- c(mediator_labels, y_label, y_label)

coef_table <- function(model) coef(summary(model))
coef_est <- function(model, term) {
  table <- coef_table(model)
  if (!term %in% rownames(table)) return(NA_real_)
  table[term, "Estimate"]
}
coef_se <- function(model, term) {
  table <- coef_table(model)
  if (!term %in% rownames(table)) return(NA_real_)
  table[term, "Std. Error"]
}
coef_t <- function(model, term) {
  table <- coef_table(model)
  if (!term %in% rownames(table)) return(NA_real_)
  table[term, "t value"]
}
coef_p <- function(model, term) {
  table <- coef_table(model)
  if (!term %in% rownames(table)) return(NA_real_)
  table[term, "Pr(>|t|)"]
}
coef_ci <- function(model, term) {
  ci <- tryCatch(stats::confint(model), error = function(e) NULL)
  if (is.null(ci) || !term %in% rownames(ci)) return(c(NA_real_, NA_real_))
  c(ci[term, 1], ci[term, 2])
}
beta_value <- function(model, term) {
  if (term == "(Intercept)") return(NA_real_)
  mf <- stats::model.frame(model)
  response <- names(mf)[1]
  predictors <- setdiff(names(mf), response)
  if (!term %in% predictors) return(NA_real_)
  y_sd <- stats::sd(mf[[response]], na.rm = TRUE)
  x_sd <- stats::sd(mf[[term]], na.rm = TRUE)
  if (!is.finite(y_sd) || !is.finite(x_sd) || y_sd == 0) return(NA_real_)
  coef_est(model, term) * x_sd / y_sd
}
model_f <- function(model) {
  f <- summary(model)$fstatistic
  if (is.null(f)) return("")
  p <- stats::pf(f[["value"]], f[["numdf"]], f[["dendf"]], lower.tail = FALSE)
  paste0("F(", as.integer(f[["numdf"]]), ", ", as.integer(f[["dendf"]]), ")=", fmt_num(f[["value"]], 3), ", p=", fmt_p(p))
}
coef_fast <- function(response, predictors, frame) {
  x_matrix <- cbind("(Intercept)" = 1, as.matrix(frame[, predictors, drop = FALSE]))
  y_vector <- frame[[response]]
  coef <- tryCatch(.lm.fit(x_matrix, y_vector)$coefficients, error = function(e) rep(NA_real_, ncol(x_matrix)))
  if (length(coef) != ncol(x_matrix)) coef <- rep(NA_real_, ncol(x_matrix))
  names(coef) <- colnames(x_matrix)
  coef
}

make_path_subsets <- function(k) {
  result <- list()
  for (size in seq_len(k)) {
    combos <- utils::combn(seq_len(k), size, simplify = FALSE)
    result <- c(result, combos)
  }
  result
}
path_subsets <- make_path_subsets(length(mediators))
path_key <- function(x_index, path_index) paste0("ind", x_index, "p", path_index)
total_key <- function(x_index) paste0("total", x_index)
path_label <- function(x_index, path) paste(c(x_labels[x_index], mediator_labels[path], y_label), collapse = "=>")

fit_path_effects <- function(frame) {
  med_coefs <- lapply(seq_along(mediators), function(i) coef_fast(mediators[i], mediator_predictors(i), frame))
  out_coef <- coef_fast(y, c(xs, mediators, controls), frame)
  values <- c()
  all_indirect <- c()
  for (x_index in seq_along(xs)) {
    path_values <- c()
    for (path_index in seq_along(path_subsets)) {
      path <- path_subsets[[path_index]]
      value <- med_coefs[[path[1]]][[xs[x_index]]]
      if (length(path) > 1) {
        for (step_index in 2:length(path)) {
          value <- value * med_coefs[[path[step_index]]][[mediators[path[step_index - 1]]]]
        }
      }
      value <- value * out_coef[[mediators[path[length(path)]]]]
      values[path_key(x_index, path_index)] <- value
      path_values <- c(path_values, value)
      all_indirect <- c(all_indirect, value)
    }
    values[total_key(x_index)] <- if (any(!is.finite(path_values))) NA_real_ else sum(path_values)
  }
  values["grand_total"] <- if (any(!is.finite(all_indirect))) NA_real_ else sum(all_indirect)
  values
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

observed_effects <- fit_path_effects(safe_df)
bootstrap_effects <- NULL
if (bootstrap_enabled) {
  set.seed(42)
  keys <- names(observed_effects)
  boot_rows <- vector("list", bootstrap_reps)
  for (rep_index in seq_len(bootstrap_reps)) {
    sample_index <- sample.int(nrow(safe_df), nrow(safe_df), replace = TRUE)
    boot_rows[[rep_index]] <- tryCatch(
      fit_path_effects(safe_df[sample_index, , drop = FALSE]),
      error = function(e) {
        fallback <- rep(NA_real_, length(keys))
        names(fallback) <- keys
        fallback
      }
    )
  }
  bootstrap_effects <- do.call(rbind, boot_rows)
  colnames(bootstrap_effects) <- keys
}

effect_stats <- function(effect_name) {
  effect <- observed_effects[[effect_name]]
  if (bootstrap_enabled && !is.null(bootstrap_effects) && effect_name %in% colnames(bootstrap_effects)) {
    dist <- bootstrap_effects[, effect_name]
    dist <- dist[is.finite(dist)]
    se <- stats::sd(dist, na.rm = TRUE)
    ci <- bootstrap_ci(dist, effect, bootstrap_method)
  } else {
    se <- NA_real_
    ci <- c(NA_real_, NA_real_)
  }
  z <- if (!is.na(se) && se > 0) effect / se else NA_real_
  p <- if (!is.na(z)) 2 * stats::pnorm(-abs(z)) else NA_real_
  significant <- !is.na(ci[1]) && !is.na(ci[2]) && ((ci[1] > 0 && ci[2] > 0) || (ci[1] < 0 && ci[2] < 0))
  list(est = effect, se = se, z = z, p = p, lower = ci[1], upper = ci[2], significant = significant)
}
conclusion_for <- function(effect_sig, cprime_p, indirect, cprime) {
  if (!effect_sig) return("中介作用不显著")
  if (!sig_bool(cprime_p)) return("完全中介")
  if (same_sign(indirect, cprime)) return("部分中介")
  "遮掩效应"
}

row_terms <- c("(Intercept)", xs, mediators, controls)
row_labels <- c("常数", x_labels, mediator_labels, control_labels)
reg_headers <- c("项", rep(c("B", "标准误", "t", "p", "β"), length(all_models)))
reg_header_rows <- list(
  c(list(list(text = "项", rowspan = 2L)), lapply(model_titles, function(title) list(text = title, colspan = 5L))),
  rep(list("B", "标准误", "t", "p", "β"), length(all_models))
)
regression_rows <- list()
for (i in seq_along(row_terms)) {
  row <- c(row_labels[i])
  for (model in all_models) {
    p <- coef_p(model, row_terms[i])
    row <- c(row, fmt_coef(coef_est(model, row_terms[i]), p), fmt_num(coef_se(model, row_terms[i]), 3), fmt_num(coef_t(model, row_terms[i]), 3), fmt_p(p), fmt_num(beta_value(model, row_terms[i]), 3))
  }
  regression_rows[[length(regression_rows) + 1]] <- row
}
regression_rows[[length(regression_rows) + 1]] <- c("样本量", unlist(lapply(all_models, function(model) c(as.character(nobs(model)), "", "", "", ""))))
regression_rows[[length(regression_rows) + 1]] <- c("R²", unlist(lapply(all_models, function(model) c(fmt_num(summary(model)$r.squared, 3), "", "", "", ""))))
regression_rows[[length(regression_rows) + 1]] <- c("调整R²", unlist(lapply(all_models, function(model) c(fmt_num(summary(model)$adj.r.squared, 3), "", "", "", ""))))
regression_rows[[length(regression_rows) + 1]] <- c("F值", unlist(lapply(all_models, function(model) c(model_f(model), "", "", "", ""))))

direct_rows <- list()
effect_process_rows <- list()
summary_rows <- list()
simplified_rows <- list()
total_indirect_rows <- list()
path_edges <- list()

add_direct_row <- function(item, model, term, effect_label = "直接效应") {
  ci <- coef_ci(model, term)
  c(effect_label, item, fmt_num(coef_est(model, term), 3), fmt_num(coef_se(model, term), 3), fmt_num(coef_t(model, term), 3), fmt_p(coef_p(model, term)), fmt_num(ci[1], 3), fmt_num(ci[2], 3))
}
for (x_index in seq_along(xs)) {
  c_total <- coef_est(total_model, xs[x_index])
  c_total_p <- coef_p(total_model, xs[x_index])
  cprime <- coef_est(outcome_model, xs[x_index])
  cprime_p <- coef_p(outcome_model, xs[x_index])
  direct_rows[[length(direct_rows) + 1]] <- add_direct_row(paste0(x_labels[x_index], "=>", y_label), outcome_model, xs[x_index])
  path_edges[[length(path_edges) + 1]] <- list(from = paste0("x", x_index), to = "y", value = paste0("c'=", fmt_coef(cprime, cprime_p)), significant = sig_bool(cprime_p))
  for (m_index in seq_along(mediators)) {
    model <- mediator_models[[m_index]]
    direct_rows[[length(direct_rows) + 1]] <- add_direct_row(paste0(x_labels[x_index], "=>", mediator_labels[m_index]), model, xs[x_index])
    path_edges[[length(path_edges) + 1]] <- list(from = paste0("x", x_index), to = paste0("m", m_index), value = fmt_coef(coef_est(model, xs[x_index]), coef_p(model, xs[x_index])), significant = sig_bool(coef_p(model, xs[x_index])))
  }
  for (path_index in seq_along(path_subsets)) {
    path <- path_subsets[[path_index]]
    indirect <- effect_stats(path_key(x_index, path_index))
    label <- path_label(x_index, path)
    conclusion <- conclusion_for(indirect$significant, cprime_p, indirect$est, cprime)
    effect_process_rows[[length(effect_process_rows) + 1]] <- c("间接效应过程", label, fmt_num(indirect$est, 3), fmt_num(indirect$se, 3), fmt_num(indirect$z, 3), fmt_p(indirect$p), fmt_num(indirect$lower, 3), fmt_num(indirect$upper, 3))
    summary_rows[[length(summary_rows) + 1]] <- c(label, fmt_coef(c_total, c_total_p), fmt_num(indirect$est, 3), fmt_num(indirect$se, 3), fmt_num(indirect$z, 3), fmt_p(indirect$p), fmt_ci(indirect$lower, indirect$upper), fmt_coef(cprime, cprime_p), conclusion)
    path_meaning <- if (length(path) > 1) "链式中介路径" else "平行中介路径"
    simplified_rows[[length(simplified_rows) + 1]] <- c(label, "间接效应", path_meaning, fmt_num(indirect$est, 3), fmt_num(indirect$lower, 3), fmt_num(indirect$upper, 3), fmt_num(indirect$se, 3), fmt_num(indirect$z, 3), fmt_p(indirect$p), conclusion)
  }
  total_indirect <- effect_stats(total_key(x_index))
  total_indirect_rows[[length(total_indirect_rows) + 1]] <- c(paste0(x_labels[x_index], "=>", y_label), fmt_num(total_indirect$est, 3), fmt_num(total_indirect$se, 3), fmt_num(total_indirect$z, 3), fmt_p(total_indirect$p), fmt_num(total_indirect$lower, 3), fmt_num(total_indirect$upper, 3))
  effect_process_rows[[length(effect_process_rows) + 1]] <- c("总效应", paste0(x_labels[x_index], "=>", y_label), fmt_num(c_total, 3), fmt_num(coef_se(total_model, xs[x_index]), 3), fmt_num(coef_t(total_model, xs[x_index]), 3), fmt_p(c_total_p), fmt_num(coef_ci(total_model, xs[x_index])[1], 3), fmt_num(coef_ci(total_model, xs[x_index])[2], 3))
}
for (m_index in seq_along(mediators)) {
  b <- coef_est(outcome_model, mediators[m_index])
  b_p <- coef_p(outcome_model, mediators[m_index])
  direct_rows[[length(direct_rows) + 1]] <- add_direct_row(paste0(mediator_labels[m_index], "=>", y_label), outcome_model, mediators[m_index])
  path_edges[[length(path_edges) + 1]] <- list(from = paste0("m", m_index), to = "y", value = fmt_coef(b, b_p), significant = sig_bool(b_p))
  if (m_index > 1) {
    for (prev_index in seq_len(m_index - 1)) {
      model <- mediator_models[[m_index]]
      term <- mediators[prev_index]
      direct_rows[[length(direct_rows) + 1]] <- add_direct_row(paste0(mediator_labels[prev_index], "=>", mediator_labels[m_index]), model, term)
      path_edges[[length(path_edges) + 1]] <- list(from = paste0("m", prev_index), to = paste0("m", m_index), value = fmt_coef(coef_est(model, term), coef_p(model, term)), significant = sig_bool(coef_p(model, term)))
    }
  }
}
grand <- effect_stats("grand_total")
total_indirect_rows[[length(total_indirect_rows) + 1]] <- c("间接效应总和", fmt_num(grand$est, 3), fmt_num(grand$se, 3), fmt_num(grand$z, 3), fmt_p(grand$p), fmt_num(grand$lower, 3), fmt_num(grand$upper, 3))

fmt_signed_term <- function(model, term, label) {
  value <- coef_est(model, term)
  if (!is.finite(value)) return("")
  sign <- if (value < 0) "" else "+"
  paste0(sign, fmt_num(value, 3), "*", label)
}
format_equation <- function(response_label, model, terms, labels) {
  paste0(response_label, "=", fmt_num(coef_est(model, "(Intercept)"), 3), paste0(mapply(function(term, label) fmt_signed_term(model, term, label), terms, labels), collapse = ""))
}
mediator_equations <- mapply(
  function(index, model) format_equation(mediator_labels[index], model, mediator_predictors(index), c(x_labels, if (index > 1) mediator_labels[seq_len(index - 1)] else character(0), control_labels)),
  seq_along(mediator_models),
  mediator_models
)
smart_text <- paste(c(
  "从上表可知：链式中介效应分析共涉及3类回归模型：",
  paste0("第一，因变量Y与自变量X进行回归模型构建：", format_equation(y_label, total_model, xs, x_labels)),
  paste0("第二，自变量X与顺序中介变量M进行逐层回归模型构建：", paste(mediator_equations, collapse = "；")),
  paste0("第三，自变量X和全部中介变量M一起与因变量Y进行回归模型构建：", format_equation(y_label, outcome_model, c(xs, mediators), c(x_labels, mediator_labels))),
  "第四，间接效应过程值通过Bootstrap抽样检验，链式路径按中介变量放入顺序生成。"
), collapse = "\n")

note_sig <- paste0("备注：* p<0.1 ** p<0.05 *** p<0.01 **** p<0.001；BootLLCI指Bootstrap抽样95%区间下限，BootULCI指Bootstrap抽样95%区间上限，bootstrap类型 = ", bootstrap_method_label, "。")
process_rows <- c(direct_rows, effect_process_rows)
sample_rows <- list(
  c("有效样本", as.character(valid_n), paste0(fmt_num(valid_n / nrow(raw_df) * 100, 3), "%")),
  c("排除无效样本", as.character(excluded_n), paste0(fmt_num(excluded_n / nrow(raw_df) * 100, 3), "%")),
  c("总计", as.character(nrow(raw_df)), "100%")
)
simplified_header_rows <- list(
  list(list(text = "项", rowspan = 2L), list(text = "符号", rowspan = 2L), list(text = "意义", rowspan = 2L), list(text = "效应值Effect", rowspan = 2L), list(text = "95% CI", colspan = 2L), list(text = "标准误SE值", rowspan = 2L), list(text = "z值/t值", rowspan = 2L), list(text = "p值", rowspan = 2L), list(text = "结论", rowspan = 2L)),
  list("下限", "上限")
)

chart_w <- 840
chart_h <- max(360, 170 + max(length(xs), length(mediators)) * 70)
x_top <- max(48, chart_h / 2 - (length(xs) - 1) * 38)
m_top <- max(48, chart_h / 2 - (length(mediators) - 1) * 38)
nodes <- list()
for (i in seq_along(xs)) nodes[[length(nodes) + 1]] <- list(key = paste0("x", i), label = x_labels[i], x = 70, y = x_top + (i - 1) * 76)
for (i in seq_along(mediators)) nodes[[length(nodes) + 1]] <- list(key = paste0("m", i), label = mediator_labels[i], x = 300 + (i - 1) * min(120, 300 / max(1, length(mediators) - 1)), y = m_top + (i - 1) * 76)
nodes[[length(nodes) + 1]] <- list(key = "y", label = y_label, x = 720, y = chart_h / 2 - 19)
path_chart <- list(chartType = "model_path", title = "模型图", data = list(width = chart_w, height = chart_h, target = y_label, nodes = nodes, edges = path_edges, defaultShowDataLabels = TRUE))

summary_text <- paste0(display_name, "共纳入 ", valid_n, " 条有效样本，生成 ", length(summary_rows), " 条中介路径。")
indirect_rows <- lapply(summary_rows, function(row) c(row[1], row[3], row[4], strsplit(row[7], " ~ ", fixed = TRUE)[[1]][1], strsplit(row[7], " ~ ", fixed = TRUE)[[1]][2], row[5], row[6]))
indirect_smart <- paste(c(
  paste0("使用Bootstrap抽样检验进行中介效应研究，抽样次数为", bootstrap_reps, "次，结果显示："),
  mapply(function(row) {
    ci <- strsplit(row[7], " ~ ", fixed = TRUE)[[1]]
    contains_zero <- suppressWarnings(as.numeric(ci[1]) <= 0 && as.numeric(ci[2]) >= 0)
    paste0("针对", row[1], "这条中介路径来看，95%区间", if (contains_zero) "包括数字0" else "不包括数字0", "(95% CI:", ci[1], "~", ci[2], ")，因此说明此条中介效应路径", if (contains_zero) "不存在。" else "存在。")
  }, summary_rows)
), collapse = "\n")
sections <- list(
  sec_table("中介效应模型检验", reg_headers, regression_rows, "上表展示链式中介涉及的逐层回归模型参数结果。", note_sig, headerRows = reg_header_rows, tableClass = "tlt--spssau"),
  sec_advice("链式中介效应模型分为三类回归模型：X对Y的总效应模型；X和前序中介变量对当前中介变量的逐层模型；X和全部中介变量对Y的直接效应模型。"),
  sec_smart(smart_text),
  sec_table("效应分析过程汇总", c("效应", "项", "Effect", "SE", "t/z", "p", "LLCI", "ULCI"), process_rows, "上表汇总直接效应、间接效应过程和总效应。", note_sig, tableClass = "tlt--spssau"),
  sec_advice("中介效应模型涉及三类效应，分别是直接效应、间接效应和总效应；直接效应为自变量X对因变量Y的回归效应，间接效应由各路径段相乘得到，总效应为直接效应与间接效应之和。"),
  sec_table("间接效应分析", c("项", "Effect", "Boot SE", "BootLLCI", "BootULCI", "z", "p"), indirect_rows, "灰色底纹在SPSSAU中用于标记链式中介；其余为平行中介。", note_sig, tableClass = "tlt--spssau"),
  sec_advice("判断间接效应时，优先查看Bootstrap 95%CI是否包含0；不包含0说明该中介路径成立。链式路径必须结合变量放入顺序解释。"),
  sec_smart(indirect_smart),
  sec_table("中介效应模型检验-简化格式", c("项", "符号", "意义", "效应值Effect", "下限", "上限", "标准误SE值", "z值/t值", "p值", "结论"), simplified_rows, "上表展示链式中介检验的横向简化格式，适合论文附表或导出后整理。", note_sig, headerRows = simplified_header_rows, tableClass = "tlt--spssau"),
  sec_table("总间接效应表格", c("项", "总间接效应", "Boot SE", "z 值", "p 值", "BootLLCI", "BootULCI"), total_indirect_rows, "当中介变量超过1个时，总间接效应用于观察所有中介路径合计后的影响。", note_sig, tableClass = "tlt--spssau"),
  sec_advice("总间接效应表示同一自变量通过全部中介路径对Y的合计影响；链式路径只说明按当前中介顺序的传导，不自动证明因果先后。"),
  sec_charts("模型图", list(path_chart)),
  sec_table("样本缺失情况汇总", c("项", "样本数", "占比"), sample_rows, "上表展示真正进入算法模型的有效样本和排除在外的无效样本情况。", tableClass = "tlt--spssau"),
  sec_refs(c("[1] The SPSSAU project (2026). SPSSAU. [Online Application Software]. Retrieved from https://www.spssau.com.", "[2] 周俊, 马世澄. SPSSAU科研数据分析方法与应用. 电子工业出版社.", "[3] Hayes, A. F. Introduction to Mediation, Moderation, and Conditional Process Analysis."))
)

result <- list(
  success = TRUE,
  name = display_name,
  headers = c("项", "c 总效应", "间接效应值", "Boot SE", "z值", "p值", "95% BootCI", "c' 直接效应", "检验结论"),
  rows = summary_rows,
  description = summary_text,
  sections = sections
)
cat(jsonlite::toJSON(sanitize_json(result), auto_unbox = TRUE, null = "null", force = TRUE, dataframe = "rows"))
