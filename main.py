import pandas as pd
import schedule
import time
import executeStrats as strats
import stratMACD
import stratBollinger
import infrastructure as inf


key1=''
secret1=''

key2=''
secret2=''


bot1 = strats.Bot(key=key1, secret=secret1)
bot2 = strats.Bot(key=key2, secret=secret2)

bot1.executeMACD('ETC', 1440, 4, 18, 3)
bot2.executeMACD('ETC', 1440, 12, 26, 9)
