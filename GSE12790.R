# http://bioinformatics-core-shared-training.github.io/microarray-analysis/
rm(list=ls())

library(affy)
library(affyPLM)
library(GEOquery)
library(genefilter)
library(cluster)
library(WGCNA)

geo_fname <- "GSE12790_series_matrix.txt.gz"
remote_fname <- paste("ftp://ftp.ncbi.nlm.nih.gov/geo/series/GSE12nnn/GSE12790/matrix/", geo_fname, sep="")
if(!file.exists(geo_fname)) download.file(remotefile, destfile)
raw <- getGEO(filename=geo_fname)
exprs(raw) <- log2(exprs(raw))

# raw
# exprs(raw)[1:5,1:5]
# summary(exprs(raw)[,1:5])
# mva.pairs(exprs(raw)[,1:4], log.it = TRUE)

# dim(raw)
# raw <- varFilter(raw)
# dim(raw)

# phenotype data
pd <- pData(raw)

# features
features <- fData(raw)
stopifnot(all(rownames(features) == rownames(exprs(raw))))

# colnames(fData(raw))
# features[grep("TP53", features$`Gene Symbol`),]
# features[which(features$`Gene Symbol` == "TP53"),]
# features[match("TP53", features$`Gene Symbol`),]
# which(features$`Gene Symbol` == "TP53")

boxplot(exprs(raw))

E <- log2(exprs(raw))
par(mfrow=c(1,2))
plot(E[1274,], xlab="Array Index ",
     col="steelblue",pch=16,
     ylab="Normalised Expression",main=rownames(E)[1274])
plot(E[10723,], xlab="Array Index ",
     col="steelblue",pch=16,
     ylab="Normalised Expression",main=rownames(E)[10723])
cor(E[1274,],E[10723,], use = "complete.obs")

# Calcuate Euclidean distances among samples
euc.dist <- dist(t(exprs(raw)))
euc.dist

# corMat <-cor(exprs(raw))
# corMat
# cor.dist <- as.dist(1 - corMat)

clust <- hclust(euc.dist)
clust
par(mfrow=c(1,1))

sample_group <- pd$characteristics_ch1
group_colors <- sample_group
levels(group_colors) <- c("yellow","blue", "red", "green", "gray", "black", "black", "black")

clust.euclid = plot(clust, labels=pd$title, cex=0.5)
plotDendroAndColors(clust.euclid,colors=groupColours)

# Examples

targetsFile <- "estrogen/estrogen.txt"
pd <- read.AnnotatedDataFrame(targetsFile, header=TRUE, sep="", row.names=1)
raw <-ReadAffy(celfile.path="estrogen", filenames=rownames(pData(pd)), phenoData = pd)
boxplot(raw, col="red", las=2)

par(mfrow=c(2,1))
hist(log2(pm(raw[,1])), breaks=100, col="steelblue", main="PM", xlim=c(4,14))
hist(log2(mm(raw[,1])), breaks=100, col="steelblue", main="MM", xlim=c(4,14))

mva.pairs(pm(raw)[,1:4], plot.method="smoothScatter")

plmset <- fitPLM(raw)
NUSE(plmset,las=2)
RLE(plmset,las=2)

par(mfrow=c(2,4))
image(raw[,1])
image(raw[,2])
image(raw[,3])
image(raw[,4])
image(raw[,5])
image(raw[,6])
image(raw[,7])
image(raw[,8])

eset <- rma(raw)
head(exprs(eset))
summary(exprs(eset))
boxplot(exprs(eset),las=2)
mva.pairs(exprs(eset)[,1:4],log.it = FALSE,plot.method="smoothScatter")
