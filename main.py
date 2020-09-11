# coding: utf-8
import functions
import time
import ccxt

period = 60   # 1m=60，1h=3600，1d=86400

status = {
    "buy_signal": False,    # TODO 今後重みを表す数値にしたい
    "sell_signal": False,

    # テクニカル分析 TODO ここに手法を増やしていく
    "analysis":{
        "akasanpei": False,
        "kurosanpei": False,
    },

    # オーダー（注文）管理
    "order":{ 
        "exist": False,
        "side": "",
        "count": 0  # キャンセルのためのカウント
    },

    # ポジション（建玉）管理
    "position":{    
        "exist": False,
        "side": ""
    }
}

close_time = ""     # 時間管理用

while True:

    ohlcv = functions.get_ohlcv(period)
    
    if ohlcv[0]["close_time"] != close_time:
        functions.show_ohlcv(ohlcv)

        if not status["position"]["exist"]: # ポジションを持っていなかったら
            status = functions.buy_signal(status, ohlcv) # 買いシグナルチェック
            status = functions.sell_signal(status, ohlcv) # 売りシグナルチェック
            functions.place_order(status, ohlcv) # シグナルに基づき注文を出す

        if status["order"]["exist"]:        # オーダーを出していたら
            status = functions.check_order(status)  # 約定チェック

        if status["position"]["exist"]:              # ポジションを持っていたら
            status = functions.settlement_position(status, ohlcv)    # 清算チェック

    close_time = ohlcv[0]["close_time"]
    time.sleep(10)


# ↓↓テスト運用↓↓

# for i in reversed(range(300)):  # 新しいデータが入ってきていると仮定
#     functions.show_ohlcv(ohlcv, i)

#     if not status["position"]["exist"]: # ポジションを持っていなかったら
#         status = functions.buy_signal(status, ohlcv, i) # 買いシグナルチェック
#         status = functions.sell_signal(status, ohlcv, i) # 売りシグナルチェック
#         functions.place_order(status, ohlcv, i) # シグナルに基づき注文を出す


#     if status["order"]["exist"]:        # オーダーを出していたら
#         status = functions.check_order(status)  # 約定チェック
    
#     if status["position"]["exist"]:              # ポジションを持っていたら
#         status = functions.settlement_position(status, ohlcv, i)    # 清算チェック
    
#     time.sleep(0.01)
