# coding: utf-8
import slack
import functions

period = 60

isRed = False
isBrack = False
while True:
    ohlcv_0 = functions.get_ohlcv(0, period)
    ohlcv_1 = functions.get_ohlcv(1, period)
    ohlcv_2 = functions.get_ohlcv(2, period)
    ohlcv_3 = functions.get_ohlcv(3, period)
    functions.show_ohlcv(ohlcv_0)
    log_time = datetime.fromtimestamp(
        ohlcv_0["close_time"]).strftime('%Y/%m/%d %H:%M')
    if functions.check_akasanpei(ohlcv_1, ohlcv_2, ohlcv_3):
        print("赤三兵")
        if not isRed:
            isRed = True
            slack.notify(text=log_time + ": 赤三兵")
            if isBrack:
                isBrack = False
    elif functions.check_kurosannpei(ohlcv_1, ohlcv_2, ohlcv_3):
        print("黒三兵")
        if not isBrack:
            isBrack = True
            slack.notify(text=log_time +: "黒三兵")
            if isRed:
                isRed = False
    else:
        print("スルー")
    time.sleep(period/2)
