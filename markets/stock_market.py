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
    def __init__(self, src_logger):
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
        self.logger = src_logger

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

    def is_nice_week(self, trader):
        current_rsi = algorithms.get_current_rsi(trader.get_dataframe(), 14)

        self.logger.info('get_bollinger_bands_width(14) ==> ' + str(trader.get_bollinger_bands_width(14)))
        self.logger.info('current rsi ==> ' + str(current_rsi))
        self.logger.info('ma_volume(5), ma_volume(20) : ' + str(trader.ma_volume(5)) + ', ' + str(trader.ma_volume(20)))

        sma10 = algorithms.sma(trader.get_dataframe(), 10)
        sma20 = algorithms.sma(trader.get_dataframe(), 20)
        rsi14 = algorithms.rsi(trader.get_dataframe(), 14)

        if algorithms.is_stc_slow_good(trader.get_dataframe(), 9, 3, 3) < 58:
            return True
        return False

    def get_check_week_point(self, trader):
        point = 0
        current_pdf = trader.get_dataframe()

        sma5 = algorithms.sma(current_pdf, 5)
        sma20 = algorithms.sma(current_pdf, 20)
        sma10 = algorithms.sma(current_pdf, 10)
        sma40 = algorithms.sma(current_pdf, 40)
        # 단기 골든 크로스 MA(5,20)
        if sma5.iloc[-1] > sma20.iloc[-1]:
            print('단기 골든 크로스 MA(5,20)')
            point += 1
        
        # 중기 골든 크로스 MA(10,40)
        if sma10.iloc[-1] > sma40.iloc[-1]:
            print('중기 골든 크로스 MA(10,40)')
            point += 1

        # 당일 거래 급증 종목(10일 평균 거래대비)
        obv, obv_ema = algorithms.get_obv(current_pdf, 10)
        if obv.iloc[-1] > obv_ema.iloc[-1]:
            print('당일 거래 급증 종목')
            point += 1
        
        # Stochastic slow(10,5,5) %K, %D 상향돌파
        if algorithms.is_stc_slow_good(trader.get_dataframe(), 9, 3, 3) < 56:
            print('Stochastic slow(9,3,3) %K, %D 상향돌파')
            point += 1
        
        # MACD Osc(12,26,9) 0선 상향돌파
        if algorithms.macd_line_over_than_signal(trader.get_dataframe(), 6, 19, 8):
            print('MACD')
            point += 1
        
        # RSI(14,9) Signal선 상향돌파
        rsi9 = algorithms.rsi(current_pdf, 9)
        rsi14 = algorithms.rsi(current_pdf, 14)
        if rsi9.iloc[-1] > rsi14.iloc[-1]:
            print('rsi')
            point += 1

        return point

    def get_check_point(self, trader):
        point = 0
        current_pdf = trader.get_dataframe()

        sma5 = algorithms.sma(current_pdf, 5)
        sma20 = algorithms.sma(current_pdf, 20)
        sma60 = algorithms.sma(current_pdf, 60)
        # 단기 골든 크로스 MA(5,20)
        if sma5.iloc[-1] > sma20.iloc[-1]:
            print('단기 골든 크로스 MA(5,20)')
            point += 1
        
        # 중기 골든 크로스 MA(20,60)
        if sma20.iloc[-1] > sma60.iloc[-1]:
            print('중기 골든 크로스 MA(20,60)')
            point += 1

        # 당일 거래 급증 종목(10일 평균 거래대비)
        obv, obv_ema = algorithms.get_obv(current_pdf, 10)
        if obv.iloc[-1] > obv_ema.iloc[-1]:
            print('당일 거래 급증 종목')
            point += 1
        
        # Stochastic slow(10,5,5) %K, %D 상향돌파
        if algorithms.is_stc_slow_good(trader.get_dataframe(), 10, 5, 5) < 56:
            print('Stochastic slow(10,5,5) %K, %D 상향돌파')
            point += 1
        
        # MACD Osc(12,26,9) 0선 상향돌파
        if algorithms.macd_line_over_than_signal(trader.get_dataframe(), 12, 26, 9):
            print('MACD')
            point += 1
        
        # RSI(14,9) Signal선 상향돌파
        rsi9 = algorithms.rsi(current_pdf, 9)
        rsi14 = algorithms.rsi(current_pdf, 14)
        if rsi9.iloc[-1] > rsi14.iloc[-1]:
            print('rsi')
            point += 1

        return point

    def check_week(self, ticker_code):
        try:
            self.week_trader = WeekTrader(ticker_code, 40)
            if self.week_trader.candles[1].trade_volume == 0:
                return False

            current_rsi = algorithms.get_current_rsi(self.week_trader.get_dataframe(), 14)
            current_price = self.week_trader.get_dataframe()['trade_price'].iloc[-1]
            sma10 = algorithms.sma(self.week_trader.get_dataframe(), 10)
            margin = algorithms.get_margin(current_price, sma10.iloc[-1])

            if self.get_check_week_point(self.week_trader) >= 5 and current_rsi < 60 and margin <= 5 :
                return True
            return False
        except Exception as e:
            print("raise error ", e)
            return False

    def check_day(self, ticker_code):
        try:
            self.day_trader = DayTrader(ticker_code, 80)
            if self.day_trader.candles[1].trade_volume == 0:
                return False

            current_rsi = algorithms.get_current_rsi(self.day_trader.get_dataframe(), 14)
            current_price = self.day_trader.get_dataframe()['trade_price'].iloc[-1]
            sma10 = algorithms.sma(self.day_trader.get_dataframe(), 10)
            margin = algorithms.get_margin(current_price, sma10.iloc[-1])

            if self.get_check_point(self.day_trader) >= 5 and current_rsi < 60 and margin <= 2 :
                return True
            return False
        except Exception as e:
            print("raise error ", e)
            return False