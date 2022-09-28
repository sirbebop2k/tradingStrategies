import infrastructure as inf
import stratMACD
import stratBollinger
import pandas as pd
import numpy as np
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

# executes trade if MACD conditions ofc, but also only if price is above upper bollinger band
# another strategy would be strong buy if MACD conditions AND above boll, weaker if only MACD
# this is streamlining data input (only pair required), but also limits it to Kraken API data
def backtestBollMACD(pair, interval, fast, slow, third, window, index=None, starting=100,
                     frac_traded=1, factor=.5, trade_fee=0, quantile=.1, mode='sma'):
    if index:
        macd_data = stratMACD.getMACDData(pair, interval, fast, slow, third).iloc[-index:]
        boll_data = stratBollinger.getBollinger(pair, interval, window, factor=factor, mode=mode).iloc[-index:]
    else:
        macd_data = stratMACD.getMACDData(pair, interval, fast, slow, third)
        boll_data = stratBollinger.getBollinger(pair, interval, window, factor=factor, mode=mode)

    frac = frac_traded
    cash = starting
    pos_del = deque()
    holding_num = 0
    indicator = 0
    num_trades = 0
    df = pd.DataFrame(index=macd_data.index)
    df['num trades'] = num_trades
    df['holdings'] = 0
    df['cash'] = cash
    df['total'] = 0

    for i in range(1, len(macd_data.index)):
        close = macd_data.iloc[i, 1]
        this_macd = macd_data.iloc[i, 0]
        last_macd = macd_data.iloc[i - 1, 0]
        boll_cross = boll_data.iloc[i, 4]

        if this_macd - last_macd > 0:
            pos_del.append(this_macd - last_macd)
            if len(pos_del) > 100:
                pos_del.popleft()

        # hist rises above 0 and cross is 1, enter long #
        if (this_macd > 0) and (last_macd < 0) and boll_cross == 1 and (indicator == 0):
            num_trades += 1
            indicator = 1
            holding_num += cash * frac / close
            cash -= holding_num * close * (1 + trade_fee)

        # exit long #
        elif (this_macd < last_macd) and (indicator == 1):
            num_trades += 1
            indicator = 0
            cash += holding_num * close * (1 - trade_fee)
            holding_num = 0

        # unusually high positive histogram change after long exit and cross is 1, re-enter long #
        elif this_macd > 0 and (indicator == 0) and (len(pos_del) == 100) and (
                this_macd - last_macd > np.quantile(pos_del, 1 - quantile)) and boll_cross == 1:
            num_trades += 1
            indicator = 1
            holding_num += cash * frac / close
            cash -= holding_num * close * (1 + trade_fee)

        df.iloc[i, 0] = num_trades
        df.iloc[i, 1] = holding_num * close
        df.iloc[i, 2] = cash
        df.iloc[i, 3] = df.iloc[i, 1] + df.iloc[i, 2]
    df['% change'] = df['total'].pct_change()
    return df