# coding: utf-8
import ccxt
import time
import requests
import config
import constrants
import slack

bitflyer = ccxt.bitflyer()
bitflyer.apiKey = config.BITFLYER['API_KEY']
bitflyer.secret = config.BITFLYER['SECRET']

ERROR_COUNT = 3


def get_ohlcv_from_cryptowatch(params):
    i = 0
    while True:
        try:
            response = requests.get(
                "https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc",
                params
            )  # TODO APIアクセス制限ある
            # [取引時間（close time），始値(open price)，高値(hogh price)，安値(low price)，終値(close price)，出来高(volume)]
            data = response.json()
            return data

        # CryptWatchからのデータ取得失敗時
        except requests.exceptions.RequestException as e:
            i += 1
            if i == ERROR_COUNT:
                slack.error(constrants.NotificationTitle.Error.value, e)
                raise e
            print("CryptWatchからOHLCVデータの取得に失敗しました: ", e)
            print("10秒後，再度実行します")
            time.sleep(10)


# 成行注文
def private_order_by_market(side, amount, backtest):
    if not backtest:
        i = 0
        while True:
            try:
                order = bitflyer.create_order(
                    symbol='BTC/JPY',
                    type='market',
                    side=side,
                    amount=amount,
                    params={"product_code": "FX_BTC_JPY"}
                )
                text = side + " の成行決済注文を出しました"
                print(text)
                slack.info(constrants.NotificationTitle.Settlement.value, text, backtest)
                time.sleep(10)      # APIの注文反映待ち
                break

            except ccxt.BaseError as e:
                i += 1
                if i == ERROR_COUNT:
                    slack.error(constrants.NotificationTitle.Error.value, e, backtest)
                    raise e
                print("BitFlyerのAPIエラー発生", e)
                print("注文が失敗しました．10秒後に再度実行します")
                time.sleep(10)
    else:
        print(side + " の成行決済注文を出しました")


# 指値注文
def private_order_by_limit(side, plice, amount, backtest):
    if not backtest: 
        i = 0
        while True:
            try:
                print("指値価格: " + str(plice))
                order = bitflyer.create_order(
                    symbol='BTC/JPY',
                    type='limit',
                    side=side,
                    price=plice,
                    amount=amount,
                    params={"product_code": "FX_BTC_JPY"}
                )
                text = "価格" + str(plice) + "で " + side + " の指値注文を出しました"
                print(text)
                slack.info(constrants.NotificationTitle.Order.value, text, backtest)
                time.sleep(10)      # APIの注文反映待ち
                break

            except ccxt.BaseError as e:
                i += 1
                if i == ERROR_COUNT:
                    slack.error(constrants.NotificationTitle.Error.value, e, backtest)
                    raise e
                print("BitFlyerのAPIエラー発生", e)
                print("注文が失敗しました．10秒後に再度実行します")
                time.sleep(10)
    else:
        print("価格" + str(plice) + "で " + side + " の指値注文を出しました")


# BitFlyerにポジションを確認する関数
def private_get_positions(backtest):
    if not backtest:
        # BitFlyerにポジションを確認
        return bitflyer.private_get_getpositions(params={"product_code": "FX_BTC_JPY"})
    else:
        return True


# BitFlyerにオーダーを確認する関数


def private_get_orders(backtest):
    if not backtest:
        # BitFlyerに注文を確認
        return bitflyer.fetch_open_orders(symbol="BTC/JPY", params={"product_code": "FX_BTC_JPY"})
    else:
        return True


# BitFlyerに担保を確認する関数
def private_get_collateral(backtest):
    if not backtest:
        # BitFlyerに担保を確認
        collateral = bitflyer.private_get_getcollateral()
        text = "預入証拠金: " + str(collateral["collateral"])\
        + "\n建玉評価損益: " + str(collateral["open_position_pnl"])\
        + "\n現在の必要証拠金: " + str(collateral["require_collateral"])\
        + "\n証拠金維持率: " + str(collateral["keep_rate"])
        print(text)
        slack.info(constrants.NotificationTitle.Info.value, text, backtest)
    else:
        return True


# BitFlyerの全てのオーダーをキャンセルする関数
def private_cancel_all_orders(orders, backtest):
    if not backtest:
        text = "以下の注文をキャンセルしました\n"
        for o in orders:
            bitflyer.cancel_order(
                symbol="BTC/JPY",
                id=o["id"],
                params={"product_code": "FX_BTC_JPY"}
            )
            text += str(o["id"]) + "\n"
        slack.info(constrants.NotificationTitle.OrderCancel.value, text, backtest)
    else:
        return