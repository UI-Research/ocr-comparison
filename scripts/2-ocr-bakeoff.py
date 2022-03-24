import pandas as pd
from fuzzywuzzy import fuzz

def import_scan(docNum):
    bm = open('comparison-output-data/benchmark/scan{}.txt'.format(docNum),'r').read()
    tx = open('comparison-output-data/textract/scan{}.txt'.format(docNum),'r').read()
    et = open('comparison-output-data/extracttable/scan{}_Page_1.txt'.format(docNum),'r').read()
    ts = open('comparison-output-data/tesseract/scan{}-text.txt'.format(docNum),'r').read()
    ad = open('comparison-output-data/adobe/scan{}.txt'.format(docNum),'r').read()
    if docNum == 2:
        et = et + open('comparison-output-data/extracttable/scan2_Page_2.txt','r').read()
        
    return [bm, et, ts, ad, tx]

def run_comparison(ocrList):
    arr = [fuzz.token_sort_ratio(ocrList[0], ocrList[i]) for i in range(1,len(ocrList))]
    return arr

if __name__ == "__main__":
    n_scans = 3 # can alter accordingly
    print('Importing scans...')
    scan_lists = [import_scan(i) for i in range(1,n_scans+1)]
    fuzzy_scores = [run_comparison(scan_list) for scan_list in scan_lists]
    col_names = ['ExtractTable', 'Tesseract', 'Adobe', 'Textract']
    df = pd.DataFrame(fuzzy_scores, columns = col_names)
    df['scan'] = range(1,n_scans+1)
    print('Saving out results...')
    df.to_csv('comparison-output-data/results.csv', index=False)
