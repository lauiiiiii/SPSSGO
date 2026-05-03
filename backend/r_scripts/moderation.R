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
fmt_num <- function(x, digits = 4) {
  if (is.null(x) || length(x) == 0 || is.na(x) || is.infinite(x)) return("\u2014")
  if (abs(x - round(x)) < 1e-12) return(as.character(as.integer(round(x))))
  sprintf(paste0("%.", digits, "f"), x)
}
sec_table <- function(title, headers, rows, description = NULL) {
  item <- list(type = "table", title = title, headers = headers, rows = rows)
  if (!is.null(description)) item$description <- description
  item
}
sec_smart <- function(content) list(type = "smart_analysis", title = "智能分析", content = content)
sec_advice <- function(content, title = "分析建议") list(type = "advice", title = title, content = content)
sec_refs <- function(items) list(type = "references", title = "参考文献", items = items)

input <- jsonlite::fromJSON(read_utf8(input_path), simplifyVector = FALSE)
input_dir <- dirname(normalizePath(input_path, winslash = "/", mustWork = TRUE))
data_file <- file.path(input_dir, input$data_file)
if (!file.exists(data_file)) stop("missing input data file")

x <- input$x
w <- input$w
y <- input$y
raw_df <- read.csv(data_file, stringsAsFactors = FALSE, check.names = FALSE)
variables <- c(x, w, y)
data <- raw_df[, variables, drop = FALSE]
for (col in variables) data[[col]] <- suppressWarnings(as.numeric(data[[col]]))
data <- stats::na.omit(data)
if (nrow(data) < 10) {
  cat(jsonlite::toJSON(list(success = FALSE, error = "调节效应分析有效样本不足。"), auto_unbox = TRUE, force = TRUE))
  quit(status = 0)
}

data$x_c <- data[[x]] - mean(data[[x]])
data$w_c <- data[[w]] - mean(data[[w]])
data$interaction <- data$x_c * data$w_c
m1 <- stats::lm(data[[y]] ~ x_c + w_c, data = data)
m2 <- stats::lm(data[[y]] ~ x_c + w_c + interaction, data = data)
sm2 <- summary(m2)
coef_df <- sm2$coefficients
ci_df <- stats::confint(m2)

coef_row <- function(term, label) {
  list(label, fmt_num(coef_df[term, "Estimate"], 4), fmt_num(coef_df[term, "Std. Error"], 4), fmt_num(coef_df[term, "t value"], 4), fmt_num(coef_df[term, "Pr(>|t|)"], 4), fmt_num(ci_df[term, 1], 4), fmt_num(ci_df[term, 2], 4))
}
rows <- list(
  coef_row("x_c", x),
  coef_row("w_c", w),
  coef_row("interaction", paste0(x, "×", w))
)

r2_1 <- summary(m1)$r.squared
r2_2 <- sm2$r.squared
delta_r2 <- r2_2 - r2_1
anova_cmp <- stats::anova(m1, m2)
comp_rows <- list(
  list("模型1（主效应）", fmt_num(r2_1, 4), "\u2014", fmt_num(summary(m1)$fstatistic[1], 4), fmt_num(stats::pf(summary(m1)$fstatistic[1], summary(m1)$fstatistic[2], summary(m1)$fstatistic[3], lower.tail = FALSE), 4)),
  list("模型2（+交互项）", fmt_num(r2_2, 4), fmt_num(delta_r2, 4), fmt_num(anova_cmp$F[2], 4), fmt_num(anova_cmp$`Pr(>F)`[2], 4))
)

cov_m <- stats::vcov(m2)
w_sd <- stats::sd(data$w_c)
simple_slope <- function(level_label, level_value) {
  slope <- coef(m2)["x_c"] + coef(m2)["interaction"] * level_value
  variance <- cov_m["x_c", "x_c"] + level_value^2 * cov_m["interaction", "interaction"] + 2 * level_value * cov_m["x_c", "interaction"]
  se <- sqrt(max(variance, 0))
  t_value <- slope / se
  p_value <- 2 * stats::pt(abs(t_value), df = stats::df.residual(m2), lower.tail = FALSE)
  crit <- stats::qt(0.975, df = stats::df.residual(m2))
  list(level_label, fmt_num(level_value, 4), fmt_num(slope, 4), fmt_num(se, 4), fmt_num(slope - crit * se, 4), fmt_num(slope + crit * se, 4), fmt_num(t_value, 4), fmt_num(p_value, 4))
}
simple_rows <- list(
  simple_slope("低水平(-1SD)", -w_sd),
  simple_slope("平均水平", 0),
  simple_slope("高水平(+1SD)", w_sd)
)

tcrit <- stats::qt(0.975, df = stats::df.residual(m2))
b1 <- coef(m2)["x_c"]
b3 <- coef(m2)["interaction"]
v11 <- cov_m["x_c", "x_c"]
v13 <- cov_m["x_c", "interaction"]
v33 <- cov_m["interaction", "interaction"]
a <- b3^2 - tcrit^2 * v33
b <- 2 * b1 * b3 - 2 * tcrit^2 * v13
c <- b1^2 - tcrit^2 * v11
disc <- b^2 - 4 * a * c
jn_rows <- list()
if (!is.na(disc) && disc >= 0 && abs(a) > 1e-12) {
  roots <- sort(c((-b - sqrt(disc)) / (2 * a), (-b + sqrt(disc)) / (2 * a)))
  jn_rows[[1]] <- list("Johnson-Neyman 临界点", fmt_num(roots[1], 4), fmt_num(roots[2], 4), "调节变量中心化值落在临界点之外时，X→Y 简单斜率通常达到显著。")
} else {
  jn_rows[[1]] <- list("Johnson-Neyman 临界点", "\u2014", "\u2014", "当前数据下未形成稳定的 Johnson-Neyman 临界区间。")
}

p_inter <- coef_df["interaction", "Pr(>|t|)"]
smart <- paste0("调节效应分析使用 R 分层回归完成，共纳入 ", nrow(data), " 条有效样本。交互项 ", x, "×", w, ifelse(p_inter < 0.05, " 显著", " 不显著"), "（B=", fmt_num(coef_df["interaction", "Estimate"], 4), "，p=", fmt_num(p_inter, 4), "），ΔR²=", fmt_num(delta_r2, 4), "。")

sections <- list(
  sec_table("分层回归结果", c("变量", "B", "SE", "t", "p", "95% CI 下限", "95% CI 上限"), rows, "变量均已中心化处理。交互项显著表示调节效应存在。"),
  sec_table("模型比较", c("模型", "R²", "ΔR²", "F", "p"), comp_rows),
  sec_table("简单斜率检验", c("W水平", "中心化值", "X→Y 简单斜率", "SE", "95% CI 下限", "95% CI 上限", "t", "p"), simple_rows, "该表对应 PROCESS 常见的 conditional effect 输出。"),
  sec_table("Johnson-Neyman 区间", c("项目", "下临界点", "上临界点", "说明"), jn_rows),
  sec_advice("若交互项显著，应结合简单斜率和 Johnson-Neyman 区间解释不同调节水平下 X 对 Y 的影响。"),
  sec_smart(smart),
  sec_refs(c("[1] Hayes, A. F. Introduction to Mediation, Moderation, and Conditional Process Analysis."))
)

result <- list(success = TRUE, name = paste0("调节效应检验：", w, "调节", x, "→", y), headers = c("变量", "B", "SE", "t", "p", "95% CI 下限", "95% CI 上限"), rows = rows, description = smart, sections = sections)
cat(jsonlite::toJSON(result, auto_unbox = TRUE, null = "null", force = TRUE, dataframe = "rows"))
