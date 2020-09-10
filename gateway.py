# coding: utf-8
import ccxt
import time
import requests

bitflyer = ccxt.bitflyer()
# TODO 外部ファイルから読み込むようにする(json形式)
bitflyer.apiKey = 'XXX'
bitflyer.secret = 'XXX'

# CryptWatchへのアクセス関数
# TODO functionsからCryptWatchへのアクセスを分離


# BitFlyerへの注文
# TODO functionsからbitflyerへのアクセスを分離
def order_to_bitflyer(symbol, type, side, amount, params):
    while True:
        try:
            order = bitflyer.create_order(
                symbol = symbol,
                type= type, 
                side= side,
                amount= amount,
                params = params)
            time.sleep(10)      # APIの注文反映待ち
            print("")
        
        except ccxt.BaseError as e:
            print("BitFlyerのAPIエラー発生", e)
            print("注文が失敗しました．10秒後に再度実行します")
            time.sleep(10)