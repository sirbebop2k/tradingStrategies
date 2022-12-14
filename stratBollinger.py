import infrastructure as inf
import pandas as pd
import matplotlib.pyplot as plt


# ema returns ema, sma returns sma. in the future, we may replace ema with GARCH(1.1) #
def getBollinger(pair, interval, window, factor=1, mode='sma'):
    df = pd.DataFrame(columns=['close', 'mean', 'upper', 'lower', 'cross'])
    data = inf.getClose(pair=pair, interval=interval)
    if mode == 'sma':
        mean = inf.getListSMA(data=data, window=window)
        vol = inf.getListVol(data=data, window=window)

    elif mode == 'ema':
        mean = inf.getListEMA(data=data, window=window)
        vol = inf.getListExpVol(data=data, window=window)

    upper = mean + factor * vol
    lower = mean - factor * vol
    df['close'] = data
    df['mean'] = mean
    df['upper'] = upper
    df['lower'] = lower

    df = df.iloc[50:]
    df = df.astype('float')

    for i in range(len(df.index)):
        if df.iloc[i,0] > df.iloc[i,2]:
            df.iloc[i,4] = 1
        elif df.iloc[i,0] < df.iloc[i,3]:
            df.iloc[i,4] = -1
        else:
            df.iloc[i,4] = 0

    return df


# purely bollinger strategy #
# two philosophies with this:
# buy when price bottoms out after crossing bottom band, with expectation of rebound
# buy right when price crosses top band, with expectation of continued momentum
# these seem to be at odds with each other, but let's try them individually and together!

# this is rebound strategy, objectively not too good
def backtestBollinger(data, starting=100, trade_fee=.001, frac=1, mode='sma'):
    cash = starting
    frac = frac
    holding_num = 0
    short_day = True
    indicator = 0
    num_trades = 0
    df = pd.DataFrame(index=data.index)
    df['num trades'] = num_trades
    df['holdings'] = 0
    df['cash'] = cash
    df['total'] = 0

    for i in range(len(data.index)):
        cross = data.iloc[i,4]
        cross_last = data.iloc[i-1, 4]
        close = data.iloc[i,0]
        close_last = data.iloc[i-1,0]

        if indicator == 0 and cross == -1 and cross_last == 0:
            indicator = 1
            num_trades += 1
            holding_num += cash * frac / close
            cash -= holding_num * close * (1 + trade_fee)
        elif indicator == 1 and cross != -1 and close<close_last:
            indicator = 0
            num_trades += 1
            cash += holding_num * close * (1 - trade_fee)
            holding_num = 0


        df.iloc[i, 0] = num_trades
        df.iloc[i, 1] = holding_num * close
        df.iloc[i, 2] = cash
        df.iloc[i, 3] = df.iloc[i, 1] + df.iloc[i, 2]

    df['% change'] = df['total'].pct_change()

    return df

# looking at the Bollinger plots, it seems that this strategy won't generate too much. might as well work to implement it, though #
# i've realized that bollinger alone isn't enough of a signal. in combination with macd, though...

def rankCoins(interval, window, factor=1, starting=100, trade_fee=.001, frac=1, mode='sma', index=None):

    # this is still an abridged list of all tradeable coins, the coins outside these are veryyy fringe #
    coins = ['ZRX', '1INCH', 'AAVE', 'GHST', 'ALGO', 'ANKR', 'ANT', 'REP', 'AXS',
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

    for item in coins:
        title = item + 'USD'
        if index:
            data = (getBollinger(title, interval=interval, window=window, factor=factor, mode=mode)).iloc[-index:]
        else:
            data = getBollinger(title, interval=interval, window=window, factor=factor, mode=mode)

        returns = backtestBollinger(data, starting=100, trade_fee=trade_fee, frac=frac, mode=mode)
        final = float(returns.iloc[-1, 2])
        dct[title] = final
        title = ''

    df = pd.DataFrame.from_dict(dct, orient='index', columns=['final'])
    df.sort_values(by=['final'], ascending=False, inplace=True)
    return df



def plotBollinger(input, start=None, end=None):
    if start is None and end is None:
        data = input

    else:
        data = input.loc[start:end]

    x = data.index
    y1 = data['close']
    y2 = data['upper']
    y3 = data['lower']
    fig, ax = plt.subplots()
    ax.plot(x, y1, label='close')
    ax.plot(x, y2, label='upper')
    ax.plot(x, y3, label='lower')
    fig.show()
