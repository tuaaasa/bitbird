# 過去データ6000件を用いてバックテストを行うプログラム

# coding: utf-8
import functions
import time


# バックテスト用パラメータ
period = 60   # 1m=60，5m=300, 1h=3600，1d=86400


status = {
    "lot": 0.01,

    "buy_signal": False,    # TODO 今後重みを表す数値にしたい
    "sell_signal": False,

    # テクニカル分析（ここに手法を増やしていく）
    "analysis": {
        "akasanpei": False,
        "kurosanpei": False,
    },

    # オーダー（注文）管理
    "order": {
        "exist": False,
        "side": "",
        "price" : 0,
        "count": 0  # キャンセルのためのカウント
    },

    # ポジション（建玉）管理
    "position": {
        "exist": False,
        "side": "",
        "price": 0,
    }, 

    # トレード記録
    "records":{
		"buy-count": 0,
		"buy-winning" : 0,
		"buy-return":[],
		"buy-profit": [],
		
		"sell-count": 0,
		"sell-winning" : 0,
		"sell-return":[],
		"sell-profit":[],
		
		"slippage":[],
		"log":[]
	},

    "backtest": True
}

# 過去6000件データ取得
ohlcv_all = functions.get_ohlcv(period, after=1514764800) 

i = 0
while 0 <= len(ohlcv_all) - (i + 500):
    ohlcv = ohlcv_all[len(ohlcv_all) - (i + 500) : len(ohlcv_all) - i]
    functions.show_ohlcv(ohlcv)

    if not status["position"]["exist"]:  # ポジションを持っていなかったら
            status = functions.buy_signal(status, ohlcv)  # 買いシグナルチェック
            status = functions.sell_signal(status, ohlcv)  # 売りシグナルチェック
            status = functions.place_order(status, ohlcv)  # シグナルに基づき注文を出す

    if status["order"]["exist"]:        # オーダーを出していたら
            status = functions.check_order(status)  # 約定チェック

    if status["position"]["exist"]:              # ポジションを持っていたら
            status = functions.settlement_position(status, ohlcv)    # 清算チェック

    i+=1

print("--------------------------")
print("開始データ : " + ohlcv_all[-1]["close_time_dt"] + "  UNIX時間 : " + str(ohlcv_all[-1]["close_time"]))
print("終了データ : " + ohlcv_all[0]["close_time_dt"] + "  UNIX時間 : " + str(ohlcv_all[0]["close_time"]))
print("合計 ： " + str(len(ohlcv_all) ) + "件のローソク足データを取得")
print("--------------------------")

functions.backtest(status)
