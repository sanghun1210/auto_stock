import pandas as pd

from pandas_datareader import data
import statistics as stats

#단순 이동 평균
def sma(pd_dataframe, time_period):
    close = pd_dataframe['trade_price']
    history = [] # to track a history of prices
    sma_values = [] # to track simple moving average values
    for close_price in close:
        history.append(close_price)
        if len(history) > time_period: # we remove oldest price because we only average over last 'time_period' prices
            del (history[0])

        sma_values.append(stats.mean(history))

    pd_dataframe = pd_dataframe.assign(ClosePrice=pd.Series(close, index=pd_dataframe.index))
    pd_dataframe = pd_dataframe.assign(Simple20DayMovingAverage=pd.Series(sma_values, index=pd_dataframe.index))

    close_price = pd_dataframe['ClosePrice']
    sma = pd_dataframe['Simple20DayMovingAverage']
    return pd_dataframe

    # import matplotlib.pyplot as plt

    # fig = plt.figure()
    # ax1 = fig.add_subplot(111, ylabel='Google price in $')
    # close_price.plot(ax=ax1, color='g', lw=2., legend=True)
    # sma.plot(ax=ax1, color='r', lw=2., legend=True)
    # plt.show()

def get_current_sma(pd_dataframe, time_period):
    goog_data = sma(pd_dataframe, time_period)
    return goog_data['Simple20DayMovingAverage'].iloc[-1]

def sma_volume(pd_dataframe, time_period):
    close = pd_dataframe['candle_acc_trade_volume']
    history = [] # to track a history of prices
    sma_values = [] # to track simple moving average values
    for close_price in close:
        history.append(close_price)
        if len(history) > time_period: # we remove oldest price because we only average over last 'time_period' prices
            del (history[0])

        sma_values.append(stats.mean(history))

    pd_dataframe = pd_dataframe.assign(ClosePrice=pd.Series(close, index=pd_dataframe.index))
    pd_dataframe = pd_dataframe.assign(MovingAverage=pd.Series(sma_values, index=pd_dataframe.index))

    close_price = pd_dataframe['ClosePrice']
    sma = pd_dataframe['MovingAverage']
    return pd_dataframe

def get_sma_volume(pd_dataframe, time_period):
    goog_data = sma_volume(pd_dataframe, time_period)
    return goog_data['MovingAverage'].iloc[-1]
