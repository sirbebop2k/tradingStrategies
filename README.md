# tradingStrategies

Welcome!

With the help of skills picked up in FINMATH 25000: Quantitative Portfolio Management and Algorithmic Trading, along with advice from friends and trusted internet sources, I've embarked on this hopefully profitable project. My strategies are currently simple and conventional. As I become more comfortable with Python and learn/think about different sources of alpha, I aim to implement fresh strategies.

I've self-taught myself Python, so any suggestions about code would be greatly appreciated! Strategy advice always welcome, of course.

## My Journey Log:
#### beginning 08/24/22
- first decided to simple MACD long/short strategy, as outlined above, on Kraken exchange
- my hypothesis: crypto returns, especially those that are predominantly traded by retail, folow momentum patterns; the trick is to find the right windows
- wrote infrastructure (connecting to Kraken API, sending orders, etc.)
- coded backtester for MACD strategy, downloaded historical OHLCVT data from Kraken
- playing with MACD strategy inputs (windows, periods, etc.)
- the big coins (BTC, ETH, etc.) initially looked good over past year(s), but taking into account fees, returns were generally abysmal
  - to minimize the effect of fees, I worked to reduce the frequency of my trades (lengthening windows, intervals, etc.) and increase the expected return per trade, and found that 1 day trading intervals were more consistently generating returns
- noticed that MACD strategy often prematurely exited positions before major swings, adjusted strategy to reenter during these swings, to positive backtesting results
- wrote code to rank the performance of each tradeable coin on Kraken with an MACD strategy, given adjustable MACD parameters and time period
  - found that MACD strategies are generally chaotic for most coins -- small adjustments in MACD parameters greatly impacted returns 
  - this implies a greater risk of overfitting
  - ETC (Ethereum Classic), however, displayed robust returns in a variety of parameters -- it's the way to go
- pondered switching exchanges; however, none offered balance of available coins vs. fees that kraken did, and gas fees on DEXs made low-volume trading especially difficult
- found out I misread the Kraken margin trading requirements -- the sec doesn't play around
  - had to change my MACD strategy to long only positions, which made it not so market-neutral anymore
  - luckily, backtested returns didn't take too big a hit
- explored options for hosting my strategy on. raspberry pis are all still sold out :( hey, college students get discounts on microsoft azure though!
- after much head-bashing, I've decided to leave azure for real devs, and am now hosting on pythonanywhere.com
- kraken seems to take awhile processing bank transfers; may switch to FTX if necessary

## To do goals:
- perhaps switch from REST to WebSockets to get more continuous data
- develop Bollinger strategy, and perhaps integrate with the exisitng MACD one
