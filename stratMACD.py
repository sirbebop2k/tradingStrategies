import infrastructure as inf
import pandas as pd
import numpy as np
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator


# calculates MACD data from closes pulled from API #
# not particularly efficient, want to only calculate those for which I need. will get to this #
def getMACDData(pair, interval, fast, slow, third):

    close = inf.getClose(pair, interval=interval)

    diff_list = (inf.getListEMA(close, window=fast) - inf.getListEMA(close, window=slow))
    diff_ema = inf.getListEMA(diff_list, window=third)
    close = close.iloc[50:]
    diff_list = diff_list.iloc[50:]
    diff_ema = diff_ema.iloc[50:]

    df = pd.DataFrame(index=close.index)
    df['histogram'] = diff_list - diff_ema
    df['close'] = close
    df = df.astype('float')

    return df
def getMACDData_manual(data, fast, slow, third):

    close = pd.DataFrame(data['close'])

    diff_list = (inf.getListEMA(close, window=fast) - inf.getListEMA(close, window=slow))
    diff_ema = inf.getListEMA(diff_list, window=third)
    close = close.iloc[50:]
    diff_list = diff_list.iloc[50:]
    diff_ema = diff_ema.iloc[50:]

    df = pd.DataFrame(index=close.index)
    df['histogram'] = diff_list - diff_ema
    df['close'] = close
    df = df.astype('float')

    return df


# idea: issue long signal when MACD line crosses above 0, maintain until MACD stops increasing # issue short signal
# when MACD line crosses above 0, maintain until MACD stops decreasing # after exiting position, re-enter if MACD
# increases/decreases by a magnitude within the {quantile} quantile of directional MACD swings #

def backtestMACD(data, starting=100, frac_traded=1, trade_fee=0, margin_fee=0, quantile=.1):
    frac = frac_traded
    cash = starting
    pos_del = deque() # list of past 100 positive MACD swings
    neg_del = deque() # list of past 100 negative MACD swings
    holding_num = 0
    short_day = True
    indicator = 0
    num_trades = 0
    df = pd.DataFrame(index=data.index)
    df['num trades'] = num_trades
    df['holdings'] = 0
    df['cash'] = cash
    df['total'] = 0

    for i in range(1, len(data.index)):
        close = data.iloc[i, 1]
        this = data.iloc[i, 0]
        last = data.iloc[i - 1, 0]

        if this - last > 0:
            pos_del.append(this - last)
        elif this - last < 0:
            neg_del.append(this - last)

        if len(pos_del) > 100:
            pos_del.popleft()
        if len(neg_del) > 100:
            neg_del.popleft()

        if indicator == -1:
            short_day = True
        elif indicator != -1:
            short_day = False

        if short_day:
            cash -= holding_num * close * (- margin_fee * 12)

        # hist rises above 0, enter long #
        if (this > 0) and (last < 0) and (indicator == 0):
            num_trades += 1
            indicator = 1
            holding_num += cash * frac / close
            cash -= holding_num * close * (1 + trade_fee)

        # exit long #
        elif (this < last) and (indicator == 1):
            num_trades += 1
            indicator = 0
            cash += holding_num * close * (1 - trade_fee)
            holding_num = 0

        # unusually high positive histogram change after long exit, re-enter long #
        elif this > 0 and (indicator == 0) and (len(pos_del) == 100) and (
                this - last > np.quantile(pos_del, 1 - quantile)):
            num_trades += 1
            indicator = 1
            holding_num += cash * frac / close
            cash -= holding_num * close * (1 + trade_fee)

        # hist dips below 0, enter short #
        elif (this < 0) and (last > 0) and (indicator == 0):
            num_trades += 1
            indicator = -1
            holding_num -= cash * frac / close
            cash -= holding_num * close * (1 - trade_fee - margin_fee)

        # exit short #
        elif (this > last) and (indicator == -1):
            num_trades += 1
            indicator = 0
            cash += holding_num * close * (1 + trade_fee)
            holding_num = 0

        # unusually high negative histogram change after short exit, re-enter short #
        elif this < 0 and (indicator == 0) and (len(neg_del) == 100) and (this - last < np.quantile(neg_del, quantile)):
            num_trades += 1
            indicator = -1
            holding_num -= cash * frac / close
            cash -= holding_num * close * (1 - trade_fee - margin_fee)

        # corner cases where the peak only lasts one period #
        elif (this > 0) and (indicator == -1):
            num_trades += 1
            indicator = 1
            holding_num += 2 * cash * frac / close
            cash -= holding_num * close * (1 + trade_fee)

        elif (this < 0) and (indicator == 1):
            num_trades += 1
            indicator = -1
            holding_num -= 2 * cash * frac / close
            cash -= holding_num * close * (1 - trade_fee - margin_fee)

        df.iloc[i, 0] = num_trades
        df.iloc[i, 1] = holding_num * close
        df.iloc[i, 2] = cash
        df.iloc[i, 3] = df.iloc[i, 1] + df.iloc[i, 2]
    df['% change'] = df['total'].pct_change()

    return df

# turns out, no shorting! this is the above strategy, except long only #
def backtestLongMACD(data, starting=100, frac_traded=1, trade_fee=0, quantile=.1):
    frac = frac_traded
    cash = starting
    pos_del = deque()
    holding_num = 0
    indicator = 0
    num_trades = 0
    df = pd.DataFrame(index=data.index)
    df['num trades'] = num_trades
    df['holdings'] = 0
    df['cash'] = cash
    df['total'] = 0

    for i in range(1, len(data.index)):
        close = data.iloc[i, 1]
        this = data.iloc[i, 0]
        last = data.iloc[i - 1, 0]

        if this - last > 0:
            pos_del.append(this - last)

        if len(pos_del) > 100:
            pos_del.popleft()

        # hist rises above 0, enter long #
        if (this > 0) and (last < 0) and (indicator == 0):
            num_trades += 1
            indicator = 1
            holding_num += cash * frac / close
            cash -= holding_num * close * (1 + trade_fee)

        # exit long #
        elif (this < last) and (indicator == 1):
            num_trades += 1
            indicator = 0
            cash += holding_num * close * (1 - trade_fee)
            holding_num = 0

        # unusually high positive histogram change after long exit, re-enter long #
        elif this > 0 and (indicator == 0) and (len(pos_del) == 100) and (
                this - last > np.quantile(pos_del, 1 - quantile)):
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


def plotMACD(input, start=None, end=None):
    if start is None and end is None:
        data = input

    else:
        data = input.loc[start:end]

    x = data.index
    y1 = data['histogram']
    y2 = data['close']
    fig, (ax1, ax2) = plt.subplots(2, 1)
    ax1.plot(x, y2, label='close')
    ax2.plot(x, y1, label='histogram')
    ax1.xaxis.set_minor_locator(AutoMinorLocator(4))
    ax2.xaxis.set_minor_locator(AutoMinorLocator(4))
    ax1.grid(which='major')
    ax1.grid(which='minor')
    ax2.grid(which='major')
    ax2.grid(which='minor')
    fig.autofmt_xdate(rotation=45)
    fig.show()


# ranking coins based off of performance in indicated MACD configuration, over the past {index} periods #
# margin=True if able to take short positions #
def rankCoins(interval, fast, slow, third, index=None, trade_fee=0, quantile=.1, margin=False):

    # Kraken has a different list of margin-tradeable coins than regularly tradeable #
    margin_list = ['AAVE', 'ALGO', 'APE', 'AVAX', 'AXS', 'BAT', 'BTC', 'BCH',
                   'ADA', 'LINK', 'ATOM', 'CRV', 'DASH', 'DAI', 'MANA', 'DOGE',
                   'EOS', 'ETH', 'ETC', 'FIL', 'KAVA', 'KEEP', 'KSM', 'LTC',
                   'LRC', 'XMR', 'NANO', 'OMG', 'PAXG', 'DOT', 'MATIC', 'XRP',
                   'SOL', 'SC', 'XLM', 'GRT', 'SAND', 'XTZ', 'TRX', 'UNI', 'WAVES', 'ZEC']

    # this is still an abridged list, the coins outside these are veryyy fringe #
    full_list = ['ZRX', '1INCH', 'AAVE', 'GHST', 'ALGO', 'ANKR', 'ANT', 'REP', 'AXS',
                 'BADGER', 'BNT', 'BAL', 'BAND', 'BAT', 'BNC', 'BTC', 'BCH', 'ADA',
                 'CTSI', 'LINK', 'CHZ', 'COMP', 'ATOM', 'CQT', 'CRV', 'DAI', 'DASH',
                 'MANA', 'DOGE', 'EWT', 'ENJ', 'MLN', 'EOS', 'ETH', 'ETC', 'FIL', 'FLOW',
                 'GNO', 'ICX', 'KAR', 'KAVA', 'KEEP', 'KSM', 'KNC', 'LSK', 'LTC',
                 'LPT', 'LRC', 'MKR', 'MINA', 'XMR', 'MOVR', 'NANO', 'OCEAN', 'OMG',
                 'OXT', 'OGN', 'PAXG', 'PERP', 'PHA', 'DOT', 'MATIC', 'QTUM', 'QNT',
                 'RARI', 'RAY', 'REN', 'XRP', 'SRM', 'SHIB', 'SDN', 'SC', 'SOL', 'XLM',
                 'STORJ', 'SUSHI', 'SNX', 'TBTC', 'USDT', 'XTZ', 'GRT', 'SAND', 'TRX',
                 'UNI', 'WAVES', 'WBTC', 'YFI', 'ZEC']

    dct = dict()

    if margin:
        coins = margin_list
    else:
        coins = full_list

    for item in coins:
        title = item + 'USD'
        if index:
            data = (getMACDData(title, interval=interval, fast=fast, slow=slow, third=third)).iloc[-index:]
        else:
            data = getMACDData(title, interval=interval, fast=fast, slow=slow, third=third)

        if margin:
            returns = backtestMACD(data, starting=100, trade_fee=trade_fee, frac_traded=1, quantile=quantile)
        else:
            returns = backtestLongMACD(data, starting=100, trade_fee=trade_fee, frac_traded=1, quantile=quantile)
        final = float(returns.iloc[-1, 2])
        dct[title] = final
        title = ''

    df = pd.DataFrame.from_dict(dct, orient='index', columns=['final'])
    df.sort_values(by=['final'], ascending=False, inplace=True)
    return df
