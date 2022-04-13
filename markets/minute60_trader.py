import json
import time
import requests
import urllib
import time
 
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from .base_trader import BaseTrader

from .candle import *
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Minute60Trader(BaseTrader):
    def __init__(self, market_name):
        super().__init__(market_name)
        self.candles = init_candle_list(market_name)
        self.trader_name = 'Minute60Trader'

def init_candle_list(ticker) :
    candles = []
    url = 'http://finance.naver.com/item/sise_time.nhn?code=' + ticker
    req = Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0')
    with urlopen(req) as doc:
        source = BeautifulSoup(doc, "html.parser")
        maxPage= source.find_all('table',align="center")
    
        for date_count in range(0, 5):
            target_date = datetime.today() - relativedelta(days=1)
            target_date = target_date - relativedelta(days=date_count)
            for i in reversed(range(16)):        
                str_target_date = target_date.strftime("%Y%m%d")

                if i < 9: break
                if i < 10: str_target_date = str_target_date + '0' + str(i) + '0000'
                else : str_target_date = str_target_date + str(i) + '0000'
                                        
                url = 'http://finance.naver.com/item/sise_time.nhn?code=' + ticker + '&thistime=' + str_target_date 
                print(url)
                req2 = Request(url)
                req2.add_header('User-Agent', 'Mozilla/5.0')
                html = urlopen(req2)
                source = BeautifulSoup(html.read(), "html.parser")
                srlists=source.find_all("tr")
                isCheckNone = None

                for i in range(1, len(srlists)):
                    if(srlists[i].span != isCheckNone):
                        srlists[i].td.text
                        if ":00" in str(srlists[i].find_all("td", align="center")[0].text):
                            str_day = target_date.strftime("%Y%m%d")
                            target_time = str_day + ' | ' + srlists[i].find_all("td", align="center")[0].text
                        
                            trade_price = srlists[i].find_all("td", class_="num")[0].text  #종가
                            opening_price = srlists[i].find_all("td", class_="num")[2].text #시가
                            high_price = srlists[i].find_all("td", class_="num")[3].text  #고가
                            low_price = srlists[i].find_all("td", class_="num")[4].text  #저가
                            trade_volume = srlists[i].find_all("td", class_="num")[5].text  #거래량
                            print(target_time, trade_price)
                            candle = Candle(target_time, int(opening_price.replace(',', '')), int(high_price.replace(',', '')), int(trade_price.replace(',', '')), int(low_price.replace(',', '')), int(trade_volume.replace(',', '')))
                            candles.append(candle)
                        else:
                            continue
                
        return candles


from selenium import webdriver
from selenium.webdriver.common.keys import Keys




def main():
    tr = Minute60Trader('102280')
    

if __name__ == "__main__":
	main()

