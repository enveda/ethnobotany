library("ggtree")
setwd("/Users/danielence/Documents/project_directories/team_advanced_analytics/ethnobotany/")

tree <- read.tree("np_family_tree.nwk")
circ <- ggtree(tree,layout = "circular") + geom_tiplab()
png("phylo.png",width=960,height=960)
circ
dev.off()

