import pandas as pd
import schedule
import time
import executeMACD as macd
import stratMACD
import infrastructure as inf



# bot1 = macd.MACD()
# bot2 = macd.MACD()
#
# schedule.every().day.at("00:00").do(bot1.executeMACD, coin='ETC', interval=1440, fast=4, slow=18, third=3)
# schedule.every().day.at("00:00").do(bot1.executeMACD, coin='ETC', interval=1440, fast=12, slow=26, third=9)
#
# while True:
#     schedule.run_pending()
#     time.sleep(1)

#print(stratMACD.rankCoins(1440, 3, 12, 3, index=124, trade_fee=.001))

data1 = stratMACD.getMACDData('ETCUSD', 1440, 4, 18, 3).iloc[-180:]
data2 = stratMACD.getMACDData('ETCUSD', 1440, 12, 26, 9).iloc[-180:]

print(stratMACD.backtestLongMACD(data1, trade_fee=.001))
print(stratMACD.backtestLongMACD(data2, trade_fee=.001))