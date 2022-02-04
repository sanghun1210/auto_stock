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
    def __init__(self):
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

    def get_check_week_point(self, trader):
        current_pdf = trader.get_dataframe()
        point = 0
        rsi10 = algorithms.get_current_rsi(current_pdf, 10)
        if rsi10 < 45:
            point += 1

        slow_k, slow_d = algorithms.stc_slow(current_pdf, 9, 3, 3)
        if slow_k.iloc[-1] <= 41 :
            point += 1        

        if slow_d.iloc[-1] < 36:
            point += 1

        if algorithms.obv_is_good(current_pdf):
            point += 1

        return point

    def get_check_day_point(self, trader):
        current_pdf = trader.get_dataframe()
        point = 0

        # D로 측정
        # https://www.dailyforex.com/forex-articles/2020/09/elder-triple-screen-system/151378
        # https://www.brokerxplorer.com/article/how-to-master-the-triple-screen-trading-strategy-1547
        # 시장상황에 따라 D값을 조정.
        # slow_k, slow_d = algorithms.stc_slow(current_pdf, 9, 3, 3)
        # if slow_d.iloc[-1] <= 48 :
        #     print('단기 오실레이터가 낮음')
        #     point += 1
        
        # 강도지수의 13일 이동평균을 구하면 황소와 곰의 세력의 변화를 알수 있다.
        mfi = algorithms.force_index(current_pdf, 13)
        if mfi['ForceIndex'].iloc[-1] > 0:
            print('단기 강도 지수 (+) 매수시점 ')
            point +=1

        
        # 매수 시점 파악에 용이
        fi = algorithms.force_index(current_pdf, 2)
        if fi['ForceIndex'].iloc[-1] < 0:
            print('초단기 강도 지수 (-) 매수시점 ')
            point +=1
            
        return point


    def get_check_day_point2(self, trader):
        current_pdf = trader.get_dataframe()
        point = 0

        # if slow_k.iloc[-1] > slow_d.iloc[-1]:
        #     point += 1

        # ADX_13     
        # DMP_13     
        # DMN_13
        res = algorithms.adx(current_pdf['high_price'], current_pdf['low_price'], current_pdf['trade_price'], 13)
        if res['DMP_13'].iloc[-1] > res['DMN_13'].iloc[-1] and res['ADX_13'].iloc[-1] > res['DMN_13'].iloc[-1] and res['ADX_13'].iloc[-1] < res['DMP_13'].iloc[-1] :
            point += 1
        
        # D로 측정
        # https://www.dailyforex.com/forex-articles/2020/09/elder-triple-screen-system/151378
        # https://www.brokerxplorer.com/article/how-to-master-the-triple-screen-trading-strategy-1547
        # 시장상황에 따라 D값을 조정.
        slow_k, slow_d = algorithms.stc_slow(current_pdf, 9, 3, 3)
        if slow_d.iloc[-1] <= 32 :
            print('강세 다이버전스')
            point += 1
            
        return point

        # if slow_d.iloc[-1] < 44:
        #     point+= 1

        # if algorithms.obv_is_good(current_pdf):
        #     point += 1

    #나쁜 뉴스에도 주가 더이상 떨어지지 않는다면, 이는 부화뇌동파가 주식을 모두 팔아버렸다는 의미
    #시장이 바닥권에서 움직이지 않고 머무른다.

    #거래량이 많은 가운데 주가가 떨어지면 이는 좋은 신호다.
    #거래량이 많으면 많을수록 주식은 소신파의 손으로 들어간다는 뜻.
    #매수자의 질을 분석하는 것이 주식의 질을 분석하는 것보다 중요하다.
    #매도자의 질을 분석하는 것이 매도 가치를 분석하는 것보다 중요하다.
    #주식의 질이 나쁜 보유자의 손에 있으면, 최고의 주식도 주가가 떨어질수 있기 때문이다.
    #주식이 소신파의 손에 많은가, 부화뇌동파의 손에 많은가.

    #내가 찾아야 할것은 소신파의 손에 많은 좋은 주식

    # 나의 3중 스크린 매매 시스템
    # 1. 주봉의 macd 상승
    # 2. 일봉의 stc 하락
    # 3. 일봉의 2 ema 위 (전날)

    def check_advenced(self, ticker_code):
        try:
            self.week_trader = WeekTrader(ticker_code, 45)
            if self.week_trader.candles[1].trade_volume == 0:
                return False

            week_pdf = self.week_trader.get_dataframe()
            if algorithms.bbands_width(week_pdf, 10) <= 27 :
                if algorithms.macd_line_over_than_signal2(week_pdf, 12, 26, 9) :
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
