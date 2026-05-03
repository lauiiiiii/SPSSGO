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

if (nrow(data) < 5) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "有效样本不足。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

corr_matrix <- stats::cor(data)
det_corr <- det(corr_matrix)
if (is.na(det_corr) || det_corr <= 0) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "相关矩阵不可逆，无法进行探索性因子分析。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

kmo_info <- compute_kmo(corr_matrix)
bartlett_info <- compute_bartlett(corr_matrix, nrow(data))
eigen_values <- eigen(corr_matrix)$values
factor_count <- sum(eigen_values > 1)
factor_count <- max(1, min(factor_count, length(items) - 1))

fa_result <- tryCatch(
  stats::factanal(data, factors = factor_count, rotation = "varimax", scores = "regression"),
  error = function(e) NULL
)

headers <- c("指标", "值")
rows <- list(
  list("KMO", fmt_num(kmo_info$total, 4)),
  list("相关矩阵行列式", fmt_num(det_corr, 6)),
  list("Bartlett球形检验 χ²", fmt_num(bartlett_info$chi2, 2)),
  list("Bartlett球形检验 p", fmt_num(bartlett_info$p, 6)),
  list("建议提取因子数", as.character(factor_count))
)

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
sections[[length(sections) + 1]] <- sec_table(
  "特征值与方差解释",
  c("成分", "特征值"),
  lapply(seq_along(eigen_values), function(i) list(paste0("成分", i), fmt_num(eigen_values[[i]], 4))),
  "通常可结合特征值大于 1 的 Kaiser 准则初步判断因子个数。"
)

description <- paste0(
  "对", scale_name, "进行探索性因子分析前提检验。KMO=", fmt_num(kmo_info$total, 3),
  "，Bartlett 检验", ifelse(bartlett_info$p < 0.05, "显著", "不显著"),
  "，建议提取 ", factor_count, " 个因子。"
)

if (!is.null(fa_result)) {
  loadings_matrix <- as.matrix(fa_result$loadings[])
  loading_headers <- c("题项")
  for (i in seq_len(ncol(loadings_matrix))) loading_headers <- c(loading_headers, paste0("因子", i))
  loading_rows <- list()
  for (r in seq_len(nrow(loadings_matrix))) {
    row <- list(rownames(loadings_matrix)[r])
    for (c in seq_len(ncol(loadings_matrix))) row <- c(row, list(fmt_num(loadings_matrix[r, c], 4)))
    loading_rows[[length(loading_rows) + 1]] <- row
  }
  sections[[length(sections) + 1]] <- sec_table(
    "旋转后因子载荷矩阵",
    loading_headers,
    loading_rows,
    "载荷越高，题项与对应因子的关系越强；常结合 0.4 或 0.5 作为经验判断阈值。"
  )

  uniqueness <- fa_result$uniquenesses
  communality_rows <- list()
  for (i in seq_along(uniqueness)) {
    communality_rows[[length(communality_rows) + 1]] <- list(names(uniqueness)[i], fmt_num(1 - uniqueness[[i]], 4), fmt_num(uniqueness[[i]], 4))
  }
  sections[[length(sections) + 1]] <- sec_table(
    "共同度与特殊方差",
    c("题项", "共同度", "特殊方差"),
    communality_rows
  )

  variance_rows <- list()
  ss_loadings <- fa_result$criteria["objective"] # fallback placeholder not used
  for (i in seq_len(ncol(loadings_matrix))) {
    variance_rows[[length(variance_rows) + 1]] <- list(paste0("因子", i), fmt_num(sum(loadings_matrix[, i]^2), 4))
  }
  sections[[length(sections) + 1]] <- sec_table(
    "因子强度汇总",
    c("因子", "载荷平方和"),
    variance_rows,
    "该表可用于粗略比较各因子的相对解释能力。"
  )
}

advice <- paste(
  "探索性因子分析用于识别题项背后的潜在结构。",
  "通常先看 KMO 是否达到 0.6 以上，再看 Bartlett 检验是否显著。",
  "如果载荷矩阵中某个题项在多个因子上同时较高，说明题项归属可能不够清晰。",
  sep = "\n"
)
sections[[length(sections) + 1]] <- sec_advice(advice)
sections[[length(sections) + 1]] <- sec_smart(description)
sections[[length(sections) + 1]] <- sec_refs(c(
  "[1] Kaiser, H. F. An index of factorial simplicity. Psychometrika, 1974.",
  "[2] Bartlett, M. S. A note on the multiplying factors for various chi square approximations. Journal of the Royal Statistical Society, 1954."
))

result <- list(
  success = TRUE,
  name = "因子分析（探索性）",
  headers = headers,
  rows = rows,
  description = description,
  sections = sections
)

cat(jsonlite::toJSON(result, auto_unbox = TRUE, null = "null", force = TRUE, dataframe = "rows"))
