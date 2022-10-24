from stratMACD import getMACDData
import infrastructure as inf
import pandas as pd
from collections import deque
from numpy import quantile
import time


# the basic idea: at 00:00 UTC look at OHLC data (since this is when Kraken releases their daily OHLC)
# recalculate all past MACD data, then trade based on our generated signal
# trying post only limit order to avoid maker fees
# this isn't a strategy built on speed, so it isn't essential that we execute instantly. #

# no need to ensure kraken time is >00:00, but can implement if needed


class Bot:
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    # specific conditions: rounding prices to 3 decimal places for ETC #
    # 'X' appended to front of coin #
    def executeMACD(self, coin, interval, fast, slow, third, quant=.1, frac=.99, test=False):

        pair = coin + 'USD'
        pos_del = deque()
        usd_balance = inf.getUSDBalance(key=self.key, secret=self.secret)
        coin_balance = inf.getHoldings(coin='X' + coin, key=self.key, secret=self.secret)

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
        # .99 factor to account for fees #
        if this > 0 and last < 0 and coin_balance == 0:
            print(inf.placeLimitOrder(pair=pair, direction='buy', volume=(usd_balance / bid) * frac,
                                      price=round(bid - .001, 3),
                                      oflags='post', validate=test, key=self.key, secret=self.secret))

        elif (this < last) and (coin_balance > 0):
            print(inf.placeLimitOrder(pair=pair, direction='sell', volume=coin_balance, price=round(ask + .001, 3),
                                      oflags='post', validate=test, key=self.key, secret=self.secret))

        elif this > 0 and (coin_balance == 0) and (this - last > quantile(pos_del, 1 - quant)):
            print(inf.placeLimitOrder(pair=pair, direction='buy', volume=(usd_balance / bid) * frac,
                                      price=round(bid - .001, 3),
                                      oflags='post', validate=test, key=self.key, secret=self.secret))

        t = time.strftime("%m/%d/%y - %H:%M:%S", time.localtime())

        df = pd.DataFrame({'position': coin_balance * close,
                           'balance': usd_balance,
                           'total': coin_balance * close + usd_balance},
                          index=[t])

        tl_dict = {'this MACD': round(this, 4), 'last MACD': round(last, 4), 'price': close}

        print(df)
        print(tl_dict)

        # NOT WORKING AS INTENDED, PLS FIX #
    def testExecuteMACD(self, coin, interval, fast, slow, third):
        pair = coin + 'USD'

        data = getMACDData(pair, interval=interval, fast=fast, slow=slow, third=third).iloc[150:]
        close = float(data.iloc[-1, 1])
        this = float(data.iloc[-1, 0])  # histogram this period #
        last = float(data.iloc[- 2, 0])  # histogram last period #
        bid = float((inf.getTickerInfo(pair, key=self.key, secret=self.secret)['bid'])[0])
        ask = float((inf.getTickerInfo(pair, key=self.key, secret=self.secret)['ask'])[0])
        last_closed = float((inf.getTickerInfo(pair, key=self.key, secret=self.secret)['last closed trade'])[0])

        tl_dict = {'this MACD': round(this, 4), 'last MACD': round(last, 4), 'price': close}
        bid_ask_dict = {'bid': bid, 'ask': ask, 'last closed':last_closed}

        print(data)
        print(tl_dict)
        print(bid_ask_dict)

    def test(self, coin):
        pair = coin + 'USD'

        t = time.strftime("%m/%d/%y - %H:%M:%S", time.localtime())

        coin_balance = self.position
        usd_balance = inf.getUSDBalance(key=self.key, secret=self.secret)
        close = float((inf.getTickerInfo(pair, key=self.key, secret=self.secret)['vwap'])[1])
        df = pd.DataFrame({'position': coin_balance * close,
                           'balance': usd_balance, 'total': coin_balance * close + usd_balance},
                          index=[t])

        print(df)
