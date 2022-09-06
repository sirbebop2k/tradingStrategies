import infrastructure as inf
import pandas as pd
import matplotlib.pyplot as plt


# ema returns ema, sma returns sma. in the future, we may replace ema with GARCH(1.1) #
# want to return df with close, mean, and upper/lower lines #
# notice that crossovers usually indicate a correction incoming, so we negate our signal #
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

    df = df.iloc[100:]
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
# buy/sell when
def backtestBollinger():
    pass



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
