import pandas as pd
from pandas_datareader import data

def ema(pd_dataframe):
    close = pd_dataframe['trade_price']

    num_periods = 20 # number of days over which to average
    K = 2 / (num_periods + 1) # smoothing constant
    ema_p = 0

    ema_values = [] # to hold computed EMA values
    for close_price in close:
        if (ema_p == 0): # first observation, EMA = current-price
            ema_p = close_price
        else:
            ema_p = (close_price - ema_p) * K + ema_p

        ema_values.append(ema_p)

    pd_dataframe = pd_dataframe.assign(ClosePrice=pd.Series(close, index=pd_dataframe.index))
    pd_dataframe = pd_dataframe.assign(Exponential20DayMovingAverage=pd.Series(ema_values, index=pd_dataframe.index))

    close_price = pd_dataframe['ClosePrice']
    ema = pd_dataframe['Exponential20DayMovingAverage']

    import matplotlib.pyplot as plt

    fig = plt.figure()
    ax1 = fig.add_subplot(111, ylabel='Google price in $')
    close_price.plot(ax=ax1, color='g', lw=2., legend=True)
    ema.plot(ax=ax1, color='b', lw=2., legend=True)
    plt.show()
