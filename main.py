import urllib
import time
 
from mail import *
from markets.stock_market import *
import logging

ticker_filename = 'ticker_code.txt'
except_list = ['052190', '033790', '053450', '044490', '003280' ]

def main():
    to_send_mail_list = []
    try:
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler = logging.FileHandler('stock_point.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        stock_market = StockMarket(logger)
        tickers = stock_market.get_ticker_all(ticker_filename)
        for ticker_code in tickers:
            if ticker_code in except_list:
                continue

            print('checking... ticker_code: ', ticker_code)
            stock_market.init_trader(ticker_code)
            point = stock_market.check_point(ticker_code)
            if point >= 9.4 :
                to_send_mail_list.append(ticker_code + ' point : ' + str(point))
                
        print(to_send_mail_list)
        send_mail('\r\n'.join(to_send_mail_list), "check stock result")
            
    except Exception as e:    
        print("raise error ", e)
if __name__ == "__main__":
    # execute only if run as a script
    main()