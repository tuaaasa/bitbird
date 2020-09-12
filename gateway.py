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
                slack.error(constrants.NotificationTitle.Error, e)
                raise e
            print("CryptWatchからOHLCVデータの取得に失敗しました: ", e)
            print("10秒後，再度実行します")
            time.sleep(10)


# 成行注文
def private_order_by_market(side, amount):
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
            slack.info(constrants.NotificationTitle.Settlement, text)
            time.sleep(10)      # APIの注文反映待ち
            break

        except ccxt.BaseError as e:
            i += 1
            if i == ERROR_COUNT:
                slack.error(constrants.NotificationTitle.Error, e)
                raise e
            print("BitFlyerのAPIエラー発生", e)
            print("注文が失敗しました．10秒後に再度実行します")
            time.sleep(10)

# 指値注文


def private_order_by_limit(side, plice, amount):
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
            slack.info(constrants.NotificationTitle.Order, text)
            time.sleep(10)      # APIの注文反映待ち
            break

        except ccxt.BaseError as e:
            i += 1
            if i == ERROR_COUNT:
                slack.error(constrants.NotificationTitle.Error, e)
                raise e
            print("BitFlyerのAPIエラー発生", e)
            print("注文が失敗しました．10秒後に再度実行します")
            time.sleep(10)


# BitFlyerにポジションを確認する関数
def private_get_getpositions():
    # BitFlyerにポジションを確認
    return bitflyer.private_get_getpositions(params={"product_code": "FX_BTC_JPY"})

# BitFlyerにオーダーを確認する関数


def private_get_orders():
    # BitFlyerに注文を確認
    return bitflyer.fetch_open_orders(symbol="BTC/JPY", params={"product_code": "FX_BTC_JPY"})


# BitFlyerに担保を確認する関数
def private_get_getcollateral():
    # BitFlyerに担保を確認
    return bitflyer.private_get_getcollateral()

# BitFlyerの全てのオーダーをキャンセルする関数


def private_cancel_all_orders(orders):
    text = "以下の注文をキャンセルしました\n"
    for o in orders:
        bitflyer.cancel_order(
            symbol="BTC/JPY",
            id=o["id"],
            params={"product_code": "FX_BTC_JPY"}
        )
        text += o["id"] + "\n"
    slack.info(constrants.NotificationTitle.OrderCancel, text)
