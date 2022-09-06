from stratMACD import getMACDData
import infrastructure as inf
import pandas as pd
from collections import deque
from numpy import quantile


# the basic idea: at, say, 12:00 CST look at OHLC data,
# recalculate all MACD data, then trade based on our generated signal
# try post only limit order to avoid maker fees.
# this isn't a strategy built on speed, so it isn't essential that we execute instantly.
# just need to make sure our order executes

# position = -1 short 0 flat 1 long

class MACD:
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

        self.position = 0
        self.df = pd.DataFrame(columns=['position', 'balance', 'total'])
        self.kraken_t = inf.getTime(key=self.key, secret=self.secret)
        self.not_bought = True

    # let's do (4,16,3) on ETCUSD 1440 #
    def executeMACD(self, coin, interval, fast, slow, third, quant=.1, test=False):
        pair = coin + 'USD'
        pos_del = deque()
        usd_balance = inf.getUSDBalance(key=self.key, secret=self.secret)
        if self.not_bought:
            coin_balance = 0.0
        else:
            coin_balance = inf.getHoldings(coin=coin, key=self.key, secret=self.secret)
        data = getMACDData(pair, interval=interval, fast=fast, slow=slow, third=third).iloc[150:]
        close = float(data.iloc[-1, 1])
        this = float(data.iloc[-1, 0])  # histogram this period #
        last = float(data.iloc[- 2, 0])  # histogram last period #
        bid = float((inf.getTickerInfo(pair, key=self.key, secret=self.secret)['bid'])[0])
        ask = float((inf.getTickerInfo(pair, key=self.key, secret=self.secret)['ask'])[0])

        for i in range(1, len(data.index)):
            if this - last > 0:
                pos_del.append(this - last)
            if len(pos_del) > 100:
                pos_del.popleft()

        # should implement measures just in case our post order gets cancelled, or never filled by the end #
        if this > 0 and last < 0 and self.position == 0:
            inf.placeLimitOrder(pair, 'buy', volume=usd_balance / bid, price=bid,
                                oflags='post', validate=test, key=self.key, secret=self.secret)
            self.position = 1
            self.not_bought = False
        elif (this < last) and (self.position == 1):
            inf.placeLimitOrder(pair, 'sell', volume=coin_balance, price=ask,
                                oflags='post', validate=test, key=self.key, secret=self.secret, )
            self.position = 0
        elif this > 0 and (self.position == 0) and (this - last > quantile(pos_del, 1 - quant)):
            inf.placeLimitOrder(pair, 'buy', volume=usd_balance / bid, price=bid,
                                oflags='post', validate=test, key=self.key, secret=self.secret, )
            self.position = 0
            self.not_bought = False

        df_temp = pd.DataFrame({'position': coin_balance * close,
                                'balance': usd_balance,
                                'total': coin_balance + close * usd_balance},
                               index=[self.kraken_t])
        self.df = pd.concat([self.df, df_temp])

        print(self.df)

    def test(self, coin):
        pair = coin + 'USD'
        self.position += 1
        coin_balance = self.position
        usd_balance = inf.getUSDBalance(key=self.key, secret=self.secret)
        close = float((inf.getTickerInfo(pair, key=self.key, secret=self.secret)['vwap'])[1])
        df_temp = pd.DataFrame({'position': coin_balance * close,
                                'balance': usd_balance, 'total': coin_balance * close + usd_balance},
                               index=[self.kraken_t])
        self.df = pd.concat([self.df, df_temp])

        print(self.df)

# running strat: #
