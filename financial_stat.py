
import json
import time
import requests
import pandas as pd
import math

import os
import sys
import xml.etree.ElementTree as ET

from urllib.request import urlopen, Request
from bs4 import BeautifulSoup

class FinacialStat():
    def __init__(self):
        self.annual_date = None
        self.quater_date = None

    def init_fs(self, ticker) :
        try:
            candles = []

            url = f'https://finance.naver.com/item/main.nhn?code={ticker}'
            #req.add_header('User-Agent', 'Mozilla/5.0')
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            res = requests.get(url, headers=headers)
            #print(res.text)
            df = pd.read_html(res.text)[3]
            #print(df)

            df.set_index(df.columns[0], inplace=True)
            df.index.rename('주요재무정보', inplace=True)

            # 'IFRS연결' 행 버림
            df.columns = df.columns.droplevel(2)

            # '최근 연간 실적'과 '최근 분기 실적'으로 나눔
            self.annual_date = pd.DataFrame(df).xs('최근 연간 실적', axis=1)
            self.quater_date = pd.DataFrame(df).xs('최근 분기 실적', axis=1)
            #print(self.annual_date)
        except Exception as e:
            print("raise error ", e)

    def get_current_pbr(self):
        try:
            column_count = len(self.quater_date.columns)

            for i in reversed(range(column_count)) :
                current_idx = self.quater_date.columns[i]
                current_fs = float(self.quater_date[current_idx].iloc[12])

                if current_fs == '-' :
                    continue

                if math.isnan(float(current_fs)):
                    continue
                return float(current_fs)
        except Exception as e:
            print("error pbr ", e)
            return 100

    def get_current_roe(self):
        try:
            column_count = len(self.quater_date.columns)

            for i in reversed(range(column_count)) :
                current_idx = self.quater_date.columns[i]
                current_fs = float(self.quater_date[current_idx].iloc[5])

                if current_fs == '-' :
                    continue

                if math.isnan(float(current_fs)):
                    continue

                return float(current_fs)
        except Exception as e:
            print("error pbr ", e)
            return -1

    def get_pre_roe(self):
        try:
            column_count = len(self.quater_date.columns)

            for i in reversed(range(column_count)) :
                current_idx = self.quater_date.columns[i]
                pre_idx = self.quater_date.columns[i-1]
                current_fs = float(self.quater_date[current_idx].iloc[5])
                pre_fs = float(self.quater_date[pre_idx].iloc[5])

                if current_fs == '-' :
                    continue

                if math.isnan(float(current_fs)):
                    continue

                return float(pre_fs)
        except Exception as e:
            print("error pbr ", e)
            return -1

    def get_cuurent_quater_per(self):
        try:
            column_count = len(self.quater_date.columns)

            for i in reversed(range(column_count)) :
                current_idx = self.quater_date.columns[i]
                current_fs = float(self.quater_date[current_idx].iloc[10])

                if current_fs == '-' :
                    continue

                if math.isnan(float(current_fs)):
                    continue

                print(current_fs)
                return float(current_fs)
        except Exception as e:
            print("error pbr ", e)
            return -1


    #매출액 0
    #영업이익 1
    #영업이익률 3
    def is_continous_rising_quater(self, result_type):
        try:
            column_count = len(self.quater_date.columns)

            for i in reversed(range(column_count)) :
                current_idx = self.quater_date.columns[i]
                pre_idx = self.quater_date.columns[i-1]
                third_idx = self.quater_date.columns[i-2]

                current_fs = self.quater_date[current_idx].iloc[result_type]
                pre_fs = self.quater_date[pre_idx].iloc[result_type]
                third_fs = self.quater_date[third_idx].iloc[result_type]

                if current_fs == '-' or math.isnan(float(current_fs)):
                    continue

                if pre_fs == '-' or math.isnan(float(pre_fs)) :
                    return False

                if float(current_fs) > float(pre_fs) :
                    return True
                else :
                    return False
            return False

        except Exception as e:
            print("raise error ", e)
            return False

    def is_continous_rising_quater_third(self, result_type):
        try:
            column_count = len(self.quater_date.columns)

            for i in reversed(range(column_count)) :
                current_idx = self.quater_date.columns[i]
                pre_idx = self.quater_date.columns[i-1]
                third_idx = self.quater_date.columns[i-2]

                current_fs = self.quater_date[current_idx].iloc[result_type]
                pre_fs = self.quater_date[pre_idx].iloc[result_type]
                third_fs = self.quater_date[third_idx].iloc[result_type]

                if current_fs == '-' or math.isnan(float(current_fs)):
                    continue

                if pre_fs == '-' or math.isnan(float(pre_fs)) :
                    return False

                if third_fs == '-' or math.isnan(float(third_fs)) :
                    return False

                if float(current_fs) > float(pre_fs) > float(third_fs) :
                    return True
                else:
                    return False
            return False

        except Exception as e:
            print("raise error ", e)
            return False

    def is_continous_rising_annual(self, result_type):
        try:
            column_count = len(self.annual_date.columns)

            for i in reversed(range(column_count)) :
                current_idx = self.annual_date.columns[i]
                pre_idx = self.annual_date.columns[i-1]

                #print(self.annual_date.columns)

                current_fs = self.annual_date[current_idx].iloc[result_type]
                pre_fs = self.annual_date[pre_idx].iloc[result_type]

                if current_fs == '-' or math.isnan(float(current_fs)):
                    continue

                if pre_fs == '-' or math.isnan(float(pre_fs)) :
                    return True

                if float(current_fs) > float(pre_fs) and float(current_fs) > 0:
                    return True

                return False
            return False

        except Exception as e:
            print("raise error ", e)
            return False  

if __name__ == "__main__":
    fs = FinacialStat()
    fs.init_fs('353590')
    # if fs.is_continous_rising_quater_roe(5):
    #     print('roe true')
    # else:
    #     print('roe false')

    # if fs.is_continous_rising_quater(1):
    #     print('true')
    # else:
    #     print('false')

    # fs.get_cuurent_quater_pbr()
    # fs.get_cuurent_quater_per()

    fs.is_continous_rising_annual(3)

        



