
import json
import time
import requests

import os
import sys

from .candle import *
from .calcualtor import *
from enum import Enum

import math
import pandas as pd

class BaseTrader():
    def __init__(self, market_name):
        self.market_name = market_name
        self.candles = []

    def get_dataframe(self):
        price_list = []
        high_price_list = []
        low_price_list = []
        rsi_list = []
        trade_volume_list = []
        opening_price_list = []

        for candle_unit in self.candles:
            price_list.append(candle_unit.trade_price)
            high_price_list.append(candle_unit.high_price)
            low_price_list.append(candle_unit.low_price)
            trade_volume_list.append(candle_unit.trade_volume)
            opening_price_list.append(candle_unit.opening_price)

        price_list.reverse()
        high_price_list.reverse()
        low_price_list.reverse()
        trade_volume_list.reverse()
        opening_price_list.reverse()
        df = pd.DataFrame(price_list, columns=['trade_price'])
        df.insert(1, 'high_price', high_price_list, True)
        df.insert(2, 'low_price', low_price_list, True)
        df.insert(3, 'trade_volume', trade_volume_list, True)
        df.insert(4, 'opening_price', opening_price_list, True)
        return df

    def ma(self, index):
        my_cal = Calculator(self.candles)
        return my_cal.ma(index)

    def ma_from(self, start, index):
        my_cal = Calculator(self.candles[start:])
        return my_cal.ma(index)

    def ma_volume(self, index):
        sum = 0
        for i in range(0, index): 
            sum = sum + self.candles[i].trade_volume
        return sum / index

    def is_ma_volume_up(self):
        return self.candles[0].candle_acc_trade_volume > self.ma_volume(4) and self.candles[0].is_yangbong()

    def is_volumne_min(self, index, range_count):
        vol_list = []
        for i in range(0, range_count):
            vol_list.append(self.candles[i].trade_volume)

        min_vol = min(vol_list)
        return min_vol == self.candles[index].trade_volume

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
        
    def get_ma_margin(self):
        if self.ma(50) > self.ma(15):
            return round(float(((self.ma(50) - self.ma(15)) / self.ma(50)) * 100), 2)
        else:
            return round(float(((self.ma(15) - self.ma(50)) / self.ma(15)) * 100), 2)

    def get_ma_print(self):
        if self.ma(50) > self.ma(15):
            per = str(round(float(((self.ma(50) - self.ma(15)) / self.ma(50)) * 100), 2))
            return str('+' + per + '(%)')
        else:
            per = str(round(float(((self.ma(15) - self.ma(50)) / self.ma(15)) * 100), 2))
            return str('-' + per + '(%)')

    def deviation(self, a, b):
        if a >= b:
            return a - b
        else :
            return b - a

    def get_bollinger_bands_standard_deviation(self, bol_range):
        bol_average = self.ma(bol_range)
        mysum = 0
        for i in range(0, bol_range):
            mysum += (self.deviation(bol_average, self.candles[i].trade_price) ** 2)
        avr_dev = mysum / bol_range
        return math.sqrt(float(avr_dev))


    def momentum(self, index):
        return ((self.candles[index].trade_price -  self.candles[index + 9].trade_price) / self.candles[index + 9].trade_price) * 100

    def momentum2(self, index):
        return (self.candles[index].trade_price / self.candles[index + 9].trade_price) * 100

    def get_momentum_list(self):
        mo_list = []
        for i in range(0, len(self.candles) - 10):
            mo_list.append(self.momentum(i))
        return mo_list

    def momentum_ma(self, index):
        mos = self.get_momentum_list()
        sum = 0
        for i in range(0, index): 
            sum = sum + mos[i]
        return sum / index

    def get_current_rsi(self):
        price_list = []
        rsi_list = []

        for candle_unit in self.candles:
            price_list.append(candle_unit.trade_price)
        
        price_list.reverse()  #order : past -> now
        rsi_list.append(self.rsi_calculate(price_list, 14, int(len(self.candles))))
        return rsi_list[0]


    #RSI계산 함수
    def rsi_calculate(self, l, n, sample_number): #l = price_list, n = rsi_number
        
        diff=[]
        au=[]
        ad=[]

        if len(l) != sample_number: #url call error
            return -1 
        for i in range(len(l)-1):
            diff.append(l[i+1]-l[i]) #price difference
        
        au = pd.Series(diff) #list to series
        ad = pd.Series(diff)

        au[au<0] = 0 #remove ad
        ad[ad>0] = 0 #remove au

        _gain = au.ewm(com = n, min_periods = sample_number -1).mean() #Exponentially weighted average
        _loss = ad.abs().ewm(com = n, min_periods = sample_number -1).mean()
        RS = _gain/_loss

        rsi = 100-(100 / (1+RS.iloc[-1]))

        return rsi

    def get_margin(self, a, b):
        ma = 0
        if a > b:
            ma = ((a - b) / a) * 100
        else : 
            ma = ((b - a) / b) * 100
        return ma

    def get_bollinger_bands_width(self, bol_range):
        stdev = self.get_bollinger_bands_standard_deviation(bol_range)
        high_band = self.ma(bol_range) + (stdev * 2)
        low_band = self.ma(bol_range) - (stdev * 2)
        return self.get_margin(high_band, low_band)





    


    