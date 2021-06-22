
import json
import time
import requests

import os
import sys
from . import *

from .candle import *
from .calcualtor import *
from enum import Enum

class BaseTrader():
    def __init__(self, market_name):
        self.market_name = market_name
        self.candles = []

    def ma(self, index):
        my_cal = Calculator(self.candles)
        return my_cal.ma(index)

    def ma_volume(self, start, end):
        total_volume = 0
        len = end - start
        for i in range(start, len):
            total_volume = total_volume + self.candles[i].trade_volume    
        return total_volume / len

    def is_ma_volume_up(self):
        return self.candles[0].candle_acc_trade_volume > self.ma_volume(4) and self.candles[0].is_yangbong()

    def is_pre_volumne_min(self, range_count):
        vol_list = []
        for i in range(1, range_count):
            vol_list.append(self.candles[i].candle_acc_trade_volume)

        min_vol = min(vol_list)
        return min_vol == self.candles[1].candle_acc_trade_volume

    def get_max_trade_price(self, range_count):
        trade_price_list = []
        for i in range(0, range_count):
            trade_price_list.append(self.candles[i].trade_price)
        return max(trade_price_list)

    def is_ma_growup(self):
        # 기본 바꾸면 안됨.
        return self.ma(5) > self.ma(15) 
    
    def is_ma_growup_lite(self):
        # 기본 바꾸면 안됨.
        return self.ma(4) > self.ma(8) 

    def is_goup_with_volume(self) :
        return self.candles[0].trade_price > self.candles[1].trade_price and self.candles[0].candle_acc_trade_volume > self.candles[1].candle_acc_trade_volume

    def is_pre_goup_with_volume(self) :
        return self.candles[1].trade_price > self.candles[2].trade_price and self.candles[1].candle_acc_trade_volume > self.candles[2].candle_acc_trade_volume
        
    def is_anomaly_candle(self) :
        return self.candles[0].is_yangbong() and self.candles[0].candle_acc_trade_volume > (self.candles[1].candle_acc_trade_volume * 5)

    def is_growup(self, count): 
        my_cal = Calculator(self.candles)
        return my_cal.is_growup(count)

    def is_go_down(self, count):
        my_cal = Calculator(self.candles)
        return my_cal.is_godown(count)

    def is_umbong_candle_long_than(self, index, rate):
        if self.candles[index].is_yangbong() == False:
            if self.candles[index].get_umbong_rate() >= rate:
                return True
        return False
            
    def is_exist_long_umbong(self, count, rate):
        for i in range(0, count):
            if self.is_umbong_candle_long_than(i, rate):
                return True
        return False

    def is_go_down(self):
        return self.candles[0].trade_price < self.candles[1].trade_price < self.candles[2].trade_price

    def is_pre_candle_yangbong(self):
        return self.candles[1].is_yangbong()

    def get_ma(self, count):
        return self.ma(count)

    def is_ma50_over_than_ma15(self):
        return self.ma(50) > self.ma(15)

    def is_ma120_over_than_ma15(self):
        return self.ma(120) > self.ma(15)

    def is_golden_cross(self, cross_margin):
        return self.is_ma50_over_than_ma15() and self.get_ma_margin() <= cross_margin
        
    def get_ma_margin(self):
        if self.ma(50) > self.ma(15):
            return round(float(((self.ma(50) - self.ma(15)) / self.ma(50)) * 100), 2)
        else:
            return round(float(((self.ma(15) - self.ma(50)) / self.ma(15)) * 100), 2)

    def get_ma_margin120(self):
        if self.ma(120) > self.ma(15):
            return round(float(((self.ma(120) - self.ma(15)) / self.ma(120)) * 100), 2)
        else:
            return round(float(((self.ma(15) - self.ma(120)) / self.ma(15)) * 100), 2)

    def get_ma_print(self):
        if self.ma(50) > self.ma(15):
            per = str(round(float(((self.ma(50) - self.ma(15)) / self.ma(50)) * 100), 2))
            return str('+' + per + '(%)')
        else:
            per = str(round(float(((self.ma(15) - self.ma(50)) / self.ma(15)) * 100), 2))
            return str('-' + per + '(%)')

    def set_child_trader(self, child):
        self.child = child

    def is_growup_chart1(self, mail_list):
        if self.child == None:
            print('check : None' )
            return False

        if self.is_ma50_over_than_ma15() == False:
            if self.child.is_ma50_over_than_ma15() == False:
                print('over :' + self.trader_name)
                return self.child.is_growup_chart1(mail_list)
            else:
                if self.child.is_ma_growup() and self.child.get_ma_margin() < 0.15:
                    print('check :' + self.trader_name)
                    mail_list[0] = str(' UP! :' + self.trader_name + ' margin : ' +  str(self.child.get_ma_margin()))
                    return True

        return False


    