# 多因素方差分析 R 执行脚本：负责无交互主效应模型、主表和可选事后比较。
# Python 只做数据搬运，统计口径统一放在这里，别拆回后端方法里算。
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
  paste(
    readLines(path, warn = FALSE, encoding = "UTF-8"),
    collapse = "\n"
  )
}
fmt_num <- function(x, digits = 3) {
  if (is.null(x) || length(x) == 0 || is.na(x) || is.infinite(x)) {
    "\u2014"
  } else if (abs(x - round(x)) < 1e-12) {
    as.character(as.integer(round(x)))
  } else {
    sprintf(paste0("%.", digits, "f"), x)
  }
}
sig <- function(p) {
  if (is.null(p) || length(p) == 0 || is.na(p) || is.infinite(p)) {
    ""
  } else if (p < 0.001) {
    "***"
  } else if (p < 0.01) {
    "**"
  } else if (p < 0.05) {
    "*"
  } else {
    ""
  }
}
fmt_p <- function(p) {
  if (is.null(p) || length(p) == 0 || is.na(p) || is.infinite(p)) {
    "NaN"
  } else {
    paste0(sprintf("%.3f", p), sig(p))
  }
}
fmt_posthoc_p <- function(p) {
  if (is.null(p) || length(p) == 0 || is.na(p) || is.infinite(p)) {
    "NaN"
  } else if (p < 0.001) {
    paste0(sprintf("%.3f", p), "***")
  } else if (p < 0.01) {
    paste0(sprintf("%.3f", p), "**")
  } else if (p < 0.1) {
    paste0(sprintf("%.3f", p), "*")
  } else {
    sprintf("%.3f", p)
  }
}
sec_table <- function(
  title,
  headers,
  rows,
  note = NULL,
  description = NULL,
  header_rows = NULL
) {
  item <- list(type = "table", title = title, headers = headers, rows = rows)
  if (!is.null(note)) item$note <- note
  if (!is.null(description)) item$description <- description
  if (!is.null(header_rows)) item$headerRows <- header_rows
  item
}
sec_advice <- function(content, title = "分析建议") {
  list(type = "advice", title = title, content = content)
}
sec_smart <- function(content) {
  list(type = "smart_analysis", title = "智能分析", content = content)
}
sec_refs <- function(items) {
  list(type = "references", title = "参考文献", items = items)
}
normalize_posthoc <- function(method) {
  text <- tolower(as.character(method))
  if (grepl("bonf", text) || grepl("校正", text)) {
    "bonferroni"
  } else if (grepl("sidak", text)) {
    "sidak"
  } else if (grepl("tukey", text)) {
    "tukey"
  } else {
    "none"
  }
}

input <- jsonlite::fromJSON(read_utf8(input_path), simplifyVector = FALSE)
input_dir <- dirname(
  normalizePath(input_path, winslash = "/", mustWork = TRUE)
)
data_file <- file.path(input_dir, input$data_file)
if (!file.exists(data_file)) stop("missing input data file")

factors <- unlist(input$factors)
dependent <- input$dependent
covariates <- unlist(input$covariates)
if (is.null(covariates)) covariates <- character(0)
needed <- c(factors, dependent, covariates)

raw_df <- read.csv(data_file, stringsAsFactors = FALSE, check.names = FALSE)
data <- raw_df[, needed, drop = FALSE]
data[[dependent]] <- suppressWarnings(as.numeric(data[[dependent]]))
for (cov in covariates) {
  data[[cov]] <- suppressWarnings(as.numeric(data[[cov]]))
}
for (factor_name in factors) {
  data[[factor_name]] <- as.factor(data[[factor_name]])
}
data <- stats::na.omit(data)
if (nrow(data) < max(8, length(factors) * 4)) {
  cat(jsonlite::toJSON(
    list(success = FALSE, error = "有效样本不足。"),
    auto_unbox = TRUE,
    force = TRUE
  ))
  quit(status = 0)
}

term_names <- c(factors, covariates)
formula_text <- paste(
  sprintf("`%s`", dependent),
  "~",
  paste(sprintf("`%s`", term_names), collapse = " + ")
)
model <- stats::lm(stats::as.formula(formula_text), data = data)
aov_model <- stats::aov(stats::as.formula(formula_text), data = data)
drop_table <- stats::drop1(model, test = "F")
model_summary <- summary(model)
headers <- c(
  "项", "平方和", "自由度", "均方", "F", "P", "R\u00b2", "调整R\u00b2"
)
if (isTRUE(input$include_effect_size)) {
  headers <- c(headers, "\u03b7\u00b2", "partial \u03b7\u00b2")
}

df_error <- stats::df.residual(model)
ss_error <- sum(stats::residuals(model)^2)
ms_error <- ss_error / df_error
ss_terms <- sum(drop_table[term_names, "Sum of Sq"], na.rm = TRUE)

rows <- list()
old_contrasts <- options("contrasts")
options(contrasts = c("contr.sum", "contr.poly"))
intercept_model <- stats::lm(stats::as.formula(formula_text), data = data)
options(old_contrasts)
intercept_coef <- summary(intercept_model)$coefficients
if ("(Intercept)" %in% rownames(intercept_coef)) {
  df_intercept <- 1
  f_value <- intercept_coef["(Intercept)", "t value"] ^ 2
  p_value <- stats::pf(f_value, df_intercept, df_error, lower.tail = FALSE)
  ss_intercept <- f_value * ms_error * df_intercept
  ms_intercept <- ss_intercept / df_intercept
  intercept_row <- list(
    "截距",
    fmt_num(ss_intercept),
    fmt_num(df_intercept, 0),
    fmt_num(ms_intercept),
    fmt_num(f_value),
    fmt_p(p_value),
    fmt_num(model_summary$r.squared),
    fmt_num(model_summary$adj.r.squared)
  )
  if (isTRUE(input$include_effect_size)) {
    eta <- if ((ss_terms + ss_intercept) > 0) {
      ss_intercept / (ss_terms + ss_intercept)
    } else {
      NA
    }
    partial_eta <- if ((ss_intercept + ss_error) > 0) {
      ss_intercept / (ss_intercept + ss_error)
    } else {
      NA
    }
    intercept_row <- c(intercept_row, fmt_num(eta), fmt_num(partial_eta))
  }
  rows[[length(rows) + 1]] <- intercept_row
}
for (row_name in term_names) {
  ss <- drop_table[row_name, "Sum of Sq"]
  df_val <- drop_table[row_name, "Df"]
  ms <- ss / df_val
  f_value <- drop_table[row_name, "F value"]
  p_value <- drop_table[row_name, "Pr(>F)"]
  out <- list(
    row_name,
    fmt_num(ss),
    fmt_num(df_val, 0),
    fmt_num(ms),
    fmt_num(f_value),
    fmt_p(p_value),
    "",
    ""
  )
  if (isTRUE(input$include_effect_size)) {
    if (row_name == "Residuals") {
      out <- c(out, "", "")
    } else {
      eta <- if (ss_terms > 0) ss / ss_terms else NA
      partial_eta <- if ((ss + ss_error) > 0) {
        ss / (ss + ss_error)
      } else {
        NA
      }
      out <- c(out, fmt_num(eta), fmt_num(partial_eta))
    }
  }
  rows[[length(rows) + 1]] <- out
}
error_row <- list(
  "误差",
  fmt_num(ss_error),
  fmt_num(df_error, 0),
  fmt_num(ms_error),
  "\u2014",
  "NaN",
  "",
  ""
)
if (isTRUE(input$include_effect_size)) {
  error_row <- c(error_row, "", "")
}
rows[[length(rows) + 1]] <- error_row

line_for <- function(row) {
  name <- row[[1]]
  if (name == "误差") {
    NULL
  } else {
    p_text <- row[[6]]
    p_num <- suppressWarnings(as.numeric(gsub("\\*", "", p_text)))
    if (!is.na(p_num) && p_num < 0.05) {
      paste0(
        "对于变量", name,
        "，从F检验的结果分析可以得到，显著性P值为", p_text,
        "，水平上呈现显著性，对", dependent,
        "有显著性影响，存在主效应。"
      )
    } else {
      paste0(
        "对于变量", name,
        "，从F检验的结果分析可以得到，显著性P值为", p_text,
        "，水平上不呈现显著性，对", dependent,
        "没有显著性影响，不存在主效应。"
      )
    }
  }
}
smart_lines <- c(
  "多因素方差结果显示：",
  unlist(lapply(rows, line_for))
)
smart <- paste(smart_lines, collapse = "\n")
steps <- paste(c(
  paste0(
    "1. 可应用多因素方差分析的试验数据要符合严格的要求，",
    "它们一般来源于多类试验：完全组合试验和正交试验。"
  ),
  "2. 根据多因素方差结果判断是否存在主效应。",
  "3. 如存在主效应，可以进行事后多重分析进一步挖掘。"
), collapse = "\n")

sections <- list(
  sec_advice(smart, "分析结果"),
  sec_advice(steps, "分析步骤"),
  sec_table(
    "输出结果1：多因素方差分析结果",
    headers,
    rows,
    "* p<0.05 ** p<0.01 *** p<0.001",
    paste0(
      "上表展示了多因素方差分析的结果，",
      "主效应如果显著可以进一步分析事后多重分析结果。"
    )
  ),
  sec_smart(smart),
  sec_refs(c(
    paste0(
      "[1] 陈希孺, 倪国熙. 数理统计学教程[M]. ",
      "中国科学技术大学出版社, 2009."
    ),
    paste0(
      "[2] 茆诗松, 程依明, 濮晓龙. 概率论与数理统计教程[M]. ",
      "高等教育出版社, 2011."
    ),
    paste0(
      "[3] Montgomery D C. Design and Analysis of Experiments[M]. ",
      "John Wiley & Sons, 2019."
    ),
    paste0(
      "[4] Kutner M H, Nachtsheim C J, Neter J, Li W. ",
      "Applied Linear Statistical Models[M]. McGraw-Hill/Irwin, 2005."
    )
  ))
)

if (isTRUE(input$do_post_hoc)) {
  posthoc_method <- normalize_posthoc(input$post_hoc_method)
  posthoc_sections <- list()
  ci_multiplier <- stats::qt(0.975, df_error)
  append_pair_rows <- function(pair_rows, i_label, j_label, diff, se, p, ci) {
    pair_rows[[length(pair_rows) + 1]] <- list(
      i_label,
      j_label,
      fmt_num(diff),
      fmt_num(se),
      fmt_posthoc_p(p),
      fmt_num(ci[1]),
      fmt_num(ci[2])
    )
    pair_rows[[length(pair_rows) + 1]] <- list(
      j_label,
      i_label,
      fmt_num(-diff),
      fmt_num(se),
      fmt_posthoc_p(p),
      fmt_num(-ci[2]),
      fmt_num(-ci[1])
    )
    pair_rows
  }
  sort_pair_rows <- function(pair_rows) {
    if (length(pair_rows) <= 1) return(pair_rows)
    first <- vapply(pair_rows, function(row) row[[1]], character(1))
    second <- vapply(pair_rows, function(row) row[[2]], character(1))
    first_num <- suppressWarnings(as.numeric(first))
    second_num <- suppressWarnings(as.numeric(second))
    if (all(!is.na(first_num)) && all(!is.na(second_num))) {
      pair_rows[order(first_num, second_num)]
    } else {
      pair_rows[order(first, second)]
    }
  }
  welch_lsd_pair <- function(factor_name, level_i, level_j) {
    group_i <- data[data[[factor_name]] == level_i, dependent]
    group_j <- data[data[[factor_name]] == level_j, dependent]
    n_i <- length(group_i)
    n_j <- length(group_j)
    diff <- mean(group_i) - mean(group_j)
    estimable <- n_i >= 2 && n_j >= 2 && df_error > 0
    if (!estimable) {
      return(list(diff = diff, se = NA, p = NA, estimable = FALSE))
    }

    # SPSSPRO 事后表按当前因素原始组均值比较，标准误用两组各自方差，别改回主效应系数。
    se <- sqrt(stats::var(group_i) / n_i + stats::var(group_j) / n_j)
    if (!is.finite(se) || se <= 0) {
      return(list(diff = diff, se = NA, p = NA, estimable = FALSE))
    }

    t_value <- diff / se
    p_value <- if (is.finite(t_value)) {
      2 * stats::pt(abs(t_value), df_error, lower.tail = FALSE)
    } else {
      NA
    }
    list(diff = diff, se = se, p = p_value, estimable = TRUE)
  }
  for (factor_name in factors) {
    levels_vec <- levels(data[[factor_name]])
    if (length(levels_vec) < 2) next
    pair_rows <- list()
    if (posthoc_method == "tukey") {
      tukey <- tryCatch(
        stats::TukeyHSD(aov_model, which = factor_name)[[factor_name]],
        error = function(e) NULL
      )
      if (!is.null(tukey)) {
        for (pair_name in rownames(tukey)) {
          pieces <- strsplit(pair_name, "-")[[1]]
          pair_rows <- append_pair_rows(
            pair_rows,
            pieces[1],
            pieces[2],
            tukey[pair_name, "diff"],
            NA,
            tukey[pair_name, "p adj"],
            c(tukey[pair_name, "lwr"], tukey[pair_name, "upr"])
          )
        }
      }
    } else {
      pair_count <- choose(length(levels_vec), 2)
      for (i in seq_len(length(levels_vec) - 1)) {
        for (j in seq(i + 1, length(levels_vec))) {
          pair <- welch_lsd_pair(
            factor_name,
            levels_vec[i],
            levels_vec[j]
          )
          p_value <- pair$p
          if (pair$estimable && posthoc_method == "bonferroni") {
            p_value <- min(p_value * pair_count, 1)
          }
          if (pair$estimable && posthoc_method == "sidak") {
            p_value <- 1 - (1 - p_value) ^ pair_count
          }
          ci_low <- if (pair$estimable) {
            pair$diff - ci_multiplier * pair$se
          } else {
            NA
          }
          ci_high <- if (pair$estimable) {
            pair$diff + ci_multiplier * pair$se
          } else {
            NA
          }
          pair_rows <- append_pair_rows(
            pair_rows,
            levels_vec[i],
            levels_vec[j],
            pair$diff,
            pair$se,
            p_value,
            c(ci_low, ci_high)
          )
        }
      }
    }
    if (length(pair_rows) > 0) {
      pair_rows <- sort_pair_rows(pair_rows)
      posthoc_headers <- c(
        paste0(factor_name, "(I)"),
        paste0(factor_name, "(J)"),
        "平均值差值(I-J)",
        "标准误差",
        "P",
        "95%置信区间下限",
        "95%置信区间上限"
      )
      posthoc_header_rows <- list(
        list(
          list(text = paste0(factor_name, "(I)"), rowspan = 2),
          list(text = paste0(factor_name, "(J)"), rowspan = 2),
          list(text = "平均值差值(I-J)", rowspan = 2),
          list(text = "标准误差", rowspan = 2),
          list(text = "P", rowspan = 2),
          list(text = "95%置信区间", colspan = 2)
        ),
        list("下限", "上限")
      )
      title <- if (length(posthoc_sections) == 0) {
        "输出结果2：事后多重比较结果"
      } else {
        paste0(factor_name, "事后多重比较结果")
      }
      posthoc_sections[[length(posthoc_sections) + 1]] <- sec_table(
        title,
        posthoc_headers,
        pair_rows,
        NULL,
        paste0(
          "上表使用", input$post_hoc_method,
          "方法对", factor_name,
          "各水平之间的具体差异进行分析。"
        ),
        posthoc_header_rows
      )
    }
  }
  if (length(posthoc_sections) > 0) {
    refs <- sections[[length(sections)]]
    sections <- c(sections[-length(sections)], posthoc_sections, list(refs))
  }
}

result <- list(
  success = TRUE,
  name = "多因素方差分析",
  headers = headers,
  rows = rows,
  description = "多因素方差分析完成。",
  sections = sections
)
cat(jsonlite::toJSON(
  result,
  auto_unbox = TRUE,
  null = "null",
  force = TRUE,
  dataframe = "rows"
))
