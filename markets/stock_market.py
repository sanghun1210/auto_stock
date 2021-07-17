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

    def get_bollinger_bands_width(self, trader):
        stdev = trader.get_bollinger_bands_standard_deviation()
        high_band = trader.ma(20) + (stdev * 2)
        low_band = trader.ma(20) - (stdev * 2)
        return self.get_margin(high_band, low_band)

    def get_rsi_check_point(self, trader):
        point = 0
        


    def check_week_point(self):
        point = 0
        mos_week = self.week_trader.get_momentum_list()
        self.logger.info('mos[0] ==> ' + str(mos_week[0]))
        self.logger.info('self.week_trader.rsi(0, 14) ==> ' + str(self.week_trader.rsi(0, 14)))
        self.logger.info('self.get_bollinger_bands_width(self.week_trader) ==> ' + str(self.get_bollinger_bands_width(self.week_trader)))
        self.logger.info('self.get_margin(self.week_trader.ma(5), self.week_trader.ma(10)) ==> ' + str(self.get_margin(self.week_trader.ma(5), self.week_trader.ma(10))))
        self.logger.info('self.week_trader.ma(5), self.week_trader.ma(10) ==> ' + str(self.week_trader.ma(5)) + ' ' + str(self.week_trader.ma(10)))
        self.logger.info('self.week_trader.ma_volume(3), self.week_trader.ma_volume(10) ==> ' + str(self.week_trader.ma_volume(5))  +  ' ' +str(self.week_trader.ma_volume(10))) 
        
        if self.week_trader.ma(5) > self.week_trader.ma(10) or self.get_margin(self.week_trader.ma(5), self.week_trader.ma(10)) < 0.4: point += 1
        if self.week_trader.candles[0].trade_price > self.week_trader.ma(10): point += 1
        if self.get_bollinger_bands_width(self.week_trader) <= 26: point += 1.5
        if self.week_trader.ma_volume(3) >= self.week_trader.ma_volume(10) * 1.5 : point += 1

        if self.week_trader.rsi(0, 14) >= 55: point += 1.2
        elif self.week_trader.rsi(0, 14) >= 38: point += 1
        else : point = point - 1

        if mos_week[0] >= 9:
            point = point 
        elif mos_week[0] >= -2:
            point = point * 0.8
        else:
            point = 0

        return point

    def check_day_point(self):
        point = 0

        mos_day = self.day_trader.get_momentum_list()
        self.logger.info('mos[0] ==> ' + str(mos_day[0]))
        self.logger.info('self.day_trader.rsi(0, 14) ==> ' + str(self.day_trader.rsi(0, 14)))
        self.logger.info('self.get_bollinger_bands_width(self.day_trader) ==> ' + str(self.get_bollinger_bands_width(self.day_trader)))
        self.logger.info('self.day_trader.ma(10) self.day_trader.ma(20) self.day_trader.ma(60) ==> ' + str(self.day_trader.ma(10)) + ' ' + str(self.day_trader.ma(20)) + ' ' + str(self.day_trader.ma(20)))
        self.logger.info('self.day_trader.ma_volume(3), self.day_trader.ma_volume(10) ==> ' + str(self.day_trader.ma_volume(5))  +  ' ' +str(self.day_trader.ma_volume(10))) 

        if self.get_bollinger_bands_width(self.day_trader) <= 14: point += 1.5
        if self.day_trader.ma(5) > self.day_trader.ma(20):
            point = point + 1
        elif self.get_margin(self.day_trader.ma(5), self.day_trader.ma(10)) < 0.3 and self.day_trader.rsi(0, 14) >= 60:
            point = point + 1
            
        if self.day_trader.candles[0].trade_price > self.day_trader.ma(10): point += 1
        if self.day_trader.ma_volume(3) >= self.day_trader.ma_volume(10) * 1.7 : point += 1
        
        if self.day_trader.rsi(0, 14) >= 55: point += 1.2
        elif self.day_trader.rsi(0, 14) >= 38: point += 1
        else: point = point - 1
        
        if self.day_trader.rsi(0, 14) > self.day_trader.rsi(1, 14)  : point += 1

        if mos_day[0] >= 9:
            point = point 
        elif mos_day[0] >= -1.5:
            point = point * 0.8
        else:
            point = 0

        return point

    def check_point(self, ticker_code):
        try:
            point = 0
            if self.day_trader.candles[1].trade_volume == 0:
                return False

            self.logger.info('========================================================================')
            self.logger.info('ticker code : ' + str(ticker_code))

            point_week = point + self.check_week_point()
            self.logger.info('point_week ==> ' + str(point_week))

            point_day = point + self.check_day_point()
            self.logger.info('point_day ==> ' + str(point_day))

            point = point_week + (point_day * 1.2)
            self.logger.info('total_point ==> ' + str(point))

            print('total_point ==> ' + str(point))
            return point
                
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