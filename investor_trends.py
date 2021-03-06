import pandas as pd
import datetime
import requests
import math

class InvestorTrends():
    def __init__(self, ticker):
        self.df = None
        self.init_ts(ticker)

    def init_ts(self, ticker) :
        try:

            url = f'https://finance.naver.com/item/frgn.naver?code={ticker}'
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            res = requests.get(url, headers=headers)
            self.df = pd.read_html(res.text)[2]
            self.df.columns = self.df.columns.droplevel(1)
            #print(self.df)

            # today = datetime.datetime.today()
            # str_today = today.strftime("%Y%m%d")
            # url = f'https://finance.naver.com/sise/investorDealTrendDay.nhn?bizdate={str_today}&sosok=&page=1&code={str(ticker)}'
            # print(url)
            # dfs = pd.read_html(url, skiprows=[0, 1, 2, 8, 9, 10, 16, 17], index_col=0)
            # self.df = dfs[0]

            # self.df.columns = ['개인', '외국인', '기관계', '금융투자', '보험', '투신', '은행', '기타금융', '연기금', '기타법인']
            # dt_list = [datetime.datetime.strptime(day, '%y.%m.%d') for day in self.df.index]
            # self.df.index = dt_list
        except Exception as e:
            print("raise error ", e)

    def get_cumulative_trading_volume_agency(self, period):
        try:
            item_len = len(self.df)
            sum = 0
            count = 0
            for i in range(0, item_len):
                sale_volume = self.df['기관'].iloc[i]
                sale_volume = str(sale_volume).replace(',','')
                if math.isnan(float(sale_volume)):
                    continue
                #print(float(sale_volume))
                sum += float(sale_volume)
                count+=1
                if count == period:
                    break
            return sum
            
        except Exception as e:
            print("raise error ", e)
            print(self.df)
            return 0

    def get_cumulative_trading_volume_foreigner(self, period):
        try:
            item_len = len(self.df)
            pds = pd.Series(self.df['외국인'].items())
            sum = 0
            count = 0
            for row in pds[0][1]:
                sale_volume = row
                sale_volume = str(sale_volume).replace(',','')
                if math.isnan(float(sale_volume)):
                    continue
                
                sum += float(sale_volume)
                count += 1
                if count == period:
                    break
            return sum
        except Exception as e:
            print("raise error ", e)
            print(self.df)
            return 0


    def get_buy_day_count_foreigner(self, period):
        try:
            item_len = len(self.df)
            pds = pd.Series(self.df['외국인'].items())
            sum = 0
            count = 0
            for row in pds[0][1]:
                sale_volume = row
                sale_volume = str(sale_volume).replace(',','')
                if math.isnan(float(sale_volume)):
                    continue

                if float(sale_volume) > 0:
                    sum += 1
                
                count += 1
                if count == period:
                    break
            return sum
        except Exception as e:
            print("raise error ", e)
            return 0

    def get_buy_day_count_agency(self, period):
        try:
            item_len = len(self.df)
            sum = 0
            count = 0
            for i in range(0, item_len):
                sale_volume = self.df['기관'].iloc[i]
                sale_volume = str(sale_volume).replace(',','')
                if math.isnan(float(sale_volume)):
                    continue

                if float(sale_volume) > 0:
                    sum += 1
                count += 1
                if count == period:
                    break
            return sum
        except Exception as e:
            print("raise error ", e)
            return 0

if __name__ == "__main__":
    fs = InvestorTrends('950110')
    print(fs.get_cumulative_trading_volume_agency(20))
    print(fs.get_cumulative_trading_volume_foreigner(950110))







