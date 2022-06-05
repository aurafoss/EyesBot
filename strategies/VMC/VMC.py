import sys

sys.path.append("./EyesBot")
import ccxt
import ta
import pandas as pd
from utilities.spot_ftx import SpotFtx
from utilities.custom_indicators import VMC
from datetime import datetime
import time
import json

f = open(
    "./EyesBot/secret.json",
)
secret = json.load(f)
f.close()

timeframe = "1h"
account_to_select = "VMC"
params_coin = {
    "BTC/USD": {
        "wallet_exposure": 0.1,
        "st_short_atr_window": 15,
        "st_short_atr_multiplier": 5,
        "short_ema_window": 20,
        "long_ema_window": 400
    },
    "AVAX/USD": {
        "wallet_exposure": 0.2,
        "st_short_atr_window": 15,
        "st_short_atr_multiplier": 5,
        "short_ema_window": 25,
        "long_ema_window": 400
    },
    "ETH/USD": {
        "wallet_exposure": 0.2,
        "st_short_atr_window": 15,
        "st_short_atr_multiplier": 5,
        "short_ema_window": 5,
        "long_ema_window": 400
    },
    "APE/USD": {
        "wallet_exposure": 0.2,
        "st_short_atr_window": 15,
        "st_short_atr_multiplier": 5,
        "short_ema_window": 20,
        "long_ema_window": 400
    },
    "SOL/USD": {
        "wallet_exposure": 0.2,
        "st_short_atr_window": 15,
        "st_short_atr_multiplier": 5,
        "short_ema_window": 15,
        "long_ema_window": 400
    },
    "ATOM/USD": {
        "wallet_exposure": 0.1,
        "st_short_atr_window": 15,
        "st_short_atr_multiplier": 5,
        "short_ema_window": 20,
        "long_ema_window": 400
    },
}

if sum(d["wallet_exposure"] for d in params_coin.values() if d) > 1:
    raise ValueError("Wallet exposure must be less or equal than 1")

ftx = SpotFtx(
    apiKey=secret[account_to_select]["apiKey"],
    secret=secret[account_to_select]["secret"],
    subAccountName=secret[account_to_select]["subAccountName"],
)

now = datetime.now()
current_time = now.strftime("%d/%m/%Y %H:%M:%S")
print("Execution Time :", current_time)

open_orders = ftx.get_open_order()

for order in open_orders:
    order = order["info"]
    if float(order["filledSize"]) > 0:
        print(
            f"Order on {order['market']} is partially fill, create {order['side']} Market of {order['remainingSize']} {order['market']} order to complete it"
        )
        ftx.cancel_all_open_order(order["market"])
        ftx.place_market_order(order["market"], order["side"], order["remainingSize"])
        