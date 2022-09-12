import pandas as pd
import schedule
import time
import executeStrats as strats
import stratMACD
import stratBollinger
import infrastructure as inf


# rigged to run every day at 00:00:01 UTC #

key1='insert_key1'
secret1='insert_secret1'

key2='insert_key2'
secret2='insert_secret2'


bot1 = strats.Bot(key=key1, secret=secret1)
bot2 = strats.Bot(key=key2, secret=secret2)

bot1.executeMACD('ETC', 1440, 4, 18, 3)
bot2.executeMACD('ETC', 1440, 12, 26, 9)
