import os
import jwt
import uuid
import hashlib
import json
import time
from urllib.parse import urlencode

import requests

from .base_market import *
from .base_trader import *
from .week_trader import *
from .day_trader import *
from .month_trader import *
from . import algorithms

class StockMarket(BaseMarket):
    def __init__(self, logger):
        super().__init__()
        self.market_group = None
        self.week_trader = None
        self.day_trader = None
        self.minute240_trader = None
        self.minute60_trader = None
        self.minute30_trader = None
        self.minute15_trader = None
        self.minute10_trader = None
        self.minute5_trader = None
        self.minute3_trader = None
        self.logger = logger

    def get_ticker_all(self, ticker_filename) : 
        with open(os.path.join(os.getcwd(), ticker_filename), 'r') as f:
            list_file = []
            for line in f:
                list_file.append(line.replace('\n',''))
        return list_file

    def init_trader(self, ticker_code):        
        try:
            self.week_trader = WeekTrader(ticker_code, 30)
            self.day_trader = DayTrader(ticker_code, 50)
        except Exception as e:
            print("day_trader init fail: ", e)


    def check_week1(self, ticker_code):
        try:
            point = 0
            self.week_trader = WeekTrader(ticker_code, 45)
            if self.week_trader.candles[1].trade_volume == 0:
                return False

            week_pdf = self.week_trader.get_dataframe()
            bw = algorithms.bbands_width(week_pdf, 10)
            sma10 = algorithms.get_current_sma(week_pdf, 10)

            self.logger.info('macd is ture: ' + str(algorithms.macd_line_over_than_signal2(week_pdf, 12, 26, 9)))  
            self.logger.info('week_pdf[trade_price]: ' + str(week_pdf['trade_price'].iloc[-1]))  
            self.logger.info('week_bw: ' + str(bw))  

            if algorithms.macd_line_over_than_signal2(week_pdf, 12, 26, 9) and sma10 < week_pdf['trade_price'].iloc[-1] :
                return True
            
            return False
        except Exception as e:
            print("raise error ", e)
            return False

    def get_check_day(self, trader):
        current_pdf = trader.get_dataframe()
        point = 0

        fi13 = algorithms.force_index(current_pdf, 13)
        fi2 = algorithms.force_index(current_pdf, 2)
        if fi13['ForceIndex'].iloc[-1] > 0 and fi2['ForceIndex'].iloc[-1] < 0:
            self.logger.info('force_index 통과 : ' + str(fi13['ForceIndex'].iloc[-1])) 
            print('force_index') 
            return True
        else:
            self.logger.info('force_index 실패 : ' + str(fi13['ForceIndex'].iloc[-1]))    

        # print(current_pdf['opening_price'].iloc[-1])
        # print(current_pdf['trade_price'].iloc[-1])
        # print(current_pdf['opening_price'].iloc[-1] - current_pdf['trade_price'].iloc[-1])
        if (current_pdf['trade_price'].iloc[-1] - current_pdf['opening_price'].iloc[-1]) > 0:
            if current_pdf['trade_volume'].iloc[-1]  > (current_pdf['trade_volume'].iloc[-2] * 1.5):
                self.logger.info('양봉패턴1' )  
                print('양봉패턴1')
                return True
        else :
            if current_pdf['trade_volume'].iloc[-1] < current_pdf['trade_volume'].iloc[-2] and \
               current_pdf['trade_volume'].iloc[-1] < current_pdf['trade_volume'].iloc[-3] and \
               current_pdf['trade_volume'].iloc[-1] < current_pdf['trade_volume'].iloc[-4]:
               self.logger.info('음봉패턴1' )  
               print('음봉패턴1')
               return True

        rsi = algorithms.get_current_rsi(current_pdf ,7)
        if rsi < 30 :
            self.logger.info('rsi 통과' )  
            return True
        return False


    def check_week2(self, ticker_code):
        try:
            point = 0
            self.week_trader = WeekTrader(ticker_code, 45)
            if self.week_trader.candles[1].trade_volume == 0:
                return False

            week_pdf = self.week_trader.get_dataframe()
            slow_k, slow_d = algorithms.stc_slow(week_pdf, 9, 3, 3)
            bw = algorithms.bbands_width(week_pdf, 4)

            self.logger.info('macd is ture: ' + str(algorithms.macd_line_over_than_signal2(week_pdf, 12, 26, 9)))  
            self.logger.info('week_pdf[trade_price]: ' + str(week_pdf['trade_price'].iloc[-1]))  

            ema13 = algorithms.ema(week_pdf, 13)
            sma20 = algorithms.get_current_sma(week_pdf, 20)

            # print(sma13)
            # print(week_pdf['trade_price'].iloc[-1])
  
            if algorithms.macd_line_over_than_signal2(week_pdf, 12, 26, 9) and week_pdf['trade_price'].iloc[-1] >= sma20 :
                return True
            else :
                self.logger.info('check_week2 실패:')  
                        
            return False
        except Exception as e:
            print("raise error ", e)
            return False


    #바닥을 다지는 주식을 찾는다.
    #바닥을 찾는다.
    #좋은 주식은 더이상 떨어지지 않는 주식이다.
    def get_check_day_point2(self, trader):
        current_pdf = trader.get_dataframe()
        point = 0

        slow_k, slow_d = algorithms.stc_slow(current_pdf, 7, 3, 3)
        if slow_d.iloc[-1] <= 35 :
            self.logger.info('stc_slow 통과 : ' + str(slow_d.iloc[-1]))  
            point += 1
        else:
            self.logger.info('stc_slow 실패 : ' + str(slow_d.iloc[-1]))  

        # sma20 = algorithms.get_current_sma(current_pdf, 20)
        # if current_pdf['trade_price'].iloc[-1] > sma20:
        #     point += 1

        # fi14 = algorithms.force_index(current_pdf, 14)
        # cci13 = algorithms.get_current_cci(current_pdf, 13)


        # if slow_k.iloc[-1] > slow_d.iloc[-1] :
        #     point += 1

        # sma13 = algorithms.get_current_sma(current_pdf, 13)
        # sma20 = algorithms.get_current_sma(current_pdf, 20)
        # sma60 = algorithms.get_current_sma(current_pdf, 60)

        # if current_pdf['trade_price'].iloc[-1] > sma13:
        #     cci10 = algorithms.get_current_cci(current_pdf, 10)
        #     if cci10 < 50 :
        #         point += 1
        # elif current_pdf['trade_price'].iloc[-1] > sma20:
        #     cci20 = algorithms.get_current_cci(current_pdf, 20)
        #     if cci20 < 35 :
        #         point += 1
        # elif current_pdf['trade_price'].iloc[-1] > sma60:
        #     cci60 = algorithms.get_current_cci(current_pdf, 60)
        #     if cci60 < 35 :
        #         point += 1
                
        # bw = algorithms.bbands_width(current_pdf, 2)


        # if fi14['ForceIndex'].iloc[-1] > 0 :
        #     point += 1

        # sma13 = algorithms.get_current_sma(current_pdf, 13)
        # if current_pdf['trade_price'].iloc[-1] >= sma13 or \
        #     slow_d.iloc[-1] <= 40:
        #     print('sma13 성공')
        #     point += 1

        # if cci13 < 40 :
        #     print('cci 성공')
        #     point += 1

        # if bw <= 4:
        #     print('bw 성공')
        #     point +=1

        # algorithms.bbands_is_low_touch(current_pdf, 13)


        # 진짜 이거는 아니다.
        # 다른거를 생각해봐야 한다.

        # ema13 = algorithms.ema(current_pdf, 13)
        # if ema13.iloc[-1] <= current_pdf['trade_price'].iloc[-1] :
        #     point += 1

        # fi5 = algorithms.force_index(current_pdf, 5)
        # if fi5['ForceIndex'].iloc[-1] >= 0 :
        #     self.logger.info('force_index2 통과 : ' + str(fi5['ForceIndex'].iloc[-1]))  
        #     point += 1
        # else:
        #     self.logger.info('force_index2 실패 : ' + str(fi5['ForceIndex'].iloc[-1]))  

        return point

    def check_day_pattern_result(self, ticker_code):
        try:
            day_point = 0

            self.day_trader = DayTrader(ticker_code, 150)
            if self.day_trader != None:
                return self.get_check_day(self.day_trader)  

        except Exception as e:
            print("raise error ", e)
            return False

    def get_check_point2(self, ticker_code):
        try:
            day_point = 0
            self.day_trader = DayTrader(ticker_code, 150)
            if self.day_trader != None:
                day_point = self.get_check_day_point2(self.day_trader)  

            return day_point
        except Exception as e:
            print("raise error ", e)
            return 0

    def check_month_base(self, ticker_code):
        try:
            point = 0
            self.month_trader = MonthTrader(ticker_code, 30)
            if self.month_trader.candles[1].trade_volume == 0:
                return False

            # 월봉은 중요한 차트이므로 ADX선과 같이 본다.
            month_pdf = self.month_trader.get_dataframe()
            sma13 = algorithms.get_current_sma(month_pdf, 13)
            slow_k, slow_d = algorithms.stc_slow(month_pdf, 7, 3, 3)

            if slow_d.iloc[-1] < 40 :
                return True

            # 기본
            # res = algorithms.adx(month_pdf['high_price'], month_pdf['low_price'], month_pdf['trade_price'], 14)     
            # if algorithms.macd_line_over_than_signal2(month_pdf, 12, 26, 9) and sma13 < month_pdf['trade_price'].iloc[-1] and \
            #     res['ADX_14'].iloc[-1] <= res['DMP_14'].iloc[-1] and res['ADX_14'].iloc[-1] >= res['DMN_14'].iloc[-1]:
            #     week_trader = WeekTrader(ticker_code, 50)
            #     current_pdf = week_trader.get_dataframe()
            #     slow_k, slow_d = algorithms.stc_slow(current_pdf, 7, 3, 3)
            #     # res = algorithms.adx(current_pdf['high_price'], current_pdf['low_price'], current_pdf['trade_price'], 14)   
            #     if slow_d.iloc[-1] < 45 :
            #         print('check_month_base')
            #         return True
            return False
        except Exception as e:
            print("raise error ", e)
            return False

    #주식을 왜 도박처럼 할까
    #주식을 왜 도박처럼 할까
    #주식을 왜 도박처럼 할까

    #주식은 낮은가격에 사서 높은가격에 파는것
    #좋은 종목을 오랫동안 보유하고 있는것
    #아무도 모르는 주식을 사는것
    def check_month_base_day(self, ticker_code):
        try:
            day_trader = DayTrader(ticker_code, 150)
            current_pdf = day_trader.get_dataframe()
            slow_k, slow_d = algorithms.stc_slow(current_pdf, 7, 3, 3)
            cci13 = algorithms.get_current_cci(current_pdf, 13)
            fi13 = algorithms.force_index(current_pdf, 13)
            if slow_d.iloc[-1] < 45 :
                print('check_month_base_day')
                return True
            return False
        except Exception as e:
            print("raise error ", e)
            return False

    def check_week_base(self, ticker_code):
        try:
            week_trader = WeekTrader(ticker_code, 50)
            current_pdf = week_trader.get_dataframe()
            sma20 = algorithms.get_current_sma(current_pdf, 20)
            cci13 = algorithms.get_current_cci(current_pdf, 13)
            res = algorithms.adx(current_pdf['high_price'], current_pdf['low_price'], current_pdf['trade_price'], 14)   
            if algorithms.macd_line_over_than_signal2(current_pdf, 12, 26, 9) and sma20 < current_pdf['trade_price'].iloc[-1] \
                and cci13 < 20 :
                print('check_month_base2')
                return True
            return False
        except Exception as e:
            print("raise error ", e)
            return False

    def check_week_base2(self, ticker_code):
        try:
            week_trader = WeekTrader(ticker_code, 50)
            current_pdf = week_trader.get_dataframe()
            slow_k, slow_d = algorithms.stc_slow(current_pdf, 9, 3, 3)

            bw = algorithms.bbands_width(current_pdf, 13)
            if slow_d.iloc[-1] < 40 and bw < 20:
                print('check_week_base2')
                return True
            return False
        except Exception as e:
            print("raise error ", e)
            return False

    def check_day1(self, ticker_code):
        try:
            day_trader = DayTrader(ticker_code, 150)
            current_pdf = day_trader.get_dataframe()
            cci13 = algorithms.get_current_cci(current_pdf, 13)
            slow_k, slow_d = algorithms.stc_slow(current_pdf, 7, 3, 3)
            sma13 = algorithms.get_current_sma(current_pdf, 13)
            fi14 = algorithms.force_index(current_pdf, 14)
            res = algorithms.adx(current_pdf['high_price'], current_pdf['low_price'], current_pdf['trade_price'], 13)   
            if slow_d.iloc[-1] < 40 :
                if res['ADX_13'].iloc[-1] > res['DMP_13'].iloc[-1] and slow_k.iloc[-1] < slow_d.iloc[-1] :
                    return False
                else :
                    print('check_day2')
                    return True
            return False
        except Exception as e:
            print("raise error ", e)
            return False

    def check_day2(self, ticker_code):
        try:
            day_trader = DayTrader(ticker_code, 150)
            current_pdf = day_trader.get_dataframe()
            cci13 = algorithms.get_current_cci(current_pdf, 13)
            sma20 = algorithms.get_current_sma(current_pdf, 20)
            fi13 = algorithms.force_index(current_pdf, 14)
            slow_k, slow_d = algorithms.stc_slow(current_pdf, 7, 3, 3)
            res = algorithms.adx(current_pdf['high_price'], current_pdf['low_price'], current_pdf['trade_price'], 13)     
            if algorithms.macd_line_over_than_signal2(current_pdf, 12, 26, 9) and sma20 < current_pdf['trade_price'].iloc[-1] and cci13 < 20 :
                return True
            return False
        except Exception as e:
            print("raise error ", e)
            return False

    def check_month_base2(self, ticker_code):
        try:
            point = 0
            self.week_trader = WeekTrader(ticker_code, 45)
            if self.week_trader.candles[1].trade_volume == 0:
                return False

            week_pdf = self.week_trader.get_dataframe()
            slow_k, slow_d = algorithms.stc_slow(week_pdf, 20, 12, 12)
            bw = algorithms.bbands_width(week_pdf, 4)

            if slow_k.iloc[-1] > slow_d.iloc[-1] and slow_d.iloc[-1] < 45 :
                print('check_month_base2 통과')
                return True
            else :
                self.logger.info('check_week2 실패:')  
                        
            return False
        except Exception as e:
            print("raise error ", e)
            return False


    def check_week_by_rsi(self, ticker_code):
        try:
            point = 0
            self.week_trader = WeekTrader(ticker_code, 45)
            if self.week_trader.candles[1].trade_volume == 0:
                return False

            week_pdf = self.week_trader.get_dataframe()
            rsi = algorithms.get_current_rsi(week_pdf, 13)
            slow_k, slow_d = algorithms.stc_slow(week_pdf, 7, 3, 3)

            if rsi <= 32 and slow_d.iloc[-1] < 30:
                return True
            return False
        except Exception as e:
            print("raise error ", e)
            return False

    #
    def check_pattern1(self, ticker_code):
        try:
            point = 0
            self.week_trader = WeekTrader(ticker_code, 45)
            if self.week_trader.candles[1].trade_volume == 0:
                return False

            week_pdf = self.week_trader.get_dataframe()
            rsi = algorithms.get_current_rsi(week_pdf, 13)
            slow_k, slow_d = algorithms.stc_slow(week_pdf, 7, 3, 3)
            cci13 = algorithms.get_current_cci(week_pdf, 13)

            res = algorithms.adx(week_pdf['high_price'], week_pdf['low_price'], week_pdf['trade_price'], 14)      
            if slow_k.iloc[-1] <= slow_d.iloc[-1] and res['DMP_14'].iloc[-1] > res['DMN_14'].iloc[-1] and \
                res['ADX_14'].iloc[-1] < res['DMP_14'].iloc[-1] and res['ADX_14'].iloc[-1] >= res['DMN_14'].iloc[-1]: 
                day_trader = DayTrader(ticker_code, 150)
                day_pdf = day_trader.get_dataframe()
               
                slow_k, slow_d = algorithms.stc_slow(day_pdf, 9, 3, 3)
                if slow_d.iloc[-1] < 40:
                    print('type1')
                    return True
            return False
        except Exception as e:
            print("raise error ", e)
            return False

    def check_pattern2(self, ticker_code):
        try:
            point = 0
            self.week_trader = WeekTrader(ticker_code, 45)
            if self.week_trader.candles[1].trade_volume == 0:
                return False

            week_pdf = self.week_trader.get_dataframe()
            rsi = algorithms.get_current_rsi(week_pdf, 13)
            slow_k, slow_d = algorithms.stc_slow(week_pdf, 7, 3, 3)

            if rsi <= 40 and slow_d.iloc[-1] <= 35:
                day_trader = DayTrader(ticker_code, 150)
                day_pdf = day_trader.get_dataframe()
                rsi = algorithms.get_current_rsi(day_pdf, 13)
                fi13 = algorithms.force_index(day_pdf, 13)
                fi2 = algorithms.force_index(day_pdf, 2)
                ema13 = algorithms.ema(day_pdf, 13)
                if fi13['ForceIndex'].iloc[-1] > 0 and fi2['ForceIndex'].iloc[-1] < 0:
                    return True
            return False
        except Exception as e:
            print("raise error ", e)
            return False


    def check_day_by_rsi(self, ticker_code):
        try:
            point = 0
            day_trader = DayTrader(ticker_code, 150)
            current_pdf = day_trader.get_dataframe()

            rsi = algorithms.get_current_rsi(current_pdf, 13)
            slow_k, slow_d = algorithms.stc_slow(current_pdf, 9, 3, 3)

            if rsi < 32 and slow_d.iloc[-1] < 30:
                return True
                        
            return False
        except Exception as e:
            print("raise error ", e)
            return False

    def get_week_trade_price(self, ticker_code):
        try:
            point = 0
            self.week_trader = WeekTrader(ticker_code, 45)
            if self.week_trader.candles[1].trade_volume == 0:
                return False

            week_pdf = self.week_trader.get_dataframe()
            return week_pdf['trade_price'].iloc[-1]
        except Exception as e:
            print("raise error ", e)
            return 0

    def is_yangbong(self, ticker_code):
        try:
            point = 0
            day_trader = DayTrader(ticker_code, 150)
            current_pdf = day_trader.get_dataframe()
            current_pdf['trade_price'].iloc[-1]
            return current_pdf['trade_price'].iloc[-1] - current_pdf['opening_price'].iloc[-1] 
        except Exception as e:
            print("raise error ", e)
            return 0

    def check_pattern_dmi_adx(self, ticker_code):
        try:
            point = 0
            self.week_trader = WeekTrader(ticker_code, 45)
            if self.week_trader.candles[1].trade_volume == 0:
                return False

            week_pdf = self.week_trader.get_dataframe()
            rsi = algorithms.get_current_rsi(week_pdf, 13)
            slow_k, slow_d = algorithms.stc_slow(week_pdf, 7, 3, 3)
            cci13 = algorithms.get_current_cci(week_pdf, 13)

            sma13 = algorithms.get_current_sma(week_pdf, 13)
            week_psar = algorithms.parabolic_sar(week_pdf)
            if week_pdf['trade_price'].iloc[-1] > sma13 and math.isnan(float(week_psar['PSARl_0.02_0.2'].iloc[-1])) == False :
                day_trader = DayTrader(ticker_code, 150)
                day_pdf = day_trader.get_dataframe()

                res = algorithms.adx(day_pdf['high_price'], day_pdf['low_price'], day_pdf['trade_price'], 14)    
                if res['DMP_14'].iloc[-1] > res['DMN_14'].iloc[-1] and res['ADX_14'].iloc[-1] > res['ADX_14'].iloc[-2]:
                    print('111')
                    psar = algorithms.parabolic_sar(day_pdf)
                    if math.isnan(float(psar['PSARl_0.02_0.2'].iloc[-1])) == False and psar['PSARl_0.02_0.2'].iloc[-1] < day_pdf['trade_price'].iloc[-1] and res['ADX_14'].iloc[-1] < res['DMP_14'].iloc[-1]:
                        return True



            # res = algorithms.adx(week_pdf['high_price'], week_pdf['low_price'], week_pdf['trade_price'], 14)      
            # if slow_k.iloc[-1] <= slow_d.iloc[-1] and res['DMP_14'].iloc[-1] > res['DMN_14'].iloc[-1] and \
            #     res['ADX_14'].iloc[-1] < res['DMP_14'].iloc[-1] and res['ADX_14'].iloc[-1] >= res['DMN_14'].iloc[-1]: 
            #     day_trader = DayTrader(ticker_code, 150)
            #     day_pdf = day_trader.get_dataframe()
               
            #     slow_k, slow_d = algorithms.stc_slow(day_pdf, 9, 3, 3)
            #     if slow_d.iloc[-1] < 40:
            #         print('type1')
            #         return True
            return False
        except Exception as e:
            print("raise error ", e)
            return False

    def check_pattern_dmi_adx2(self, ticker_code):
        try:
            point = 0
            self.week_trader = WeekTrader(ticker_code, 35)
            if self.week_trader.candles[1].trade_volume == 0:
                return False

            week_pdf = self.week_trader.get_dataframe()
            rsi = algorithms.get_current_rsi(week_pdf, 13)
            slow_k, slow_d = algorithms.stc_slow(week_pdf, 7, 3, 3)
            cci13 = algorithms.get_current_cci(week_pdf, 13)

            sma13 = algorithms.get_current_sma(week_pdf, 13)
            week_psar = algorithms.parabolic_sar(week_pdf)
            res = algorithms.adx(week_pdf['high_price'], week_pdf['low_price'], week_pdf['trade_price'], 14) 
            if res['DMP_14'].iloc[-1] > res['DMN_14'].iloc[-1] and res['ADX_14'].iloc[-1] > res['ADX_14'].iloc[-2] and \
                math.isnan(float(week_psar['PSARl_0.02_0.2'].iloc[-1])) == False :
                day_trader = DayTrader(ticker_code, 120)
                day_pdf = day_trader.get_dataframe()
                res = algorithms.adx(day_pdf['high_price'], day_pdf['low_price'], day_pdf['trade_price'], 14)    
                sma20 = algorithms.get_current_sma(day_pdf, 20)
                slow_k, slow_d = algorithms.stc_slow(day_pdf, 7, 3, 3)
                if slow_d.iloc[-1] <= 37 :
                    return True
            return False
        except Exception as e:
            print("raise error ", e)
            return False

    def check_pattern_dmi_adx3(self, ticker_code):
        try:
            point = 0
            self.week_trader = WeekTrader(ticker_code, 35)
            if self.week_trader.candles[1].trade_volume == 0:
                return False

            week_pdf = self.week_trader.get_dataframe()
            rsi = algorithms.get_current_rsi(week_pdf, 13)
            slow_k, slow_d = algorithms.stc_slow(week_pdf, 7, 3, 3)
            cci13 = algorithms.get_current_cci(week_pdf, 13)

            if slow_d.iloc[-1] <= 34 :
                day_trader = DayTrader(ticker_code, 120)
                day_pdf = day_trader.get_dataframe()
                slow_k, slow_d = algorithms.stc_slow(day_pdf, 7, 3, 3)
                ema13 = algorithms.ema(day_pdf, 13)
                if ema13.iloc[-1] <= day_pdf['trade_price'].iloc[-1] and slow_d.iloc[-1] < 40:
                    res = algorithms.adx(day_pdf['high_price'], day_pdf['low_price'], day_pdf['trade_price'], 14) 
                    if res['DMP_14'].iloc[-1] > res['DMN_14'].iloc[-1] and res['ADX_14'].iloc[-1] > res['ADX_14'].iloc[-2]:
                        return True
            return False
        except Exception as e:
            print("raise error ", e)
            return False

    def check_pattern_dmi_adx4(self, ticker_code):
        try:
            point = 0
            self.week_trader = WeekTrader(ticker_code, 35)
            if self.week_trader.candles[1].trade_volume == 0:
                return False

            week_pdf = self.week_trader.get_dataframe()
            rsi = algorithms.get_current_rsi(week_pdf, 13)
            slow_k, slow_d = algorithms.stc_slow(week_pdf, 7, 3, 3)
            cci13 = algorithms.get_current_cci(week_pdf, 13)

            ema13 = algorithms.ema(week_pdf, 13)

            res = algorithms.adx(week_pdf['high_price'], week_pdf['low_price'], week_pdf['trade_price'], 14) 
            if ema13.iloc[-1] <= week_pdf['trade_price'].iloc[-1] and \
                res['DMP_14'].iloc[-1] > res['DMN_14'].iloc[-1] and res['ADX_14'].iloc[-1] < res['DMP_14'].iloc[-1] :
                if res['DMP_14'].iloc[-1] > res['DMP_14'].iloc[-2] or res['DMN_14'].iloc[-1] < res['DMN_14'].iloc[-2]:
                    day_trader = DayTrader(ticker_code, 120)
                    day_pdf = day_trader.get_dataframe()
                    cci20 = algorithms.get_current_cci(day_pdf, 20)
                    if cci20 < 25 :
                        res = algorithms.adx(day_pdf['high_price'], day_pdf['low_price'], day_pdf['trade_price'], 14) 
                        if res['DMP_14'].iloc[-1] > res['DMN_14'].iloc[-1]:
                            return True
            return False
        except Exception as e:
            print("raise error ", e)
            return False