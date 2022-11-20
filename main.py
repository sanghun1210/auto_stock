import urllib
import time
 
from mail import *
from markets.stock_market import *
from financial_stat import *
from stock_list import *
#from investor_trends import *
import pickle
import json
from datetime import datetime
import logging

logger = None

# def get_aleady_check_list():
#     readList = []
#     try:
#         with open(read_file_name, 'rb') as lf:
#             readList = pickle.load(lf)
#     except Exception as e:    
#         print("get_aleady_check_list error ", e)
#     return readList

#재무분석
def check_fs(ticker_code):
    global logger
    try:
        fs = FinacialStat()
        fs.init_fs(ticker_code)

        point = 0

        current_pbr = fs.get_current_pbr()
        if current_pbr == None or math.isnan(float(current_pbr)) == True or current_pbr > 2.7 :
            return False

        current_roe = fs.get_current_roe()
        pre_roe = fs.get_pre_roe()
        current_operating_income = fs.get_current_operating_incom(1)
        # current_annual_eps = fs.get_current_annual_data(9)
        # current_quater_eps = fs.get_current_quater_data(9)
        # current_annual_roe = fs.get_current_annual_data(5)

        #print('current_pbr, current_roe, pre_roe :' + str(current_pbr) + ' ' + str(current_roe) + ' ' + str(pre_roe) )
        #ROE 7이상 PBR 0.5 미만
        logger.info(' current_roe : ' + str(current_roe) )
        logger.info(' current_pbr : ' + str(current_pbr) )
        logger.info(' fs.is_continous_rising_quater(1) : ' + str(fs.is_continous_rising_quater(1)) )
        logger.info(' fs.is_continous_rising_quater(5): ' + str(fs.is_continous_rising_quater(5)) )
        logger.info(' fs.is_continous_rising_quater_third(5): ' + str(fs.is_continous_rising_quater_third(5)) )
        
        # 기업이 성장했는가?
        # 매출액 성장 #EPS 성장
        if  fs.is_continous_rising_annual(0) and fs.is_continous_rising_annual(9) and current_operating_income > 0:
            point += 2
            # if (current_roe >= 5 and current_pbr < 1 and current_pbr >= 0) or \
            #     (current_roe >= 5 and current_operating_income > 0 and current_pbr < -1) :
            #     point += 1

        #영업이익 3분기 연속 증가
        if fs.is_continous_rising_quater_third(1):
            #print('#영업이익 3분기 이상 증가')
            logger.info('#영업이익 3분기 이상 증가')
            point += 1

        #영업이익 증가, ROE 증가(1.5이상)
        if fs.is_continous_rising_quater(5) and \
            (current_roe > (pre_roe + 1.5)):
            #print('#영업이익 증가, ROE 증가(1.5이상)')
            logger.info('#영업이익 증가, ROE 증가(1.5이상)')
            point += 1

        #ROE가 3분기 연속 증가
        if fs.is_continous_rising_quater_third(5):
            #print('#ROE가 3분기 이상 증가')
            logger.info('#ROE가 3분기 이상 증가')
            point += 1

        #평균 EPS가 3분기 높다.
        if fs.is_continous_rising_quater_advenced(9):
            #print('#EPS가 3분기 이상 증가')
            logger.info('#ROE가 3분기 이상 증가')
            point += 1

        return point
    except Exception as e:    
        # print("raise error ", e)
        return 0
    
def main():
    global logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    log_file_name = str(datetime.today().strftime("%Y%m%d%H%M"))+'.log'

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler(log_file_name)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.info('logging start')

    to_send_mail_list = []
    to_write_file_list = []

    to_send_mail_list.append('주도주체가 파는데 오르는 종목' )
    to_send_mail_list.append('주도주체가 더이상 팔게 없는 종목' )
    to_send_mail_list.append('주도주체가 다시 사고 있는 종목' )
    
    try:
        stock_market = StockMarket(logger)
        stock_list_df = get_stock_list()
        sector_dict = dict()
        ticker_dict = dict()

        for row in stock_list_df:
            try:
                logger.info('----------------------------------------------------------------')
                if row['Symbol'].isnumeric():
                    ticker_code = row['Symbol']
                    #ticker_code = '005090'
                else:
                    continue

                market = row['Market']
                name = row['Name']
                sector = row['Sector']

                if market != 'KOSDAQ' and market != 'KOSPI':
                    continue

                if sector == '':
                    continue

                log_concat_str =  str(ticker_code) + ' | ' + market + ' | ' + name
                logger.info(log_concat_str)

                to_mail = str(ticker_code)
                is_buy = False

                print('checking... ticker_code: ', ticker_code)

                #우선순위1 : 차트 확인
                pattern = 0
                # if stock_market.check_month_base(ticker_code) and stock_market.check_week_base(ticker_code) and stock_market.check_day1(ticker_code):
                #     logger.info('check_month_base 통과')
                #     pattern += 1

                # if stock_market.check_month_base2(ticker_code) and stock_market.check_week_base2(ticker_code) and stock_market.check_day2(ticker_code):
                #     logger.info('check_month_base2 통과')
                #     pattern += 2

                # if stock_market.check_week_base(ticker_code) and stock_market.check_month_base_day2(ticker_code):
                #     logger.info('check_month_base 통과')
                #     pattern += 2

                # result = stock_market.check_week_by_rsi(ticker_code) or stock_market.check_day_by_rsi(ticker_code)
                #trade_price = stock_market.get_week_trade_price(ticker_code)

                # if result == False:
                #     continue

                if stock_market.check_pattern_dmi_adx4(ticker_code) :
                    pattern += 1

                # if stock_market.check_pattern2(ticker_code) :
                #     pattern += 2

                # if stock_market.check_day_by_rsi(ticker_code) :
                #     pattern += 2

                    
                if pattern <= 0:
                    logger.info('차트 통과 실패')
                    continue

                #우선순위2 : 수급확인
                #외국인이나 기관이 들어온 종목
                # it = InvestorTrends(str(ticker_code))
                # is_buy_agency = False
                # is_buy_foreigner = False

                # agency1 = it.get_cumulative_trading_volume_agency(1)
                # foreigner1 = it.get_cumulative_trading_volume_foreigner(1)

                # sum = 0
                # if agency1 > foreigner1:
                #     if foreigner1 > 0:
                #         sum = agency1 - foreigner1
                #     else:
                #         sum = agency1 + foreigner1
                # else : 
                #     if agency1 > 0:
                #         sum = foreigner1 - agency1 
                #     else:
                #         sum = agency1 + agency1 

                # print(agency1, foreigner1)
                # print(sum)

                # 성과. 혹은 실적 점수
                #point = check_fs(ticker_code)
                if True :
                    to_write_file_list.append(str(ticker_code))

                    if pattern == 1 : to_mail ='[P1] ' + to_mail
                    if pattern == 2 : to_mail ='[P2] ' + to_mail
                    if pattern == 3 : to_mail ='[P3] ' + to_mail

                    concat_str = to_mail + ' | ' + market + ' | ' + name  + ' | ' + sector  

                    logger.info('매수 목록에 추가')
                    to_send_mail_list.append(concat_str)
                    print(concat_str)

                    if sector in sector_dict :
                        count = sector_dict[sector]
                        sector_dict[sector] = count + 1
                    else : 
                        sector_dict[sector] = 1
                else:
                    logger.info('재무상태 좋지 않음.')


            except Exception as e:
                continue

        print(to_send_mail_list)

        msg = '\r\n'.join(to_send_mail_list)
        sorted_dict = sorted(sector_dict.items(), key = lambda item: item[1], reverse = True)
        msg = msg + '\r\n\r\n'

        for item in sorted_dict:
            msg = msg + '\r\n' + str(item)

        # for key in sorted_dict.keys():
        #     msg = msg + key + ' : ' + sorted_dict[key]

        send_mail(msg, "check stock result")
        # with open(write_file_name, 'wb') as wf:
        #     pickle.dump(to_write_file_list, wf)

        print(sector_dict)            
    except Exception as e:    
        print("raise error ", e)
        
if __name__ == "__main__":
    # execute only if run as a script
    main()