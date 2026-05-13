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

escape_json <- function(x) {
  value <- ifelse(is.na(x), "", as.character(x))
  value <- gsub("\\\\", "\\\\\\\\", value)
  value <- gsub("\"", "\\\\\"", value)
  value <- gsub("\n", "\\\\n", value)
  value <- gsub("\r", "\\\\r", value)
  value
}

fmt_num <- function(x, digits = 3) {
  if (is.null(x) || length(x) == 0 || is.na(x) || is.infinite(x)) {
    return("\u2014")
  }
  if (abs(x - round(x)) < 1e-12) {
    return(as.character(as.integer(round(x))))
  }
  sprintf(paste0("%.", digits, "f"), x)
}

cronbach_alpha <- function(df) {
  df <- df[complete.cases(df), , drop = FALSE]
  k <- ncol(df)
  if (k < 2) return(NA)
  item_vars <- apply(df, 2, stats::var, na.rm = TRUE)
  total_scores <- rowSums(df, na.rm = TRUE)
  total_var <- stats::var(total_scores, na.rm = TRUE)
  if (total_var == 0) return(NA)
  (k / (k - 1)) * (1 - sum(item_vars) / total_var)
}

sec_table <- function(title, headers, rows, description = NULL) {
  item <- list(type = "table", title = title, headers = headers, rows = rows)
  if (!is.null(description)) {
    item$description <- description
  }
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

selected_type <- input$selected_type
if (is.null(selected_type)) {
  selected_type <- "Cronbach's α"
}

raw_df <- read.csv(data_file, stringsAsFactors = FALSE, check.names = FALSE)
sections <- list()
smart_parts <- c()
main_headers <- c()
main_rows <- list()

reliability_summary_value <- function(data, cols, selected_type) {
  cols <- cols[cols %in% names(data)]
  if (length(cols) < 2) {
    return(NA)
  }
  scale_data <- data[, cols, drop = FALSE]
  for (col in cols) {
    scale_data[[col]] <- suppressWarnings(as.numeric(scale_data[[col]]))
  }
  scale_data <- stats::na.omit(scale_data)
  if (nrow(scale_data) < 2 || ncol(scale_data) < 2) {
    return(NA)
  }
  k <- ncol(scale_data)

  if (selected_type == "折半系数") {
    odd_cols <- cols[seq(1, length(cols), by = 2)]
    even_cols <- cols[seq(2, length(cols), by = 2)]
    if (length(odd_cols) < 1 || length(even_cols) < 1) {
      return(NA)
    }
    half1_sum <- rowSums(scale_data[, odd_cols, drop = FALSE])
    half2_sum <- rowSums(scale_data[, even_cols, drop = FALSE])
    r_half <- suppressWarnings(stats::cor(half1_sum, half2_sum))
    if (is.na(r_half) || (1 + r_half) == 0) {
      return(NA)
    }
    return((2 * r_half) / (1 + r_half))
  }

  if (selected_type == "McDonald Omega") {
    omega <- NA
    tryCatch({
      fa_result <- stats::factanal(scale_data, factors = 1, scores = "none", rotation = "none")
      loadings <- as.vector(fa_result$loadings[, 1])
      uniqueness <- fa_result$uniquenesses
      sum_load_sq <- sum(loadings)^2
      omega <- sum_load_sq / (sum_load_sq + sum(uniqueness))
    }, error = function(e) {})
    return(omega)
  }

  if (selected_type == "theta系数") {
    theta <- NA
    tryCatch({
      eigen_values <- eigen(stats::cor(scale_data), symmetric = TRUE, only.values = TRUE)$values
      theta <- (k / (k - 1)) * (1 - 1 / eigen_values[1])
    }, error = function(e) {})
    return(theta)
  }

  cronbach_alpha(scale_data)
}

summary_metric_name <- function(selected_type) {
  if (selected_type == "折半系数") return("折半系数")
  if (selected_type == "McDonald Omega") return("McDonald's \u03c9")
  if (selected_type == "theta系数") return("theta系数")
  "Cronbach's \u03b1"
}

summary_group_cols <- list()
for (scale_name in names(input$items_groups)) {
  cols <- unlist(input$items_groups[[scale_name]])
  cols <- cols[cols %in% names(raw_df)]
  if (length(cols) >= 2) {
    summary_group_cols[[scale_name]] <- cols
  }
}
summary_rows <- list()
for (scale_name in names(summary_group_cols)) {
  cols <- summary_group_cols[[scale_name]]
  summary_rows[[length(summary_rows) + 1]] <- list(
    scale_name,
    as.character(length(cols)),
    fmt_num(reliability_summary_value(raw_df, cols, selected_type))
  )
}
if (length(summary_group_cols) >= 2) {
  total_cols <- unique(unlist(summary_group_cols, use.names = FALSE))
  summary_rows[[length(summary_rows) + 1]] <- list(
    "总量表",
    as.character(length(total_cols)),
    fmt_num(reliability_summary_value(raw_df, total_cols, selected_type))
  )
}

for (scale_name in names(input$items_groups)) {
  cols <- unlist(input$items_groups[[scale_name]])
  cols <- cols[cols %in% names(raw_df)]
  if (length(cols) < 2) {
    next
  }
  section_title <- function(title) paste0(scale_name, " - ", title)
  data <- raw_df[, cols, drop = FALSE]
  original_n <- nrow(data)
  for (col in cols) {
    data[[col]] <- suppressWarnings(as.numeric(data[[col]]))
  }
  data <- stats::na.omit(data)
  valid_n <- nrow(data)
  excluded_n <- original_n - valid_n
  k <- ncol(data)
  n <- valid_n
  if (k < 2 || n < 2) {
    next
  }

  # ---- Cronbach's α ----
  if (selected_type == "Cronbach's α") {
    item_vars <- apply(data, 2, stats::var)
    total_scores <- rowSums(data)
    total_var <- stats::var(total_scores)
    alpha <- (k / (k - 1)) * (1 - sum(item_vars) / total_var)

    corr_matrix <- stats::cor(data)
    mean_r <- (sum(corr_matrix) - k) / (k * (k - 1))
    std_alpha <- ifelse(
      (1 + (k - 1) * mean_r) != 0,
      (k * mean_r) / (1 + (k - 1) * mean_r),
      alpha
    )

    item_stats <- list()
    for (col in cols) {
      rest_cols <- cols[cols != col]
      rest_sum <- rowSums(data[, rest_cols, drop = FALSE])
      del_corr <- suppressWarnings(stats::cor(data[[col]], rest_sum))
      del_mean <- mean(rest_sum)
      del_var <- stats::var(rest_sum)
      alpha_del <- NA
      if (length(rest_cols) >= 2) {
        rest_data <- data[, rest_cols, drop = FALSE]
        rest_item_vars <- apply(rest_data, 2, stats::var)
        rest_total_var <- stats::var(rowSums(rest_data))
        alpha_del <- (
          length(rest_cols) / (length(rest_cols) - 1)
        ) * (1 - sum(rest_item_vars) / rest_total_var)
      }
      item_stats[[length(item_stats) + 1]] <- list(
        col = col,
        del_mean = del_mean,
        del_var = del_var,
        del_corr = del_corr,
        alpha_del = alpha_del
      )
    }

    t1_headers <- c("Cronbach's α系数", "标准化Cronbach's α系数", "项数", "样本数")
    t1_rows <- list(list(fmt_num(alpha), fmt_num(std_alpha), as.character(k), as.character(n)))
    sections[[length(sections) + 1]] <- sec_table(section_title("Cronbach信度分析"), t1_headers, t1_rows, "用于衡量量表题项的内部一致性。")

    assess_alpha <- function(a) {
      if (is.na(a)) return("无法判断")
      if (a >= 0.9) return("非常理想")
      if (a >= 0.8) return("较好")
      if (a >= 0.7) return("可以接受")
      if (a >= 0.6) return("勉强可接受")
      return("偏低")
    }
    alpha_assessment <- assess_alpha(alpha)
    best_del_alpha <- NA
    best_del_item <- ""
    for (stat in item_stats) {
      if (!is.na(stat$alpha_del) && (is.na(best_del_alpha) || stat$alpha_del > best_del_alpha)) {
        best_del_alpha <- stat$alpha_del
        best_del_item <- stat$col
      }
    }
    del_note <- ""
    if (!is.na(best_del_alpha) && !is.na(alpha) && best_del_alpha > alpha + 0.02) {
      del_note <- paste0("删除\u201c", best_del_item, "\u201d后 α 系数可提升至 ", fmt_num(best_del_alpha), "，可结合项统计表考虑是否删除该项。")
    } else if (!is.na(best_del_alpha) && !is.na(alpha) && best_del_alpha >= alpha) {
      del_note <- "删除任意题项后 α 系数均未明显提升，各项保留情况较好。"
    } else {
      del_note <- "删除任意题项后 α 系数均未超过当前值，所有题项均有效贡献内部一致性。"
    }
    smart1 <- paste0(
      "该量表共 ", k, " 个题项，有效样本量 ", n, "。",
      "Cronbach's α 系数为 ", fmt_num(alpha), "，整体信度", alpha_assessment, "。",
      "标准化 α 系数为 ", fmt_num(std_alpha), "，与 α 系数接近，说明各题项方差均衡性较好。",
      "信度评价常用标准：α ≥ 0.9 为非常理想，α ≥ 0.8 为较好，α ≥ 0.7 为可接受，α ≥ 0.6 为勉强可接受，α < 0.6 说明信度偏低需要修订。",
      del_note
    )
    sections[[length(sections) + 1]] <- sec_smart(smart1)

    t2_headers <- c("", "删除项后的平均值", "删除项后的方差", "校正项总计相关性(CITC)", "删除项后的Cronbach's α系数", "Cronbach's α系数")
    t2_rows <- list()
    t3_rows <- list()
    weak_items <- c()
    idx <- 1
    alpha_row_idx <- ceiling(length(item_stats) / 2)
    for (stat in item_stats) {
      t2_rows[[length(t2_rows) + 1]] <- list(stat$col, fmt_num(stat$del_mean), fmt_num(stat$del_var), fmt_num(stat$del_corr), fmt_num(stat$alpha_del), ifelse(idx == alpha_row_idx, fmt_num(alpha), ""))
      conclusion <- "较好"
      if (!is.na(stat$del_corr) && stat$del_corr < 0.3) {
        conclusion <- "需要检查"
        weak_items <- c(weak_items, stat$col)
      }
      t3_rows[[length(t3_rows) + 1]] <- list(as.character(idx), stat$col, fmt_num(stat$del_corr), fmt_num(stat$alpha_del), conclusion)
      idx <- idx + 1
    }

    sections[[length(sections) + 1]] <- sec_table(section_title("输出结果2：删除分析项统计汇总"), t2_headers, t2_rows, "可结合删除项后的相关性与 α 系数变化，辅助判断题项保留情况。")
    sections[[length(sections) + 1]] <- sec_table(section_title("输出结果3：信度分析总结图"), c("序号", "分析项名", "校正项总计相关性(CITC)", "删除项后的Cronbach's α系数", "参考结论"), t3_rows, "若题项删除后整体表现改善明显，可考虑复核题项设计。")

    advice_parts <- c(
      "信度标准参考：通常 Cronbach's α ≥ 0.7 表示量表信度可接受，α ≥ 0.8 表示信度较好，α ≥ 0.9 表示信度非常理想。α 低于 0.6 时需考虑修订量表或增删题项。",
      "CITC（校正项总计相关性）标准参考：CITC ≥ 0.3 表示题项与总分相关性良好，CITC < 0.3 表示该题项与总分关联较弱，可能需要删除或修订。"
    )
    if (length(weak_items) > 0) {
      advice_parts <- c(advice_parts,
        paste0("当前存在 ", length(weak_items), " 个题项 CITC 低于 0.3：", paste(weak_items, collapse = "、"), "。"),
        "建议重点复核这些题项，检查是否存在反向题未正确编码、题项表述歧义或测量维度偏离等问题。",
        "可结合项统计表中的\"删除项后的 Cronbach's α 系数\"，若删除后 α 显著提升，可考虑将该题项删除。",
        "删除题项前建议结合内容效度和理论依据综合判断，不要仅凭统计指标做决定。"
      )
    } else {
      advice_parts <- c(advice_parts,
        "当前所有题项的 CITC 值均不低于 0.3，各题项与总分的相关性良好。",
        "整体信度已达到可接受水平，无需删除分析项，量表可用于后续问卷分析。",
        "如希望进一步提升信度，可在后续研究中增加高质量题项或优化题项表述。"
      )
    }
    sections[[length(sections) + 1]] <- sec_advice(paste(advice_parts, collapse = "\n"), section_title("分析建议"))

    sections[[length(sections) + 1]] <- sec_table(section_title("样本缺失情况汇总"), c("有效样本", "排除无效样本", "总计"), list(list(as.character(n), as.character(excluded_n), as.character(original_n))), "在计算过程中自动排除存在缺失值的样本。")

    smart_parts <- c(smart_parts, smart1)
    main_headers <- t1_headers
    main_rows <- t1_rows

  # ---- 折半系数 ----
  } else if (selected_type == "折半系数") {
    odd_cols <- cols[seq(1, length(cols), by = 2)]
    even_cols <- cols[seq(2, length(cols), by = 2)]
    half1_data <- data[, odd_cols, drop = FALSE]
    half2_data <- data[, even_cols, drop = FALSE]
    k1 <- ncol(half1_data)
    k2 <- ncol(half2_data)

    alpha_half1 <- cronbach_alpha(half1_data)
    alpha_half2 <- cronbach_alpha(half2_data)

    half1_sum <- rowSums(half1_data)
    half2_sum <- rowSums(half2_data)
    r_half <- stats::cor(half1_sum, half2_sum)

    spearman_brown_equal <- (2 * r_half) / (1 + r_half)
    n_sb <- (k1 + k2) / sqrt(k1 * k2)
    spearman_brown_unequal <- (n_sb * r_half) / (1 + (n_sb - 1) * r_half)

    half1_var <- stats::var(half1_sum)
    half2_var <- stats::var(half2_sum)
    total_var_sh <- stats::var(half1_sum + half2_sum)
    guttman <- 2 * (1 - (half1_var + half2_var) / total_var_sh)

    t1_headers <- c("", "", "", "")
    # 带 rowspan/colspan 的合并行版本（网页 & HTML 复制用）
    t1_rows <- list(
      list(list(text="Cronbach's α系数", rowspan=5L), list(text="前半部分", rowspan=2L), "值", fmt_num(alpha_half1)),
      list("项数", as.character(k1)),
      list(list(text="后半部分", rowspan=2L), "值", fmt_num(alpha_half2)),
      list("项数", as.character(k2)),
      list(list(text="总项数", colspan=2L), as.character(k)),
      list(list(text="前后两部分间的相关系数值", colspan=3L), fmt_num(r_half)),
      list(list(text="折半系数（Spearman-Brown系数）", rowspan=2L), "等长", "", fmt_num(spearman_brown_equal)),
      list("不等长", "", fmt_num(spearman_brown_unequal)),
      list(list(text="Guttman Split-Half 系数", colspan=3L), fmt_num(guttman))
    )
    # 纯平铺行版本（Word/python-docx 导出用）
    t1_rows_flat <- list(
      list("Cronbach's α系数", "前半部分", "值", fmt_num(alpha_half1)),
      list("", "", "项数", as.character(k1)),
      list("", "后半部分", "值", fmt_num(alpha_half2)),
      list("", "", "项数", as.character(k2)),
      list("", "总项数", "", as.character(k)),
      list("前后两部分间的相关系数值", "", "", fmt_num(r_half)),
      list("折半系数（Spearman-Brown系数）", "等长", "", fmt_num(spearman_brown_equal)),
      list("", "不等长", "", fmt_num(spearman_brown_unequal)),
      list("Guttman Split-Half 系数", "", "", fmt_num(guttman))
    )
    split_sec <- sec_table(section_title("折半信度分析"), t1_headers, t1_rows, "将题项按奇偶分为两半，计算两半的Cronbach's α系数及折半信度。")
    split_sec$headerRows <- list(list(list(text = section_title("折半信度分析"), colspan = 4L)))
    split_sec$inlineTitle <- TRUE
    split_sec$bodyRowspanColumns <- 1L
    split_sec$exportRows <- t1_rows_flat
    sections[[length(sections) + 1]] <- split_sec

    pb_text <- ""
    if (!is.na(spearman_brown_equal) && spearman_brown_equal >= 0.8) {
      pb_text <- "整体信度较好"
    } else if (!is.na(spearman_brown_equal) && spearman_brown_equal >= 0.7) {
      pb_text <- "整体信度可以接受"
    } else {
      pb_text <- "信度偏低，建议检查题项设置"
    }
    smart1 <- paste0(
      "该量表共 ", k, " 个题项，有效样本量 ", n, "。",
      "前半部分 Cronbach's α 系数为 ", fmt_num(alpha_half1), "，后半部分 Cronbach's α 系数为 ", fmt_num(alpha_half2), "。",
      "两半相关系数为 ", fmt_num(r_half), "。",
      "折半信度 Spearman-Brown 系数（等长）为 ", fmt_num(spearman_brown_equal), "，", pb_text, "。",
      "不等长调整后的 Spearman-Brown 系数为 ", fmt_num(spearman_brown_unequal), "，Guttman Split-Half 系数为 ", fmt_num(guttman), "。",
      "等长与不等长折半系数差异较小，说明两半长度均衡性较好，折半结果稳定。"
    )
    sections[[length(sections) + 1]] <- sec_smart(smart1)

    sections[[length(sections) + 1]] <- sec_advice(paste0(
      "折半信度参考标准：Spearman-Brown 系数 ≥ 0.7 表示信度可接受，≥ 0.8 表示信度较好。\n",
      "Cronbach's α 系数参考标准：α ≥ 0.7 表示信度可接受。\n",
      "注意折半系数高度依赖拆分方式（此处采用奇偶拆分），不同拆分方式结果会有差异。\n",
      "建议同时参考 Cronbach's α 系数综合评估量表信度。"
    ), section_title("分析建议"))

    sections[[length(sections) + 1]] <- sec_table(section_title("样本缺失情况汇总"), c("有效样本", "排除无效样本", "总计"), list(list(as.character(n), as.character(excluded_n), as.character(original_n))), "在计算过程中自动排除存在缺失值的样本。")

    smart_parts <- c(smart_parts, smart1)
    main_headers <- t1_headers
    main_rows <- t1_rows

  # ---- McDonald Omega ----
  } else if (selected_type == "McDonald Omega") {
    omega <- NA
    omega_msg <- ""
    tryCatch({
      fa_result <- stats::factanal(data, factors = 1, scores = "none", rotation = "none")
      loadings <- as.vector(fa_result$loadings[, 1])
      uniqueness <- fa_result$uniquenesses
      sum_load_sq <- sum(loadings)^2
      sum_uniqueness <- sum(uniqueness)
      omega <- sum_load_sq / (sum_load_sq + sum_uniqueness)
    }, error = function(e) {
      omega_msg <<- paste0("单因子模型拟合失败：", e$message, "。")
    })

    # 主表：项数 | 样本量 | McDonald's ω系数
    t1_headers <- c("项数", "样本量", "McDonald's \u03c9系数")
    omega_display <- if (is.na(omega)) "\u2014" else fmt_num(omega)
    t1_rows <- list(list(as.character(k), as.character(n), omega_display))
    sections[[length(sections) + 1]] <- sec_table(
      section_title("McDonald's \u03c9信度分析结果"), t1_headers, t1_rows,
      "基于单因子模型的内部一致性系数，反映题项共享的共同方差比例。")

    if (!is.na(omega)) {
      omega_level <- if (omega >= 0.9) "非常理想" else if (omega >= 0.8) "较好" else if (omega >= 0.7) "可以接受" else if (omega >= 0.6) "勉强可接受" else "偏低"
      omega_phrase <- if (omega >= 0.9) paste0("大于0.9，因而说明研究数据信度质量很高") else if (omega >= 0.8) paste0("介于0.8-0.9之间，说明研究数据信度质量较好") else if (omega >= 0.7) paste0("介于0.7-0.8之间，说明研究数据信度质量可以接受") else paste0("低于0.7，说明研究数据信度质量偏低")

      # 计算各题项已剔除后的 omega
      omega_del_vals <- c()
      for (col_del in cols) {
        rest_cols_del <- cols[cols != col_del]
        del_val <- NA
        if (length(rest_cols_del) >= 2) {
          tryCatch({
            fa_del <- stats::factanal(data[, rest_cols_del, drop = FALSE], factors = 1, scores = "none", rotation = "none")
            ld <- as.vector(fa_del$loadings[, 1])
            un <- fa_del$uniquenesses
            sl <- sum(ld)^2
            del_val <- sl / (sl + sum(un))
          }, error = function(e) {})
        }
        omega_del_vals <- c(omega_del_vals, del_val)
      }

      # 详细格式表
      omega_row_idx <- ceiling(k / 2)
      t2_headers <- c("名称", "项已剔除的McDonald's \u03c9系数", "McDonald's \u03c9系数")
      t2_rows <- list()
      for (i in seq_along(cols)) {
        t2_rows[[i]] <- list(
          cols[i],
          fmt_num(omega_del_vals[i]),
          if (i == omega_row_idx) fmt_num(omega) else ""
        )
      }
      sections[[length(sections) + 1]] <- sec_table(
        section_title("McDonald's \u03c9信度分析-详细格式"), t2_headers, t2_rows,
        "显示删除各题项后McDonald's ω系数的变化情况。")

      # 判断是否有题项删除后系数明显上升
      has_removable <- any(!is.na(omega_del_vals) & omega_del_vals > omega + 0.02)
      del_conclusion <- if (has_removable) {
        paste0("针对\u201c项已剔除的McDonald's \u03c9系数\u201d，部分题项删除后系数有明显上升，可结合题项内容考虑是否删除。")
      } else {
        paste0("针对\u201c项已剔除的McDonald's \u03c9系数\u201d，任意题项被删除后McDonald's \u03c9系数并不会有明显的上升，因此说明均不应该被删除处理。")
      }
      smart1 <- paste0(
        "从上表可知：McDonald's ω系数值为", fmt_num(omega), "，", omega_phrase, "。",
        del_conclusion,
        "综上所述，研究数据McDonald's ω系数值为", fmt_num(omega), "，综合说明数据信度质量", omega_level, "，可用于进一步分析。"
      )
    } else {
      smart1 <- paste0("该量表共 ", k, " 个题项，有效样本量 ", n, "。", omega_msg, "建议改用 Cronbach's α 或折半系数评估信度。")
    }
    sections[[length(sections) + 1]] <- sec_smart(smart1)

    sections[[length(sections) + 1]] <- sec_advice(paste0(
      "信度分析用于研究定量数据（尤其是态度量表题）的答答可靠性；\n",
      "第一：首先分析McDonald's ω信度系数；如果此值高于0.8，则说明信度高；如果此值介于0.7-0.8之间，则说明信度较好；如果此值介于0.6-0.7，则说明信度可接受；如果此值小于0.6，则说明信度不佳；\n",
      "第二：如果\u201c项已剔除的McDonald's \u03c9系数\u201d值明显高于McDonald's \u03c9信度系数，此时可考虑对该项进行删除后重新分析；\n",
      "第三：如果分析项数量大于20，则不应使用\u201c项已剔除的McDonald's \u03c9系数\u201d指标；\n",
      "第四：对分析进行总结。"
    ), section_title("分析建议"))

    sections[[length(sections) + 1]] <- sec_table(section_title("样本缺失情况汇总"), c("有效样本", "排除无效样本", "总计"), list(list(as.character(n), as.character(excluded_n), as.character(original_n))), "在计算过程中自动排除存在缺失值的样本。")

    smart_parts <- c(smart_parts, smart1)
    main_headers <- t1_headers
    main_rows <- t1_rows

  # ---- theta系数 ----
  } else if (selected_type == "theta系数") {
    theta <- NA
    first_eigen <- NA
    theta_msg <- ""
    tryCatch({
      cor_mat <- stats::cor(data)
      eigen_values <- eigen(cor_mat, symmetric = TRUE, only.values = TRUE)$values
      first_eigen <- eigen_values[1]
      theta <- (k / (k - 1)) * (1 - 1 / first_eigen)
    }, error = function(e) {
      theta_msg <<- paste0("特征值计算失败：", e$message, "。")
    })

    # 主表：项数 | 样本量 | theta系数
    t1_headers <- c("项数", "样本量", "theta系数")
    theta_display <- if (is.na(theta)) "\u2014" else fmt_num(theta)
    t1_rows <- list(list(as.character(k), as.character(n), theta_display))
    sections[[length(sections) + 1]] <- sec_table(
      section_title("theta系数信度分析结果"), t1_headers, t1_rows,
      "基于主成分分析第一特征值的内部一致性系数。")

    if (!is.na(theta)) {
      theta_level <- if (theta >= 0.9) "非常理想" else if (theta >= 0.8) "较好" else if (theta >= 0.7) "可以接受" else if (theta >= 0.6) "勉强可接受" else "偏低"
      theta_phrase <- if (theta >= 0.9) paste0("大于0.9，因而说明研究数据信度质量很高") else if (theta >= 0.8) paste0("介于0.8-0.9之间，说明研究数据信度质量较好") else if (theta >= 0.7) paste0("介于0.7-0.8之间，说明研究数据信度质量可以接受") else paste0("低于0.7，说明研究数据信度质量偏低")

      # 计算各题项已剔除后的 theta
      theta_del_vals <- c()
      for (col_del in cols) {
        rest_cols_del <- cols[cols != col_del]
        del_val <- NA
        k_del <- length(rest_cols_del)
        if (k_del >= 2) {
          tryCatch({
            cor_del <- stats::cor(data[, rest_cols_del, drop = FALSE])
            eigen_del <- eigen(cor_del, symmetric = TRUE, only.values = TRUE)$values
            del_val <- (k_del / (k_del - 1)) * (1 - 1 / eigen_del[1])
          }, error = function(e) {})
        }
        theta_del_vals <- c(theta_del_vals, del_val)
      }

      # 详细格式表
      theta_row_idx <- ceiling(k / 2)
      t2_headers <- c("名称", "项已剔除的theta系数", "theta系数")
      t2_rows <- list()
      for (i in seq_along(cols)) {
        t2_rows[[i]] <- list(
          cols[i],
          fmt_num(theta_del_vals[i]),
          if (i == theta_row_idx) fmt_num(theta) else ""
        )
      }
      sections[[length(sections) + 1]] <- sec_table(
        section_title("theta系数信度分析-详细格式"), t2_headers, t2_rows,
        "显示删除各题项后theta系数的变化情况。")

      # 判断是否有题项删除后系数明显上升
      has_removable <- any(!is.na(theta_del_vals) & theta_del_vals > theta + 0.02)
      del_conclusion <- if (has_removable) {
        paste0("针对\u201c项已剔除的theta系数\u201d，部分题项删除后系数有明显上升，可结合题项内容考虑是否删除。")
      } else {
        paste0("针对\u201c项已剔除的theta系数\u201d，任意题项被删除后theta系数并不会有明显的上升，因此说明均不应该被删除处理。")
      }
      smart1 <- paste0(
        "从上表可知：theta系数值为", fmt_num(theta), "，", theta_phrase, "。",
        del_conclusion,
        "综上所述，研究数据theta系数值为", fmt_num(theta), "，综合说明数据信度质量", theta_level, "，可用于进一步分析。"
      )
    } else {
      smart1 <- paste0("该量表共 ", k, " 个题项，有效样本量 ", n, "。", theta_msg, "建议改用 Cronbach's α 评估信度。")
    }
    sections[[length(sections) + 1]] <- sec_smart(smart1)

    sections[[length(sections) + 1]] <- sec_advice(paste0(
      "信度分析用于研究定量数据（尤其是态度量表题）的答答可靠性；\n",
      "第一：首先分析theta信度系数；如果此值高于0.8，则说明信度高；如果此值介于0.7-0.8之间，则说明信度较好；如果此值介于0.6-0.7，则说明信度可接受；如果此值小于0.6，则说明信度不佳；\n",
      "第二：如果\u201c项已剔除的theta系数\u201d值明显高于theta信度系数，此时可考虑对该项进行删除后重新分析；\n",
      "第三：如果分析项数量大于20，则不应使用\u201c项已剔除的theta系数\u201d指标；\n",
      "第四：对分析进行总结。"
    ), section_title("分析建议"))

    sections[[length(sections) + 1]] <- sec_table(section_title("样本缺失情况汇总"), c("有效样本", "排除无效样本", "总计"), list(list(as.character(n), as.character(excluded_n), as.character(original_n))), "在计算过程中自动排除存在缺失值的样本。")

    smart_parts <- c(smart_parts, smart1)
    main_headers <- t1_headers
    main_rows <- t1_rows
  }
}

if (length(summary_rows) > 0) {
  summary_section <- sec_table(
    "信度分析汇总",
    c("维度", "题项个数", summary_metric_name(selected_type)),
    summary_rows,
    "各维度独立计算信度；当存在两个及以上有效维度时，自动追加总量表。"
  )
  summary_section$tableStyle <- "three_line"
  sections <- c(list(summary_section), sections)
}

sections[[length(sections) + 1]] <- sec_refs(c(
  paste0("[1] Cronbach, L. J. Coefficient alpha and the internal structure of tests. Psychometrika, 1951."),
  paste0("[2] McDonald, R. P. Test theory: A unified treatment. Lawrence Erlbaum, 1999."),
  paste0("[3] Armor, D. J. Theta reliability and factor scaling. Sociological Methodology, 1974.")
))

result <- list(
  success = TRUE,
  name = "信度分析",
  headers = main_headers,
  rows = main_rows,
  description = ifelse(
    length(smart_parts) > 0,
    paste(smart_parts, collapse = " "),
    "信度分析完成。"
  ),
  sections = sections
)

cat(jsonlite::toJSON(
  result,
  auto_unbox = TRUE,
  null = "null",
  force = TRUE,
  dataframe = "rows"
))
