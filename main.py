import urllib
import time
 
from mail import *
from markets.stock_market import *

ticker_filename = 'ticker_code.txt'
except_list = ['052190', '033790', '053450', '044490', '003280' ]

def main():
    to_send_mail_list = []
    try:
        stock_market = StockMarket()
        tickers = stock_market.get_ticker_all(ticker_filename)
        for ticker_code in tickers:
            if ticker_code in except_list:
                continue

            print('checking... ticker_code: ', ticker_code)
            stock_market.init_trader(ticker_code)
            # if stock_market.is_2021_6month_pattern1(ticker_code):
            #     print('2021 6month good1')
            #     to_send_mail_list.append(ticker_code + ' wow1')

            if stock_market.is_2021_6month_pattern3(ticker_code):
                print('2021 6month good2')
                to_send_mail_list.append(ticker_code + ' wow2')
                
            # if stock_market.is_pattern5_good(ticker_code):
            #     to_send_mail_list.append(ticker_code + 'wow5')                
                #to_send_mail_list.append(ticker_code)
            # if stock_market.is_nice_day(ticker_code):
            #     to_send_mail_list.append(ticker_code)
            #     print('wow')
            #     time.sleep(2)     

        print(to_send_mail_list)
        send_mail('\r\n'.join(to_send_mail_list), "check stock result")
            
    except Exception as e:    
        print("raise error ", e)
if __name__ == "__main__":
    # execute only if run as a script
    main()