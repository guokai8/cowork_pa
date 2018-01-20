rm(list=ls())

library("plyr")
library("ggplot2")

tcga_data <- read.table("tcga_expr/Breast_Invasive_Carcinoma_1000.expr", header = TRUE)
# tcga_data <- read.table("tcga_expr/Kidney_Chromophobe.expr", header = TRUE)
meta_data <- tcga_data[,1:3]
expr_data <- tcga_data[,4:ncol(tcga_data)]
rm(tcga_data)

num_samples <- nrow(meta_data)
stopifnot(num_samples == nrow(expr_data))
gene_names <- colnames(expr_data)
num_genes <- length(gene_names)

meta_data[,"sampletype"] <- as.character(meta_data[,"sampletype"])
min_expr <- min(expr_data[expr_data > 0])
expr_data[expr_data <= 0] <- min_expr / 2.0

expr_data <- cbind(expr_data, meta_data[,"sampletype"])
colnames(expr_data)[ncol(expr_data)] <- "sampletype"

# Boxplots of gene expressions
# observations (points) are overlayed and jittered
qplot(sampletype, log(expr_data[1]), data=expr_data, 
      geom = c("boxplot","jitter"),
      fill = sampletype, main = "Gene Expression",
      xlab = "Sample Type", ylab="Gene Expression")

count <- 0
for(i in 1:num_genes) {
  tumor_expr <- expr_data[expr_data$sampletype == 1,][,i]
  if(max(tumor_expr) < 0.001) next
  tumor_expr <- tumor_expr[tumor_expr >= min_expr]
  if(length(tumor_expr) < 3) next
  normal_expr <- expr_data[expr_data$sampletype == 11,][,i]
  normal_expr <- normal_expr[normal_expr >= min_expr]
  if(length(normal_expr) < 3) next
  ttest <- t.test(log(tumor_expr), log(normal_expr))
  if(is.na(ttest[['p.value']])) {
    next
  }
  if(ttest[['p.value']] < 1e-20) {
    cat(sprintf("%s: p-value(%e), tumor mean(%e), normal mean(%e)\n", 
                gene_names[i], 
                ttest[['p.value']],
                mean(tumor_expr),
                mean(normal_expr)))
    count <- count + 1
  }
}
count
