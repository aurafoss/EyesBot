import sys

sys.path.append("./EyesBot")
import ccxt
import ta
import pandas as pd
from utilities.spot_ftx import SpotFtx
from datetime import datetime
import time
import json

f = open(
    "./EyesBot/secret.json",
)
secret = json.load(f)
f.close()

timeframe = "1h"
account_to_select = "CrossEMA+RSI"

params_coin = {
    "BTC/USD": {
        "wallet_exposure": 0.2,
    },
    "ETH/USD": {
        "wallet_exposure": 0.2,
    },
    "BNB/USD": {
        "wallet_exposure": 0.2,
    },
    "SOL/USD": {
        "wallet_exposure": 0.2,
    },
    "APE/USD": {
        "wallet_exposure": 0.1,
    },
    "ATOM/USD": {
        "wallet_exposure": 0.1,
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

df_list = {}
for pair in params_coin:
    params = params_coin[pair]
    ftx.cancel_all_open_order(pair)
    df = ftx.get_last_historical(pair, timeframe, 1000)
    # -- Populate indicators --
    df['ema1'] = ta.trend.ema_indicator(close = df['close'], window = 25) # Moyenne exponentiel courte
    df['ema2'] = ta.trend.ema_indicator(close = df['close'], window = 45) # Moyenne exponentiel moyenne
    df['sma_long'] = ta.trend.sma_indicator(close = df['close'], window = 600) # Moyenne simple longue
    df['stoch_rsi'] = ta.momentum.stochrsi(close = df['close'], window = 14) # Stochastic RSI non moyenné (K=1 sur Trading View)

    df_list[pair] = df

coin_balance = ftx.get_all_balance()
coin_in_usd = ftx.get_all_balance_in_usd()
usd_balance = coin_balance["USD"]
del coin_balance["USD"]
del coin_in_usd["USD"]
total_balance = usd_balance + sum(coin_in_usd.values())
available_wallet_pct = 1

positions = []
for coin in coin_in_usd:
    if coin_balance[coin] > float(ftx.get_min_order_amount(coin + "/USD")):
        positions.append(coin + "/USD")
        available_wallet_pct -= params_coin[coin + "/USD"]["wallet_exposure"]

pair_to_check = list(set(params_coin.keys()) - set(positions))
#Achat
for pair in pair_to_check:
    # iloc -2 to get the last completely close candle
    row = df_list[pair].iloc[-2]
    if row['ema1'] > row['ema2'] and row['stoch_rsi'] < 0.8 and row['close'] > row['sma_long']:
        buy_limit_price = float(ftx.convert_price_to_precision(pair, row["ema_short"]))
        buy_quantity_in_usd = usd_balance * (
            params_coin[pair]["wallet_exposure"] / available_wallet_pct
        )
        buy_quantity = float(
            ftx.convert_amount_to_precision(pair, buy_quantity_in_usd / buy_limit_price)
        )
        exchange_buy_quantity = buy_quantity * buy_limit_price
        print(
            f"Place Buy Limit Order: {buy_quantity} {pair[:-4]} at the price of {buy_limit_price}$ ~{round(exchange_buy_quantity, 2)}$"
        )
        ftx.place_limit_order(pair, "buy", buy_quantity, buy_limit_price)
#Vente
for pair in positions:
    row = df_list[pair].iloc[-2]
    if row['ema2'] > row['ema1'] and row['stoch_rsi'] > 0.2:#definition d'ordre de vente
        sell_limit_price = float(ftx.convert_price_to_precision(pair, row["ema_short"]))
        sell_quantity = float(
            ftx.convert_amount_to_precision(pair, coin_balance[pair[:-4]])
        )
        exchange_sell_quantity = sell_quantity * sell_limit_price
        print(
            f"Place Sell Limit Order: {sell_quantity} {pair[:-4]} at the price of {sell_limit_price}$ ~{round(exchange_sell_quantity, 2)}$"
        )
        ftx.place_limit_order(pair, "sell", sell_quantity, sell_limit_price)

new_coin_in_usd = ftx.get_all_balance_in_usd()
new_coin_in_usd = {x: y for x, y in new_coin_in_usd.items() if y != 0}
for coin in new_coin_in_usd:
    new_coin_in_usd[coin] = str(round(new_coin_in_usd[coin], 2)) + " $"
print("My current balance in USD:", new_coin_in_usd)