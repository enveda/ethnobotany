library(ggtreeExtra)
library(ggtree)
library(treeio)
library(tidytree)
library(ggstar)
library(ggplot2)
library(ggnewscale)
library(reshape)

tree <- read.newick("./temp_phylogenetic_viz/np_family_tree.nwk")
dat2 <-
  read.table(
    "./temp_phylogenetic_viz/family_indication_count_normalized.tsv",
    sep = "\t",
    header = TRUE,
    row.names = 1,
    fill = TRUE
  )
dat2$rowname <- rownames(dat2)
dat2 <- melt(dat2) # melting helps with plotting in geom_fruit()

nodeids <- nodeid(tree, tree$node.label)
nodedf <- data.frame(node = nodeids)
labdf <-
  data.frame(node = nodeids, label = tree$node.label)

# The circular layout tree.
p <-
  ggtree(tree,
         layout = "fan",
         size = 0.5,# line thickness
         open.angle = 0) + # gives it a nice gap
  geom_tiplab(align=TRUE, geom = 'text', size=2) +
  new_scale_fill() +
  geom_fruit(
    # lets you map whatever plot to a histogram
    data = dat2,
    geom = geom_tile, # basically a heat map
    mapping = aes(y = rowname, x = variable, fill = value),
    color = "#666666", # color of the lines
    offset = 0.15,
    size = 0.02 # width of lines (maybe)
  ) +
  scale_fill_viridis_b(option = "viridis", name = "value") #+ #bins before coloring
# scale_fill_gradient(high = "#F67280", low = "#16EB96") + # use if you want enveda colors (looks gross, might need a lot of massaging in illustrator)
# theme_minimal() #+
# scale_fill_viridis_c(option = "magma", name = "value") # could use continuous viridis theme
# scale_alpha_continuous(range = c(0, 1), guide = guide_legend(keywidth = 0.3,keyheight = 0.3,order = 5)) # alpha = transparency

p

#install.packages("svglite")
library(svglite)
ggsave(
  "with_text.svg", #infinite zoom; good for editing in illustrator
  plot = p,
  width = 12,
  height = 12,
  units = 'in',
  dpi = 300 # good for publishing
)
