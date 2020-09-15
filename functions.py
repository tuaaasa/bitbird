# coding: utf-8
from datetime import datetime
import time
import gateway
import constrants
import slack
import numpy as np

REALBODY_RATE = 0.3
INCREASE_RATE = 0.0003
ORDER_BUY = "buy"
ORDER_SELL = "sell"

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

    data = gateway.get_ohlcv_from_cryptowatch(params)

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
def show_all_ohlcv(ohlcv_data_list):
    for i in ohlcv_data_list:
        print("UNIX時間：" + str(i["close_price"])
              + " 　時間：" + str(i["close_time_dt"])
              + " 　始値：" + str(i["open_price"])
              + " 　高値：" + str(i["high_price"])
              + " 　安値：" + str(i["low_price"])
              + " 　終値：" + str(i["close_price"])
              + " 　出来高：" + str(i["volume"])
              )


# 陽線陰線チェック関数
def __isPositive(ohlcv_data):
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
def __isAscend(ohlcv_data, last_ohlcv_data):
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
def __isDescend(ohlcv_data, last_ohlcv_data):
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
def __check_candle(ohlcv_data, order_type):
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
def __check_akasanpei(ohlcv_data_list, n=0):
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
        # return __isPositive(ohlcv_data) and __check_candle(ohlcv_data, ORDER_BUY)
        return __isPositive(ohlcv_data)

    # 形成中のローソクは加味しないのでohlcv_data[n+0]は使わない
    if all(isPositiveCandle(v) for v in target_ohlcv_data_list) and __isAscend(ohlcv_data_list[n+1], ohlcv_data_list[n+2]) and __isAscend(ohlcv_data_list[n+2], ohlcv_data_list[n+3]):
        return True
    else:
        return False


# 黒三兵による売りサイン
def __check_kurosannpei(ohlcv_data_list, n=0):
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
        # return not __isPositive(ohlcv_data) and __check_candle(ohlcv_data, ORDER_SELL)
        return not __isPositive(ohlcv_data)

    # 形成中のローソクは加味しないのでohlcv_data[n+0]は使わない
    if all(isNegativeCandle(v) for v in target_ohlcv_data_list) and __isDescend(ohlcv_data_list[n+1], ohlcv_data_list[n+2]) and __isDescend(ohlcv_data_list[n+2], ohlcv_data_list[n+3]):
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
    if __check_akasanpei(ohlcv_data_list, begin):
        status["buy_signal"] = True
        print(
            "赤三兵 " + str(ohlcv_data_list[begin+1]["close_price"]) + "で買いを入れます")
    return status


# SELLシグナルをチェックする関数
def sell_signal(status, ohlcv_data_list, begin=0):
    """
    【返り値】
    status（リスト型）
    シグナル発生：status[order] True
    シグナルなし：status[order]: Flase
    """
    # 黒三兵
    if __check_kurosannpei(ohlcv_data_list, begin):
        status["sell_signal"] = True
        print(
            "黒三兵 " + str(ohlcv_data_list[begin+1]["close_price"]) + "で売りを入れます")
    return status


# 注文を出す関数
# TODO 両方のシグナルが発生した場合はどうする？
def place_order(status, ohlcv_data_list):
    if status["buy_signal"]:
        # BitFlyerに買いオーダーを出す
        gateway.private_order_by_limit(
            'buy', ohlcv_data_list[1]["close_price"], status["lot"], status["backtest"])  # 赤三兵用．[1]で1個前の終値を利用している
        status["order"]["exist"] = True
        status["order"]["side"] = "BUY"
        status["order"]["price"] = round(ohlcv_data_list[1]["close_price"] * status["lot"])

    if status["sell_signal"]:
        # BitFlyerに売りオーダーを出す
        gateway.private_order_by_limit(
            'sell', ohlcv_data_list[1]["close_price"], status["lot"], status["backtest"])  # 黒三兵用．[1]で1個前の終値を利用している
        status["order"]["exist"] = True
        status["order"]["side"] = "SELL"
        status["order"]["price"] = round(ohlcv_data_list[1]["close_price"] * status["lot"])

    # シグナル初期化
    status["buy_signal"] = False
    status["sell_signal"] = False
    return status


# 注文が約定したか確認する関数
def check_order(status):

    position = gateway.private_get_positions(status["backtest"])
    orders = gateway.private_get_orders(status["backtest"])

    if position:
        text = "注文が約定しました"
        print(text)
        slack.info(constrants.NotificationTitle.Position.value, text, status["backtest"])
        status["order"]["exist"] = False
        status["order"]["count"] = 0
        status["position"]["exist"] = True
        status["position"]["side"] = status["order"]["side"]
        status["position"]["price"] = status["order"]["price"]
        status["order"]["side"] = ""  # オーダーサイドを初期化

    else:
        if orders:
            print("未約定の注文があります")
            for o in orders:
                print(o["id"])  # 未約定注文一覧表示
            status["order"]["count"] += 1
            if status["order"]["count"] > 6:
                status = __cancel_order(orders, status)    # 時間経過によるキャンセル処理
        else:
            print("注文が遅延しているようです")     # BitFlyerの反映遅延対策

    return status


def __cancel_order(orders, status):

    gateway.private_cancel_all_orders(orders, status["backtest"])
    print("約定しなかった注文をキャンセルしました")
    status["order"]["count"] = 0
    status["order"]["exist"] = False

    # 通信スレ違いで約定する可能があるため20秒後に再度確認
    print("20秒後に，注文が約定していないかを再確認します")
    time.sleep(20)
    position = gateway.private_get_positions(status["backtest"])
    if not position:
        print("現在，ポジションはありません")
    else:
        print("現在，ポジションがあります")
        status["position"]["exist"] = True
        status["position"]["side"] = position[0]["side"]

    return status


# ポジジョンを清算するか関数
def settlement_position(status, ohlcv_data_list, begin=0):

    if status["position"]["side"] == "BUY":
        if ohlcv_data_list[begin]["close_price"] < ohlcv_data_list[begin+1]["close_price"]:
            print("前回の終値を下回ったので" +
                  str(ohlcv_data_list[begin]["close_price"]) + "あたりで成行決済します")
            gateway.private_order_by_market('sell', status["lot"], status["backtest"])       # BitFlyerに売りの清算注文を出す
            __record_trade(status, ohlcv_data_list)
            status["position"]["exist"] = False

    if status["position"]["side"] == "SELL":
        if ohlcv_data_list[begin]["close_price"] > ohlcv_data_list[begin+1]["close_price"]:
            print("前回の終値を上回ったので" +
                  str(ohlcv_data_list[begin]["close_price"]) + "あたりで成行決済します")
            gateway.private_order_by_market('buy', status["lot"], status["backtest"])        # BitFlyerに買いの清算注文を出す
            status["position"]["exist"] = False
            __record_trade(status, ohlcv_data_list)
    gateway.private_get_collateral(status["backtest"])
    
    return status


# 各トレードのパフォーマンスを記録する関数
def __record_trade(status, ohlcv_data_list):
    slippage = 0.0 # スリッページの設定

	# 取引手数料等の計算
    entry_price = status["position"]["price"]
    exit_price = round(ohlcv_data_list[0]["close_price"] * status["lot"])
    trade_cost = round( exit_price * slippage )
    
    print("スリッページ・手数料として " + str(trade_cost) + "円を考慮します\n")
    status["records"]["slippage"].append(trade_cost)

    # 値幅の計算
    buy_profit = exit_price - entry_price - trade_cost
    sell_profit = entry_price - exit_price - trade_cost
    

    # 利益が出てるかの計算
    if status["position"]["side"] == "BUY":
        status["records"]["buy-count"] += 1
        status["records"]["buy-profit"].append( buy_profit )
        status["records"]["buy-return"].append( round( buy_profit / entry_price * 100, 4 ))
        if buy_profit  > 0:
            status["records"]["buy-winning"] += 1
            print(str(buy_profit) + "円の利益です\n")
        else:
            print(str(buy_profit) + "円の損失です\n")

    if status["position"]["side"] == "SELL":
        status["records"]["sell-count"] += 1
        status["records"]["sell-profit"].append( sell_profit )
        status["records"]["sell-return"].append( round( sell_profit / entry_price * 100, 4 ))
        if sell_profit > 0:
            status["records"]["sell-winning"] += 1
            print(str(sell_profit) + "円の利益です\n")
        else:
            print(str(sell_profit) + "円の損失です\n")    
    return status


# バックテストの集計用の関数
def backtest(status):
	
	buy_gross_profit = np.sum(status["records"]["buy-profit"])
	sell_gross_profit = np.sum(status["records"]["sell-profit"])
	
	print("バックテストの結果")
	print("--------------------------")
	print("買いエントリの成績")
	print("--------------------------")
	print("トレード回数  :  {}回".format(status["records"]["buy-count"] ))
	print("勝率          :  {}％".format(round(status["records"]["buy-winning"] / status["records"]["buy-count"] * 100,1)))
	print("平均リターン  :  {}％".format(round(np.average(status["records"]["buy-return"]),4)))
	print("総損益        :  {}円".format( np.sum(status["records"]["buy-profit"]) ))
	
	print("--------------------------")
	print("売りエントリの成績")
	print("--------------------------")
	print("トレード回数  :  {}回".format(status["records"]["sell-count"] ))
	print("勝率          :  {}％".format(round(status["records"]["sell-winning"] / status["records"]["sell-count"] * 100,1)))
	print("平均リターン  :  {}％".format(round(np.average(status["records"]["sell-return"]),4)))
	print("総損益        :  {}円".format( np.sum(status["records"]["sell-profit"]) ))
	
	print("--------------------------")
	print("総合の成績")
	print("--------------------------")
	print("総損益        :  {}円".format( np.sum(status["records"]["sell-profit"]) + np.sum(status["records"]["buy-profit"]) ))
	print("手数料合計    :  {}円".format( np.sum(status["records"]["slippage"]) ))