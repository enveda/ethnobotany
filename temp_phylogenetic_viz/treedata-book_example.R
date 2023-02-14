library(ggtree)
library(treeio)
## example tree from https://support.bioconductor.org/p/72398/
tree <- read.tree(text= paste("(Organism1.006G249400.1:0.03977,", 
                              "(Organism2.022118m:0.01337,(Organism3.J34265.1:0.00284,",
                              "Organism4.G02633.1:0.00468)0.51:0.0104):0.02469);"))
p <- ggtree(tree) + geom_tiplab()  


tree <- read.tree(text = "((A, B), (C, D));")
d <- data.frame(label = LETTERS[1:4], 
                label2 = c("sunflower", "tree", "snail", "mushroom"))

## rename_taxa use 1st column as key and 2nd column as value by default                
## rename_taxa(tree, d)
rename_taxa(tree, d, label, label2) %>% write.tree

tree2 <- full_join(tree, d, by = "label")
tree2

