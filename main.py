# coding: utf-8
import functions
import time

period = 3600   # 1m=60，1h=3600，1d=86400
ohlcv = functions.get_ohlcv(period)

status = {
    "order": False,         # オーダーある？
    "position": False       # ポジションある？
}

for i in reversed(range(300)):  # 新しいデータが入ってきていると仮定
    functions.show_ohlcv(ohlcv, i)

    # BUYシグナルチェック
    if not status["position"]:
        status = functions.buy_signal(status, ohlcv, i)

    if status["order"]:
        status = functions.check_order(status) # オーダーの約定をチェック
    
    if status["position"]:
        status = functions.settlement_position(status, ohlcv, i)
    
    time.sleep(0.01)
