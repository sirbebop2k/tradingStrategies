# this is ridiculous PyCharm... #
import time
import hashlib
import urllib.parse
import urllib.request
import hmac
import base64
import pandas as pd
from datetime import datetime
import requests
import matplotlib.pyplot as plt

api_url = 'https://api.kraken.com'

# this so that one doesn't have to retype key and secret every time to access API #
# replace 'kraken_api_key1.txt' with your own default API key and secret, of course #
# if no API pair, may set key1='', secret1='' to access public endpoints #
with open('kraken_api_key1.txt', 'r') as r:
    lines = r.read().splitlines()
    def_key = lines[0]
    def_secret = lines[1]

# credit to https://www.youtube.com/watch?v=XjVesu_G5yQ&t=1681s for API authentication methods #
def get_kraken_signature(urlpath, data, secretkey):
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()
    mac = hmac.new(base64.b64decode(secretkey), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()


def kraken_response(urlpath, data, api_key, api_pass):
    headers = {"API-Key": api_key, "API-Sign": get_kraken_signature(urlpath, data, api_pass)}
    resp = requests.post(api_url + urlpath, headers=headers, data=data)
    return resp

# coin=None for all holdings, specify coin for float num of coin holding #
def getHoldings(coin=None, key=def_key, secret=def_secret):
    thing = kraken_response('/0/private/Balance', {'nonce': str(int(time.time() * 1000))}, key, secret).json()
    if thing['error'] == ['EAPI:Invalid key']:
        raise Exception('Key and/or Secret Invalid')

    if coin:
        holding = float(thing['result'][coin])
        return holding
    else:
        df = pd.DataFrame.from_dict(thing['result'], orient='index', columns=['quantity'])
        df = df.astype(float)
        return df


def getUSDBalance(key=def_key, secret=def_secret):
    thing = kraken_response('/0/private/Balance', {'nonce': str(int(time.time() * 1000))}, key, secret).json()
    if thing['error'] == ['EAPI:Invalid key']:
        raise Exception('Key and/or Secret Invalid')

    balance = float((thing['result'])['ZUSD'])

    return balance


def getDepositMethods(key=def_key, secret=def_secret):
    thing = kraken_response('/0/private/DepositMethods', {'nonce': str(int(time.time() * 1000))}, key,
                            secret).json()
    if thing['error'] == ['EAPI:Invalid key']:
        raise Exception('Key and/or Secret Invalid')

    return thing['result']


def getTradeVolume(key=def_key, secret=def_secret):
    thing = kraken_response('/0/private/TradeVolume', {'nonce': str(int(time.time() * 1000))}, key, secret).json()
    if thing['error'] == ['EAPI:Invalid key']:
        raise Exception('Key and/or Secret Invalid')

    df = pd.DataFrame.from_dict(thing['result'], orient='index')

    return df


def getOHLC(pair, interval=1, timestamp=0, key=def_key, secret=def_secret):
    if timestamp == 0:
        thing = kraken_response('/0/public/OHLC',
                                {'nonce': str(int(time.time() * 1000)), 'pair': pair, 'interval': interval},
                                key, secret).json()
    else:
        thing = kraken_response('/0/public/OHLC',
                                {'nonce': str(int(time.time() * 1000)), 'pair': pair, 'interval': interval,
                                 'since': timestamp},
                                key, secret).json()
    df = pd.DataFrame((thing['result'])[list(thing['result'])[0]],
                      columns=['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'])
    df['time'] = df['time'].apply(lambda x: datetime.fromtimestamp(x))
    df.set_index('time', inplace=True)
    df = df.astype('float')

    return df


def getClose(pair, interval=1, timestamp=0, key=def_key, secret=def_secret):
    df = getOHLC(pair, interval, timestamp, key, secret)
    close = pd.DataFrame(df['close'])
    return close


def getTickerInfo(pair, key=def_key, secret=def_secret):
    thing = kraken_response('/0/public/Ticker',
                            {'nonce': str(int(time.time() * 1000)), 'pair': pair}, key, secret).json()
    dct = thing['result'][list(thing['result'])[0]]
    dct['ask'] = dct.pop('a')
    dct['bid'] = dct.pop('b')
    dct['last closed trade'] = dct.pop('c')
    dct['volume'] = dct.pop('v')
    dct['vwap'] = dct.pop('p')
    dct['trade number'] = dct.pop('t')
    dct['low'] = dct.pop('l')
    dct['high'] = dct.pop('h')
    dct['open'] = dct.pop('o')

    return dct


def placeLimitOrder(key, secret, pair, direction, volume, price, oflags=None, validate=False):
    conditions = {'nonce': str(int(time.time() * 1000)),
                  'pair': pair,
                  'ordertype': 'limit',
                  'type': direction,
                  'volume': volume,
                  'price': price,
                  'validate': validate}
    if oflags:
        conditions['oflags'] = oflags

    thing = kraken_response('/0/private/AddOrder',
                            conditions, key, secret).json()
    if thing['error'] == ['EAPI:Invalid key']:
        raise Exception('Key and/or Secret Invalid')

    return thing

def placeMarketOrder(key, secret, pair, direction, volume, validate=False):
    conditions = {'nonce': str(int(time.time() * 1000)),
                  'pair': pair,
                  'ordertype': 'market',
                  'type': direction,
                  'volume': volume,
                  'validate': validate}

    thing = kraken_response('/0/private/AddOrder',
                            conditions, key, secret).json()
    if thing['error'] == ['EAPI:Invalid key']:
        raise Exception('Key and/or Secret Invalid')

    return thing


def getTime(key=def_key, secret=def_secret):
    thing = kraken_response('/0/public/Time', {'nonce': str(int(time.time() * 1000))}, key, secret).json()
    t = (thing['result'])[list(thing['result'])[0]]

    return t


# for backtesting #

def getHoldReturns(pair, interval, start=None, end=None):
    data = getClose(pair, interval)
    df = pd.DataFrame()
    df['close'] = data
    df['% change'] = df['close'].pct_change()

    return df



def getSharpe(returns, periods, rfr=.02989):

    result = returns['% change'].iloc[2:] + 1
    result = result.resample(periods).prod() - 1

    if periods == '1D':
        mean_excess = result.mean() * 365 - rfr
        vol = result.std() * (365 ** 0.5)

    elif periods == '1M':
        mean_excess = result.mean() * 12 - rfr
        vol = result.std() * (12 ** 0.5)

    sharpe = mean_excess / vol

    df = pd.DataFrame(columns=['Mean', 'Vol', 'Sharpe'], index=['Strat'])
    df['Mean'] = mean_excess
    df['Vol'] = vol
    df['Sharpe'] = sharpe

    return df


def plotHistogram(returns, periods):

    result = returns['% change'].iloc[2:] + 1
    result = result.resample(periods).prod() - 1

    n, bins, patches = plt.hist(result)

    plt.grid(True)
    plt.figure(figsize=(.5, .5))
    plt.show()


# all EMAs to have \alpha = 2/(N+1) #
def getEMA(data, window):
    calcs = data.ewm(span=window).mean()
    ema = calcs.iloc[-1, 0]

    return ema


def getListEMA(data, window):
    calcs = data.ewm(span=window).mean()

    return calcs


def getListSMA(data, window):
    calcs = data.rolling(window=window).mean()

    return calcs


def getListVol(data, window):
    calcs = data.rolling(window=window).std()

    return calcs


# hm let's see if this works #
# if not, we may simply create a df of SMAs, and then set df... will have to use iloc, sadly #
def getListExpVol(data, window):
    calcs = data.ewm(span=window).std()

    return calcs
