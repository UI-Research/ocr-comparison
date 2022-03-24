# OCR Comparison
This repository compares four representative OCR offerings in an accuracy "bake off" on three scanned documents of poor-quality (askew/blurry, strange table formatting, and handwritten.)

## Required R libraries
- `tesseract`
- `tidyverse`
-  `urbnthemes`

## Required Python libraries
- `Extracttable`
- `boto3`
- `pandas`
- `fuzzywuzzy`

# Summary of Files
###  `comparison-input-data/`
- contains the input document scans used to evaluate accuracy. Note that Scan #2 is also split into separate files for each of its two pages so that the *textract-to-csv.py* script runs properly.
### `comparison-output-data/`
- contains the extracted text for each OCR service and the "ground truth" benchmark for comparison purposes.
- **benchmark/ocr-tables.xlsx** provides side-by-side comparisons of tabular output for ExtractTable, Textract, and the ground truth.
### `scripts/`
- **1a-extracttable-to-text-and-csv.py** performs OCR on each document using ExtractTable's API and outputs both text files and CSV files with extracted text and tabular data
- **1b-tesseract-to-text.R** performs OCR on each document using the *tesseract* package in R 
- **1c-textract-to-text.py** performs OCR on each document using the AWS Textract API and outputs text files with extracted text (requires AWS credentials and creating an S3 bucket)
- **1d-textract-to-csv.py** extracts tabular data from each document using the AWS Textract API and outputs CSV files with extracted text
(requires AWS credentials)
- **2-ocr-bakeoff.py** computes scores from the fuzzy matching analysis using *token sort ratio* from the *fuzzywuzzy* package to compare document accuracy against the benchmark.
- **3-results-viz.R** plots a side-by-side bar chart depicting these results.
- Note: Adobe simply uses a click-based interface to run OCR and export the results as plain text

## Replication
This text analysis can be replicated with other documents by following these steps:
1. Save each document in PDF, PNG, or JPEG format in the `comparison-input-data/` directory.
2. Alter the file names in each OCR script (1a-1d) with your file names. Note: Textract requires AWS credentials and ExtractTable requires an API key.
3. Add "ground truth" text files in the `comparison-output-data/benchmark/` directory (likely requires typing them manually)
4. Run scripts in the order they appear above.

## Setting up API Key and AWS Credentials
- Information on accessing an API Key for ExtractTable is found [here](https://documenter.getpostman.com/view/6396033/SVfMS9xu?version=latest).
- Information on setting up AWS credentials needed to access Textract and other AWS services is found [here](https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/setup-credentials.html).
- Information on setting up an S3 bucket in AWS, which is needed to run **1c-textract-to-text.py**, is found [here](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html).


## Useful Extensions
The results from this "bake off" are publicly available and offer a framework for further evaluation. We would love to see the following:
1. More diverse types of documents added to the three used here that cover other scanning issues that complicate OCR efforts
2. Additional OCR offerings! The four used here are meant to be representative and obviously not exhaustive. Please feel free to create new scripts and directories that build off this initial effort. 
