# coding: utf-8
import ccxt
from pprint import pprint

bitflyer = ccxt.bitflyer()
bitflyer.apiKey = 'SZz2PtRTJDU8e6RPA9dp5r'
bitflyer.secret = 'XXX'

collateral = bitflyer.private_get_getcollateral()
pprint( collateral )