
import json
import time
import requests
import urllib
import time
 
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from .base_trader import *
from .candle import *

def init_candle_list(ticker, count) :
    candles = []
    url = 'http://finance.naver.com/item/sise_day.nhn?code=' + ticker
    req = Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0')
    with urlopen(req) as doc:
        source = BeautifulSoup(doc, "html.parser")
        maxPage= source.find_all('table',align="center")
        # mp = maxPage[0].find_all('td',class_="pgRR")
        # mpNum = int(mp[0].a.get('href')[-3:])
                                                    
        for page in range(1, int(count/10)):
            url = 'http://finance.naver.com/item/sise_day.nhn?code=' + ticker + '&page=' + str(page)
            req2 = Request(url)
            req2.add_header('User-Agent', 'Mozilla/5.0')
            html = urlopen(req2)
            source = BeautifulSoup(html.read(), "html.parser")
            srlists=source.find_all("tr")
            isCheckNone = None
            
            for i in range(1,len(srlists)-1):
                if(srlists[i].span != isCheckNone):
                    srlists[i].td.text
                    datatime = srlists[i].find_all("td", align="center")[0].text  #날짜
                    trade_price = srlists[i].find_all("td", class_="num")[0].text  #종가
                    opening_price = srlists[i].find_all("td", class_="num")[2].text #시가
                    high_price = srlists[i].find_all("td", class_="num")[3].text  #고가
                    low_price = srlists[i].find_all("td", class_="num")[4].text  #저가
                    trade_volume = srlists[i].find_all("td", class_="num")[5].text  #거래량
                    candle = Candle(datatime, int(opening_price.replace(',', '')), int(high_price.replace(',', '')), int(trade_price.replace(',', '')), int(trade_volume.replace(',', '')))
                    candles.append(candle)

            if (len(candles) >= count):
                break
        return candles


class DayTrader(BaseTrader):
    def __init__(self, market_name, count):
        super().__init__(market_name)
        self.candles = init_candle_list(market_name, count)
        self.trader_name = 'DayTrader'

    


