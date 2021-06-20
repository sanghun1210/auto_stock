from .candle import *

class Calculator():
    def __init__(self, candles):
        self.candles = candles

    def get_max_trade_price_candle(self):
        temp_candle = self.candles[0]
        for candle in self.candles :
            if temp_candle.trade_price < candle.trade_price:
                temp_candle = candle
        return temp_candle

    def get_min_trade_price_candle(self):
        temp_candle = self.candles[0]
        for candle in self.candles :
            if temp_candle.trade_price > candle.trade_price:
                temp_candle = candle
        return temp_candle

    def is_growup_avr(self, start):
        sum = 0
        for i in range(start, start + 4): 
            sum = sum + self.candles[start + i].trade_price
        return self.candles[start].trade_price >= (sum / 4)

    def is_godown_avr(self, start):
        sum = 0
        for i in range(start, start + 4): 
            sum = sum + self.candles[start + i].trade_price
        return self.candles[start].trade_price <= (sum / 4)

    def ma(self, index):
        sum = 0
        for i in range(0, index): 
            sum = sum + self.candles[0 + i].trade_price
        return sum / index

    def is_goup(self, count):
        for i in range(0, count):
            if self.candles[i].trade_price <= self.candles[i+1].trade_price :
                return False
        return True

    def is_godown(self, count):
        for i in range(0, count + 1):
            if self.is_godown_avr(i) == False:
                return False
        return True

    def is_growup(self, count):
        for i in range(0, count + 1):
            if self.is_growup_avr(i) == False:
                return False
        return True

    def is_yangbong_rate_uniform(self, count):
        for i in range(0, count + 1):
            if self.candles[i].is_yangbong() :
                if self.candles[i].get_yangbong_rate() <= 8:
                    continue
                else:
                    return False
            else : 
                return False
        return True
    
    def is_growup_uniform(self, count):
        for i in range(0, count + 1):
            if self.is_growup_avr(i) == False:
                return False

        if self.is_yangbong_rate_uniform(count):
            return True

        return False
    

