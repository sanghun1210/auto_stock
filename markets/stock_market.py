import os
import jwt
import uuid
import hashlib
import json
import time
from urllib.parse import urlencode

import requests

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
        # rsi10 = algorithms.get_current_rsi(current_pdf, 10)
        # if rsi10 <= 40:
        #     print('과매도')
        #     point += 1

        if algorithms.bbands_width(current_pdf, 10) <= 19:
            print('긴 횡보')
            point += 1

        #Stochastic slow(10,5,5) %K, %D 상향돌파
        slow_k, slow_d = algorithms.stc_slow(current_pdf, 9, 3, 3)
        if slow_d.iloc[-1] <= 30:
            print('Stochastic slow(9,3,3) %K, %D 상향돌파')
            point += 1

        sma10 = algorithms.sma(current_pdf, 10)
        if sma10.iloc[-1] > current_pdf['trade_price'].iloc[-1] :
            point += 1

        return point

    def get_check_point(self, trader):
        current_pdf = trader.get_dataframe()
        point = 0

        # rsi10 = algorithms.get_current_rsi(current_pdf, 10)
        # if rsi10 <= 39:
        #     print('과매도')
        #     point += 1

        if algorithms.bbands_width(current_pdf, 10) <= 11:
            print('긴 횡보')
            point += 1
        
        # Stochastic slow(10,5,5) %K, %D 상향돌파
        slow_k, slow_d = algorithms.stc_slow(current_pdf, 9, 3, 3)
        if slow_d.iloc[-1] <= 30:
            print('Stochastic slow(9,3,3) %K, %D 상향돌파')
            point += 1

        sma10 = algorithms.sma(current_pdf, 10)
        if sma10.iloc[-1] > current_pdf['trade_price'].iloc[-1] :
            point += 1
    
        return point

    #나쁜 뉴스에도 주가 더이상 떨어지지 않는다면, 이는 부화뇌동파가 주식을 모두 팔아버렸다는 의미
    #시장이 바닥권에서 움직이지 않고 머무른다.

    #거래량이 많은 가운데 주가가 떨어지면 이는 좋은 신호다.
    #거래량이 많으면 많을수록 주식은 소신파의 손으로 들어간다는 뜻.
    #매수자의 질을 분석하는 것이 주식의 질을 분석하는 것보다 중요하다.
    #매도자의 질을 분석하는 것이 매도 가치를 분석하는 것보다 중요하다.
    #주식의 질이 나쁜 보유자의 손에 있으면, 최고의 주식도 주가가 떨어질수 있기 때문이다.
    #주식이 소신파의 손에 많은가, 부화뇌동파의 손에 많은가.

    #내가 찾아야 할것은 소신파의 손에 많은 좋은 주식

    def check_week(self, ticker_code):
        try:
            self.week_trader = WeekTrader(ticker_code, 30)
            if self.week_trader.candles[1].trade_volume == 0:
                return False

            if self.get_check_week_point(self.week_trader) >= 3 :
                return True
            return False
        except Exception as e:
            print("raise error ", e)
            return False

    def check_day(self, ticker_code):
        try:
            self.day_trader = DayTrader(ticker_code, 100)
            if self.day_trader.candles[1].trade_volume == 0:
                return False

            if self.get_check_point(self.day_trader) >= 3  :
                return True
            return False
        except Exception as e:
            print("raise error ", e)
            return False