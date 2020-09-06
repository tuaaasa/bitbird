# coding: utf-8
import requests
from datetime import datetime
import time
import slackweb
# デバッグ用
# response = requests.get("https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc",params = { "periods" : 60 })
# CryptowatchからOHLCV取得

slack = slackweb.Slack(
    "https://hooks.slack.com/services/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")


def get_ohlcv(candle, period):
    """
    candle：何本前のローソク（現在なら0を入れる）
    period：足のレンジ（1m=60，1h=3600，1d=86400）
    returnデータ [取引時間（close time），始値(open price)，高値(hogh price)，安値(low price)，終値(close price)，出来高(volume)]
    """
    # APIで価格を取得する
    # 与えられた引数（ローソク足）のOHLCV取得
    response = requests.get(
        "https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc", params={"periods": period})
    data = response.json()
    # 指定されたローソクのOHLCVを取得
    ohlcv = data["result"][str(period)][-(candle+1)]
    return{
        "close_time": ohlcv[0],
        "open_price": ohlcv[1],
        "high_price": ohlcv[2],
        "low_price": ohlcv[3],
        "close_price": ohlcv[4],
        "volume": ohlcv[5]
    }
# OHLCV表示関数


def show_ohlcv(ohlcv_data):
    return "時間： " + datetime.fromtimestamp(ohlcv_data["close_time"]).strftime('%Y/%m/%d %H:%M')\
        + "\n始値： " + str(ohlcv_data["open_price"])\
        + "\n高値： " + str(ohlcv_data["high_price"])\
        + "\n安値： " + str(ohlcv_data["low_price"])\
        + "\n終値： " + str(ohlcv_data["close_price"])\
        + "\n出来高： " + str(ohlcv_data["volume"])\

# 陽線陰線チェック関数


def check_positive(ohlcv_data):
    """
    陽線：True
    陰線：False
    """
    if ohlcv_data["close_price"] > ohlcv_data["open_price"]:
        return True
    else:
        return False
# 上昇チェック関数


def check_ascend(ohlcv_data, last_ohlcv_data):
    """
    【条件】
    （始値＞前の始値）かつ（終値＞前の終値）
    """
    if ohlcv_data["open_price"] > last_ohlcv_data["open_price"] and ohlcv_data["close_price"] > last_ohlcv_data["close_price"]:
        return True
    else:
        return False
# 赤三兵による買いサイン


def check_akasanpei(ohlcv_data_1, ohlcv_data_2, ohlcv_data_3):
    """
    【条件】
    1．3足連続で（終値＞始値）の足が続いている．
    2．3回連続で始値と終値が前の足より上昇している．
    【引数】
    ohlcv_data_1：1つ前のローソク．
    ohlcv_data_2：2つ前のローソク．
    ohlcv_data_3：3つ前のローソク．
    """
    if check_positive(ohlcv_data_1) and check_positive(ohlcv_data_2) and check_positive(ohlcv_data_3) and check_ascend(ohlcv_data_1, ohlcv_data_2) and check_ascend(ohlcv_data_2, ohlcv_data_3):
        return True
    else:
        return False


# 黒三兵による売りサイン（未実装）
# def check_kurosannpei(ohlcv_data_0, ohlcv_data_1, ohlcv_data_2):
# ここからがメイン処理
# 最終的な注文を行う
while True:
    ohlcv_0 = get_ohlcv(0, 60)
    ohlcv_1 = get_ohlcv(1, 60)
    ohlcv_2 = get_ohlcv(2, 60)
    ohlcv_3 = get_ohlcv(3, 60)
    if check_akasanpei(ohlcv_1, ohlcv_2, ohlcv_3):
        slack.notify(text=show_ohlcv(ohlcv_0))
    else:
        print("スルー")
    time.sleep(0)