# coding: utf-8
import requests
import ccxt
import config

bitflyer = ccxt.bitflyer()
bitflyer.apiKey = config.BITFLYER['API_KEY']
bitflyer.secret = config.BITFLYER['SECRET']
