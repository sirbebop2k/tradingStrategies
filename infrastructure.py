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

api_url = 'https://api.kraken.com'

with open('kraken_api_key1.txt', 'r') as r:
    lines = r.read().splitlines()
    key1 = lines[0]
    secret1 = lines[1]


def get_kraken_signature(urlpath, data, secretkey):
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()
    mac = hmac.new(base64.b64decode(secretkey), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()


# more copy paste until we figure this out #
def kraken_response(urlpath, data, api_key, api_pass):
    headers = {"API-Key": api_key, "API-Sign": get_kraken_signature(urlpath, data, api_pass)}
    resp = requests.post(api_url + urlpath, headers=headers, data=data)
    return resp


# methods to tidy up our outputs lol #

def getHoldings(coin=None, key=key1, secret=secret1):
    thing = kraken_response('/0/private/Balance', {'nonce': str(int(time.time() * 1000))}, key, secret).json()
    if coin:
        holding = float(thing['result'][coin])
        return holding
    else:
        df = pd.DataFrame.from_dict(thing['result'], orient='index', columns=['quantity'])
        df = df.astype(float)
        return df


def getUSDBalance(key=key1, secret=secret1):
    thing = kraken_response('/0/private/Balance', {'nonce': str(int(time.time() * 1000))}, key, secret).json()
    balance = float((thing['result'])['ZUSD'])

    return balance


def getDepositMethods(key=key1, secret=secret1):
    thing = kraken_response('/0/private/DepositMethods', {'nonce': str(int(time.time() * 1000))}, key,
                            secret).json()
    return thing['result']


def getTradeVolume(key=key1, secret=secret1):
    thing = kraken_response('/0/private/TradeVolume', {'nonce': str(int(time.time() * 1000))}, key, secret).json()
    df = pd.DataFrame.from_dict(thing['result'], orient='index')
    return df


def getOHLC(pair, interval=1, timestamp=0, key=key1, secret=secret1):
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

    return df


def getClose(pair, interval=1, timestamp=0, key=key1, secret=secret1):
    df = getOHLC(pair, interval, timestamp, key, secret)
    close = pd.DataFrame(df['close'])
    return close


def getTickerInfo(pair, key=key1, secret=secret1):
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

    return thing


def getTime(key=key1, secret=secret1):
    thing = kraken_response('/0/public/Time', {'nonce': str(int(time.time() * 1000))}, key, secret).json()
    t = (thing['result'])[list(thing['result'])[0]]

    return t


# for backtesting #


def getSharpe(returns, periods):

    result = returns['% change'].iloc[2:] + 1
    result = result.resample(periods).prod() - 1

    if periods == '1D':
        mean = result.mean() * 12 - .02989
        vol = result.std() * (12 ** 0.5)

    elif periods == '1M':
        mean = result.mean() * 365 - .02989
        vol = result.std() * (365 ** 0.5)

    sharpe = mean / vol

    df = pd.DataFrame(columns=['Mean', 'Vol', 'Sharpe'], index=['Strat'])
    df['Mean'] = mean
    df['Vol'] = vol
    df['Sharpe'] = sharpe

    return df


##


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
