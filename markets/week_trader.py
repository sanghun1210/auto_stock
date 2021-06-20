
import json
import time
import requests
from .base_trader import *

import os
import sys
import xml.etree.ElementTree as ET

from urllib.request import urlopen, Request
from bs4 import BeautifulSoup

from .candle import *
from .calcualtor import *

def init_candle_list(ticker, count) :
    candles = []

    url = f'https://fchart.stock.naver.com/sise.nhn?symbol={ticker}&timeframe=week&count={count}&requestType=0'
    req = Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0')
    with urlopen(req) as doc:
        xml_data = doc.read().decode('EUC-KR')
        root = ET.fromstring(xml_data)

        for index, each in enumerate(root.findall('.//item')):
            temp = each.attrib['data'].split('|')
            datatime = temp[0]
            opening_price = temp[1]
            high_price = temp[2]
            low_price = temp[3]
            trade_price = temp[4]
            trade_volume = temp[5]
            candle = Candle(datatime, int(opening_price.replace(',', '')), int(high_price.replace(',', '')), int(trade_price.replace(',', '')), int(trade_volume.replace(',', '')))
            candles.append(candle)
        candles.reverse()
    return candles

class WeekTrader(BaseTrader):
    def __init__(self, market_name, count):
        super().__init__(market_name)
        self.candles = init_candle_list(market_name, count)
        self.trader_name = 'WeekTrader'

    def is_ma_growup2(self):
        return self.ma(15) > self.ma(50) 

    


