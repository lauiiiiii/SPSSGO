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
  if (is.null(x) || length(x) == 0 || is.na(x) || is.infinite(x)) {
    return("\u2014")
  }
  if (abs(x - round(x)) < 1e-12) {
    return(as.character(as.integer(round(x))))
  }
  sprintf(paste0("%.", digits, "f"), x)
}

sec_table <- function(title, headers, rows, description = NULL, note = NULL) {
  item <- list(type = "table", title = title, headers = headers, rows = rows)
  if (!is.null(description)) item$description <- description
  if (!is.null(note)) item$note <- note
  item
}

sec_smart <- function(content) {
  list(type = "smart_analysis", title = "智能分析", content = content)
}

sec_advice <- function(content, title = "分析建议") {
  list(type = "advice", title = title, content = content)
}

sec_refs <- function(items) {
  list(type = "references", title = "参考文献", items = items)
}

input <- jsonlite::fromJSON(read_utf8(input_path), simplifyVector = FALSE)
input_dir <- dirname(normalizePath(input_path, winslash = "/", mustWork = TRUE))
data_file <- file.path(input_dir, input$data_file)
if (!file.exists(data_file)) {
  stop("missing input data file")
}

raw_df <- read.csv(data_file, stringsAsFactors = FALSE, check.names = FALSE)
factor_names <- names(input$factor_map)
if (length(factor_names) == 0) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "请至少为一个因子放入题项。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

factor_map <- list()
variables <- c()
for (factor_name in factor_names) {
  cols <- unlist(input$factor_map[[factor_name]])
  cols <- cols[cols %in% names(raw_df)]
  if (length(cols) >= 2) {
    factor_map[[factor_name]] <- cols
    variables <- unique(c(variables, cols))
  }
}

if (length(factor_map) == 0) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "请至少为一个因子放入题项。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}
if (length(variables) < 3) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "至少需要3个题项。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

data <- raw_df[, variables, drop = FALSE]
for (col in variables) data[[col]] <- suppressWarnings(as.numeric(data[[col]]))
data <- stats::na.omit(data)
if (nrow(data) < 5) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "有效样本不足。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

model_lines <- c()
for (factor_name in names(factor_map)) {
  model_lines <- c(model_lines, paste0(factor_name, " =~ ", paste(factor_map[[factor_name]], collapse = " + ")))
}
model_desc <- paste(model_lines, collapse = "\n")

fit <- tryCatch(
  lavaan::cfa(model_desc, data = data, std.lv = TRUE, missing = "listwise"),
  error = function(e) e
)
if (inherits(fit, "error")) {
  cat(jsonlite::toJSON(list(success = FALSE, error = paste0("CFA 拟合失败：", fit$message)), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

fit_measure_names <- c("chisq", "df", "pvalue", "cfi", "tli", "rmsea", "srmr", "gfi", "agfi", "nfi", "aic", "bic")
fit_measure <- lavaan::fitMeasures(fit, fit_measure_names)
chi2 <- unname(fit_measure["chisq"])
dof <- unname(fit_measure["df"])
cmin_df <- ifelse(!is.na(chi2) && !is.na(dof) && dof != 0, chi2 / dof, NA)

param_est <- lavaan::parameterEstimates(fit, standardized = TRUE)
loading_df <- param_est[param_est$op == "=~", ]
loading_headers <- c("因子", "题项", "非标准化载荷", "标准化载荷", "Std. Err", "z-value", "p-value")
loading_rows <- list()
for (i in seq_len(nrow(loading_df))) {
  row <- loading_df[i, ]
  loading_rows[[length(loading_rows) + 1]] <- list(
    as.character(row$lhs),
    as.character(row$rhs),
    fmt_num(row$est, 4),
    fmt_num(row$std.all, 4),
    fmt_num(row$se, 4),
    fmt_num(row$z, 4),
    fmt_num(row$pvalue, 4)
  )
}

latent_cov_df <- param_est[param_est$op == "~~" & param_est$lhs %in% names(factor_map) & param_est$rhs %in% names(factor_map), ]
latent_cov_rows <- list()
for (i in seq_len(nrow(latent_cov_df))) {
  row <- latent_cov_df[i, ]
  latent_cov_rows[[length(latent_cov_rows) + 1]] <- list(
    as.character(row$lhs),
    as.character(row$rhs),
    fmt_num(row$est, 4),
    fmt_num(row$std.all, 4),
    fmt_num(row$se, 4),
    fmt_num(row$z, 4),
    fmt_num(row$pvalue, 4)
  )
}

resid_var_df <- param_est[param_est$op == "~~" & param_est$lhs %in% variables & param_est$rhs %in% variables & param_est$lhs == param_est$rhs, ]
resid_rows <- list()
for (i in seq_len(nrow(resid_var_df))) {
  row <- resid_var_df[i, ]
  resid_rows[[length(resid_rows) + 1]] <- list(
    as.character(row$lhs),
    fmt_num(row$est, 4),
    fmt_num(row$std.all, 4),
    fmt_num(row$se, 4),
    fmt_num(row$z, 4),
    fmt_num(row$pvalue, 4)
  )
}

cr_ave_rows <- list()
sqrt_ave_map <- list()
for (factor_name in names(factor_map)) {
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

factor_order <- names(factor_map)
latent_corr <- tryCatch(lavaan::lavInspect(fit, "cor.lv"), error = function(e) NULL)
fl_rows <- list()
htmt_rows <- list()
if (!is.null(latent_corr)) {
  for (row_factor in factor_order) {
    row <- list(row_factor)
    for (col_factor in factor_order) {
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
for (factor_name in factor_order) {
  others <- factor_order[factor_order != factor_name]
  max_corr <- 0
  if (!is.null(latent_corr) && length(others) > 0) {
    max_corr <- max(abs(latent_corr[factor_name, others]))
  }
  sqrt_ave <- sqrt_ave_map[[factor_name]]
  dv_rows[[length(dv_rows) + 1]] <- list(factor_name, fmt_num(sqrt_ave, 4), fmt_num(max_corr, 4), ifelse(!is.na(sqrt_ave) && sqrt_ave > max_corr, "通过", "需关注"))
}

mi <- tryCatch(lavaan::modindices(fit), error = function(e) NULL)
mi_rows <- list()
if (!is.null(mi) && nrow(mi) > 0) {
  mi <- mi[order(-mi$mi), ]
  top_n <- min(10, nrow(mi))
  for (i in seq_len(top_n)) {
    row <- mi[i, ]
    mi_rows[[length(mi_rows) + 1]] <- list(
      paste(as.character(row$lhs), as.character(row$op), as.character(row$rhs)),
      fmt_num(row$mi, 3),
      fmt_num(row$epc, 4),
      "可结合理论判断是否释放该参数"
    )
  }
}

fit_headers <- c("指标", "值")
fit_rows <- list(
  list("样本量", as.character(nrow(data))),
  list("题项数", as.character(length(variables))),
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

sections <- list()
summary_rows <- list()
for (factor_name in factor_order) {
  summary_rows[[length(summary_rows) + 1]] <- list(factor_name, as.character(length(factor_map[[factor_name]])))
}
summary_rows[[length(summary_rows) + 1]] <- list("汇总", as.character(length(variables)))
summary_rows[[length(summary_rows) + 1]] <- list("分析样本量", as.character(nrow(data)))

sections[[length(sections) + 1]] <- sec_table("输出结果1：因子基本汇总表", c("Factor", "数量"), summary_rows, "上表展示了各因子题项数量与分析样本量。")
sections[[length(sections) + 1]] <- sec_table("输出结果2：因子载荷系数表", loading_headers, loading_rows, "标准化载荷通常希望大于 0.5。", "注：P<0.05 通常表示路径达到显著水平。")
sections[[length(sections) + 1]] <- sec_table("输出结果3：模型评价", c("因子", "题项数", "CR", "AVE", "sqrt(AVE)"), cr_ave_rows, "可用于检查聚合效度与内部一致性。")
if (length(fl_rows) > 0) sections[[length(sections) + 1]] <- sec_table("输出结果4：Pearson相关与AVE平方根值", c("因子", factor_order), fl_rows, "对角线为 sqrt(AVE)，非对角线为潜变量相关系数。")
sections[[length(sections) + 1]] <- sec_table("输出结果5：模型拟合指标", fit_headers, fit_rows, "通常结合 CFI、TLI、RMSEA、SRMR 等指标综合判断模型拟合情况。")
sections[[length(sections) + 1]] <- sec_table("输出结果6：因子协方差表", c("因子A", "因子B", "协方差", "标准化相关", "Std. Err", "z-value", "p-value"), latent_cov_rows)
sections[[length(sections) + 1]] <- sec_table("误差方差", c("题项", "误差方差", "标准化误差方差", "Std. Err", "z-value", "p-value"), resid_rows)
sections[[length(sections) + 1]] <- sec_table("判别效度结论", c("因子", "sqrt(AVE)", "最大相关系数", "判别效度"), dv_rows)
if (length(mi_rows) > 0) sections[[length(sections) + 1]] <- sec_table("模型修正建议（MI）", c("建议参数", "MI", "EPC", "建议"), mi_rows, "修正指数越高，说明释放该参数可能显著改善模型拟合；但必须结合理论判断。")

fit_issue <- c()
if (!is.na(cmin_df) && cmin_df >= 3) fit_issue <- c(fit_issue, "卡方自由度比偏高")
if (!is.na(unname(fit_measure["cfi"])) && unname(fit_measure["cfi"]) < 0.9) fit_issue <- c(fit_issue, "CFI 偏低")
if (!is.na(unname(fit_measure["rmsea"])) && unname(fit_measure["rmsea"]) >= 0.1) fit_issue <- c(fit_issue, "RMSEA 偏高")
if (!is.na(unname(fit_measure["srmr"])) && unname(fit_measure["srmr"]) >= 0.08) fit_issue <- c(fit_issue, "SRMR 偏高")

smart <- paste0(
  "对选中题项进行了 ", length(factor_order), " 因子验证性因子分析。模型拟合结果为：CFI=",
  fmt_num(unname(fit_measure["cfi"]), 3), "，TLI=", fmt_num(unname(fit_measure["tli"]), 3),
  "，RMSEA=", fmt_num(unname(fit_measure["rmsea"]), 3), "，SRMR=", fmt_num(unname(fit_measure["srmr"]), 3), "。"
)
if (length(fit_issue) > 0) {
  smart <- paste0(smart, " 当前需重点关注：", paste(fit_issue, collapse = "、"), "。")
} else {
  smart <- paste0(smart, " 主要拟合指标整体较为稳定。")
}
sections[[length(sections) + 1]] <- sec_smart(smart)
sections[[length(sections) + 1]] <- sec_advice(paste(
  "验证性因子分析用于检验预设测量模型是否成立。",
  "通常希望标准化载荷大于 0.5，CFI/TLI 越接近 1 越好，RMSEA/SRMR 越小越好。",
  "修正指数只能作为辅助线索，不能替代理论判断。",
  sep = "\n"
))
sections[[length(sections) + 1]] <- sec_refs(c(
  "[1] Rosseel, Y. lavaan: An R Package for Structural Equation Modeling. Journal of Statistical Software, 2012.",
  "[2] Hair, J. F. et al. Multivariate Data Analysis."
))

result <- list(
  success = TRUE,
  name = "验证性因子分析",
  headers = loading_headers,
  rows = loading_rows,
  description = smart,
  sections = sections
)

cat(jsonlite::toJSON(result, auto_unbox = TRUE, null = "null", force = TRUE, dataframe = "rows"))
