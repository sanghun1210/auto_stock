import urllib
import time
 
from mail import *
from markets.stock_market import *
from financial_stat import *
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
            to_mail = str(ticker_code)
            is_buy = False
            if ticker_code in except_list:
                continue

            fs = FinacialStat()
            fs.init_fs(ticker_code)

            print('checking... ticker_code: ', ticker_code)
            if stock_market.check_week(ticker_code) :
                if fs.is_continous_rising_quater(1) and fs.is_continous_rising_annual(1) :
                    to_mail = to_mail + ' - week  '
                    print('check fs week!!!!!!')
                    is_buy = True

            if stock_market.check_day(ticker_code):
                if fs.is_continous_rising_quater(1) :
                    to_mail = to_mail + ' - day  '
                    print('check fs day!!!!!!')
                    is_buy = True

            if is_buy:
                to_send_mail_list.append(to_mail)
                    
        print(to_send_mail_list)
        send_mail('\r\n'.join(to_send_mail_list), "check stock result")
            
    except Exception as e:    
        print("raise error ", e)
        
if __name__ == "__main__":
    # execute only if run as a script
    main()