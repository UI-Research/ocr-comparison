library(tesseract)
library(tidyverse)

tesseract_to_text <- function(input_file, engine){
  output_file <- str_remove(input_file, pattern = '\\..*')
  ocr(paste0('comparison-input-data/',input_file), engine = engine) %>%
    cat(file = paste0('comparison-output-data/tesseract/',output_file,'-text.txt'))
  
}

print("Document conversion: ")
eng <- tesseract('eng')
docs <- c('scan1.pdf', 'scan2.pdf', 'scan3.png')
walk(.x = docs, .f = tesseract_to_text, engine = eng)