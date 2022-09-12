# tradingStrategies

Welcome!

With the help of skills picked up in FINMATH 25000: Quantitative Portfolio Management and Algorithmic Trading, along with advice from friends and trusted internet sources, I've embarked on this prospectively profitable project. My strategies are currently simple and conventional. As I become more comfortable with Python and learn/think about different sources of alpha, I aim to implement fresh strategies.

All my Python is self-taught, so any suggestions about code would be greatly appreciated! Strategy advice always welcome, of course.

## Table of Contents:
* executeStrats.py: methods for implementing strategy and executing trades; object oriented to facilitate execution of multiple strategies in multiple Kraken accounts
* infrastructure.py: methods for interacting with Kraken REST API, along with methods generally useful for a variety of strategies and backtesting
* main.py: implementing strategy
* stratMACD.py: methods useful specifically for MACD, including backtesting
* stratBollinger.py: methods useful specifically for Bollinger, including backtesting; **unfinished**
* testing.ipynb: Jupyter Notebook detailing concise Sharpe comparisons and visualisations

## My Journey Log:
#### beginning 08/24/22
- First decided to simple MACD long/short strategy, as outlined above, on Kraken exchange
- My hypothesis: crypto returns, especially those that are predominantly traded by retail, folow momentum patterns; the trick is to find the right windows
- Wrote infrastructure (connecting to Kraken API, sending orders, etc.)
- Coded backtester for MACD strategy, downloaded historical OHLCVT data from Kraken
- Playing with MACD strategy inputs (windows, periods, etc.)
- The big coins (BTC, ETH, etc.) initially looked good over past year(s), but taking into account fees, returns were generally abysmal
  - To minimize the effect of fees, I worked to reduce the frequency of my trades (lengthening windows, intervals, etc.) and increase the expected return per trade, and found that 1 day trading intervals were more consistently generating returns
- Noticed that MACD strategy often prematurely exited positions before major swings, adjusted strategy to reenter during these swings, to positive backtesting results
- Wrote code to rank the performance of each tradeable coin on Kraken with an MACD strategy, given adjustable MACD parameters and time period
  - Found that MACD strategies are generally chaotic for most coins -- small adjustments in MACD parameters greatly impacted returns 
  - This implies a greater risk of overfitting
  - ETC (Ethereum Classic), however, displayed robust returns in a variety of parameters -- it's the way to go
- Pondered switching exchanges; however, none offered balance of available coins vs. fees that kraken did, and gas fees on DEXs made low-volume trading especially difficult
  - To avoid large taker fees, will solely submit post only limit orders.
  - This strategy doesn't rely on speed; as long as the order executes at our desired price we should be golden
- Found out I misread the Kraken margin trading requirements -- the SEC really doesn't play around
  - Had to change my MACD strategy to long only positions, which made it not so market-neutral anymore
  - Luckily, backtested returns didn't take too big a hit. Most positive PnLs came from long positions, it historically seems.
- Explored options for hosting my strategy on. Raspberry Pis are all still sold out :( hey, college students get discounts on Microsoft Azure though!
- After much head-bashing, I've decided to leave Azure for real devs, and am now hosting on pythonanywhere.com
- Kraken seems to take awhile processing bank transfers; may switch to FTX if necessary

## To do goals:
- Enact measures to deal with order not being filled (though extremely unlikely)
- Develop Bollinger strategy, and perhaps integrate with the exisitng MACD one
-  Strengthen MACD strategy by scaling our positions with stength of MACD swing (on top of existing measure)
- Perhaps switch from REST to WebSockets to get more continuous data
