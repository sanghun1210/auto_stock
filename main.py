import urllib
import time
 
from mail import *
from markets.stock_market import *
from financial_stat import *
from stock_list import *
import pickle

read_file_name = '2022-01-13-1400.txt'
write_file_name = '2022-01-14-1400.txt'

def get_aleady_check_list():
    readList = []
    try:
        with open(read_file_name, 'rb') as lf:
            readList = pickle.load(lf)
    except Exception as e:    
        print("get_aleady_check_list error ", e)
    return readList
    
def main():
    to_send_mail_list = []
    to_write_file_list = []
    
    try:
        stock_market = StockMarket()
        tickers = get_stock_list()
        check_list = get_aleady_check_list()

        for ticker_code in tickers:
            to_mail = str(ticker_code)
            is_buy = False

            fs = FinacialStat()
            fs.init_fs(ticker_code)

            print('checking... ticker_code: ', ticker_code)
            pbr = fs.get_cuurent_quater_pbr()
            if pbr == None or math.isnan(float(pbr)) == True or pbr >= 3.0 :
                continue

            if fs.is_continous_rising_quater(1) == False :
                continue

            if stock_market.check_week(ticker_code) :
                to_mail = to_mail + ' - week  '
                print('check fs week!!!!!!')
                is_buy = True

            if stock_market.check_day(ticker_code):
                to_mail = to_mail + ' - day  '
                print('check fs day!!!!!!')
                is_buy = True 

            if is_buy:
                to_write_file_list.append(str(ticker_code))

                if str(ticker_code) in check_list:
                    print('aleady in list')
                    continue

                per = fs.get_cuurent_quater_per()
                if per != None and math.isnan(float(pbr)) == False  :
                    to_mail = to_mail + ' per :  ' + str(per)
                    print('per :' +  str(per))
                    if per <= 43: 
                        to_send_mail_list.append(to_mail)
                else:
                    to_send_mail_list.append(to_mail)
        print(to_send_mail_list)
        send_mail('\r\n'.join(to_send_mail_list), "check stock result")
        with open(write_file_name, 'wb') as wf:
            pickle.dump(to_write_file_list, wf)
            
    except Exception as e:    
        print("raise error ", e)
        
if __name__ == "__main__":
    # execute only if run as a script
    main()