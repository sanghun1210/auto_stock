import urllib
import time
 
from mail import *
from markets.stock_market import *

ticker_filename = 'ticker_code.txt'

def main():
    to_send_mail_list = []
    try:
        stock_market = StockMarket()
        tickers = stock_market.get_ticker_all(ticker_filename)
        for ticker_code in tickers:
            print('checking... ticker_code: ', ticker_code)
            if stock_market.is_nice_week(ticker_code):
                to_send_mail_list.append(ticker_code)
                print('wow')
                time.sleep(10)  
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