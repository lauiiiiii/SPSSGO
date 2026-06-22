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

fmt_num_trim <- function(x, digits = 3) {
  if (is.null(x) || length(x) == 0 || is.na(x) || is.infinite(x)) {
    return("\u2014")
  }
  if (abs(x - round(x)) < 1e-12) {
    return(as.character(as.integer(round(x))))
  }
  sub("\\.?0+$", "", sprintf(paste0("%.", digits, "f"), x))
}

fmt_p <- function(p) {
  if (is.null(p) || length(p) == 0 || is.na(p) || is.infinite(p)) {
    return("-")
  }
  stars <- if (p < 0.01) {
    "***"
  } else if (p < 0.05) {
    "**"
  } else if (p < 0.1) {
    "*"
  } else {
    ""
  }
  paste0(sprintf("%.3f", p), stars)
}

fmt_p_plain <- function(p) {
  if (is.null(p) || length(p) == 0 || is.na(p) || is.infinite(p)) {
    return("-")
  }
  sprintf("%.3f", p)
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

emit_error <- function(message) {
  cat(jsonlite::toJSON(
    list(success = FALSE, error = message),
    auto_unbox = TRUE,
    force = TRUE
  ))
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
  emit_error("请至少为一个因子放入题项。")
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
  emit_error("请至少为一个因子放入题项。")
  quit(status = 0)
}
if (length(variables) < 3) {
  emit_error("至少需要3个题项。")
  quit(status = 0)
}

data <- raw_df[, variables, drop = FALSE]
for (col in variables) data[[col]] <- suppressWarnings(as.numeric(data[[col]]))
data <- stats::na.omit(data)
if (nrow(data) < 5) {
  emit_error("有效样本不足。")
  quit(status = 0)
}

model_lines <- c()
for (factor_name in names(factor_map)) {
  model_lines <- c(
    model_lines,
    paste0(
      factor_name,
      " =~ ",
      paste(factor_map[[factor_name]], collapse = " + ")
    )
  )
}
second_order_model <- isTRUE(input$second_order_model)
second_order_models <- list()
has_second_order_models <- !is.null(input$second_order_models) &&
  length(input$second_order_models) > 0
if (has_second_order_models) {
  for (model in input$second_order_models) {
    model_name <- if (!is.null(model$name) && nzchar(model$name)) {
      model$name
    } else {
      paste0("二阶模型", length(second_order_models) + 1)
    }
    selected_members <- unlist(model$members)
    selected_members <- selected_members[
      selected_members %in% names(factor_map)
    ]
    second_order_models[[length(second_order_models) + 1]] <- list(
      name = model_name,
      members = selected_members
    )
  }
} else {
  second_order_factor <- if (
    !is.null(input$second_order_factor) &&
      nzchar(input$second_order_factor)
  ) {
    input$second_order_factor
  } else {
    "二阶模型1"
  }
  second_order_members <- names(factor_map)
  if (!is.null(input$second_order_members)) {
    selected_members <- unlist(input$second_order_members)
    selected_members <- selected_members[
      selected_members %in% names(factor_map)
    ]
    if (length(selected_members) > 0) {
      second_order_members <- selected_members
    }
  }
  second_order_models[[1]] <- list(
    name = second_order_factor,
    members = second_order_members
  )
}
second_order_model_names <- if (length(second_order_models) > 0) {
  paste(
    vapply(second_order_models, function(model) model$name, character(1)),
    collapse = "、"
  )
} else {
  "二阶模型1"
}
if (second_order_model && length(factor_map) >= 2) {
  for (model in second_order_models) {
    if (length(model$members) < 2) {
      emit_error(paste0(model$name, " 至少需要选择2个一阶因子。"))
      quit(status = 0)
    }
    model_lines <- c(
      model_lines,
      paste0(model$name, " =~ ", paste(model$members, collapse = " + "))
    )
  }
}
model_desc <- paste(model_lines, collapse = "\n")

fit <- tryCatch(
  lavaan::cfa(model_desc, data = data, std.lv = FALSE, missing = "listwise"),
  error = function(e) e
)
if (inherits(fit, "error")) {
  emit_error(paste0("CFA 拟合失败：", fit$message))
  quit(status = 0)
}

fit_measure_names <- c(
  "chisq", "df", "pvalue", "cfi", "tli", "rmsea",
  "srmr", "gfi", "agfi", "nfi", "aic", "bic"
)
fit_measure <- lavaan::fitMeasures(fit, fit_measure_names)
chi2 <- unname(fit_measure["chisq"])
dof <- unname(fit_measure["df"])
cmin_df <- ifelse(!is.na(chi2) && !is.na(dof) && dof != 0, chi2 / dof, NA)

param_est <- lavaan::parameterEstimates(fit, standardized = TRUE)
loading_df <- param_est[param_est$op == "=~", ]
second_order_names <- vapply(
  second_order_models,
  function(model) model$name,
  character(1)
)
first_order_loading_df <- loading_df[
  loading_df$lhs %in% names(factor_map) &
    loading_df$rhs %in% variables,
]
second_order_loading_df <- loading_df[
  loading_df$lhs %in% second_order_names &
    loading_df$rhs %in% names(factor_map),
]
loading_headers <- c(
  "因子", "变量", "非标准载荷系数", "标准化载荷系数", "z", "S.E.", "P"
)
loading_rows <- list()
for (i in seq_len(nrow(first_order_loading_df))) {
  row <- first_order_loading_df[i, ]
  loading_rows[[length(loading_rows) + 1]] <- list(
    as.character(row$lhs),
    as.character(row$rhs),
    fmt_num_trim(row$est, 3),
    fmt_num_trim(row$std.all, 3),
    ifelse(is.na(row$z), "-", fmt_num_trim(row$z, 3)),
    ifelse(
      is.na(row$z),
      "-",
      ifelse(is.na(row$se), "-", fmt_num_trim(row$se, 3))
    ),
    fmt_p(row$pvalue)
  )
}
second_order_loading_headers <- c(
  "二阶模型", "一阶因子", "非标准载荷系数", "标准化载荷系数",
  "z", "S.E.", "P"
)
second_order_loading_rows <- list()
for (i in seq_len(nrow(second_order_loading_df))) {
  row <- second_order_loading_df[i, ]
  second_order_loading_rows[[length(second_order_loading_rows) + 1]] <- list(
    as.character(row$lhs),
    as.character(row$rhs),
    fmt_num_trim(row$est, 3),
    fmt_num_trim(row$std.all, 3),
    ifelse(is.na(row$z), "-", fmt_num_trim(row$z, 3)),
    ifelse(
      is.na(row$z),
      "-",
      ifelse(is.na(row$se), "-", fmt_num_trim(row$se, 3))
    ),
    fmt_p(row$pvalue)
  )
}

first_order_cov_df <- param_est[
  param_est$op == "~~" &
    param_est$lhs %in% names(factor_map) &
    param_est$rhs %in% names(factor_map),
]
covariance_names <- if (second_order_model && length(second_order_names) > 1) {
  second_order_names
} else {
  names(factor_map)
}
latent_cov_df <- param_est[
  param_est$op == "~~" &
    param_est$lhs %in% covariance_names &
    param_est$rhs %in% covariance_names,
]
latent_cov_rows <- list()
for (i in seq_len(nrow(latent_cov_df))) {
  row <- latent_cov_df[i, ]
  if (as.character(row$lhs) == as.character(row$rhs)) {
    next
  }
  latent_cov_rows[[length(latent_cov_rows) + 1]] <- list(
    as.character(row$lhs),
    as.character(row$rhs),
    fmt_num_trim(row$est, 3),
    fmt_num_trim(row$se, 3),
    ifelse(is.na(row$z), "-", fmt_num_trim(row$z, 3)),
    fmt_p(row$pvalue),
    fmt_num_trim(row$std.all, 3)
  )
}

resid_var_df <- param_est[
  param_est$op == "~~" &
    param_est$lhs %in% variables &
    param_est$rhs %in% variables &
    param_est$lhs == param_est$rhs,
]
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
  factor_loadings <- first_order_loading_df[
    first_order_loading_df$lhs == factor_name,
  ]
  std_loadings <- as.numeric(factor_loadings$std.all)
  std_loadings <- std_loadings[!is.na(std_loadings)]
  err_vars <- 1 - std_loadings^2
  sum_load <- sum(std_loadings)
  sum_load_sq <- sum(std_loadings^2)
  sum_err <- sum(err_vars)
  cr <- ifelse(
    (sum_load^2 + sum_err) > 0,
    (sum_load^2) / (sum_load^2 + sum_err),
    NA
  )
  ave <- ifelse(
    (sum_load_sq + sum_err) > 0,
    sum_load_sq / (sum_load_sq + sum_err),
    NA
  )
  sqrt_ave <- ifelse(!is.na(ave) && ave >= 0, sqrt(ave), NA)
  sqrt_ave_map[[factor_name]] <- sqrt_ave
  cr_ave_rows[[length(cr_ave_rows) + 1]] <- list(
    factor_name,
    fmt_num_trim(ave, 3),
    fmt_num_trim(cr, 3)
  )
}

factor_order <- names(factor_map)
latent_corr <- tryCatch(
  lavaan::lavInspect(fit, "cor.lv"),
  error = function(e) NULL
)
fl_rows <- list()
htmt_rows <- list()
if (!is.null(latent_corr)) {
  for (row_index in seq_along(factor_order)) {
    row_factor <- factor_order[row_index]
    row <- list(row_factor)
    for (col_index in seq_along(factor_order)) {
      col_factor <- factor_order[col_index]
      if (row_index == col_index) {
        row <- c(row, list(fmt_num_trim(sqrt_ave_map[[row_factor]], 3)))
      } else if (row_index > col_index) {
        cov_match <- first_order_cov_df[
          ((first_order_cov_df$lhs == row_factor &
              first_order_cov_df$rhs == col_factor) |
             (first_order_cov_df$lhs == col_factor &
                first_order_cov_df$rhs == row_factor)) &
            first_order_cov_df$lhs != first_order_cov_df$rhs,
        ]
        p_text <- if (nrow(cov_match) > 0) fmt_p(cov_match$pvalue[1]) else "-"
        row <- c(
          row,
          list(paste0(
            fmt_num_trim(latent_corr[row_factor, col_factor], 3),
            "(", p_text, ")"
          ))
        )
      } else {
        row <- c(row, list(""))
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
  dv_rows[[length(dv_rows) + 1]] <- list(
    factor_name,
    fmt_num(sqrt_ave, 4),
    fmt_num(max_corr, 4),
    ifelse(!is.na(sqrt_ave) && sqrt_ave > max_corr, "通过", "需关注")
  )
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

fit_headers <- c(
  "常用指标", "X²", "df", "P", "卡方自由度比",
  "GFI", "RMSEA", "RMR", "CFI", "NFI", "NNFI"
)
fit_rows <- list(
  list(
    "判断标准",
    "-", "-", ">0.05", "<3", ">0.9", "<0.10",
    "<0.05", ">0.9", ">0.9", ">0.9"
  ),
  list(
    "值",
    fmt_num_trim(chi2, 3),
    fmt_num_trim(dof, 0),
    fmt_p_plain(unname(fit_measure["pvalue"])),
    fmt_num_trim(cmin_df, 3),
    fmt_num_trim(unname(fit_measure["gfi"]), 3),
    fmt_num_trim(unname(fit_measure["rmsea"]), 3),
    fmt_num_trim(unname(fit_measure["srmr"]), 3),
    fmt_num_trim(unname(fit_measure["cfi"]), 3),
    fmt_num_trim(unname(fit_measure["nfi"]), 3),
    fmt_num_trim(unname(fit_measure["tli"]), 3)
  )
)

sections <- list()
summary_rows <- list()
summary_headers <- c("Factor", "数量")
for (factor_name in factor_order) {
  summary_rows[[length(summary_rows) + 1]] <- list(
    factor_name,
    as.character(length(factor_map[[factor_name]]))
  )
}
summary_rows[[length(summary_rows) + 1]] <- list(
  "汇总",
  as.character(length(variables))
)
summary_rows[[length(summary_rows) + 1]] <- list(
  "分析样本量",
  as.character(nrow(data))
)
summary_desc <- paste(
  "上表展示样本频数统计，包括各因子的字段频数、总计、总样本频数。",
  "CFA分析要求样本量至少是因子内个别量表的5倍以上，",
  "一般情况下至少需要200个样本。",
  sep = "\n"
)
summary_smart <- paste0(
  "本数据集共有因子数量", length(factor_order), "个，变量数", length(variables),
  "个，样本数", nrow(data),
  ifelse(
    second_order_model,
    paste0("，并设置", second_order_model_names, "作为二阶因子。"),
    "。"
  ),
  ifelse(nrow(data) >= 200, "满足常见样本量建议。", "不满足验证性因子分析基本数据要求。")
)

loading_desc <- paste(
  "上表为模型的因子载荷系数表，包括潜变量、分析项、非标准载荷系数、z检验结果等。",
  "因子载荷系数对因子内测量变量进行筛选，",
  "一般来说，测量变量通过显著性检验(P<0.05)，",
  "且标准化载荷系数值大于0.6，可表明测量变量符合因子要求，",
  "条件差距太大可以考虑删除变量。",
  "如果测量关系良好，通常来说，标准化载荷系数值基本上均会大于0.6。",
  sep = "\n"
)

loading_smart_lines <- c("由因子载荷系数表可知：")
for (factor_name in factor_order) {
  factor_loadings <- first_order_loading_df[
    first_order_loading_df$lhs == factor_name,
  ]
  good_items <- factor_loadings$rhs[
    !is.na(factor_loadings$std.all) & factor_loadings$std.all >= 0.6
  ]
  sig_items <- factor_loadings$rhs[
    !is.na(factor_loadings$pvalue) & factor_loadings$pvalue < 0.05
  ]
  if (length(good_items) > 0) {
    loading_smart_lines <- c(loading_smart_lines, paste0(
      "因子（", factor_name, "）的测量项（",
      paste(good_items, collapse = "、"),
      "）标准化载荷系数较高，可认为具有足够的方差解释率表现在同一因子上。"
    ))
  } else if (length(sig_items) > 0) {
    loading_smart_lines <- c(loading_smart_lines, paste0(
      "因子（", factor_name, "）的测量项通过显著性检验，但标准化载荷仍需重点关注。"
    ))
  }
}

second_order_loading_desc <- paste(
  "上表展示二阶模型对一阶因子的载荷关系。",
  "标准化载荷越高，说明该一阶因子越能代表对应二阶模型。",
  "二阶模型下，一阶因子之间的共同变异主要由二阶因子解释。",
  sep = "\n"
)
second_order_smart_lines <- c("二阶因子载荷系数表显示：")
for (row in second_order_loading_rows) {
  std_value <- suppressWarnings(as.numeric(row[[4]]))
  level <- ifelse(
    !is.na(std_value) && abs(std_value) >= 0.7,
    "较强",
    ifelse(!is.na(std_value) && abs(std_value) >= 0.5, "中等", "较弱")
  )
  second_order_smart_lines <- c(
    second_order_smart_lines,
    paste0(
      row[[2]], "归属于", row[[1]], "，标准化载荷为",
      row[[4]], "，代表性", level, "。"
    )
  )
}

model_desc_text <- paste(
  "上表展示了模型AVE和CR指标结果，根据平均公因子方差抽取量（AVE）与组合信度（CR）结果可以用于表示因子内对变量的聚合效度。",
  "一般来说AVE高于0.5或CR高于0.7表明聚合效度较高，只需要看其中一个即可。",
  "AVE（平均提取方差值）：是统计学中检验结构变量内部一致性的统计量。",
  "CR（Construct Reliability）：结构信度，",
  "反映了每个潜变量中所有题目是否一致性地解释该潜变量，",
  "当该值高于0.70时表示该潜变量具有较好的建构信度。",
  sep = "\n"
)
model_smart_lines <- c("模型AVE和CR的检验结果显示：")
for (row in cr_ave_rows) {
  model_smart_lines <- c(model_smart_lines, paste0(
    "基于", row[[1]], "，平均方差抽取量（AVE）的值为", row[[2]],
    ifelse(suppressWarnings(as.numeric(row[[2]])) >= 0.5, "，大于0.5", "，小于0.5"),
    "，组合信度CR值为", row[[3]], "，大于0.7，说明因子内的测量指标提取",
    ifelse(suppressWarnings(as.numeric(row[[2]])) >= 0.5, "优秀。", "较好。")
  ))
}

cor_title <- if (second_order_model) {
  "潜变量相关与AVE平方根值"
} else {
  "Pearson相关与AVE平方根值"
}
cor_label <- if (second_order_model) {
  "潜变量相关系数"
} else {
  "Pearson相关系数"
}
fl_desc <- paste(
  paste0("上表展示了因子间", cor_label, "与AVE平方根值的结果。"),
  "该表用于研究因子的区分效度是否表现较优秀。",
  "斜对角线是平均方差抽取量的平方根，用于表明因子内部的相关性强度。",
  paste0(
    "若因子的平均方差抽取量（AVE）的平方根大于其他因子的",
    cor_label,
    "，则说明其具有较为优秀的区分效度。"
  ),
  sep = "\n"
)

fit_desc <- paste(
  "上表展示了模型的拟合指标，可以适当选择一些指标进行评价，若所有指标均不满足，可以考虑根据2、3对因子的测量指标进行删除或者重构。",
  "常用指标包括卡方自由度比、GFI、RMSEA、RMR、CFI、NFI和NNFI。其它的一些指标通常使用较少，可结合实际情况进行选择使用即可。",
  "卡方和自由度df主要用于比较多个模型，卡方值越小越好，自由度反映了模型的复杂程度，模型越简单，自由度越多，反之，模型越复杂，自由度越少。",
  "GFI（拟合优度指数）：主要是运用列定系数和回归标准差，",
  "检验模型对样本观测值的拟合程度。",
  "其值在0-1之间，越接近0表示拟合越差。",
  "GFI>0.9，认为模型拟合较好。",
  "RMSEA（近似误差均方根）：一般情况下，RMSEA在0.1以下（越小越好）。",
  "RMR（均方根残差）：该指标通过测量预测相关和实际观察相关的平均残差，衡量模型的拟合程度。如果RMR<0.1，则认为模型拟合较好。",
  "CFI（比较拟合指数）：该指数在对假设模型和独立模型比较时，",
  "其值在0-1之间，越接近0表示拟合越差，越接近1表示拟合越好。",
  "一般情况，CFI≥0.9，认为模型拟合较好。",
  "NNFI（非规范拟合系数）和CFI(比较拟合指数)：其值越大越好，所拟合的模型表现较好。",
  sep = "\n"
)

cov_title <- if (second_order_model && length(second_order_names) > 1) {
  "二阶模型协方差表"
} else {
  "因子协方差表"
}
cov_left_header <- if (second_order_model && length(second_order_names) > 1) {
  "模型A"
} else {
  "因子A"
}
cov_right_header <- if (second_order_model && length(second_order_names) > 1) {
  "模型B"
} else {
  "因子B"
}
cov_desc <- paste(
  "上表展示了协方差分析结果，包括非标准系数、标准误、z检验值、显著性P值、标准系数。",
  "可通过标准系数分析两个潜变量之间的关联性。",
  "标准系数值一般越接近1，说明两个潜变量之间关联性越强。",
  ifelse(
    second_order_model,
    "二阶模型下，优先查看二阶因子载荷；多个二阶模型时再查看二阶模型协方差。",
    ""
  ),
  sep = "\n"
)
cov_smart_lines <- c("协方差分析的结果显示：")
for (row in latent_cov_rows) {
  std_value <- suppressWarnings(as.numeric(row[[7]]))
  level <- ifelse(
    !is.na(std_value) && abs(std_value) >= 0.7,
    "较强",
    ifelse(!is.na(std_value) && abs(std_value) >= 0.4, "中等", "较弱")
  )
  cov_smart_lines <- c(
    cov_smart_lines,
    paste0(
      row[[1]], "与", row[[2]], "标准估计系数为",
      row[[7]], "，呈现", level, "的关联性。"
    )
  )
}

# ── 可复现 R 代码（用于增加分析透明度） ──
r_code_model_lines <- c()
for (fn in names(factor_map)) {
  r_code_model_lines <- c(r_code_model_lines, paste0("  ", fn, " =~ ", paste(factor_map[[fn]], collapse = " + ")))
}
if (second_order_model) {
  for (model in second_order_models) {
    r_code_model_lines <- c(r_code_model_lines, paste0("  ", model$name, " =~ ", paste(model$members, collapse = " + ")))
  }
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
  "# 拟合\n",
  "fit <- cfa(model, data = data, std.lv = FALSE, missing = \"listwise\")\n\n",
  "# 查看结果\n",
  "summary(fit, standardized = TRUE, fit.measures = TRUE)\n",
  "parameterEstimates(fit, standardized = TRUE)"
)

sections[[length(sections) + 1]] <- sec_table(
  "输出结果1：因子基本汇总表",
  summary_headers,
  summary_rows,
  summary_desc
)
sections[[length(sections) + 1]] <- sec_smart(summary_smart)
sections[[length(sections) + 1]] <- sec_table(
  "输出结果2：因子载荷系数表",
  loading_headers,
  loading_rows,
  loading_desc,
  "注：***、**、*分别代表1%、5%、10%的显著性水平"
)
sections[[length(sections) + 1]] <- sec_smart(
  paste(loading_smart_lines, collapse = "\n")
)
result_index <- 3
if (second_order_model && length(second_order_loading_rows) > 0) {
  sections[[length(sections) + 1]] <- sec_table(
    paste0("输出结果", result_index, "：二阶因子载荷系数表"),
    second_order_loading_headers,
    second_order_loading_rows,
    second_order_loading_desc,
    "注：***、**、*分别代表1%、5%、10%的显著性水平"
  )
  sections[[length(sections) + 1]] <- sec_smart(
    paste(second_order_smart_lines, collapse = "\n")
  )
  result_index <- result_index + 1
}
sections[[length(sections) + 1]] <- sec_table(
  paste0("输出结果", result_index, "：模型评价"),
  c("Factor", "平均方差萃取AVE值", "组合信度CR值"),
  cr_ave_rows,
  model_desc_text
)
sections[[length(sections) + 1]] <- sec_smart(
  paste(model_smart_lines, collapse = "\n")
)
result_index <- result_index + 1
if (length(fl_rows) > 0) {
  sections[[length(sections) + 1]] <- sec_table(
    paste0("输出结果", result_index, "：", cor_title),
    c("", factor_order),
    fl_rows,
    fl_desc,
    paste(
      "注：***、**、*分别代表1%、5%、10%的显著性水平",
      "斜对角线数字为该因子AVE的根号值"
    )
  )
  result_index <- result_index + 1
}
sections[[length(sections) + 1]] <- sec_table(
  paste0("输出结果", result_index, "：模型拟合指标"),
  fit_headers,
  fit_rows,
  fit_desc,
  "注：***、**、*分别代表1%、5%、10%的显著性水平"
)
result_index <- result_index + 1
if (length(latent_cov_rows) > 0) {
  sections[[length(sections) + 1]] <- sec_table(
    paste0("输出结果", result_index, "：", cov_title),
    c(
      cov_left_header, cov_right_header, "非标准估计系数", "标准误",
      "z", "P", "标准估计系数"
    ),
    latent_cov_rows,
    cov_desc,
    "注：***、**、*分别代表1%、5%、10%的显著性水平"
  )
  sections[[length(sections) + 1]] <- sec_smart(
    paste(cov_smart_lines, collapse = "\n")
  )
}

fit_issue <- c()
if (!is.na(cmin_df) && cmin_df >= 3) fit_issue <- c(fit_issue, "卡方自由度比偏高")
if (!is.na(unname(fit_measure["cfi"])) &&
      unname(fit_measure["cfi"]) < 0.9) {
  fit_issue <- c(fit_issue, "CFI 偏低")
}
if (!is.na(unname(fit_measure["rmsea"])) &&
      unname(fit_measure["rmsea"]) >= 0.1) {
  fit_issue <- c(fit_issue, "RMSEA 偏高")
}
if (!is.na(unname(fit_measure["srmr"])) &&
      unname(fit_measure["srmr"]) >= 0.08) {
  fit_issue <- c(fit_issue, "SRMR 偏高")
}

smart <- paste0(
  "对选中题项进行了 ", length(factor_order), " 因子",
  ifelse(second_order_model, "二阶", ""),
  "验证性因子分析。模型拟合结果为：CFI=",
  fmt_num(unname(fit_measure["cfi"]), 3),
  "，TLI=",
  fmt_num(unname(fit_measure["tli"]), 3),
  "，RMSEA=",
  fmt_num(unname(fit_measure["rmsea"]), 3),
  "，SRMR=",
  fmt_num(unname(fit_measure["srmr"]), 3),
  "。"
)
if (length(fit_issue) > 0) {
  smart <- paste0(smart, " 当前需重点关注：", paste(fit_issue, collapse = "、"), "。")
} else {
  smart <- paste0(smart, " 主要拟合指标整体较为稳定。")
}
sections[[length(sections) + 1]] <- list(type = "text", title = "可复现 R 代码", content = r_code, description = "以下为本次分析实际执行的 R 代码，可直接复制到 R 环境中复现结果。数据文件请自行替换。")
sections[[length(sections) + 1]] <- sec_refs(c(
  paste(
    "[1] Rosseel, Y. lavaan: An R Package for Structural",
    "Equation Modeling. Journal of Statistical Software, 2012."
  ),
  "[2] Hair, J. F. et al. Multivariate Data Analysis."
))

result <- list(
  success = TRUE,
  name = "验证性因子分析",
  headers = loading_headers,
  rows = loading_rows,
  description = smart,
  sections = sections,
  r_code = r_code
)

cat(jsonlite::toJSON(
  result,
  auto_unbox = TRUE,
  null = "null",
  force = TRUE,
  dataframe = "rows"
))
