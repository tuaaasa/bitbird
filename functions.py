# coding: utf-8
import requests
from datetime import datetime
import time
import ccxt

REALBODY_RATE = 0.3
INCREASE_RATE = 0.0003
ORDER_BUY = "buy"
ORDER_SELL = "sell"

# TODO ここに入れたくはない
bitflyer = ccxt.bitflyer()
bitflyer.apiKey = 'SZz2PtRTJDU8e6RPA9dp5r'
bitflyer.secret = 'fkhxWqnEoj6m4QyzTzfhO5X+bSml6DCu3N/uhMHyIkM='


# OHLCVデータ取得関数
def get_ohlcv(period, before=0, after=0):
    """
    period: 時間足（1m=60，1h=3600，1d=86400）
    before: 開始位置
    after: 終了位置
    ※before = after = 0 なら直近500件データ取得

    【返り値】
    OHLCVデータ（リスト型，新しいデータが先頭）
    [UNIX取引時間（close time），取引時間（close time dt），始値(open price)，高値(hogh price)，安値(low price)，終値(close price)，出来高(volume)]
    """
    ohlcv = []
    params = {"periods": period}
    if before != 0:
        params["before"] = before
    if after != 0:
        params["after"] = after
    response = requests.get(
        "https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc", params)  # TODO APIアクセス制限ある
    data = response.json()

    # [取引時間（close time），始値(open price)，高値(hogh price)，安値(low price)，終値(close price)，出来高(volume)]
    if data["result"][str(period)] is not None:
        for i in data["result"][str(period)]:
            ohlcv.insert(0, {"close_time": i[0],
                             "close_time_dt": datetime.fromtimestamp(i[0]).strftime('%Y/%m/%d %H:%M'),
                             "open_price": i[1],
                             "high_price": i[2],
                             "low_price": i[3],
                             "close_price": i[4],
                             "volume": i[5]})
    return ohlcv


# OHLCV表示関数
def show_ohlcv(ohlcv_data, begin=0, num=1):
    """
    ohlcv_data: リスト型OHLCVデータ
    begin: 開始位置
    num: 表示個数
    """
    for i in range(begin, begin + num):
        print("UNIX時間：" + str(ohlcv_data[i]["close_time"])
              + " 　時間：" + str(ohlcv_data[i]["close_time_dt"])
              + " 　始値：" + str(ohlcv_data[i]["open_price"])
              + " 　高値：" + str(ohlcv_data[i]["high_price"])
              + " 　安値：" + str(ohlcv_data[i]["low_price"])
              + " 　終値：" + str(ohlcv_data[i]["close_price"])
              + " 　出来高：" + str(ohlcv_data[i]["volume"])
              )


# 全てのOHLCV表示関数
def show_all_ohlcv(ohlcv_data):
    """
    ohlcv_data: リスト型OHLCVデータ
    """
    for i in ohlcv_data:
        print("UNIX時間：" + str(i["close_price"])
              + " 　時間：" + str(i["close_time_dt"])
              + " 　始値：" + str(i["open_price"])
              + " 　高値：" + str(i["high_price"])
              + " 　安値：" + str(i["low_price"])
              + " 　終値：" + str(i["close_price"])
              + " 　出来高：" + str(i["volume"])
              )


# 陽線陰線チェック関数
def isPositive(ohlcv_data):
    """
    【返り値】
    陽線：True
    陰線：False
    """
    if ohlcv_data["close_price"] > ohlcv_data["open_price"]:
        return True
    else:
        return False


# 上昇チェック関数
def isAscend(ohlcv_data, last_ohlcv_data):
    """
    【条件】
    （始値＞前の始値）かつ（終値＞前の終値）→ 上昇
    （始値＜前の始値）かつ（終値＜前の終値）→ 下降
    【返り値】
    上昇：True
    それ以外：Flase
    """
    if ohlcv_data["open_price"] > last_ohlcv_data["open_price"] and ohlcv_data["close_price"] > last_ohlcv_data["close_price"]:
        return True
    else:
        return False


# 下降チェック関数
def isDescend(ohlcv_data, last_ohlcv_data):
    """
    【条件】
    （始値＞前の始値）かつ（終値＞前の終値）→ 上昇
    （始値＜前の始値）かつ（終値＜前の終値）→ 下降
    【返り値】
    下降：Flase
    それ以外：True
    """
    if ohlcv_data["open_price"] < last_ohlcv_data["open_price"] and ohlcv_data["close_price"] < last_ohlcv_data["close_price"]:
        return True
    else:
        return False


# ろうそくの大きさ判定
def check_candle(ohlcv_data, order_type):
    realbody_rate = abs(ohlcv_data["close_price"] - ohlcv_data["open_price"]) / (
        ohlcv_data["high_price"]-ohlcv_data["low_price"])
    increase_rate = (ohlcv_data["close_price"] / ohlcv_data["open_price"])-1

    if order_type == ORDER_BUY:
        if ohlcv_data["close_price"] < ohlcv_data["open_price"] or increase_rate < INCREASE_RATE or realbody_rate < REALBODY_RATE:
            return False
        else:
            return True

    if order_type == ORDER_SELL:
        if ohlcv_data["close_price"] > ohlcv_data["open_price"] or increase_rate > -INCREASE_RATE or realbody_rate < REALBODY_RATE:
            return False
        else:
            return True


# 赤三兵による買いサイン
def check_akasanpei(ohlcv_data_list, n=0):
    """
    【条件】
    1．3足連続で（終値＞始値）の足が続いている．
    2．3回連続で始値と終値が前の足より上昇している．
    【引数】
    ohlcv_data: リスト型OHLCVデータ．
    n: 確認する足（指定しなければ現状況）
    【返り値】
    シグナル発生：True．
    シグナルなし：False．
    """
    target_ohlcv_data_list = [ohlcv_data_list[i+1] for i in range(
        n, n+3)]  # [ohlcv_data_list[n+1], ohlcv_data_list[n+2], ohlcv_data_list[n+3]]

    def isPositiveCandle(ohlcv_data):
        return isPositive(ohlcv_data) and check_candle(ohlcv_data, ORDER_BUY)

    # 形成中のローソクは加味しないのでohlcv_data[n+0]は使わない
    # https://qiita.com/l_v_yonsama/items/07e754193ed88ed0baaf#%E9%85%8D%E5%88%97%E3%81%AE%E3%81%99%E3%81%B9%E3%81%A6%E3%81%AE%E8%A6%81%E7%B4%A0%E3%81%8C%E9%80%9A%E3%82%8B%E3%81%8B%E3%81%A9%E3%81%86%E3%81%8B%E3%82%92%E3%83%86%E3%82%B9%E3%83%88
    if all(isPositiveCandle(v) for v in target_ohlcv_data_list) and isAscend(ohlcv_data_list[n+1], ohlcv_data_list[n+2]) and isAscend(ohlcv_data_list[n+2], ohlcv_data_list[n+3]):
        return True
    else:
        return False


# 黒三兵による売りサイン
def check_kurosannpei(ohlcv_data_list, n=0):
    """
    【条件】
    1．3足連続で（終値＜始値）の足が続いている．
    2．3回連続で始値と終値が前の足より下降している．
    【引数】
    ohlcv_data: リスト型OHLCVデータ．
    n: 確認する足（指定しなければ現状況）
    【返り値】
    シグナル発生：True．
    シグナルなし：False．
    """
    target_ohlcv_data_list = [ohlcv_data_list[i+1] for i in range(n, n+3)]

    def isNegativeCandle(ohlcv_data):
        return not isPositive(ohlcv_data) and check_candle(ohlcv_data, ORDER_SELL)

    # 形成中のローソクは加味しないのでohlcv_data[n+0]は使わない
    if all(isNegativeCandle(v) for v in target_ohlcv_data_list) and isDescend(ohlcv_data_list[n+1], ohlcv_data_list[n+2]) and isDescend(ohlcv_data_list[n+2], ohlcv_data_list[n+3]):
        return True
    else:
        return False


# BUYシグナルをチェックする関数
def buy_signal(status, ohlcv_data_list, begin=0):
    """
    【返り値】
    status（リスト型）
    シグナル発生：status[order] True
    シグナルなし：status[order]: Flase
    """
    # 赤三兵
    if check_akasanpei(ohlcv_data_list, begin):
        status["buy_signal"] = True
        print("赤三兵 " + str(ohlcv_data_list[begin+1]["close_price"]) + "で買いを入れます")

    return status


# BUYシグナルをチェックする関数
def sell_signal(status, ohlcv_data_list, begin=0):
    """
    【返り値】
    status（リスト型）
    シグナル発生：status[order] True
    シグナルなし：status[order]: Flase
    """
    # 黒三兵
    if check_kurosannpei(ohlcv_data_list, begin):
        status["sell_signal"] = True
        print("黒三兵 " + str(ohlcv_data_list[begin+1]["close_price"]) + "で売りを入れます")

    return status


# 注文を出す関数
# TODO 両方のシグナルが発生した場合はどうする？
def place_order(status, ohlcv_data_list):
    if status["buy_signal"]:

        # BitFlyerに買いオーダーを出す
        order = bitflyer.create_order(
				symbol = 'BTC/JPY',
				type='market',          #成行注文 
				side='buy',
				amount='0.01',
				params = { "product_code" : "FX_BTC_JPY" })
        print(str(ohlcv_data_list[0]["close_price"]) + "で買いの成行注文を出しました")
        status["order"]["exist"] = True
        status["order"]["side"] = "BUY"

    if status["sell_signal"]:

        # BitFlyerに売りオーダーを出す
        order = bitflyer.create_order(
				symbol = 'BTC/JPY',
				type='market',          #成行注文 
				side='sell',
				amount='0.01',
				params = { "product_code" : "FX_BTC_JPY" })
        print(str(ohlcv_data_list[0]["close_price"]) + "で売りの成行注文を出しました")
        status["order"]["exist"] = True
        status["order"]["side"] = "SELL"

    # シグナル初期化
    status["buy_signal"] = False
    status["sell_signal"] = False
    return status


# 注文が約定したか確認する関数
def check_order(status):
    
    position = bitflyer.private_get_getpositions(params = { "product_code" : "FX_BTC_JPY" })    # BitFlyerにポジションを確認
    orders = bitflyer.fetch_open_orders(symbol = "BTC/JPY", params = { "product_code" : "FX_BTC_JPY" })     #BitFlyerに注文を確認 

    if position:
        print("注文が約定しました")
        status["order"]["exist"] = False
        status["position"]["exist"] = True
        status["position"]["side"] = status["order"]["side"]
        status["order"]["side"] = ""    #オーダーサイドを初期化
    else:
        if orders:
            print("未約定の注文があります")
            for o in orders:
                print(o["id"])  # 未約定注文一覧表示
            status["order"]["count"] += 1
            if status["order"]["count"] > 6:
                status = cancel_order(orders, status)    # 時間経過によるキャンセル処理
        else:
            print("注文が遅延しているようです")     # BitFlyerの反映遅延対策

    return status


def cancel_order(orders, status):
    
    for o in orders:
        bitflyer.cancel_order(
            symbol = "BTC/JPY",
			id = o["id"],
			params = { "product_code" : "FX_BTC_JPY" }
        )
    print("約定しなかった注文をキャンセルしました")
    status["order"]["count"] = 0
    status["order"]["exist"] = False

    # 通信スレ違いで約定する可能があるため20秒後に再度確認
    print("20秒後に，再度注文が約定していないかを確認します")
    time.sleep(20)
    position = bitflyer.private_get_getpositions( params = { "product_code" : "FX_BTC_JPY" })
    if not position:
        print("現在，未決済のポジションはありません")
    else:
        print("現在，まだ未決済のポジションがあります")
        status["position"]["exist"] = True
        status["position"]["side"] = position[0]["side"]
    
    return status
        

# ポジジョンを清算するか関数
# この実装では清算戦略を立てづらい 清算シグナルとsettlementを関数で分けるか
# これでは清算のオーダーが通ったか確認できない（成行注文だからいいのか？）
def settlement_position(status, ohlcv_data_list, begin=0):

    if status["position"]["side"] == "BUY":
        if ohlcv_data_list[begin]["close_price"] < ohlcv_data_list[begin+1]["close_price"]:
            print("前回の終値を下回ったので" + str(ohlcv_data_list[begin]["close_price"]) + "あたりで成行決済します")

            # BitFlyerに清算注文を出す
            order = bitflyer.create_order(
				symbol = 'BTC/JPY',
				type='market',
				side='sell',
				amount='0.01',
				params = { "product_code" : "FX_BTC_JPY" })

            status["position"]["exist"] = False
            status["position"]["side"] = ""

    if status["position"]["side"] == "SELL":
        if ohlcv_data_list[begin]["close_price"] > ohlcv_data_list[begin+1]["close_price"]:
            print("前回の終値を上回ったので" + str(ohlcv_data_list[begin]["close_price"]) + "あたりで成行決済します")

            # BitFlyerに清算注文を出す
            order = bitflyer.create_order(
				symbol = 'BTC/JPY',
				type='market',
				side='buy',
				amount='0.01',
				params = { "product_code" : "FX_BTC_JPY" })

            status["position"]["exist"] = False
            status["position"]["side"] = ""

    return status