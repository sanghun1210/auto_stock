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

    def is_nice_main_trader(self, trader, max_bol_width):
        if trader.candles[0].trade_price >= trader.ma(10) and \
            trader.get_current_rsi() >= 50 and algorithms.macd_line_over_than_signal(trader.get_dataframe()):
            self.logger.info('week_trader.rsi(0, 14)' + str(trader.get_current_rsi()))
            return True

    # def is_nice_trader(self, trader, max_bol_width):
    #     current_rsi = trader.get_current_rsi()
    #     mos = trader.get_momentum_list()

    #     self.logger.info('get_bollinger_bands_width(14) ==> ' + str(trader.get_bollinger_bands_width(14)))
    #     self.logger.info('current rsi ==> ' + str(current_rsi))
    #     self.logger.info('mos[0], trader.momentum_ma(4) : ' + str(mos[0]) + ', ' + str(trader.momentum_ma(4)))
    #     self.logger.info('ma_volume(5), ma_volume(20) : ' + str(trader.ma_volume(5)) + ', ' + str(trader.ma_volume(20)))
        
    #     if algorithms.macd_line_over_than_signal2(trader.get_dataframe(), 6, 19, 6) and \
    #         algorithms.bbands_width(trader.get_dataframe(), 10) < max_bol_width:
    #             return True

    def is_nice_week(self, trader):
        current_rsi = trader.get_current_rsi()
        mos = trader.get_momentum_list()

        self.logger.info('get_bollinger_bands_width(14) ==> ' + str(trader.get_bollinger_bands_width(14)))
        self.logger.info('current rsi ==> ' + str(current_rsi))
        self.logger.info('mos[0], trader.momentum_ma(4) : ' + str(mos[0]) + ', ' + str(trader.momentum_ma(4)))
        self.logger.info('ma_volume(5), ma_volume(20) : ' + str(trader.ma_volume(5)) + ', ' + str(trader.ma_volume(20)))
        
        # if algorithms.macd_line_over_than_signal(trader.get_dataframe(), 12, 26, 9):
        #     return True

        slow_k, slow_d = algorithms.stc_slow(trader.get_dataframe())

        if algorithms.macd_line_over_than_signal(trader.get_dataframe(), 12, 26, 9) and \
            algorithms.is_stc_slow_good(trader.get_dataframe()) < 50 and \
            trader.get_dataframe()['trade_price'].iloc[-1] > algorithms.get_current_sma(trader.get_dataframe(), 10) and \
            algorithms.bbands_width(trader.get_dataframe(), 10) < 20:
            return True
        return False

    # def is_nice_day(self, trader, max_bol_width):
    #     slow_k, slow_d = algorithms.stc_slow(trader.get_dataframe())
    #     if algorithms.is_stc_slow_good(trader.get_dataframe()) < 40 :
    #        return True

    def check_week(self, ticker_code):
        try:
            self.week_trader = WeekTrader(ticker_code, 40)
            if self.week_trader.candles[1].trade_volume == 0:
                return False

            if self.is_nice_week(self.week_trader):
                print('wow_week')
                is_nice_week = True
                return True
        except Exception as e:
            print("raise error ", e)
            return False

    def check_day(self, ticker_code):
        try:
            self.day_trader = DayTrader(ticker_code, 80)
            if self.day_trader.candles[1].trade_volume == 0:
                return False

            if self.is_nice_day(self.day_trader, 30):
                print('wow_day!!!')
                return True
            return False
        except Exception as e:
            print("raise error ", e)
            return False