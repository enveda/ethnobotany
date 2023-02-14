library("ggtree")
library("ggplot2")
library("dplyr")
library("sjstats")
setwd("/Users/danielence/Documents/project_directories/team_advanced_analytics/ethnobotany/")

tree <- read.tree("np_family_tree.nwk")
circ <- ggtree(tree, layout = "circular") + geom_tiplab()
#rownames(df) <- tree$tip.label
png("phylo.png")
circ
dev.off()

df <- read.table("family_indication_count_normalized.tsv",sep="\t",header=TRUE,row.names = 1)
df$label <- rownames(df)
tree2 <- full_join(tree,df,by="label")
circ2 <- ggtree(tree2,layout="circular") + geom_tiplab(aes(label))
png("phylo2.png")
circ2
dev.off()


p1 <- gheatmap(circ, df1, offset=.8, width=.2,
               colnames_angle = 95, colnames_offset_y = .25,
               font.size=6, legend_title="Normalized Indication Count") + 
      scale_fill_gradient(low = "lightblue", 
                          high = "blue", 
                          na.value = NA, 
                          name="Normalized\nIndication\nCount")
png("phylo_heatmap.1.png",width=960,height=960)
p1
dev.off()

p2 <- gheatmap(circ, df2, offset=.8, width=.2,
               colnames_angle = 95, colnames_offset_y = .25,
               font.size=6, legend_title="Normalized Indication Count") + 
  scale_fill_gradient(low = "lightblue", 
                      high = "blue", 
                      na.value = NA, 
                      name="Normalized\nIndication\nCount")
png("phylo_heatmap.1.png",width=960,height=960)
p2
dev.off()

