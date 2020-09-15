# coding: utf-8
import functions
import time
import sys

status = {
    "lot": 0.01,

    "buy_signal": False, 
    "sell_signal": False,

    # テクニカル分析（ここに手法を増やしていく）
    "analysis_entry": {
        "buy": {
            "akasanpei": True,
            "donchan_breakout": True,
            "opening range breakout": True
        },

        "sell": {
            "kurosanpei": True,
            "donchan_breakout": True,
            "opening range breakout": True
        }
    },

    "analysis_close": {
        "close_price": False, 
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

    "backtest": False
}

# ローソク足の設定
period = 60   # 1m=60，1h=3600，1d=86400

if len(sys.argv) == 1:
    print("取引モードで起動します")
elif len(sys.argv) == 2:
    if sys.argv[1] == "backtest":
        print("バックテストモードで起動します")
        status["backtest"] = True
    else:
        print("要求されたコマンドはありません")
        print("プログラムを終了します")
        sys.exit()
else:
    print("引数オーバーです")
    print("プログラムを終了します")
    sys.exit()

# マーケットチェック関数
def __check_market(status, ohlcv):
    if not status["position"]["exist"]:                         # ポジションを持っていなかったら
        status = functions.buy_signal(status, ohlcv)            # 買いシグナルチェック
        status = functions.sell_signal(status, ohlcv)           # 売りシグナルチェック
        status = functions.place_order(status, ohlcv)           # シグナルに基づき注文を出す

    if status["order"]["exist"]:                                # オーダーを出していたら
        status = functions.check_order(status)                  # 約定チェック

    if status["position"]["exist"]:                             # ポジションを持っていたら
        status = functions.settlement_position(status, ohlcv)   # 清算チェック
    
    return status

# 取引モード
if not status["backtest"]:
    close_time = ""     # 時間管理用
    while True:

        ohlcv = functions.get_ohlcv(period)

        if ohlcv[0]["close_time"] != close_time:
            functions.show_ohlcv(ohlcv)
            status = __check_market(status, ohlcv)
        close_time = ohlcv[0]["close_time"]
        time.sleep(10)


# バックテストモード
else:
    # 過去6000件データ取得
    ohlcv_all = functions.get_ohlcv(period, after=1514764800) 

    i = 0
    while 0 <= len(ohlcv_all) - (i + 500):
        ohlcv = ohlcv_all[len(ohlcv_all) - (i + 500) : len(ohlcv_all) - i]
        functions.show_ohlcv(ohlcv)
        status = __check_market(status, ohlcv)
        i+=1

    print("--------------------------")
    print("開始データ : " + ohlcv_all[-1]["close_time_dt"] + "  UNIX時間 : " + str(ohlcv_all[-1]["close_time"]))
    print("終了データ : " + ohlcv_all[0]["close_time_dt"] + "  UNIX時間 : " + str(ohlcv_all[0]["close_time"]))
    print("合計 ： " + str(len(ohlcv_all) ) + "件のローソク足データを取得")
    print("--------------------------")

    functions.backtest(status)