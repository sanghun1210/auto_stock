import urllib
import time
 
from mail import *
from markets.stock_market import *
from financial_stat import *
from stock_list import *
from investor_trends import *
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
            logger.info('#ROE 7이상 PBR 0.5 미만')
            count += 1

        #영업이익 증가, ROE 증가(1.5이상)
        if fs.is_continous_rising_quater(1) and fs.is_continous_rising_quater(5) and \
            (current_roe > (pre_roe +1.5)):
            #print('#영업이익 증가, ROE 증가(1.5이상)')
            logger.info('#영업이익 증가, ROE 증가(1.5이상)')
            count += 1

        #ROE가 3분기 이상 증가
        if fs.is_continous_rising_quater_third(5):
            #print('#ROE가 3분기 이상 증가')
            logger.info('#ROE가 3분기 이상 증가')
            count += 1

        #영업이익 3분기 이상 증가
        if fs.is_continous_rising_quater_third(1):
            #print('#영업이익 3분기 이상 증가')
            logger.info('#영업이익 3분기 이상 증가')
            count += 1

        if fs.is_continous_rising_annual(3):
            logger.info('#영업이익 3년 이상 증가')
            count += 10

        #todo : PBR이 3분기 이상 낮아짐
        logger.info('재무분석결과 : ' + str(count) )
        return count
    except Exception as e:    
        print("raise error ", e)
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

    to_send_mail_list.append(' [T1] : 거래량 바닥 확인, 장대 음봉 확인 시 매매 불가 , 가능한 60분봉에서 stc 가 30미만인것으로 매매' )
    to_send_mail_list.append(' [T2] : 지지선 확인, 강세 다이버전스 확인, 그 외 매매 불가, 가능한 60분봉의 macd가 상승추세인것을 확인 ' )
    
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
                else:
                    continue

                market = row['Market']
                name = row['Name']
                sector = row['Sector']

                log_concat_str =  str(ticker_code) + ' | ' + market + ' | ' + name
                logger.info(log_concat_str)

                to_mail = str(ticker_code)
                pattern = 0
                is_buy = False

                print('checking... ticker_code: ', ticker_code)

                #우선순위1 : 차트 확인
                if stock_market.check_advenced(ticker_code) :
                    logger.info('check_advenced 통과')
                    if stock_market.get_check_point(ticker_code) >= 3 :
                        logger.info('pattern1 통과')
                        pattern = 1
                    elif stock_market.get_check_point2(ticker_code) >= 2 :
                        logger.info('pattern2 통과')
                        pattern = 2
                    else :
                        logger.info('일간 차트 통과 실패')
                        continue
                else:
                    logger.info('check_advenced 차트 통과 실패')
                    continue

                #우선순위2 : 수급확인
                #외국인이나 기관이 들어온 종목
                it = InvestorTrends(str(ticker_code))
                is_buy_agency = False
                is_buy_foreigner = False
                if it.get_cumulative_trading_volume_agency(20) > 0 : 
                    logger.info('기관매수')
                    is_buy_agency = True
                if it.get_cumulative_trading_volume_foreigner(10) > 0 :
                    logger.info('외국인매수')
                    is_buy_foreigner = True

                # if is_buy_agency == False and is_buy_foreigner  == False:
                #     continue

                # 성과. 혹은 실적 점수
                p_score = check_fs(ticker_code)
                if p_score > 0 and p_score != 10:
                    to_write_file_list.append(str(ticker_code))
                    # if str(ticker_code) in check_list:
                    #     print('aleady in list')
                    #     continue
                    # else:

                    if pattern == 1 :
                        to_mail ='[T1] ' + to_mail 
                    else :
                        to_mail ='[T2] ' + to_mail 

                    concat_str = to_mail + ' | ' + market + ' | ' + name  + ' | ' + sector + ' | ' + str(p_score)
                    if is_buy_agency :
                        concat_str = concat_str + ' | 기관매수'
                    if is_buy_foreigner :
                        concat_str = concat_str + ' | 외국인매수'

                    ticker_dict[concat_str] = p_score

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

        # sorted_ticker_dict = sorted(sector_dict.items(), key = lambda item: item[1], reverse = True)

        # msg = ''

        # for item in sorted_ticker_dict:
        #     msg = msg + '\r\n' + str(item)
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