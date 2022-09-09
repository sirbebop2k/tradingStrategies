import pandas as pd
import schedule
import time
import executeStrats as strats
import stratMACD
import stratBollinger
import infrastructure as inf



#bot1 = strats.Bot(key='S9Y05pXGGbVG3z3q9LNAGLTjfF2K3b9gZnwZ7YF6Exw9xN1pzU4x/XLK',secret='glVRPbr9SrcIWkZRysnd81uM17JaFlwJZ/EE1Hr2qAkDYcaJTjcy5x08O8yt1WnMvZFH4CfniLxpSFregfASJQ==')
# bot2 = macd.MACD()
#
# schedule.every().day.at("00:00").do(bot1.executeMACD, coin='ETC', interval=1440, fast=4, slow=18, third=3)
# schedule.every().day.at("00:00").do(bot1.executeMACD, coin='ETC', interval=1440, fast=12, slow=26, third=9)
#
# while True:
#     schedule.run_pending()
#     time.sleep(1)

#print(stratMACD.rankCoins(1440, 3, 12, 3, index=124, trade_fee=.001))


data = stratBollinger.getBollinger('SCUSD', 1440, 20)
stratBollinger.plotBollinger(data, start='2022-01-01', end='2022-09-01')
print(inf.getHoldings())
