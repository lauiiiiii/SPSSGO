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

fmt_num <- function(x, digits = 3) {
  if (is.null(x) || length(x) == 0 || is.na(x) || is.infinite(x)) {
    return("\u2014")
  }
  if (abs(x - round(x)) < 1e-12) {
    return(as.character(as.integer(round(x))))
  }
  sprintf(paste0("%.", digits, "f"), x)
}

sec_table <- function(title, headers, rows, description = NULL) {
  item <- list(type = "table", title = title, headers = headers, rows = rows)
  if (!is.null(description)) item$description <- description
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

compute_kmo <- function(corr_matrix) {
  inv_corr <- solve(corr_matrix)
  partial <- -cov2cor(inv_corr)
  diag(partial) <- 0
  corr_sq <- corr_matrix ^ 2
  partial_sq <- partial ^ 2
  diag(corr_sq) <- 0
  diag(partial_sq) <- 0
  kmo_per_item <- colSums(corr_sq) / (colSums(corr_sq) + colSums(partial_sq))
  kmo_total <- sum(corr_sq) / (sum(corr_sq) + sum(partial_sq))
  list(per_item = kmo_per_item, total = kmo_total)
}

compute_bartlett <- function(corr_matrix, n) {
  p <- ncol(corr_matrix)
  chi2 <- -(n - 1 - (2 * p + 5) / 6) * log(det(corr_matrix))
  dof <- p * (p - 1) / 2
  p_value <- stats::pchisq(chi2, df = dof, lower.tail = FALSE)
  list(chi2 = chi2, p = p_value, dof = dof)
}

input <- jsonlite::fromJSON(read_utf8(input_path), simplifyVector = FALSE)
input_dir <- dirname(normalizePath(input_path, winslash = "/", mustWork = TRUE))
data_file <- file.path(input_dir, input$data_file)
if (!file.exists(data_file)) {
  stop("missing input data file")
}

raw_df <- read.csv(data_file, stringsAsFactors = FALSE, check.names = FALSE)
items <- unlist(input$items)
items <- items[items %in% names(raw_df)]
scale_name <- ifelse(is.null(input$scale_name) || !nzchar(input$scale_name), "量表", input$scale_name)

if (length(items) < 3) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "需要至少3个题目。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

data <- raw_df[, items, drop = FALSE]
for (col in items) {
  data[[col]] <- suppressWarnings(as.numeric(data[[col]]))
}
data <- stats::na.omit(data)

if (nrow(data) < 3) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "有效样本不足。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

corr_matrix <- stats::cor(data)
det_corr <- det(corr_matrix)
if (is.na(det_corr) || det_corr <= 0) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "相关矩阵不可逆，无法进行效度分析。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

kmo_info <- compute_kmo(corr_matrix)
bartlett_info <- compute_bartlett(corr_matrix, nrow(data))

headers <- c("指标", "值")
rows <- list(
  list("KMO", fmt_num(kmo_info$total, 4)),
  list("相关矩阵行列式", fmt_num(det_corr, 6)),
  list("Bartlett球形检验 χ²", fmt_num(bartlett_info$chi2, 2)),
  list("Bartlett球形检验 p", fmt_num(bartlett_info$p, 6))
)

kmo_desc <- "不太适合"
if (!is.na(kmo_info$total)) {
  if (kmo_info$total >= 0.9) {
    kmo_desc <- "非常适合"
  } else if (kmo_info$total >= 0.8) {
    kmo_desc <- "适合"
  } else if (kmo_info$total >= 0.7) {
    kmo_desc <- "较适合"
  } else if (kmo_info$total >= 0.6) {
    kmo_desc <- "勉强适合"
  }
}

sections <- list()
sections[[length(sections) + 1]] <- sec_table(
  "KMO和Bartlett检验",
  headers,
  rows,
  "KMO 检验衡量变量间偏相关程度，Bartlett 检验判断相关矩阵是否为单位阵。"
)
sections[[length(sections) + 1]] <- sec_table(
  "各题项 KMO",
  c("题项", "KMO"),
  lapply(seq_along(items), function(i) list(items[[i]], fmt_num(kmo_info$per_item[[i]], 4)))
)

advice <- paste(
  "效度检验用于判断数据是否适合进行因子分析。",
  "第一：KMO值>0.9非常适合，0.8~0.9适合，0.7~0.8较适合，0.6~0.7勉强适合，<0.6不太适合。",
  "第二：Bartlett球形检验p<0.05说明变量间存在显著相关，适合进行因子分析。",
  sep = "\n"
)
sections[[length(sections) + 1]] <- sec_advice(advice)

description <- paste0(
  "对", scale_name, "进行效度检验。KMO值为", fmt_num(kmo_info$total),
  "，", kmo_desc, "进行因子分析；Bartlett球形检验结果",
  ifelse(bartlett_info$p < 0.05, "显著", "不显著"),
  "（χ²=", fmt_num(bartlett_info$chi2, 2), "，p=", fmt_num(bartlett_info$p, 6), "），说明数据",
  ifelse(bartlett_info$p < 0.05, "适合", "不适合"),
  "进行因子分析。"
)
sections[[length(sections) + 1]] <- sec_smart(description)
sections[[length(sections) + 1]] <- sec_refs(c(
  "[1] Kaiser, H. F. An index of factorial simplicity. Psychometrika, 1974.",
  "[2] Bartlett, M. S. A note on the multiplying factors for various chi square approximations. Journal of the Royal Statistical Society, 1954."
))

result <- list(
  success = TRUE,
  name = paste0("效度检验：", scale_name),
  headers = headers,
  rows = rows,
  description = description,
  sections = sections
)

cat(jsonlite::toJSON(result, auto_unbox = TRUE, null = "null", force = TRUE, dataframe = "rows"))
