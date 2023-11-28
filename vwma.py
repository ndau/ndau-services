#!/usr/bin/env python3

#  ----- ---- --- -- -
#  Copyright 2019 Oneiro NA, Inc. All Rights Reserved.
# 
#  Licensed under the Apache License 2.0 (the "License").  You may not use
#  this file except in compliance with the License.  You can obtain a copy
#  in the file LICENSE in the source distribution or at
#  https://www.apache.org/licenses/LICENSE-2.0.txt
#  - -- --- ---- -----

import requests
from requests import request
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import time
import sys
import pyotp
import math
import subprocess

#URL_VINEX = 'https://api.vinex.network/api/v2/get-ticker?market=usdt_ndau'
URL_BITMART = 'https://api-cloud.bitmart.com/spot/v1/ticker?symbol=NDAU_USDT'
URL_BITTREX = 'https://api.bittrex.com/v3/markets/NDAU-USDT/summary'
URL_KUCOIN = 'https://api.kucoin.com/api/v1/market/stats?symbol=NDAU-USDT'
#URL_LIQUID = 'https://api.liquid.com/products/749'

PRICE_DELTA = 0      # Always record the price, even if it doesn't change

def main():
    """
    Get price info from exchanges and submit market price tx
    """

#    vinex_USDT = 0
#    vinex_NDAU = 0
    bitmart_USDT = 0
    bitmart_NDAU = 0
    bittrex_USDT = 0
    bittrex_NDAU = 0
#    kucoin_USDT = 0
#    kucoin_NDAU = 0
#    liquid_USDT = 0
#    liquid_NDAU = 0

#    try:
#        resp = session.get(URL_VINEX)
#        print(f"Vinex resp = {resp}")
#        if resp.ok:
#            jsonvinex = json.loads(resp.text)
#            vinex_USDT = jsonvinex['data']['quoteVolume']
#            vinex_NDAU = jsonvinex['data']['baseVolume']
#            if vinex_NDAU != 0:
#                print(f'Vinex price = {vinex_USDT/vinex_NDAU}')
#    except (ConnectionError, Timeout, TooManyRedirects) as e:
#        print(e)

    try:
        resp = requests.get(URL_BITMART)
        print(f"Bitmart resp = {resp}")
        if resp.ok:
            jsonbitmart = json.loads(resp.text)
            bitmart_USDT = float(jsonbitmart['data']['tickers'][0]['quote_volume_24h'])
            bitmart_NDAU = float(jsonbitmart['data']['tickers'][0]['base_volume_24h'])
            if bitmart_NDAU != 0:
                print(f'Bitmart price = {bitmart_USDT/bitmart_NDAU}')
                print(f'USDT volume {bitmart_USDT}, NDAU volume {bitmart_NDAU}')
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

    try:
        resp = requests.get(URL_BITTREX)
        print(f"Bittrex resp = {resp}")
        if resp.ok:
            jsonbittrex = json.loads(resp.text)
            bittrex_USDT = float(jsonbittrex['quoteVolume'])
            bittrex_NDAU = float(jsonbittrex['volume'])
            if bittrex_NDAU != 0:
                print(f'Bittrex price = {bittrex_USDT/bittrex_NDAU}')
                print(f'USDT volume {bittrex_USDT}, NDAU volume {bittrex_NDAU}')

    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

#    try:
#        resp = requests.get(URL_KUCOIN)
#        print(f"KuCoin resp = {resp}")
#        if resp.ok:
#            jsonkucoin = json.loads(resp.text)
#            kucoin_USDT = float(jsonkucoin['data']['volValue'])
#            kucoin_NDAU = float(jsonkucoin['data']['vol'])
#            if kucoin_NDAU != 0:
#                print(f'KuCoin price = {kucoin_USDT/kucoin_NDAU}')
#                print(f'USDT volume {kucoin_USDT}, NDAU volume {kucoin_NDAU}')
#
#    except (ConnectionError, Timeout, TooManyRedirects) as e:
#        print(e)

#    try:
#        resp = session.get(URL_LIQUID)
#        print(f"Liquid resp = {resp}")
#        if resp.ok:
#            jsonliquid = json.loads(resp.text)
#            liquid_USDT = float(jsonliquid['last_price_24h'])
#            liquid_NDAU = float(jsonliquid['volume_24h'])
#            liquid_USDT = liquid_USDT * liquid_NDAU
#            if liquid_NDAU != 0:
#                print(f'Liquid price = {liquid_USDT/liquid_NDAU}')
#    except (ConnectionError, Timeout, TooManyRedirects) as e:
#        print(e)

#    total_NDAU = (vinex_NDAU + bitmart_NDAU + bittrex_NDAU + liquid_NDAU + kucoin_NDAU)
#    total_USDT = (vinex_USDT + bitmart_USDT + bittrex_USDT + liquid_USDT + kucoin_USDT)

#    total_NDAU = (bitmart_NDAU + bittrex_NDAU + kucoin_NDAU)
#    total_USDT = (bitmart_USDT + bittrex_USDT + kucoin_USDT)

    total_NDAU = (bittrex_NDAU)
    total_USDT = (bittrex_USDT)

    if  total_NDAU > 0:
        market_price = total_USDT / total_NDAU
        print(f'Total USDT {total_USDT}, total NDAU {total_NDAU}, average (market) price {market_price}')

        NANOCENTSPERDOLLAR = 100000000000.0
        new_price = math.floor(market_price * NANOCENTSPERDOLLAR)

        GET_MARKET_URL = "https://mainnet-1.ndau.tech:3030/price/current"

        try:
            resp = requests.get(GET_MARKET_URL)
            if resp.ok:
                print(f'json resp = {resp.json()}')
            else:
                print(f'resp code = {resp.status_code}')
                print(f'resp text = {resp.text}')
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)

        respjson = resp.json()
        current_price = respjson["marketPrice"]
        print(f'New ${new_price/100000000000}, current ${current_price/100000000000}')

        # Don't update the price if it has changed by less than PRICE_DELTA
        change = abs((new_price / current_price) - 1) * 100 # Change in %
        print(f"Price change is {change}%")
        if (change >= PRICE_DELTA) or (sys.argv[1] == "force"):

#            print(f'Recording updated price')
#            RECORDPRICE_SECRET = 'JBCUNEALIN5G67QT'
#            totp = pyotp.TOTP(RECORDPRICE_SECRET)
#            otp_code = totp.now()

#            SET_MARKET_URL = f'http://localhost:20036/setmarketprice/submit/mainnet?newprice={new_price}&otp={otp_code}'
#            print(f'market price URL = {SET_MARKET_URL}')
#            try:
#                resp = requests.get(SET_MARKET_URL)
#                if resp.ok:
#                    print(f'json resp = {resp.json()}')
#                else:
#                    print(f'resp code = {resp.status_code}')
#                    print(f'resp text = {resp.text}')
#            except (ConnectionError, Timeout, TooManyRedirects) as e:
#                    print(e)

            rp = subprocess.run(["/home/ec2-user/recordprice.sh", "mainnet", "submit", str(new_price)])
            rp = subprocess.run(["/home/ec2-user/recordprice.sh", "testnet", "submit", str(new_price)])

#            RECORDPRICE_SECRET = 'JBCUNEALIN5G67QT'
#            totp = pyotp.TOTP(RECORDPRICE_SECRET)
#            otp_code = totp.now()

#            SET_MARKET_URL = f'http://localhost:20036/setmarketprice/submit/testnet?newprice={new_price}&otp={otp_code}'
#            print(f'market price URL = {SET_MARKET_URL}')
#            try:
#                resp = requests.get(SET_MARKET_URL)
#                if resp.ok:
#                    print(f'json resp = {resp.json()}')
#                else:
#                    print(f'resp code = {resp.status_code}')
#                    print(f'resp text = {resp.text}')
#            except (ConnectionError, Timeout, TooManyRedirects) as e:
#                print(e)

        else:
            print(f'Price has not changed, no update needed.')

if __name__ == "__main__":
    main()
