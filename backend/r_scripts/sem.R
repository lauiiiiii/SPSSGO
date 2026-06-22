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

# P 值格式化：加显著性星标（对齐 SPSSPRO）
fmt_p <- function(p, digits = 3) {
  if (is.null(p) || length(p) == 0 || is.na(p)) return("\u2014")
  p_num <- as.numeric(p)
  star <- ""
  if (!is.na(p_num)) {
    if (p_num < 0.01) star <- "***"
    else if (p_num < 0.05) star <- "**"
    else if (p_num < 0.1) star <- "*"
  }
  # 接近 0 的 P 值：始终显示指定小数位数，而非简写为 "0"
  if (abs(p_num) < 1e-15) p_num <- 0
  paste0(sprintf(paste0("%.", digits, "f"), p_num), star)
}

# 因子名转中文标签（对齐 SPSSPRO）
factor_label <- function(fn, labels) {
  if (!is.null(labels) && !is.null(labels[[fn]])) return(labels[[fn]])
  fn  # fallback: return as-is
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
factor_labels <- input$factor_labels  # 中文标签映射，如 {"F1":"因子1"}
SIG_NOTE <- "\u6ce8\uff1a***\u3001**\u3001*\u5206\u522b\u4ee3\u88681%\u30015%\u300110%\u7684\u663e\u8457\u6027\u6c34\u5e73"  # "注：***、**、*分别代表1%、5%、10%的显著性水平"
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

# 检查列是否存在
missing_cols <- setdiff(variables, names(raw_df))
if (length(missing_cols) > 0) {
  cat(jsonlite::toJSON(list(success = FALSE, error = paste0("以下变量不存在：", paste(missing_cols, collapse = "、"), "。")), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

# 转换为数值型，并检查转换结果
for (col in variables) {
  original <- data[[col]]
  converted <- suppressWarnings(as.numeric(original))
  n_na_after <- sum(is.na(converted))
  n_na_before <- sum(is.na(original))
  if (n_na_after > n_na_before) {
    # 有非数值数据被转换为 NA
    non_numeric_count <- n_na_after - n_na_before
    cat(jsonlite::toJSON(list(success = FALSE, error = paste0(
      "变量 '", col, "' 包含 ", non_numeric_count, " 个非数值数据。请确保所有题项数据为数值型（如 1, 2, 3, 4, 5）。"
    )), auto_unbox = TRUE, force = TRUE))
    quit(status = 0)
  }
  data[[col]] <- converted
}

data <- stats::na.omit(data)
n_complete <- nrow(data)
n_vars <- length(variables)
min_required <- max(20, n_vars * 2)
if (n_complete < min_required) {
  n_raw <- nrow(raw_df)
  n_missing <- n_raw - n_complete
  cat(jsonlite::toJSON(list(success = FALSE, error = paste0(
    "SEM 有效样本不足。原始数据 ", n_raw, " 条，缺失删除 ", n_missing, " 条，剩余 ", n_complete, " 条完整数据，至少需要 ", min_required, " 条。"
  )), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

# ── 公用拟合函数（优先使用标记变量法 std.lv=FALSE，对齐 SPSSPRO/SPSSAU） ──
build_model_desc <- function(fm, fn, structural) {
  mlines <- c()
  for (f in fn) {
    mlines <- c(mlines, paste0(f, " =~ ", paste(fm[[f]], collapse = " + ")))
  }
  paste(c(mlines, structural), collapse = "\n")
}

try_fit_sem <- function(fm, fn, dat, structural) {
  desc <- build_model_desc(fm, fn, structural)
  fits <- list(
    list(name = "标记变量法", std.lv = FALSE),
    list(name = "标准化方差法", std.lv = TRUE),
    list(name = "MLR稳健", std.lv = TRUE, estimator = "MLR"),
    list(name = "强制收敛", std.lv = FALSE, control = list(optim.force.converged = TRUE))
  )
  for (a in fits) {
    call_args <- c(
      list(model = desc, data = dat, missing = "listwise", std.lv = a$std.lv),
      if (is.null(a$estimator)) list() else list(estimator = a$estimator),
      if (is.null(a$control)) list() else list(control = a$control)
    )
    fit <- tryCatch(
      do.call(lavaan::sem, call_args),
      error = function(e) e
    )
    if (inherits(fit, "error")) next
    conv <- tryCatch(lavaan::lavInspect(fit, "converged"), error = function(e) FALSE)
    if (isTRUE(conv)) return(list(fit = fit, desc = desc))
  }
  NULL
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

model_desc <- build_model_desc(factor_map, factor_names, structural_lines)

fit <- NULL
converged <- FALSE
# 记录实际使用的拟合方法，用于生成可复现 R 代码
estimation_method <- "sem(model, data = data, std.lv = FALSE, missing = \"listwise\")"
fit_attempts <- list(
  list(name = "标记变量法", std.lv = FALSE, call_str = "sem(model, data = data, std.lv = FALSE, missing = \"listwise\")"),
  list(name = "标准化方差法", std.lv = TRUE, call_str = "sem(model, data = data, std.lv = TRUE, missing = \"listwise\")"),
  list(name = "MLR稳健", std.lv = TRUE, estimator = "MLR", call_str = "sem(model, data = data, std.lv = TRUE, estimator = \"MLR\", missing = \"listwise\")"),
  list(name = "强制收敛", std.lv = FALSE, control = list(optim.force.converged = TRUE), call_str = "sem(model, data = data, std.lv = FALSE, missing = \"listwise\", control = list(optim.force.converged = TRUE))")
)

for (attempt in fit_attempts) {
  call_args <- c(
    list(model = model_desc, data = data, missing = "listwise", std.lv = attempt$std.lv),
    if (is.null(attempt$estimator)) list() else list(estimator = attempt$estimator),
    if (is.null(attempt$control)) list() else list(control = attempt$control)
  )
  fit <- tryCatch(
    do.call(lavaan::sem, call_args),
    error = function(e) e
  )
  if (inherits(fit, "error")) next
  converged <- tryCatch(lavaan::lavInspect(fit, "converged"), error = function(e) FALSE)
  if (isTRUE(converged)) {
    estimation_method <- attempt$call_str
    break
  }
}

# 拟合失败时，自动剔除完全共线变量后重试
dropped_vars <- c()
dropped_reasons <- list()

if (!inherits(fit, "lavaan") || !isTRUE(converged)) {
  # 定位零方差变量
  for (v in variables) {
    col_sd <- stats::sd(data[[v]], na.rm = TRUE)
    if (!is.na(col_sd) && col_sd < 1e-6) {
      dropped_vars <- c(dropped_vars, v)
      dropped_reasons[[v]] <- paste0("方差接近零")
    }
  }
  # 定位完全共线变量对
  if (n_vars >= 2) {
    cor_matrix <- tryCatch(stats::cor(data, use = "complete.obs"), error = function(e) NULL)
    if (!is.null(cor_matrix)) {
      for (i in seq_len(n_vars - 1)) {
        if (variables[i] %in% dropped_vars) next
        for (j in seq(i + 1, n_vars)) {
          if (variables[j] %in% dropped_vars) next
          r <- abs(cor_matrix[i, j])
          if (!is.na(r) && r >= 0.999) {
            dropped_vars <- c(dropped_vars, variables[j])
            dropped_reasons[[variables[j]]] <- paste0(
              "与 '", variables[i], "' 完全线性相关（|r|=", fmt_num(r, 4), "）"
            )
          }
        }
      }
    }
  }
  
  if (length(dropped_vars) > 0) {
    keep_vars <- variables[!variables %in% dropped_vars]
    if (length(keep_vars) >= 2) {
      # 重建 factor_map
      # 找出 structural_lines 中引用的因子，这些因子即使只剩1个题项也要保留
      referenced_factors <- c()
      for (sl in structural_lines) {
        parts <- strsplit(sl, " ~ ")[[1]]
        referenced_factors <- c(referenced_factors, trimws(parts[1]))
        preds <- strsplit(parts[2], " \\+ ")[[1]]
        referenced_factors <- c(referenced_factors, trimws(preds))
      }
      referenced_factors <- unique(referenced_factors)
      new_map <- list()
      for (fn in factor_names) {
        nv <- factor_map[[fn]][!factor_map[[fn]] %in% dropped_vars]
        # 被路径引用的因子保留（至少1个题项），其他因子需要至少2个
        min_required <- if (fn %in% referenced_factors) 1 else 2
        if (length(nv) >= min_required) new_map[[fn]] <- nv
      }
      if (length(new_map) >= 1) {
        new_data <- data[, keep_vars, drop = FALSE]
        new_fn <- names(new_map)
        # 过滤 structural_lines：只保留 new_fn 中存在的因子对应的路径
        new_structural <- structural_lines[sapply(structural_lines, function(sl) {
          dep <- strsplit(sl, " ~ ")[[1]][1]
          preds <- strsplit(strsplit(sl, " ~ ")[[1]][2], " \\+ ")[[1]]
          dep %in% new_fn && all(trimws(preds) %in% new_fn)
        })]
        if (length(new_structural) == 0 && length(new_fn) >= 2) {
          new_structural <- c(paste0(new_fn[length(new_fn)], " ~ ", paste(new_fn[-length(new_fn)], collapse = " + ")))
        }
        new_model_desc <- build_model_desc(new_map, new_fn, new_structural)
        # 用新数据重试拟合方式
        for (attempt in fit_attempts) {
          new_call_args <- c(
            list(model = new_model_desc, data = new_data, missing = "listwise", std.lv = attempt$std.lv),
            if (is.null(attempt$estimator)) list() else list(estimator = attempt$estimator),
            if (is.null(attempt$control)) list() else list(control = attempt$control)
          )
          fit <- tryCatch(
            do.call(lavaan::sem, new_call_args),
            error = function(e) e
          )
          if (inherits(fit, "error")) next
          converged <- tryCatch(lavaan::lavInspect(fit, "converged"), error = function(e) FALSE)
          if (isTRUE(converged)) {
            estimation_method <- attempt$call_str
            # 更新所有全局状态，后续结果提取基于新数据
            factor_map <- new_map
            factor_names <- new_fn
            structural_lines <- new_structural
            data <- new_data
            variables <- keep_vars
            n_vars <- length(variables)
            n_complete <- nrow(data)
            model_desc <- new_model_desc
            break
          }
        }
      }
    }
  }
}

if (!inherits(fit, "lavaan") || !isTRUE(converged)) {
  err_msg <- if (inherits(fit, "error")) {
    paste0("SEM 拟合失败：", fit$message)
  } else {
    "SEM 模型未收敛，已尝试 3 种估计方法均失败。可能原因：\n1. 样本量过小（建议 n > 题项数 × 5）；\n2. 题项与因子匹配不当，部分载荷接近零；\n3. 模型设定复杂度过高；\n4. 变量间相关性过低或存在多重共线性。\n建议：检查各题项间相关系数矩阵，或将观测变量合并/删减后重试。"
  }
  cat(jsonlite::toJSON(list(success = FALSE, error = err_msg), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

fit_measure <- tryCatch(
  lavaan::fitMeasures(fit, c("chisq", "df", "pvalue", "cfi", "tli", "rmsea", "srmr", "rmr", "gfi", "agfi", "nfi", "aic", "bic")),
  error = function(e) structure(rep(NA, 13), names = c("chisq", "df", "pvalue", "cfi", "tli", "rmsea", "srmr", "rmr", "gfi", "agfi", "nfi", "aic", "bic"))
)
chi2 <- unname(fit_measure["chisq"])
dof <- unname(fit_measure["df"])
cmin_df <- ifelse(!is.na(chi2) && !is.na(dof) && dof != 0, chi2 / dof, NA)

param_est <- lavaan::parameterEstimates(fit, standardized = TRUE)
loading_df <- param_est[param_est$op == "=~", ]
path_df <- param_est[param_est$op == "~" & param_est$lhs %in% factor_names & param_est$rhs %in% factor_names, ]
resid_df <- param_est[param_est$op == "~~" & param_est$lhs %in% variables & param_est$rhs %in% variables & param_est$lhs == param_est$rhs, ]
latent_cov_df <- param_est[param_est$op == "~~" & param_est$lhs %in% factor_names & param_est$rhs %in% factor_names, ]

loading_rows <- list()
prev_factor <- NA
for (i in seq_len(nrow(loading_df))) {
  row <- loading_df[i, ]
  z_val <- fmt_num(row$z, 4)
  se_val <- fmt_num(row$se, 4)
  # 标记变量（est=1, se=0, z=NA）: z、S.E.、p 都显示 —
  if (is.na(row$z)) {
    z_val <- "\u2014"
    se_val <- "\u2014"
  } else if (abs(row$se) < 1e-8) {
    se_val <- "\u2014"
  }
  cur_factor <- factor_label(as.character(row$lhs), factor_labels)
  # 只在每组第一行显示因子名，后续行留空
  if (!is.na(prev_factor) && prev_factor == cur_factor) {
    cur_factor <- ""
  }
  prev_factor <- factor_label(as.character(row$lhs), factor_labels)
  loading_rows[[length(loading_rows) + 1]] <- list(
    cur_factor,
    as.character(row$rhs),
    fmt_num(row$est, 4),
    fmt_num(row$std.all, 4),
    z_val,
    se_val,
    fmt_p(row$pvalue, 3)
  )
}

path_rows <- list()
for (i in seq_len(nrow(path_df))) {
  row <- path_df[i, ]
  path_rows[[length(path_rows) + 1]] <- list(
    factor_label(as.character(row$rhs), factor_labels), "\u2192",
    factor_label(as.character(row$lhs), factor_labels),
    fmt_num(row$est, 4), fmt_num(row$std.all, 4), fmt_num(row$se, 4), fmt_num(row$z, 4),
    fmt_p(row$pvalue, 3)
  )
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
  cr_ave_rows[[length(cr_ave_rows) + 1]] <- list(factor_label(factor_name, factor_labels), as.character(length(factor_map[[factor_name]])), fmt_num(cr, 4), fmt_num(ave, 4), fmt_num(sqrt_ave, 4))
}

latent_corr <- tryCatch(lavaan::lavInspect(fit, "cor.lv"), error = function(e) NULL)
fl_rows <- list()
if (!is.null(latent_corr)) {
  for (row_factor in factor_names) {
    row <- list(factor_label(row_factor, factor_labels))
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
  dv_rows[[length(dv_rows) + 1]] <- list(factor_label(factor_name, factor_labels), fmt_num(sqrt_ave, 4), fmt_num(max_corr, 4), ifelse(!is.na(sqrt_ave) && sqrt_ave > max_corr, "通过", "需关注"))
}

resid_rows <- list()
for (i in seq_len(nrow(resid_df))) {
  row <- resid_df[i, ]
  resid_rows[[length(resid_rows) + 1]] <- list(as.character(row$lhs), fmt_num(row$est, 4), fmt_num(row$std.all, 4), fmt_num(row$se, 4), fmt_num(row$z, 4), fmt_num(row$pvalue, 4))
}

latent_cov_rows <- list()
for (i in seq_len(nrow(latent_cov_df))) {
  row <- latent_cov_df[i, ]
  # 避免重复（对称矩阵只取 lhs < rhs 的对角线下方）
  if (as.character(row$lhs) >= as.character(row$rhs)) next
  latent_cov_rows[[length(latent_cov_rows) + 1]] <- list(
    factor_label(as.character(row$lhs), factor_labels), "\u2194",
    factor_label(as.character(row$rhs), factor_labels),
    fmt_num(row$est, 4), fmt_num(row$std.all, 4), fmt_num(row$se, 4), fmt_num(row$z, 4),
    fmt_p(row$pvalue, 3)
  )
}

endogenous <- unique(path_df$lhs)
score_rows <- list()
if (length(endogenous) > 0) {
  r2_vals <- tryCatch(lavaan::inspect(fit, "r2"), error = function(e) NULL)
  if (!is.null(r2_vals)) {
    for (name in names(r2_vals)) {
      score_rows[[length(score_rows) + 1]] <- list(factor_label(name, factor_labels), fmt_num(r2_vals[[name]], 4), "—", as.character(nrow(data)))
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
      effect_rows[[length(effect_rows) + 1]] <- list(factor_label(pred, factor_labels), factor_label(dep, factor_labels), fmt_num(direct[pred, dep], 4), fmt_num(indirect[pred, dep], 4), fmt_num(total[pred, dep], 4))
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
  list("χ²", fmt_num(chi2, 4)),
  list("df", fmt_num(dof, 0)),
  list("χ²/df", fmt_num(cmin_df, 4)),
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

# ── 路径图数据（用于前端渲染） ──
# 布局：多列纵向，因子少时单列，多了自动分2列或3列
# 每个因子的观测变量放在该因子右侧
path_nodes <- list()
node_positions <- list()

node_w <- 110
node_h <- 36
n_factors <- length(factor_names)

# 根据因子数量决定列数
if (n_factors <= 3) {
  n_cols <- 1
} else if (n_factors <= 6) {
  n_cols <- 2
} else {
  n_cols <- 3
}

# 每列因子数（尽量均匀分配）
factors_per_col <- ceiling(n_factors / n_cols)

# 布局参数
col_x_base <- 80        # 第一列因子 x 坐标
col_spacing <- 300      # 列间距
indicator_offset <- 180 # 观测变量相对因子的 x 偏移
factor_gap <- 130       # 同列因子纵向间距
indicator_gap <- 44     # 同因子内观测变量纵向间距

# 计算每个因子组的纵向空间
group_heights <- sapply(factor_names, function(fn) {
  n_obs <- length(factor_map[[fn]])
  max(node_h, n_obs * indicator_gap)
})

# 按列分配因子，计算每列高度
col_heights <- numeric(n_cols)
for (col in seq_len(n_cols)) {
  start_idx <- (col - 1) * factors_per_col + 1
  end_idx <- min(col * factors_per_col, n_factors)
  if (start_idx <= n_factors) {
    col_group_hs <- group_heights[start_idx:end_idx]
    col_heights[col] <- sum(col_group_hs) + (length(col_group_hs) - 1) * factor_gap + 60
  }
}
canvas_h <- max(max(col_heights), 400)
canvas_w <- col_x_base + (n_cols - 1) * col_spacing + node_w + indicator_offset + node_w + 40

# 放置因子和观测变量
for (col in seq_len(n_cols)) {
  start_idx <- (col - 1) * factors_per_col + 1
  end_idx <- min(col * factors_per_col, n_factors)
  if (start_idx > n_factors) break

  factor_x <- col_x_base + (col - 1) * col_spacing
  indicator_x <- factor_x + indicator_offset
  current_y <- 30

  for (i in start_idx:end_idx) {
    fn <- factor_names[i]
    node_label <- if (!is.null(factor_labels[[fn]])) factor_labels[[fn]] else fn
    group_h <- group_heights[i]

    # 因子节点（椭圆）
    factor_y <- current_y + (group_h - node_h) / 2
    path_nodes[[length(path_nodes) + 1]] <- list(
      key = fn,
      label = node_label,
      x = factor_x,
      y = factor_y,
      w = node_w,
      h = node_h,
      shape = "ellipse"
    )
    node_positions[[fn]] <- list(x = factor_x, y = factor_y)

    # 观测变量（矩形）放在因子右侧
    obs_vars <- factor_map[[fn]]
    n_obs <- length(obs_vars)
    obs_total_h <- n_obs * indicator_gap
    obs_start_y <- factor_y + (node_h - obs_total_h) / 2
    for (j in seq_along(obs_vars)) {
      v <- obs_vars[j]
      path_nodes[[length(path_nodes) + 1]] <- list(
        key = v,
        label = v,
        x = indicator_x,
        y = obs_start_y + (j - 1) * indicator_gap,
        w = node_w,
        h = node_h,
        shape = "rect"
      )
      node_positions[[v]] <- list(x = indicator_x, y = obs_start_y + (j - 1) * indicator_gap)
    }

    current_y <- current_y + group_h + factor_gap
  }
}

# 边：测量模型（因子→题项）+ 结构模型（因子→因子）
path_edges <- list()

# 测量模型边
for (fn in factor_names) {
  for (v in factor_map[[fn]]) {
    from_pos <- node_positions[[fn]]
    to_pos <- node_positions[[v]]
    if (is.null(from_pos) || is.null(to_pos)) next
    # 获取载荷值
    loading_row <- loading_df[loading_df$lhs == fn & loading_df$rhs == v, ]
    value <- if (nrow(loading_row) > 0) paste0("β=", fmt_num(loading_row$std.all[1], 3)) else ""
    sig <- if (nrow(loading_row) > 0 && !is.na(loading_row$pvalue[1]) && loading_row$pvalue[1] < 0.05) TRUE else FALSE
    path_edges[[length(path_edges) + 1]] <- list(
      from = fn,
      to = v,
      value = value,
      significant = sig
    )
  }
}

# 结构模型边
for (i in seq_len(nrow(path_df))) {
  row <- path_df[i, ]
  from <- as.character(row$rhs)
  to <- as.character(row$lhs)
  from_pos <- node_positions[[from]]
  to_pos <- node_positions[[to]]
  if (is.null(from_pos) || is.null(to_pos)) next
  value <- paste0("β=", fmt_num(row$std.all, 3))
  sig <- !is.na(row$pvalue) && row$pvalue < 0.05
  path_edges[[length(path_edges) + 1]] <- list(
    from = from,
    to = to,
    value = value,
    significant = sig
  )
}

model_path_data <- list(
  chartType = "model_path",
  title = "模型路径图",
  nodes = path_nodes,
  edges = path_edges,
  width = canvas_w,
  height = canvas_h
)

# ── 构建输出 sections（对齐 SPSSPRO 格式） ─

# 1. 模型结果（公式展示，使用中文标签）
model_formula <- paste0(
  "测量模型：\n",
  paste(sapply(factor_names, function(fn) {
    paste0(factor_label(fn, factor_labels), " =~ ", paste(factor_map[[fn]], collapse = " + "))
  }), collapse = "\n"),
  "\n\n结构模型：\n",
  paste(sapply(structural_lines, function(sl) {
    # 将 "F3 ~ F1 + F2" 中的因子名替换为中文标签
    parts <- strsplit(sl, " ~ ")[[1]]
    lhs_label <- factor_label(parts[1], factor_labels)
    rhs_parts <- strsplit(parts[2], " \\+ ")[[1]]
    rhs_labels <- sapply(rhs_parts, function(x) factor_label(trimws(x), factor_labels))
    paste0(lhs_label, " ~ ", paste(rhs_labels, collapse = " + "))
  }), collapse = "\n")
)
if (length(dropped_vars) > 0) {
  model_formula <- paste0(
    "【自动剔除共线变量】以下变量因完全共线或零方差被自动剔除：",
    paste(sapply(dropped_vars, function(v) paste0("'", v, "'（", dropped_reasons[[v]], "）")), collapse = "；"),
    "。\n\n",
    model_formula
  )
}
model_result_section <- list(
  type = "text",
  title = "模型结果",
  content = model_formula
)

# ── 智能分析（分三段，分别放在对应表格后面） ──
loading_smart_parts <- c()
path_smart_parts <- c()
fit_smart_parts <- c()

# 1）因子载荷解读
loading_smart_parts <- c(loading_smart_parts, paste0("本次分析共包含", length(factor_names), "个潜变量，合计", length(variables), "个观测指标。表中所列标准化载荷系数（Std.Estimate）衡量各观测指标对其所属潜变量的贡献程度。"))
loading_smart_parts <- c(loading_smart_parts, "根据Hair等（2010）的建议，标准化载荷系数绝对值应不低于0.5，理想状态下应达到0.7以上。若载荷系数低于0.5，表明该题项对潜变量的解释力不足，可考虑予以删除或修正。")

for (fn in factor_names) {
  fn_loadings <- loading_df[loading_df$lhs == fn, ]
  fn_label <- factor_label(fn, factor_labels)
  n_items <- nrow(fn_loadings)
  # 所有题项的载荷（包括标记变量）
  all_std <- abs(fn_loadings$std.all)
  all_std <- all_std[!is.na(all_std)]
  loading_min <- if (length(all_std) > 0) min(all_std) else NA
  loading_max <- if (length(all_std) > 0) max(all_std) else NA

  valid_idx <- which(!is.na(fn_loadings$z))
  loading_smart_parts <- c(loading_smart_parts, paste0(
    "【", fn_label, "】该潜变量共纳入", n_items, "个测量指标，"
  ))
  if (length(valid_idx) > 0) {
    valid_ld <- fn_loadings[valid_idx, ]
    sig_count <- sum(valid_ld$pvalue < 0.05, na.rm = TRUE)
    avg_std <- mean(abs(valid_ld$std.all), na.rm = TRUE)

    # 统计各级别载荷项数
    ideal_count <- sum(abs(valid_ld$std.all) >= 0.7, na.rm = TRUE)
    acceptable_count <- sum(abs(valid_ld$std.all) >= 0.5 & abs(valid_ld$std.all) < 0.7, na.rm = TRUE)
    weak_count <- sum(abs(valid_ld$std.all) < 0.5, na.rm = TRUE)

    loading_smart_parts <- c(loading_smart_parts, paste0(
      "标准化载荷系数范围为", fmt_num(loading_min, 3), "~", fmt_num(loading_max, 3), "，",
      "平均载荷系数", fmt_num(avg_std, 3), "。其中", sig_count, "个指标通过显著性检验（P<0.05）。"
    ))

    # 逐题项分析
    for (row_i in seq_len(nrow(fn_loadings))) {
      ld_row <- fn_loadings[row_i, ]
      v_name <- as.character(ld_row$rhs)
      coef_val <- ld_row$std.all
      p_val <- ld_row$pvalue
      is_marker <- is.na(ld_row$z)

      if (is_marker) {
        loading_smart_parts <- c(loading_smart_parts, paste0(
          "  指标\"", v_name, "\"为参照指标（标记变量），其非标准化载荷固定为1，",
          "标准化载荷系数", fmt_num(coef_val, 3), "，不作显著性检验。"
        ))
      } else {
        abs_coef <- abs(coef_val)
        sig_text <- if (!is.na(p_val) && p_val < 0.05) paste0("通过显著性检验（P=", fmt_p(p_val, 3), "）") else paste0("未通过显著性检验（P=", fmt_p(p_val, 3), "）")
        loading_smart_parts <- c(loading_smart_parts, paste0(
          "  指标\"", v_name, "\"：标准化载荷系数", fmt_num(coef_val, 3), "，",
          if (abs_coef >= 0.5) {
            if (abs_coef >= 0.7) {
              paste0("表明该题项对\"", fn_label, "\"的解释力很强，是构成该潜变量的核心指标，")
            } else {
              paste0("表明该题项对\"", fn_label, "\"具有较好的代表性，")
            }
          } else {
            paste0("低于0.5的建议阈值，对\"", fn_label, "\"的解释力不足，建议结合修正指数（MI）考虑是否保留该题项，")
          },
          sig_text, "。"
        ))
      }
    }

    # 整体评价
    loading_smart_parts <- c(loading_smart_parts, paste0(
      "  综合评价：", fn_label, "的平均载荷为", fmt_num(avg_std, 3), "，",
      if (avg_std >= 0.7) {
        "整体测量质量非常好，各题项均较好地反映了该潜变量的构念内涵。"
      } else if (avg_std >= 0.5) {
        paste0("整体测量质量可接受。", if (weak_count > 0) paste0("但", weak_count, "个题项载荷低于0.5，建议重点关注并考虑是否删除或修正。") else "各题项均达到可接受水平。")
      } else {
        "整体测量质量有待提升，较多题项载荷偏低，建议审视该潜变量的测量结构，考虑删减弱项或重新设计题项。"
      }
    ))

  } else {
    loading_smart_parts <- c(loading_smart_parts, paste0(
      "标准化载荷系数范围为", fmt_num(loading_min, 3), "~", fmt_num(loading_max, 3), "。",
      "所有题项均为标记变量，无法进行显著性检验，各项载荷系数均需结合理论和修正指数进一步评估。"
    ))
  }

  # 题项数过少的警告
  if (n_items <= 2) {
    loading_smart_parts <- c(loading_smart_parts, paste0(
      "   注意：", fn_label, "仅包含", n_items, "个题项，题项数偏少可能导致模型识别困难或参数估计不稳定。",
      "理想的潜变量应至少包含3个测量指标。建议在后续研究中增加题项数量。"
    ))
  }
}

# 2）结构路径解读
if (nrow(path_df) > 0) {
  path_smart_parts <- c(path_smart_parts, "结构模型反映了潜变量之间的因果关系，标准化路径系数（β）衡量自变量潜变量对因变量潜变量的直接影响大小。P值用于检验该路径系数是否显著不为零。")
  for (i in seq_len(nrow(path_df))) {
    p_row <- path_df[i, ]
    p_rhs <- factor_label(as.character(p_row$rhs), factor_labels)
    p_lhs <- factor_label(as.character(p_row$lhs), factor_labels)
    p_val <- p_row$pvalue
    coef_std <- fmt_num(p_row$std.all, 3)
    if (is.na(p_val) || p_val < 0.05) {
      direction <- if (p_row$std.all > 0) "正向" else "负向"
      path_smart_parts <- c(path_smart_parts, paste0(
        "路径\"", p_rhs, "\"→\"", p_lhs, "\"：标准化路径系数β=", coef_std, "，P=", fmt_p(p_val, 3), "（<0.05），",
        "表明", p_rhs, "对", p_lhs, "具有显著的", direction, "影响。在其他条件不变的情况下，", p_rhs, "每增加1个标准差单位，", p_lhs, "预期变动", coef_std, "个标准差单位。"
      ))
    } else {
      path_smart_parts <- c(path_smart_parts, paste0(
        "路径\"", p_rhs, "\"→\"", p_lhs, "\"：标准化路径系数β=", coef_std, "，P=", fmt_p(p_val, 3), "（≥0.05），",
        "未通过显著性检验，表明", p_rhs, "对", p_lhs, "的直接效应不显著，该路径在统计意义上不支持。"
      ))
    }
  }
}

# 3）模型拟合评价
rmsea_val <- unname(fit_measure["rmsea"])
cfi_val <- unname(fit_measure["cfi"])
gfi_val <- unname(fit_measure["gfi"])
tli_val <- unname(fit_measure["tli"])
srmr_val <- unname(fit_measure["rmr"])
fit_smart_parts <- c(fit_smart_parts, "模型整体拟合指标是判断所设结构方程模型是否可被接受的重要依据。常用的评价标准参见模型拟合指标表中的参考标准行。")
fit_judge <- c()
if (!is.na(rmsea_val) && rmsea_val < 0.08) {
  fit_judge <- c(fit_judge, paste0("RMSEA=", fmt_num(rmsea_val, 3), "（＜0.08，良好）"))
} else if (!is.na(rmsea_val)) {
  fit_judge <- c(fit_judge, paste0("RMSEA=", fmt_num(rmsea_val, 3), "（≥0.08，欠佳）"))
}
if (!is.na(cfi_val) && cfi_val > 0.9) {
  fit_judge <- c(fit_judge, paste0("CFI=", fmt_num(cfi_val, 3), "（>0.9，良好）"))
} else if (!is.na(cfi_val)) {
  fit_judge <- c(fit_judge, paste0("CFI=", fmt_num(cfi_val, 3), "（≤0.9，欠佳）"))
}
if (!is.na(gfi_val) && gfi_val > 0.9) {
  fit_judge <- c(fit_judge, paste0("GFI=", fmt_num(gfi_val, 3), "（>0.9，良好）"))
} else if (!is.na(gfi_val)) {
  fit_judge <- c(fit_judge, paste0("GFI=", fmt_num(gfi_val, 3), "（≤0.9，欠佳）"))
}
if (!is.na(tli_val) && tli_val > 0.9) {
  fit_judge <- c(fit_judge, paste0("TLI=", fmt_num(tli_val, 3), "（>0.9，良好）"))
} else if (!is.na(tli_val)) {
  fit_judge <- c(fit_judge, paste0("TLI=", fmt_num(tli_val, 3), "（≤0.9，欠佳）"))
}
if (length(fit_judge) > 0) {
  fit_smart_parts <- c(fit_smart_parts, paste0("本模型拟合结果：", paste(fit_judge, collapse = "；"), "。"))
} else {
  fit_smart_parts <- c(fit_smart_parts, "拟合指标详见模型拟合指标表。")
}

loading_smart_section <- sec_smart(paste(loading_smart_parts, collapse = "\n"))
path_smart_section <- sec_smart(paste(path_smart_parts, collapse = "\n"))
fit_smart_section <- sec_smart(paste(fit_smart_parts, collapse = "\n"))

# ── 各表 section 带图表说明 ──

# 2. 结构方程模型拟合指标（基本信息表）
basic_info_rows <- list(
  list("样本量", as.character(nrow(data))),
  list("题项数", as.character(length(variables))),
  list("潜变量数", as.character(length(factor_names))),
  list("结构路径数", as.character(nrow(path_df))),
  list("χ²", fmt_num(chi2, 4)),
  list("df", fmt_num(dof, 0)),
  list("p", fmt_num(unname(fit_measure["pvalue"]), 4))
)
fit_basic_section <- sec_table("结构方程模型拟合指标", c("指标", "值"), basic_info_rows,
  description = "上表列示了样本量、题项与潜变量数量、结构路径数以及模型χ²检验的基本信息。χ²检验的P值若大于0.05，表明模型隐含的协方差矩阵与样本协方差矩阵无显著差异，模型拟合良好；但χ²对样本量敏感，大样本下易显著，需结合其它拟合指标综合判断。")

# 3. 因子载荷系数表
loading_section <- sec_table("因子载荷系数表", c("\u56e0\u5b50", "\u53d8\u91cf", "\u975e\u6807\u51c6\u8f7d\u8377\u7cfb\u6570", "\u6807\u51c6\u5316\u8f7d\u8377\u7cfb\u6570", "z", "S.E.", "P"), loading_rows, note = SIG_NOTE,
  description = "上表展示了各潜变量与其观测指标之间的因子载荷系数。每个潜变量的第一个指标被设为参照指标（标记变量），其非标准化载荷固定为1，因此不提供标准误与显著性检验结果。标准化载荷系数反映观测指标对潜变量的相对重要性，一般认为标准化载荷系数≥0.5可接受，≥0.7较为理想。")

# 4. 模型拟合指标（横向格式，对齐 SPSSPRO；含参考标准行）
fit_index_row <- list(
  fmt_num(chi2, 3),
  fmt_num(dof, 0),
  ifelse(!is.na(unname(fit_measure["pvalue"])) && unname(fit_measure["pvalue"]) < 0.05, "<0.05", fmt_num(unname(fit_measure["pvalue"]), 3)),
  fmt_num(cmin_df, 3),
  fmt_num(unname(fit_measure["gfi"]), 3),
  fmt_num(unname(fit_measure["rmsea"]), 3),
  fmt_num(unname(fit_measure["rmr"]), 3),
  fmt_num(unname(fit_measure["cfi"]), 3),
  fmt_num(unname(fit_measure["nfi"]), 3),
  fmt_num(unname(fit_measure["tli"]), 3)
)
fit_index_ref_row <- list(
  "\u2014", "\u2014", ">0.05", "<3", ">0.9", "<0.10", "<0.05", ">0.9", ">0.9", ">0.9"
)
fit_index_section <- sec_table("模型拟合指标", c("\u03c7\u00b2", "df", "P", "\u5361\u65b9\u81ea\u7531\u5ea6\u6bd4", "GFI", "RMSEA", "RMR", "CFI", "NFI", "NNFI"), list(fit_index_ref_row, fit_index_row), note = SIG_NOTE,
  description = "上表第二行为常用拟合指标的参考标准，第三行为本次模型的拟合结果。χ²/df＜3表明模型简约性可接受；GFI、CFI、NFI、NNFI均大于0.9表明模型拟合良好；RMSEA＜0.08表明近似误差在可接受范围；RMR＜0.05表明残差均方根较小，模型拟合较好。若多个指标同时未达标准，建议参考模型修正建议（MI）对模型进行调整。")

# 5. 模型回归系数表（结构路径）
path_section <- sec_table("模型回归系数表", c("Factor(\u6f5c\u53d8\u91cf)", "\u2192", "\u5206\u6790\u9879(\u663e\u53d8\u91cf)", "\u975e\u6807\u51c6\u5316\u7cfb\u6570", "\u6807\u51c6\u5316\u7cfb\u6570", "\u6807\u51c6\u8bef", "Z", "P"), path_rows, note = SIG_NOTE,
  description = "上表展示了路径节点的回归系数，可类比为一元线性回归的系数估计。标准化路径系数（β）反映了自变量变化1个标准差时因变量标准差的预期变动量，系数的正负号代表影响方向。P值用于检验该路径系数是否显著不为零：若P<0.05，则拒绝原假设，认为该路径具有统计学意义；若P≥0.05，则表明该路径的直接效应不显著。")

# 6. 路径节点协方差关系表
latent_cov_section <- sec_table("路径节点协方差关系表", c("\u56e0\u5b50A", "\u2194", "\u56e0\u5b50B", "\u975e\u6807\u51c6\u4f30\u8ba1\u7cfb\u6570", "\u6807\u51c6\u4f30\u8ba1\u7cfb\u6570", "\u6807\u51c6\u8bef", "z", "P"), latent_cov_rows, note = SIG_NOTE,
  description = "上表展示了潜变量之间的协方差（相关）关系。标准化协方差系数反映了两个潜变量之间的关联强度。若标准化系数较高且通过显著性检验，说明因子间存在较强的相关关系，可考虑根据理论依据在模型中添加相关路径以改善拟合。")

# 7. 参考文献
refs_section <- sec_refs(c("[1] Rosseel, Y. lavaan: An R Package for Structural Equation Modeling. Journal of Statistical Software, 2012.", "[2] Hair, J. F. et al. Multivariate Data Analysis."))

# ── 可复现 R 代码（用于增加分析透明度） ──
r_code_model_lines <- c()
for (fn in factor_names) {
  r_code_model_lines <- c(r_code_model_lines, paste0("  ", fn, " =~ ", paste(factor_map[[fn]], collapse = " + ")))
}
for (sl in structural_lines) {
  r_code_model_lines <- c(r_code_model_lines, paste0("  ", sl))
}
r_code_model_block <- paste(r_code_model_lines, collapse = "\n")

r_code <- paste0(
  "library(lavaan)\n\n",
  "# 读取数据（请将 \"your_data.csv\" 替换为实际数据文件路径）\n",
  "data <- read.csv(\"your_data.csv\")\n\n",
  "# 模型设定\n",
  "model <- '\n",
  r_code_model_block,
  "\n'\n\n",
  "# 拟合（本次分析实际使用的拟合方法）\n",
  "fit <- ", estimation_method, "\n\n",
  "# 查看结果\n",
  "summary(fit, standardized = TRUE, fit.measures = TRUE)\n",
  "parameterEstimates(fit, standardized = TRUE)"
)
if (length(dropped_vars) > 0) {
  r_code <- paste0(
    "# 注意：以下变量因共线性/零方差被自动剔除：",
    paste(dropped_vars, collapse = "、"),
    "\n",
    r_code
  )
}

model_path_section <- list(type = "model_path", title = "模型路径图", chart = model_path_data)

sections <- list(
  model_result_section,
  model_path_section,
  fit_basic_section,
  loading_section,
  loading_smart_section,
  fit_index_section,
  fit_smart_section,
  path_section,
  path_smart_section,
  latent_cov_section,
  list(type = "code", title = "可复现 R 代码", content = r_code, language = "R", description = "以下为本次分析实际执行的 R 代码，可直接复制到 R 环境中复现结果。数据文件请自行替换。"),
  refs_section
)

# 更多分析（折叠区）
more_sections <- list()
if (length(cr_ave_rows) > 0) more_sections[[length(more_sections) + 1]] <- sec_table("聚合效度与组合信度", c("潜变量", "题项数", "CR", "AVE", "sqrt(AVE)"), cr_ave_rows)
fl_headers <- c("潜变量", sapply(factor_names, function(x) factor_label(x, factor_labels)))
if (length(fl_rows) > 0) more_sections[[length(more_sections) + 1]] <- sec_table("Fornell-Larcker 判据", fl_headers, fl_rows, "对角线为 sqrt(AVE)，非对角线为潜变量相关。")
if (length(dv_rows) > 0) more_sections[[length(more_sections) + 1]] <- sec_table("判别效度结论", c("因子", "sqrt(AVE)", "最大相关系数", "判别效度"), dv_rows)
if (length(score_rows) > 0) more_sections[[length(more_sections) + 1]] <- sec_table("内生潜变量解释力", c("潜变量", "R²", "调整后 R²", "样本量"), score_rows)
if (length(effect_rows) > 0) more_sections[[length(more_sections) + 1]] <- sec_table("直接效应/间接效应/总效应", c("自变量", "因变量", "直接效应", "间接效应", "总效应"), effect_rows)
if (length(mi_rows) > 0) more_sections[[length(more_sections) + 1]] <- sec_table("模型修正建议（MI）", c("建议参数", "MI", "EPC", "建议"), mi_rows, "修正指数越高，说明释放该参数可能显著改善模型拟合；但必须结合理论判断。")

result <- list(
  success = TRUE,
  name = "结构方程模型 (SEM)",
  # 主结果固定展示因子载荷，结构路径系数在 sections 的"模型回归系数表"里，避免重复输出
  headers = c("\u56e0\u5b50", "\u53d8\u91cf", "\u975e\u6807\u51c6\u8f7d\u8377\u7cfb\u6570", "\u6807\u51c6\u5316\u8f7d\u8377\u7cfb\u6570", "z", "S.E.", "P"),
  rows = loading_rows,
  description = "",
  sections = sections,
  more_sections = more_sections,
  r_code = r_code
)

cat(jsonlite::toJSON(result, auto_unbox = TRUE, null = "null", force = TRUE, dataframe = "rows"))
