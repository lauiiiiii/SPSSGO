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

data <- raw_df[, variables, drop = FALSE]
for (col in variables) data[[col]] <- suppressWarnings(as.numeric(data[[col]]))
valid_mask <- stats::complete.cases(data)
valid_n <- sum(valid_mask)
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
mediator_predictors <- function() c(x, z, if (moderate_x_m) xz else character(0), controls)
outcome_predictors <- function() c(
  x,
  mediators,
  z,
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

fits <- fit_all(safe_df)
all_models <- c(fits$mediators, list(fits$outcome))
model_titles <- c(mediator_labels, y_label)
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
indirect_effect <- function(fits, mediator_index, z_value) {
  a <- coef_value(fits$mediators[[mediator_index]], x)
  if (moderate_x_m) a <- a + coef_value(fits$mediators[[mediator_index]], xz) * z_value
  b <- coef_value(fits$outcome, mediators[mediator_index])
  if (moderate_m_y) b <- b + coef_value(fits$outcome, paste0(mediators[mediator_index], "_x_", z)) * z_value
  a * b
}
effect_keys <- c("direct_mean")
for (m_index in seq_along(mediators)) {
  for (level in z_levels) effect_keys <- c(effect_keys, paste0("ind_m", m_index, "_", level$key))
}
compute_effects <- function(frame) {
  fit <- fit_all(frame)
  values <- c(direct_mean = direct_effect(fit, z_mean))
  for (m_index in seq_along(mediators)) {
    for (level in z_levels) values[paste0("ind_m", m_index, "_", level$key)] <- indirect_effect(fit, m_index, level$value)
  }
  values
}
observed_effects <- compute_effects(safe_df)

set.seed(42)
boot_rows <- vector("list", bootstrap_reps)
for (rep_index in seq_len(bootstrap_reps)) {
  sample_index <- sample.int(nrow(safe_df), nrow(safe_df), replace = TRUE)
  boot_rows[[rep_index]] <- tryCatch(
    compute_effects(safe_df[sample_index, , drop = FALSE]),
    error = function(e) {
      fallback <- rep(NA_real_, length(effect_keys))
      names(fallback) <- effect_keys
      fallback
    }
  )
}
bootstrap_effects <- do.call(rbind, boot_rows)
colnames(bootstrap_effects) <- effect_keys
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

row_terms <- unique(c("(Intercept)", x, z, if (moderate_x_m || moderate_x_y) xz else character(0), mediators, if (moderate_m_y) paste0(mediators, "_x_", z) else character(0), controls))
reg_headers <- c("项", rep(c("B", "SE", "t值", "p值", "β"), length(all_models)))
reg_header_rows <- list(
  c(list(list(text = "项", rowspan = 2L)), lapply(model_titles, function(title) list(text = title, colspan = 5L))),
  rep(list("B", "SE", "t值", "p值", "β"), length(all_models))
)
regression_rows <- list()
for (term in row_terms) {
  row <- c(label_for(term))
  for (model_obj in all_models) {
    p <- coef_p(model_obj, term)
    row <- c(row, fmt_coef(coef_value(model_obj, term), p), fmt_num(coef_se(model_obj, term), 3), fmt_num(coef_t(model_obj, term), 3), fmt_p(p), fmt_num(beta_value(model_obj, term), 3))
  }
  regression_rows[[length(regression_rows) + 1]] <- row
}
regression_rows[[length(regression_rows) + 1]] <- c("样本量", unlist(lapply(all_models, function(model_obj) c(as.character(nobs(model_obj)), "", "", "", ""))))
regression_rows[[length(regression_rows) + 1]] <- c("R²", unlist(lapply(all_models, function(model_obj) c(fmt_num(summary(model_obj)$r.squared, 3), "", "", "", ""))))
regression_rows[[length(regression_rows) + 1]] <- c("调整R²", unlist(lapply(all_models, function(model_obj) c(fmt_num(summary(model_obj)$adj.r.squared, 3), "", "", "", ""))))
regression_rows[[length(regression_rows) + 1]] <- c("F值", unlist(lapply(all_models, function(model_obj) c(model_f(model_obj), "", "", "", ""))))

direct <- effect_stats("direct_mean")
direct_rows <- list(c(fmt_num(direct$est, 3), fmt_num(direct$se, 3), fmt_num(direct$z, 3), fmt_p(direct$p), fmt_num(direct$lower, 3), fmt_num(direct$upper, 3)))

conditional_rows <- list()
conditional_text <- c()
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
note_sig <- paste0("备注：* p<0.1 ** p<0.05 *** p<0.01 **** p<0.001；BootLLCI指Bootstrap抽样95%区间下限，BootULCI指Bootstrap抽样95%区间上限，bootstrap类型 = ", bootstrap_method_label, "。")
moderator_levels_label <- if (moderator_levels_method == "quantile") "P25、P50、P75分位数" else "低水平(-1SD)、平均值、高水平(+1SD)"
smart <- paste(c(
  paste0("本次路径设置对应 PROCESS Model ", model, "：", path_desc, "。"),
  paste0("调节中介效应模型共分为两类回归模型：第一类为因变量Y的回归模型；第二类为因变量M的回归模型，如果有多个中介变量则分别建立多个模型。"),
  paste0("Bootstrap抽样次数为", bootstrap_reps, "次，条件间接效应以", z_label, "的", moderator_levels_label, "进行检验。")
), collapse = "\n")

sections <- list(
  sec_table("回归模型汇总表格", reg_headers, regression_rows, "上表将调节中介涉及的回归模型结果全部列出。", note_sig, headerRows = reg_header_rows, tableClass = "tlt--spssau"),
  sec_advice(paste0("本次路径设置对应 PROCESS Model ", model, "。用户只需关注被调节路径：", path_desc, "。")),
  sec_smart(smart),
  sec_table("直接效应（Direct Effect）结果", c("Effect", "SE", "z值", "p值", "LLCI", "ULCI"), direct_rows, "直接效应表示在调节变量平均值水平下，X对于Y的影响情况。", "备注：LLCI指估计值95%区间下限，ULCI指估计值95%区间上限。", tableClass = "tlt--spssau"),
  sec_table("条件间接效应（Conditional Indirect Effect）结果", c("中介变量", "Z水平", "Effect", "BootSE", "BootLLCI", "BootULCI"), conditional_rows, "该表为调节中介的核心表格，展示调节变量在不同水平时的间接效应。", note_sig, tableClass = "tlt--spssau"),
  sec_advice("如果某一水平下 Bootstrap 95%CI 不包括0，说明该水平下存在中介效应；不同水平下显著性或方向不同，可作为调节中介存在的证据。"),
  sec_smart(paste(conditional_text, collapse = "\n")),
  sec_table("回归模型汇总表格-简化格式", c("项", model_titles), simplified_rows, "上表为回归模型汇总表格的横向简化格式，括号中为t值。", note_sig, tableClass = "tlt--spssau"),
  sec_refs(c("[1] Hayes, A. F. Introduction to Mediation, Moderation, and Conditional Process Analysis.", "[2] The SPSSAU project (2026). SPSSAU. [Online Application Software]. Retrieved from https://www.spssau.com."))
)

result <- list(
  success = TRUE,
  name = "调节中介",
  headers = c("中介变量", "Z水平", "Effect", "BootSE", "BootLLCI", "BootULCI"),
  rows = conditional_rows,
  description = smart,
  sections = sections
)
cat(jsonlite::toJSON(sanitize_json(result), auto_unbox = TRUE, null = "null", force = TRUE, dataframe = "rows"))
