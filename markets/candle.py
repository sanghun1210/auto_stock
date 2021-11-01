class Candle():
    def __init__(self, candle_date_time, opening_price, high_price, trade_price, low_price, trade_volume):
        self.candle_date_time = candle_date_time
        self.opening_price = opening_price
        self.high_price = high_price
        self.trade_price = trade_price
        self.low_price = low_price
        self.trade_volume = trade_volume

    def is_yangbong(self):
        return (self.trade_price - self.opening_price) > 0