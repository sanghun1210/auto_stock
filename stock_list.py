import FinanceDataReader as fdr
import pandas as pd
import csv

def get_stock_list():
    try:
        krx_list = fdr.StockListing("KRX")
        krx_list.to_csv('test.csv', encoding="cp949")
    except Exception as e:    
        print("raise error ", e)
    
    code = []
    return_df = []
    with open('test.csv', mode='r', encoding='cp949') as target_csv:
        df = csv.DictReader(target_csv, delimiter=',')
        for n, row in enumerate(df):
            if not n:#skip header
                continue

            # if row['Industry'].isspace() or row['Industry'] == '':
            #     continue

            return_df.append(row)

    if return_df != None:
        return return_df

if __name__ == "__main__":
    # execute only if run as a script
    get_stock_list()
        

