# coding: utf-8
import slack
import functions

period = 60
ohlcv = functions.get_ohlcv(period)

for i in range(300):
    functions.show_ohlcv(ohlcv, i, 1)
    if functions.check_akasanpei(ohlcv, i):
        print("赤三兵")
    if functions.check_kurosannpei(ohlcv, i):
        print("黒三平")