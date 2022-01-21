import urllib
import time
 
from mail import *
from markets.stock_market import *
from financial_stat import *
from stock_list import *
from investor_trends import *
import pickle

read_file_name = '2022-01-17-1501.txt'
write_file_name = '2022-01-19-1500.txt'

def get_aleady_check_list():
    readList = []
    try:
        with open(read_file_name, 'rb') as lf:
            readList = pickle.load(lf)
    except Exception as e:    
        print("get_aleady_check_list error ", e)
    return readList

#재무분석
def check_fs(ticker_code):
    try:
        fs = FinacialStat()
        fs.init_fs(ticker_code)

        print('checking... ticker_code: ', ticker_code)
        current_pbr = fs.get_current_pbr()
        if current_pbr == None or math.isnan(float(current_pbr)) == True or current_pbr > 2.4 :
            return False

        current_roe = fs.get_current_roe()
        pre_roe = fs.get_pre_roe()

        #print('current_pbr, current_roe, pre_roe :' + str(current_pbr) + ' ' + str(current_roe) + ' ' + str(pre_roe) )
        #ROE 7이상 PBR 0.5 미만
        count = 0
        if current_roe > 7 and current_pbr < 0.5:
            #print('#ROE 7이상 PBR 0.5 미만')
            count += 1

        #영업이익 증가, ROE 증가(1.5이상)
        if fs.is_continous_rising_quater(1) and fs.is_continous_rising_quater(5) and \
            (current_roe > (pre_roe +1.5)):
            #print('#영업이익 증가, ROE 증가(1.5이상)')
            count += 2

        #ROE가 3분기 이상 증가
        if fs.is_continous_rising_quater_third(5):
            #print('#ROE가 3분기 이상 증가')
            count += 4

        #영업이익 3분기 이상 증가
        if fs.is_continous_rising_quater_third(1):
            #print('#영업이익 3분기 이상 증가')
            count += 8

        #todo : PBR이 3분기 이상 낮아짐
        return count
    except Exception as e:    
        print("raise error ", e)
        return 0
    
def main():
    to_send_mail_list = []
    to_write_file_list = []


    to_send_mail_list.append('1 : ROE 7이상 PBR 0.5 미만')
    to_send_mail_list.append('2 : 영업이익 증가, ROE 증가(1.5이상) -> ROE가 얼마나 증가했는지 체크 필요(많이 오를수록 좋다. 3이상)')
    to_send_mail_list.append('4 : ROE가 3분기 이상 증가 -> ROE가 얼마나 증가했는지 체크 필요(많이오를수록 좋다.)')
    to_send_mail_list.append('8 : 영업이익 3분기 이상 증가 -> 작년에 비해서 얼마나 증가했는가')
    
    try:
        stock_market = StockMarket()
        tickers = get_stock_list()
        check_list = get_aleady_check_list()

        for ticker_code in tickers:
            to_mail = str(ticker_code)
            is_buy = False

            result = check_fs(ticker_code)
            if result == 0:
                continue

            it = InvestorTrends(str(ticker_code))
            print(it.get_cumulative_trading_volume_agency(5) ,it.get_cumulative_trading_volume_foreigner(5) )
            if it.get_cumulative_trading_volume_agency(5) < 0 and it.get_cumulative_trading_volume_foreigner(5) < 0:
                continue

            if stock_market.check_advenced(ticker_code) and \
                stock_market.get_check_point(ticker_code) >= 5 :
                to_mail = to_mail 
                is_buy = True 

            if is_buy:
                to_write_file_list.append(str(ticker_code))
                if str(ticker_code) in check_list:
                    print('aleady in list')
                    continue
                else:
                    print('wow!!!')
                    agency_count = it.get_buy_day_count_agency(5)
                    foreigner_count = it.get_buy_day_count_foreigner(5)
                    to_send_mail_list.append(to_mail + ' favorite code : ' + str(result) + ' trade_count : ' + str(agency_count)+ ', ' + str(foreigner_count))
        print(to_send_mail_list)
        send_mail('\r\n'.join(to_send_mail_list), "check stock result")
        with open(write_file_name, 'wb') as wf:
            pickle.dump(to_write_file_list, wf)
            
    except Exception as e:    
        print("raise error ", e)
        
if __name__ == "__main__":
    # execute only if run as a script
    main()