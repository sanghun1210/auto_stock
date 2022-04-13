import os
import jwt
import uuid
import hashlib
import json
import time
from urllib.parse import urlencode

import requests

from markets.algorithms.obv import obv_is_good

from .base_market import *
from .week_trader import *
from .day_trader import *
from .minute240_trader import *
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

    def get_margin(self, a, b):
        ma = 100
        if a > b:
            ma = ((a - b) / a) * 100
        else : 
            ma = ((b - a) / b) * 100
        return ma

    def init_trader(self, ticker_code):        
        try:
            self.week_trader = WeekTrader(ticker_code, 30)
            self.day_trader = DayTrader(ticker_code, 50)
        except Exception as e:
            print("day_trader init fail: ", e)

    def get_check_day_point(self, trader):
        current_pdf = trader.get_dataframe()
        point = 0

        res = algorithms.adx(current_pdf['high_price'], current_pdf['low_price'], current_pdf['trade_price'], 13)
        if res['DMP_13'].iloc[-1] > res['DMN_13'].iloc[-1] and res['ADX_13'].iloc[-1] > res['DMN_13'].iloc[-1] :
            self.logger.info('adx 통과 ')     
            point += 1
        else:
            self.logger.info('adx 실패 ')     

                   
        cci = algorithms.get_current_cci(current_pdf, 20)
        self.logger.info('cci : ' + str(cci)) 
        if cci <= 50:
            self.logger.info('cci 통과 ')  
            point += 1
        else:
            self.logger.info('cci 실패 ')  

        obv, obv_ema = algorithms.get_obv(current_pdf, 5)
        self.logger.info('obv : ' + str(obv.iloc[-1])) 
        self.logger.info('obv_ema : ' + str(obv_ema.iloc[-1])) 

        if obv.iloc[-1] < obv_ema.iloc[-1] :
            self.logger.info('obv 통과 ')  
            point += 1     
        else:
            self.logger.info('obv 실패 ')  

        # bw = algorithms.bbands_width(current_pdf, 10)
        # if bw <= 13 :
        #     point += 1

        
        # 강도지수의 13일 이동평균을 구하면 황소와 곰의 세력의 변화를 알수 있다.
        # mfi = algorithms.force_index(current_pdf, 13)
        # if mfi['ForceIndex'].iloc[-1] > 0:
        #     #print('단기 강도 지수 (+) 매수시점 ')
        #     point +=1

        # 매수 시점 파악에 용이
        # fi = algorithms.force_index(current_pdf, 2)
        # if fi['ForceIndex'].iloc[-1] < 0:
        #     #print('초단기 강도 지수 (-) 매수시점 ')
        #     point +=1
        return point


    def get_check_day_point2(self, trader):
        current_pdf = trader.get_dataframe()
        point = 0

        # if slow_k.iloc[-1] > slow_d.iloc[-1]:
        #     point += 1

        # ADX_13     
        # DMP_13     
        # DMN_13
        # res = algorithms.adx(current_pdf['high_price'], current_pdf['low_price'], current_pdf['trade_price'], 13)
        # if res['DMP_13'].iloc[-1] > res['DMN_13'].iloc[-1] and res['ADX_13'].iloc[-1] > res['DMN_13'].iloc[-1] :
        #     point += 1
        
        # D로 측정
        # https://www.dailyforex.com/forex-articles/2020/09/elder-triple-screen-system/151378
        # https://www.brokerxplorer.com/article/how-to-master-the-triple-screen-trading-strategy-1547
        # 시장상황에 따라 D값을 조정.
        slow_k, slow_d = algorithms.stc_slow(current_pdf, 9, 3, 3)
        if slow_d.iloc[-1] <= 33 :
            self.logger.info('stc_slow 통과 ')  
            point += 1
        else:
            self.logger.info('stc_slow 실패 ')  


        week_pdf = self.week_trader.get_dataframe()
        cci = algorithms.get_current_cci(week_pdf, 20)
        self.logger.info('cci : ' + str(cci)) 
        if cci <= 40:
            self.logger.info('주간 cci 통과 ')  
            point += 1
        else:
            self.logger.info('주간 cci 실패 ')  
    
        return point

    def check_advenced(self, ticker_code):
        try:
            self.week_trader = WeekTrader(ticker_code, 45)
            if self.week_trader.candles[1].trade_volume == 0:
                return False

            week_pdf = self.week_trader.get_dataframe()
            slow_k, slow_d = algorithms.stc_slow(week_pdf, 9, 3, 3)

            res = algorithms.adx(week_pdf['high_price'], week_pdf['low_price'], week_pdf['trade_price'], 13)
            self.logger.info('macd is ture: ' + str(algorithms.macd_line_over_than_signal2(week_pdf, 12, 26, 9)))  
            self.logger.info('adx is true : ' + str(res['DMP_13'].iloc[-1] > res['DMN_13'].iloc[-1]))  
            if algorithms.macd_line_over_than_signal2(week_pdf, 12, 26, 9) and \
                res['DMP_13'].iloc[-1] > res['DMN_13'].iloc[-1] :
                return True
            
            return False
        except Exception as e:
            print("raise error ", e)
            return False

    def get_check_point(self, ticker_code):
        try:
            day_point = 0

            self.day_trader = DayTrader(ticker_code, 120)
            if self.day_trader != None:
                day_point = self.get_check_day_point(self.day_trader)  

            return day_point
        except Exception as e:
            print("raise error ", e)
            return 0

    def get_check_point2(self, ticker_code):
        try:
            day_point = 0

            if self.day_trader != None:
                day_point = self.get_check_day_point2(self.day_trader)  

            return day_point
        except Exception as e:
            print("raise error ", e)
            return 0
