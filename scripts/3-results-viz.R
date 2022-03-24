library(forcats)
library(dplyr)
library(readr)
library(magrittr)
library(tidyr)
library(ggplot2)
library(urbnthemes)
set_urbn_defaults(style = "print")

names <- c('Blurry and Rotated', 'Tricky Tables', 'Handwritten')

results <- read_csv('comparison-output-data/results.csv')
results <- results %>%
  mutate(scan = factor(names, levels=names)) %>%
  pivot_longer(cols = ExtractTable:Textract) %>%
  rename(ocr = name, score = value) %>%
  mutate(ocr = factor(ocr))

ggplot(results, aes(x = scan, y = score, fill = fct_reorder(ocr, score))) + 
  geom_bar(stat='identity', width=0.5, position='dodge') + 
  labs(x='Document', y='Token Sort Ratio Score')
      
ggsave('img/results.png')
