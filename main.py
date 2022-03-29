import urllib
import time
 
from mail import *
from markets.stock_market import *
from financial_stat import *
from stock_list import *
from investor_trends import *
import pickle

read_file_name = '2022-03-23-15000.txt'
write_file_name = '2022-03-28-1400.txt'

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

        current_pbr = fs.get_current_pbr()
        if current_pbr == None or math.isnan(float(current_pbr)) == True or current_pbr > 2.5 :
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
            count += 1

        #ROE가 3분기 이상 증가
        if fs.is_continous_rising_quater_third(5):
            #print('#ROE가 3분기 이상 증가')
            count += 1

        #영업이익 3분기 이상 증가
        if fs.is_continous_rising_quater_third(1):
            #print('#영업이익 3분기 이상 증가')
            count += 1

        if fs.is_continous_rising_annual(3):
            count += 10

        #todo : PBR이 3분기 이상 낮아짐
        return count
    except Exception as e:    
        print("raise error ", e)
        return 0
    
def main():
    to_send_mail_list = []
    to_write_file_list = []


    # to_send_mail_list.append('1 : ROE 7이상 PBR 0.5 미만')
    # to_send_mail_list.append('2 : 영업이익 증가, ROE 증가(1.5이상) -> ROE가 얼마나 증가했는지 체크 필요(많이 오를수록 좋다. 3이상)')
    # to_send_mail_list.append('4 : ROE가 3분기 이상 증가 -> ROE가 얼마나 증가했는지 체크 필요(많이오를수록 좋다.)')
    # to_send_mail_list.append('8 : 영업이익 3분기 이상 증가 -> 작년에 비해서 얼마나 증가했는가')


    to_send_mail_list.append(' [P1] : 거래량 바닥 확인, 장대 음봉 시 매매 불가 ' )
    to_send_mail_list.append(' [P2] : 지지선 확인, 강세 다이버전스 확인, 그 외 매매 불가 ' )
    
    try:
        stock_market = StockMarket()
        stock_list_df = get_stock_list()
        #check_list = get_aleady_check_list()

        for row in stock_list_df:
            try:
                if row['Symbol'].isnumeric():
                    ticker_code = row['Symbol']
                else:
                    continue

                market = row['Market']
                name = row['Name']
                sector = row['Sector']

                to_mail = str(ticker_code)
                pattern = 0
                is_buy = False

                print('checking... ticker_code: ', ticker_code)

                #우선순위1 : 차트 확인
                if stock_market.check_advenced(ticker_code) :
                    if stock_market.get_check_point(ticker_code) >= 3 :
                        pattern = 1
                    elif stock_market.get_check_point2(ticker_code) >= 1 :
                        pattern = 2
                    else :
                        continue
                else:
                    continue

                print('step2')

                #우선순위2 : 수급확인
                #외국인이나 기관이 들어온 종목
                it = InvestorTrends(str(ticker_code))
                is_buy_agency = False
                is_buy_foreigner = False
                if it.get_cumulative_trading_volume_agency(20) > 0 : 
                    is_buy_agency = True
                if it.get_cumulative_trading_volume_foreigner(10) > 0 :
                    is_buy_foreigner = True

                if is_buy_agency == False and is_buy_foreigner  == False:
                    continue

                # 성과. 혹은 실적 점수
                p_score = check_fs(ticker_code)
                if p_score > 0 and p_score != 10:
                    to_write_file_list.append(str(ticker_code))
                    # if str(ticker_code) in check_list:
                    #     print('aleady in list')
                    #     continue
                    # else:
                    concat_str = to_mail + ' | ' + market + ' | ' + name  + ' | ' + sector + ' | p_score : ' + str(p_score)
                    to_send_mail_list.append(concat_str)
                    print(concat_str)
            except Exception as e:
                continue

        print(to_send_mail_list)
        send_mail('\r\n'.join(to_send_mail_list), "check stock result")
        with open(write_file_name, 'wb') as wf:
            pickle.dump(to_write_file_list, wf)
            
    except Exception as e:    
        print("raise error ", e)
        
if __name__ == "__main__":
    # execute only if run as a script
    main()