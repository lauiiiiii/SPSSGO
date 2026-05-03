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

if (is.null(input_path) || !file.exists(input_path)) {
  stop("missing --input json file")
}

read_utf8 <- function(path) {
  paste(readLines(path, warn = FALSE, encoding = "UTF-8"), collapse = "\n")
}

fmt_num <- function(x, digits = 4) {
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

raw_df <- read.csv(data_file, stringsAsFactors = FALSE, check.names = FALSE)
factor_map <- input$factor_map
factor_names <- names(factor_map)
if (length(factor_names) == 0) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "SEM 至少需要一组测量题项。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

variables <- c()
clean_map <- list()
for (factor_name in factor_names) {
  cols <- unlist(factor_map[[factor_name]])
  cols <- cols[cols %in% names(raw_df)]
  if (length(cols) >= 2) {
    clean_map[[factor_name]] <- cols
    variables <- unique(c(variables, cols))
  }
}
factor_map <- clean_map
factor_names <- names(factor_map)
if (length(factor_names) == 0) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "每个潜变量至少需要 2 个测量题项。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

data <- raw_df[, variables, drop = FALSE]
for (col in variables) data[[col]] <- suppressWarnings(as.numeric(data[[col]]))
data <- stats::na.omit(data)
if (nrow(data) < max(30, length(variables) * 3)) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "SEM 有效样本不足，建议至少满足样本量>30且达到题项数的3倍。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

measurement_lines <- c()
for (factor_name in factor_names) {
  measurement_lines <- c(measurement_lines, paste0(factor_name, " =~ ", paste(factor_map[[factor_name]], collapse = " + ")))
}

structural_paths <- input$structural_paths
structural_lines <- c()
if (!is.null(structural_paths) && length(structural_paths) > 0) {
  for (item in structural_paths) {
    left <- item$dependent
    rights <- unlist(item$predictors)
    rights <- rights[rights %in% factor_names]
    if (!is.null(left) && left %in% factor_names && length(rights) > 0) {
      structural_lines <- c(structural_lines, paste0(left, " ~ ", paste(rights, collapse = " + ")))
    }
  }
}
if (length(structural_lines) == 0 && length(factor_names) >= 2) {
  structural_lines <- c(paste0(factor_names[length(factor_names)], " ~ ", paste(factor_names[-length(factor_names)], collapse = " + ")))
}

model_desc <- paste(c(measurement_lines, structural_lines), collapse = "\n")

fit <- tryCatch(
  lavaan::sem(model_desc, data = data, std.lv = TRUE, missing = "listwise"),
  error = function(e) e
)
if (inherits(fit, "error")) {
  cat(jsonlite::toJSON(list(success = FALSE, error = paste0("SEM 拟合失败：", fit$message)), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

fit_measure_names <- c("chisq", "df", "pvalue", "cfi", "tli", "rmsea", "srmr", "gfi", "agfi", "nfi", "aic", "bic")
fit_measure <- lavaan::fitMeasures(fit, fit_measure_names)
chi2 <- unname(fit_measure["chisq"])
dof <- unname(fit_measure["df"])
cmin_df <- ifelse(!is.na(chi2) && !is.na(dof) && dof != 0, chi2 / dof, NA)

param_est <- lavaan::parameterEstimates(fit, standardized = TRUE)
loading_df <- param_est[param_est$op == "=~", ]
path_df <- param_est[param_est$op == "~" & param_est$lhs %in% factor_names & param_est$rhs %in% factor_names, ]
resid_df <- param_est[param_est$op == "~~" & param_est$lhs %in% variables & param_est$rhs %in% variables & param_est$lhs == param_est$rhs, ]
latent_cov_df <- param_est[param_est$op == "~~" & param_est$lhs %in% factor_names & param_est$rhs %in% factor_names, ]

loading_rows <- list()
for (i in seq_len(nrow(loading_df))) {
  row <- loading_df[i, ]
  loading_rows[[length(loading_rows) + 1]] <- list(as.character(row$lhs), as.character(row$rhs), fmt_num(row$est, 4), fmt_num(row$std.all, 4), fmt_num(row$se, 4), fmt_num(row$z, 4), fmt_num(row$pvalue, 4))
}

path_rows <- list()
for (i in seq_len(nrow(path_df))) {
  row <- path_df[i, ]
  path_rows[[length(path_rows) + 1]] <- list(as.character(row$lhs), as.character(row$rhs), fmt_num(row$est, 4), fmt_num(row$std.all, 4), fmt_num(row$se, 4), fmt_num(row$z, 4), fmt_num(row$pvalue, 4))
}

cr_ave_rows <- list()
sqrt_ave_map <- list()
for (factor_name in factor_names) {
  factor_loadings <- loading_df[loading_df$lhs == factor_name, ]
  std_loadings <- as.numeric(factor_loadings$std.all)
  std_loadings <- std_loadings[!is.na(std_loadings)]
  err_vars <- 1 - std_loadings^2
  sum_load <- sum(std_loadings)
  sum_load_sq <- sum(std_loadings^2)
  sum_err <- sum(err_vars)
  cr <- ifelse((sum_load^2 + sum_err) > 0, (sum_load^2) / (sum_load^2 + sum_err), NA)
  ave <- ifelse((sum_load_sq + sum_err) > 0, sum_load_sq / (sum_load_sq + sum_err), NA)
  sqrt_ave <- ifelse(!is.na(ave) && ave >= 0, sqrt(ave), NA)
  sqrt_ave_map[[factor_name]] <- sqrt_ave
  cr_ave_rows[[length(cr_ave_rows) + 1]] <- list(factor_name, as.character(length(factor_map[[factor_name]])), fmt_num(cr, 4), fmt_num(ave, 4), fmt_num(sqrt_ave, 4))
}

latent_corr <- tryCatch(lavaan::lavInspect(fit, "cor.lv"), error = function(e) NULL)
fl_rows <- list()
if (!is.null(latent_corr)) {
  for (row_factor in factor_names) {
    row <- list(row_factor)
    for (col_factor in factor_names) {
      if (row_factor == col_factor) {
        row <- c(row, list(fmt_num(sqrt_ave_map[[row_factor]], 4)))
      } else {
        row <- c(row, list(fmt_num(latent_corr[row_factor, col_factor], 4)))
      }
    }
    fl_rows[[length(fl_rows) + 1]] <- row
  }
}

dv_rows <- list()
for (factor_name in factor_names) {
  others <- factor_names[factor_names != factor_name]
  max_corr <- 0
  if (!is.null(latent_corr) && length(others) > 0) max_corr <- max(abs(latent_corr[factor_name, others]))
  sqrt_ave <- sqrt_ave_map[[factor_name]]
  dv_rows[[length(dv_rows) + 1]] <- list(factor_name, fmt_num(sqrt_ave, 4), fmt_num(max_corr, 4), ifelse(!is.na(sqrt_ave) && sqrt_ave > max_corr, "通过", "需关注"))
}

resid_rows <- list()
for (i in seq_len(nrow(resid_df))) {
  row <- resid_df[i, ]
  resid_rows[[length(resid_rows) + 1]] <- list(as.character(row$lhs), fmt_num(row$est, 4), fmt_num(row$std.all, 4), fmt_num(row$se, 4), fmt_num(row$z, 4), fmt_num(row$pvalue, 4))
}

latent_cov_rows <- list()
for (i in seq_len(nrow(latent_cov_df))) {
  row <- latent_cov_df[i, ]
  latent_cov_rows[[length(latent_cov_rows) + 1]] <- list(as.character(row$lhs), as.character(row$rhs), fmt_num(row$est, 4), fmt_num(row$std.all, 4), fmt_num(row$se, 4), fmt_num(row$z, 4), fmt_num(row$pvalue, 4))
}

endogenous <- unique(path_df$lhs)
score_rows <- list()
if (length(endogenous) > 0) {
  r2_vals <- tryCatch(lavaan::inspect(fit, "r2"), error = function(e) NULL)
  if (!is.null(r2_vals)) {
    for (name in names(r2_vals)) {
      score_rows[[length(score_rows) + 1]] <- list(name, fmt_num(r2_vals[[name]], 4), "—", as.character(nrow(data)))
    }
  }
}

effect_rows <- list()
if (nrow(path_df) > 0) {
  direct <- matrix(0, nrow = length(factor_names), ncol = length(factor_names), dimnames = list(factor_names, factor_names))
  for (i in seq_len(nrow(path_df))) {
    row <- path_df[i, ]
    if (row$rhs %in% factor_names && row$lhs %in% factor_names && !is.na(row$std.all)) direct[row$rhs, row$lhs] <- row$std.all
  }
  total <- direct
  current <- direct
  for (i in seq_len(max(length(factor_names) - 1, 1))) {
    current <- current %*% direct
    total <- total + current
    if (all(abs(current) < 1e-10)) break
  }
  indirect <- total - direct
  for (pred in factor_names) {
    for (dep in factor_names) {
      if (pred == dep) next
      if (abs(total[pred, dep]) < 1e-10 && abs(direct[pred, dep]) < 1e-10) next
      effect_rows[[length(effect_rows) + 1]] <- list(pred, dep, fmt_num(direct[pred, dep], 4), fmt_num(indirect[pred, dep], 4), fmt_num(total[pred, dep], 4))
    }
  }
}

mi <- tryCatch(lavaan::modindices(fit), error = function(e) NULL)
mi_rows <- list()
if (!is.null(mi) && nrow(mi) > 0) {
  mi <- mi[order(-mi$mi), ]
  top_n <- min(10, nrow(mi))
  for (i in seq_len(top_n)) {
    row <- mi[i, ]
    mi_rows[[length(mi_rows) + 1]] <- list(paste(as.character(row$lhs), as.character(row$op), as.character(row$rhs)), fmt_num(row$mi, 3), fmt_num(row$epc, 4), "可结合理论判断是否释放该参数")
  }
}

fit_rows <- list(
  list("样本量", as.character(nrow(data))),
  list("题项数", as.character(length(variables))),
  list("潜变量数", as.character(length(factor_names))),
  list("结构路径数", as.character(nrow(path_df))),
  list("Chi-square", fmt_num(chi2, 4)),
  list("df", fmt_num(dof, 0)),
  list("CMIN/DF", fmt_num(cmin_df, 4)),
  list("p", fmt_num(unname(fit_measure["pvalue"]), 4)),
  list("CFI", fmt_num(unname(fit_measure["cfi"]), 4)),
  list("GFI", fmt_num(unname(fit_measure["gfi"]), 4)),
  list("AGFI", fmt_num(unname(fit_measure["agfi"]), 4)),
  list("NFI", fmt_num(unname(fit_measure["nfi"]), 4)),
  list("TLI", fmt_num(unname(fit_measure["tli"]), 4)),
  list("RMSEA", fmt_num(unname(fit_measure["rmsea"]), 4)),
  list("SRMR", fmt_num(unname(fit_measure["srmr"]), 4)),
  list("AIC", fmt_num(unname(fit_measure["aic"]), 4)),
  list("BIC", fmt_num(unname(fit_measure["bic"]), 4))
)

sections <- list(
  sec_table("模型拟合指标", c("指标", "值"), fit_rows, "当前版本使用 lavaan 估计协方差型 SEM，拟合指标口径更接近 AMOS 常见报告。"),
  sec_table("测量模型载荷", c("潜变量", "题项", "非标准化载荷", "标准化载荷", "Std. Err", "z", "p"), loading_rows, "该表对应外部模型载荷表。"),
  sec_table("结构路径系数", c("因变量", "自变量", "非标准化路径", "标准化路径", "Std. Err", "z", "p"), path_rows, "标准化路径更适合跨路径比较。"),
  sec_table("聚合效度与组合信度", c("潜变量", "题项数", "CR", "AVE", "sqrt(AVE)"), cr_ave_rows),
  sec_table("Fornell-Larcker 判据", c("潜变量", factor_names), fl_rows, "对角线为 sqrt(AVE)，非对角线为潜变量相关。"),
  sec_table("误差方差", c("题项", "误差方差", "标准化误差方差", "Std. Err", "z", "p"), resid_rows),
  sec_table("潜变量协方差与相关", c("潜变量1", "潜变量2", "协方差", "标准化相关", "Std. Err", "z", "p"), latent_cov_rows),
  sec_table("判别效度结论", c("因子", "sqrt(AVE)", "最大相关系数", "判别效度"), dv_rows)
)
if (length(score_rows) > 0) sections[[length(sections) + 1]] <- sec_table("内生潜变量解释力", c("潜变量", "R²", "调整后R²", "样本量"), score_rows)
if (length(effect_rows) > 0) sections[[length(sections) + 1]] <- sec_table("直接效应/间接效应/总效应", c("自变量", "因变量", "直接效应", "间接效应", "总效应"), effect_rows)
if (length(mi_rows) > 0) sections[[length(sections) + 1]] <- sec_table("模型修正建议（MI）", c("建议参数", "MI", "EPC", "建议"), mi_rows, "修正指数越高，说明释放该参数可能显著改善模型拟合；但必须结合理论判断。")

fit_issue <- c()
if (!is.na(cmin_df) && cmin_df >= 3) fit_issue <- c(fit_issue, "卡方自由度比偏高")
if (!is.na(unname(fit_measure["cfi"])) && unname(fit_measure["cfi"]) < 0.9) fit_issue <- c(fit_issue, "CFI 偏低")
if (!is.na(unname(fit_measure["rmsea"])) && unname(fit_measure["rmsea"]) >= 0.08) fit_issue <- c(fit_issue, "RMSEA 偏高")
if (!is.na(unname(fit_measure["srmr"])) && unname(fit_measure["srmr"]) >= 0.08) fit_issue <- c(fit_issue, "SRMR 偏高")
sig_paths <- c()
for (i in seq_len(nrow(path_df))) {
  row <- path_df[i, ]
  if (!is.na(row$pvalue) && row$pvalue < 0.05) sig_paths <- c(sig_paths, paste0(row$rhs, "→", row$lhs))
}

smart <- paste0("SEM 拟合完成，共纳入 ", nrow(data), " 个有效样本、", length(factor_names), " 个潜变量。模型拟合指标为 CFI=", fmt_num(unname(fit_measure["cfi"]), 3), "、TLI=", fmt_num(unname(fit_measure["tli"]), 3), "、RMSEA=", fmt_num(unname(fit_measure["rmsea"]), 3), "、SRMR=", fmt_num(unname(fit_measure["srmr"]), 3), "。")
if (length(fit_issue) > 0) smart <- paste0(smart, " 当前需要重点关注：", paste(fit_issue, collapse = "、"), "。") else smart <- paste0(smart, " 主要拟合指标整体较为稳定。")
if (length(sig_paths) > 0) smart <- paste0(smart, " 结构路径中显著的关系包括：", paste(sig_paths, collapse = "、"), "。")

sections[[length(sections) + 1]] <- sec_advice(paste("SEM 结果建议综合从三层解读：", "第一：先看模型拟合指标是否达到常用阈值；", "第二：再看测量模型的载荷、CR、AVE、Fornell-Larcker；", "第三：最后解释结构路径、总效应与 R²。", sep = "\n"))
sections[[length(sections) + 1]] <- sec_smart(smart)
sections[[length(sections) + 1]] <- sec_refs(c("[1] Rosseel, Y. lavaan: An R Package for Structural Equation Modeling. Journal of Statistical Software, 2012.", "[2] Hair, J. F. et al. Multivariate Data Analysis."))

result <- list(
  success = TRUE,
  name = "结构方程模型(SEM)",
  headers = if (length(path_rows) > 0) c("因变量", "自变量", "非标准化路径", "标准化路径", "Std. Err", "z", "p") else c("潜变量", "题项", "非标准化载荷", "标准化载荷", "Std. Err", "z", "p"),
  rows = if (length(path_rows) > 0) path_rows else loading_rows,
  description = smart,
  sections = sections
)

cat(jsonlite::toJSON(result, auto_unbox = TRUE, null = "null", force = TRUE, dataframe = "rows"))
