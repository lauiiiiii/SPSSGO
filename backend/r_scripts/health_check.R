args <- commandArgs(trailingOnly = TRUE)

response <- paste0(
  "{\"success\":true,",
  "\"engine\":\"R\",",
  "\"script\":\"health_check.R\",",
  "\"message\":\"R runtime is available\"",
  "}"
)

cat(response)
