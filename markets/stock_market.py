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
from .minute60_trader import *
from .minute30_trader import *
from .minute15_trader import *
from .minute10_trader import *
from .minute5_trader import *
from .minute3_trader import *
from .minute1_trader import *

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

    def init_traders(self, ticker_code):
        try:
            # self.minute1_trader = Minute1Trader(market_name, 120)
            # time.sleep(0.1)
            # self.minute3_trader = Minute3Trader(market_name, 120)
            # time.sleep(0.1)
            # self.minute5_trader = Minute5Trader(market_name, 120)
            # time.sleep(0.1)
            # self.minute10_trader = Minute10Trader(market_name, 120)
            # time.sleep(0.1)
            # self.minute15_trader = Minute15Trader(market_name, 120)
            # time.sleep(0.1)
            # self.minute30_trader = Minute30Trader(market_name, 120)
            # time.sleep(0.1)
            # self.minute60_trader = Minute60Trader(market_name, 120)
            # time.sleep(0.1)
            # self.minute240_trader = Minute240Trader(market_name, 120)
            # time.sleep(0.1)

            print('checking... ticker_code: ', ticker_code)
            
            self.day_trader = DayTrader(ticker_code, 70)
            return True
        except Exception as e:    
            print("raise error ", e)
            return False

    # 저점 근처에서 거래량이 고갈되었는지 확인 (todo)
    # 손잡이를 만든후 거래량이 증가했는지 확인
    # 자기 자신이 가장 클경우에 대한 대비가 필요 (todo)
    def is_pattern1_good(self, ticker_code):
        try:
            self.week_trader = WeekTrader(ticker_code, 40)
            self.day_trader = DayTrader(ticker_code, 50)
            # if self.week_trader.is_ma_growup() and self.week_trader.get_ma_margin() <= 0.5:
            #     print('wow1')
            #     return True

            if  self.week_trader.candles[0].trade_price > self.week_trader.ma(10) : 
                if self.get_margin(self.week_trader.get_max_trade_price(15), self.week_trader.candles[0].trade_price) <= 1.2:
                    if self.day_trader.candles[0].trade_volume > 0 and self.day_trader.candles[0].trade_volume >= self.day_trader.candles[1].trade_volume * 1.5:
                        print('wow2')
                        return True
            return False
        except Exception as e:
            print("raise error ", e)
            return False

    def is_pattern2_good(self, ticker_code):
        try:
            self.day_trader = DayTrader(ticker_code, 70)
            if self.day_trader.candles[0].trade_price > self.day_trader.ma(20) :
                if self.day_trader.get_max_trade_price(24) >= self.day_trader.candles[0].trade_price or self.get_margin(self.day_trader.get_max_trade_price(24), self.day_trader.candles[0].trade_price) <= 1.4:
                    if self.day_trader.ma_volume(0, 2) > self.day_trader.ma_volume(2, 9) * 2:
                        print('wow3')
                        return True
            return False
        except Exception as e:
            return False

    def is_pattern3_volumne_good(self, trader):
        if trader.candles[0].trade_volume > 0 and trader.candles[0].is_yangbong() == False and trader.is_volumne_min(0, 7):
            print('min')
            return True
        if trader.candles[0].trade_volume > 0 and trader.candles[0].trade_volume > trader.candles[1].trade_volume * 1.5:
            return True
        return False
        

    def is_pattern3_good(self, ticker_code):
        try:
            self.week_trader = WeekTrader(ticker_code, 40)
            self.day_trader = DayTrader(ticker_code, 50)
            if self.week_trader.candles[0].trade_price >= self.week_trader.ma(15) :
                if self.day_trader.candles[0].trade_price >= self.day_trader.ma(15):
                    if self.is_pattern3_volumne_good(self.day_trader):
                        print('wow3')
                        return True
            return False
        except Exception as e:
            print("raise error ", e)
            return False

    def is_pattern4_good(self, ticker_code):
        try:
            self.week_trader = WeekTrader(ticker_code, 60)
            self.day_trader = DayTrader(ticker_code, 70)

            stdev = self.week_trader.get_bollinger_bands_standard_deviation()
            high_band = self.week_trader.ma(20) + (stdev * 2)
            low_band = self.week_trader.ma(20) - (stdev * 2)

            if self.get_margin(high_band, low_band) <= 18:
                if self.week_trader.candles[0].trade_price >= self.week_trader.ma_volume(10) and self.week_trader.candles[0].trade_volume > 0:
                    if self.day_trader.ma_volume(3) > self.day_trader.ma_volume(7):
                        print('wow4')
                        return True
            return False
        except Exception as e:
            print("raise error ", e)
            return False

    def is_2021_6month_pattern(self, ticker_code):
        try:
            self.week_trader = WeekTrader(ticker_code, 60)
            self.day_trader = DayTrader(ticker_code, 70)

            stdev = self.day_trader.get_bollinger_bands_standard_deviation()
            high_band = self.day_trader.ma(20) + (stdev * 2)
            low_band = self.day_trader.ma(20) - (stdev * 2)

            if self.get_margin(high_band, low_band) <= 16:
                if self.day_trader.candles[0].trade_volume > 0 and self.week_trader.candles[0].trade_price > self.week_trader.ma(10):
                    if self.day_trader.candles[0].trade_price > self.day_trader.ma(20) :
                        if self.day_trader.candles[0].trade_volume > self.day_trader.candles[1].trade_volume:
                            print('2020_6month good')
                            return True
            return False
        except Exception as e:
            print("raise error ", e)
            return False

    def init_trader(self, ticker_code):        
        try:
            self.week_trader = WeekTrader(ticker_code, 30)
            self.day_trader = DayTrader(ticker_code, 70)
        except Exception as e:
            print("day_trader init fail: ", e)

    def is_2021_6month_pattern1(self, ticker_code):
        try:
            if self.day_trader.candles[0].trade_volume == 0:
                return False

            if self.week_trader.ma(5) < self.week_trader.ma(10):
                return False

            stdev = self.day_trader.get_bollinger_bands_standard_deviation()
            high_band = self.day_trader.ma(20) + (stdev * 2)
            low_band = self.day_trader.ma(20) - (stdev * 2)
            if self.day_trader.ma(20) > self.day_trader.ma(60) or (self.day_trader.ma(60) > self.day_trader.ma(20) and self.get_margin(self.day_trader.ma(60), self.day_trader.ma(20) > 7)):
                if self.get_margin(high_band, low_band) <= 13:
                    if self.day_trader.ma(5) > self.day_trader.ma(60) and self.get_margin(self.day_trader.ma(5), self.day_trader.ma(20)) <= 0.8:
                        return True
            return False
            
        except Exception as e:
            print("raise error ", e)
            return False

    def is_2021_6month_pattern2(self, ticker_code):
        try:
            if self.day_trader.candles[0].trade_volume == 0:
                return False

            if self.week_trader.ma(5) < self.week_trader.ma(10):
                return False

            stdev = self.day_trader.get_bollinger_bands_standard_deviation()
            high_band = self.day_trader.ma(20) + (stdev * 2)
            low_band = self.day_trader.ma(20) - (stdev * 2)
            if self.get_margin(high_band, low_band) <= 13:
                if self.get_margin(self.day_trader.ma(20), self.day_trader.ma(60)) <= 0.5 and self.day_trader.candles[0].trade_price >= self.day_trader.ma(20):
                    if self.day_trader.candles[0].trade_price >= self.day_trader.ma(5):
                        return True
            return False
            
        except Exception as e:
            print("raise error ", e)
            return False

    def is_2021_6month_pattern3(self, ticker_code):
        try:            
            if self.day_trader.candles[1].trade_volume == 0:
                return False

            if self.week_trader.ma(5) < self.week_trader.ma(10):
                return False

            if self.day_trader.rsi(0, 14) < 50:
                return False

            mos = self.day_trader.get_momentum_list()
            if mos[0] >= 0 and mos[0] > self.day_trader.momentum_ma(5) and mos[0] <= 7:
                stdev = self.day_trader.get_bollinger_bands_standard_deviation()
                high_band = self.day_trader.ma(20) + (stdev * 2)
                low_band = self.day_trader.ma(20) - (stdev * 2)
                if self.get_margin(high_band, low_band) <= 15:
                    if self.day_trader.ma(5) >= self.day_trader.ma(10) and self.get_margin(self.day_trader.ma(5), self.day_trader.ma(10)) <= 0.7 and self.day_trader.ma(5) >= self.day_trader.ma(60):
                        return True
            return False
                
        except Exception as e:
            print("raise error ", e)
            return False

    # def is_pattern5_good(self, ticker_code):
    #     try:
    #         day_trader = DayTrader(ticker_code, 70)
                
    #         if day_trader.candles[0].trade_volume > 0:
    #             if day_trader.ma(5) >= day_trader.ma(60) or self.get_margin(day_trader.ma(15), day_trader.ma(50)) <= 1.2):
    #                 print('wow5')
    #                 return True
    #         return False
    #     except Exception as e:
    #         print("raise error ", e)
    #         return False