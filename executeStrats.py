from stratMACD import getMACDData
import infrastructure as inf
import pandas as pd
from collections import deque
from numpy import quantile
import time


# the basic idea: at 00:00 UTC look at OHLC data
#   (since this is when Kraken releases their daily OHLC)
# recalculate all past MACD data, then trade based on our generated signal
# trying post only limit order to avoid maker fees
# this isn't a strategy built on speed,
#   so it isn't essential that we execute instantly. #

# no need to ensure kraken time is >00:00, but can implement if needed


class Bot:
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    # specific conditions: rounding prices to 3 decimal places for ETC #
    # 'X' appended to front of coin #
    def executeMACD(self, coin, interval, fast, slow, third,
                    quant=.1, frac=.99, test=False):

        pair = coin + 'USD'

        # deque of positive MACD swings
        pos_del = deque()

        # current USD balance
        usd_balance = inf.getUSDBalance(key=self.key, secret=self.secret)

        # current balance (quantity) of coin of interest
        # note: may need to replace 'X' with alternative
        #   depending on Kraken specifications
        coin_balance = inf.getHoldings(coin='X' + coin, key=self.key,
                                       secret=self.secret)

        # determines what may be rounded as effectively zero coin balance
        # in the future, should scale with coin value.
        effective_zero = 0.1 ** 4

        data = getMACDData(pair, interval=interval,
                           fast=fast, slow=slow, third=third).iloc[150:-1]
        close = float(data.iloc[-1, 1])
        this = float(data.iloc[-1, 0])  # histogram this period #
        last = float(data.iloc[- 2, 0])  # histogram last period #
        bid = float((inf.getTickerInfo(pair, key=self.key,
                                       secret=self.secret)['bid'])[0])
        ask = float((inf.getTickerInfo(pair, key=self.key,
                                       secret=self.secret)['ask'])[0])

        # setting pos_del
        for i in range(len(data.index)-200, len(data.index)):
            diff = float(data.iloc[i, 0])-float(data.iloc[i-1, 0])
            if diff > 0:
                pos_del.append(diff)
            if len(pos_del) > 100:
                pos_del.popleft()

        ### should implement measures just in case our
        #   post order gets cancelled, or never filled by the end #
        # .99 factor to account for fees #
        # places buy order when MACD goes negative to positive, and balance is zero #
        if this > 0 and last < 0 and coin_balance <= effective_zero:
            print(inf.placeLimitOrder(pair=pair, direction='buy',
                                      volume=(usd_balance / bid) * frac,
                                      price=round(bid - .001, 3),
                                      oflags='post', validate=test,
                                      key=self.key, secret=self.secret))

        # places sell order when MACD starts downtrend,
        #   and when coin balance is non-negligible
        elif (this < last) and (coin_balance >= effective_zero):
            print(inf.placeLimitOrder(pair=pair, direction='sell',
                                      volume=coin_balance,
                                      price=round(ask + .001, 3),
                                      oflags='post', validate=test,
                                      key=self.key, secret=self.secret))

        # places buy order when MACD change is in certain quartile of positive upswings
        elif this > 0 and (coin_balance <= effective_zero)\
                and (this - last > quantile(pos_del, 1 - quant)):
            print(inf.placeLimitOrder(pair=pair, direction='buy',
                                      volume=(usd_balance / bid) * frac,
                                      price=round(bid - .001, 3),
                                      oflags='post', validate=test,
                                      key=self.key, secret=self.secret))

        t = time.strftime("%m/%d/%y - %H:%M:%S", time.localtime())

        df = pd.DataFrame({'position': coin_balance * close,
                           'balance': usd_balance,
                           'total': coin_balance * close + usd_balance},
                          index=[t])

        tl_dict = {'this MACD': round(this, 4),
                   'last MACD': round(last, 4), 'price': close}

        print(df)
        print(tl_dict)

        # NOT WORKING AS INTENDED, PLS FIX #
    def testExecuteMACD(self, coin, interval, fast, slow, third):
        pair = coin + 'USD'

        data = getMACDData(pair, interval=interval, fast=fast,
                           slow=slow, third=third).iloc[150:-1]
        close = float(data.iloc[-1, 1])
        this = float(data.iloc[-1, 0])  # histogram this period #
        last = float(data.iloc[- 2, 0])  # histogram last period #
        bid = float((inf.getTickerInfo(pair, key=self.key,
                                       secret=self.secret)['bid'])[0])
        ask = float((inf.getTickerInfo(pair, key=self.key,
                                       secret=self.secret)['ask'])[0])
        last_closed = float((inf.getTickerInfo(pair, key=self.key,
                                               secret=self.secret)['last closed trade'])[0])

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
        close = float((inf.getTickerInfo(pair, key=self.key,
                                         secret=self.secret)['vwap'])[1])
        df = pd.DataFrame({'position': coin_balance * close,
                           'balance': usd_balance,
                           'total': coin_balance * close + usd_balance},
                          index=[t])

        print(df)
