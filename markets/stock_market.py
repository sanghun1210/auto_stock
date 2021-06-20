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
        ma = 0
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

    def is_nice_week(self, ticker_code):
        try:
            self.week_trader = WeekTrader(ticker_code, 60)
            if self.week_trader.is_ma_growup() and self.week_trader.get_ma_margin() <= 0.5:
                print('wow1')
                return True

            # if self.week_trader.is_ma_growup2() and self.get_margin(self.week_trader.get_max_trade_price(24), self.week_trader.candles[0].trade_price) < 1.7:
            #     print('wow2')
            #     return True

            # if self.week_trader.is_ma_growup() and self.week_trader.get_ma_margin120() < 0.5:
            #     print('wow')
            #     return True
        except Exception as e:
            return False

    def is_nice_day(self, ticker_code):
        try:
            self.day_trader = DayTrader(ticker_code, 70)
            if self.day_trader.is_ma_growup() and self.day_trader.ma(5) > self.day_trader.ma(50) and self.get_margin(self.day_trader.ma(5), self.day_trader.ma(50)) < 1 and self.get_margin(self.day_trader.get_max_trade_price(24), self.day_trader.candles[0].trade_price) <= 2:
                print('wow3')
                return True
        except Exception as e:
            return False

        