# coding: utf-8
import ccxt
import time
import requests

bitflyer = ccxt.bitflyer()
# TODO 外部ファイルから読み込むようにする(json形式)
bitflyer.apiKey = 'XXX'
bitflyer.secret = 'XXX'

# CryptWatchへのアクセス関数
def get_ohlcv_from_cryptowatch(params):
    while True:
        try:
            response = requests.get("https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc", params)  # TODO APIアクセス制限ある
            data = response.json()  # [取引時間（close time），始値(open price)，高値(hogh price)，安値(low price)，終値(close price)，出来高(volume)]
            return data

        # CryptWatchからのデータ取得失敗時
        except requests.exceptions.RequestException as e:
            print("CryptWatchからOHLCVデータの取得に失敗しました: ", e)
            print("10秒後，再度実行します")
            time.sleep(10)  


# 成行注文
def private_order_by_market(side, amount):
    while True:
        try:
            order = bitflyer.create_order(
                symbol = 'BTC/JPY',
                type= 'market', 
                side= side,
                amount= amount,
                params = { "product_code" : "FX_BTC_JPY" })
            print(side + " の成行注文を出しました")
            time.sleep(10)      # APIの注文反映待ち
            break
        
        except ccxt.BaseError as e:
            print("BitFlyerのAPIエラー発生", e)
            print("注文が失敗しました．10秒後に再度実行します")
            time.sleep(10)

# 指値注文
def private_order_by_limit(side, plice, amount):
    while True:
        try:
            print("指値価格: " + str(plice))
            order = bitflyer.create_order(
                symbol = 'BTC/JPY',
                type= 'limit', 
                side= side,
                price= plice,
                amount= amount,
                params = { "product_code" : "FX_BTC_JPY" })
            print("価格" + str(plice)  + "で " + side + " の指値注文を出しました")
            time.sleep(10)      # APIの注文反映待ち
            break
        
        except ccxt.BaseError as e:
            print("BitFlyerのAPIエラー発生", e)
            print("注文が失敗しました．10秒後に再度実行します")
            time.sleep(10)
            

# BitFlyerにポジションを確認する関数
def private_get_getpositions():
    return bitflyer.private_get_getpositions(params = { "product_code" : "FX_BTC_JPY" })    # BitFlyerにポジションを確認

# BitFlyerにオーダーを確認する関数
def private_get_orders():
    return bitflyer.fetch_open_orders(symbol = "BTC/JPY", params = { "product_code" : "FX_BTC_JPY" })     #BitFlyerに注文を確認

# BitFlyerの全てのオーダーをキャンセルする関数
def private_cancel_all_orders(orders):
    for o in orders:
        bitflyer.cancel_order(
            symbol = "BTC/JPY",
			id = o["id"],
			params = { "product_code" : "FX_BTC_JPY" }
        )