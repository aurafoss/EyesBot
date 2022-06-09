import sys

sys.path.append("./EyesBot")
import ccxt
import ta
import pandas as pd
import numpy as np
from utilities.spot_ftx import SpotFtx
from utilities.custom_indicators import VMC, SuperTrend
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
        "wallet_exposure": 0.2,
        "wtChannelLen": 15,
        "wtAverageLen": 5,
        "wtMALen": 20,
        "rsiMFIperiod": 20,
        "rsiMFIMultiplier": 20,
        "rsiMFIPosY": 400
    },
    "SOL/USD": {
        "wallet_exposure": 0.2,
        "wtChannelLen": 15,
        "wtAverageLen": 5,
        "wtMALen": 25,
        "rsiMFIperiod": 20,
        "rsiMFIMultiplier": 20,
        "rsiMFIPosY": 400
    },
    "ETH/USD": {
        "wallet_exposure": 0.2,
        "wtChannelLen": 15,
        "wtAverageLen": 5,
        "wtMALen": 5,
        "rsiMFIperiod": 20,
        "rsiMFIMultiplier": 20,
        "rsiMFIPosY": 400
    },
    "APE/USD": {
        "wallet_exposure": 0.2,
        "wtChannelLen": 15,
        "wtAverageLen": 5,
        "wtMALen": 20,
        "rsiMFIperiod": 20,
        "rsiMFIMultiplier": 20,
        "rsiMFIPosY": 400
    },
    "AVAX/USD": {
        "wallet_exposure": 0.1,
        "wtChannelLen": 15,
        "wtAverageLen": 5,
        "wtMALen": 15,
        "rsiMFIperiod": 20,
        "rsiMFIMultiplier": 20,
        "rsiMFIPosY": 400
    },
    "ATOM/USD": {
        "wallet_exposure": 0.1,
        "wtChannelLen": 15,
        "wtAverageLen": 5,
        "wtMALen": 20,
        "rsiMFIperiod": 20,
        "rsiMFIMultiplier": 20,
        "rsiMFIPosY": 400
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
    def chop(high, low, close, window=14):
        tr1 = pd.DataFrame(high - low).rename(columns={0: 'tr1'})
        tr2 = pd.DataFrame(abs(high - close.shift(1))
                       ).rename(columns={0: 'tr2'})
        tr3 = pd.DataFrame(abs(low - close.shift(1))
                       ).rename(columns={0: 'tr3'})
        frames = [tr1, tr2, tr3]
        tr = pd.concat(frames, axis=1, join='inner').dropna().max(axis=1)
        atr = tr.rolling(1).mean()
        highh = high.rolling(window).max()
        lowl = low.rolling(window).min()
        chop_serie = 100 * np.log10((atr.rolling(window).sum()) /
                          (highh - lowl)) / np.log10(window)
        return pd.Series(chop_serie, name="CHOP")
    
    svmc = VMC(
        df["self"],
        df["open"],
        df["high"],
        df["low"],
        df["close"],
        params["wtChannelLen"],
        params["wtAverageLen"],
        params["wtMALen"],
        params["rsiMFIperiod"],
        params["rsiMFIMultiplier"],
        params["rsiMFIPosY"]       
    )

    df['HLC3'] = (df['high'] +df['close'] + df['low'])/3
    vmc = VMC(high =df['high'],low = df['low'],close=df['HLC3'],open=df['open'])
    df['VMC_WAVE1'] = svmc.wave_1()
    df['VMC_WAVE2'] = svmc.wave_2()
    vmc = VMC(high =df['high'],low = df['low'],close=df['close'],open=df['open'])
    df['MONEY_FLOW'] = svmc.money_flow()
    df['EMA50'] = ta.trend.ema_indicator(close = df['close'], window = 50)
    df['EMA200'] = ta.trend.ema_indicator(close = df['close'], window = 200)
    df["CHOP"] = chop(df['high'],df['low'],df['close'],window=14)
    df['ema1'] = ta.trend.ema_indicator(close = df['close'], window = 5) # Moyenne exponentielle 1
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
    previousRow = df_list[pair].iloc[-3]
    if row['EMA50'] > row ['EMA200'] and row ['close'] > row['EMA50']  and row['MONEY_FLOW'] >  0 and row['VMC_WAVE1'] < 0 and row['VMC_WAVE2'] < 0 and row['VMC_WAVE1'] > row['VMC_WAVE2'] and previousRow['VMC_WAVE1'] < previousRow['VMC_WAVE2'] and row['CHOP'] <50: #ligne choix achat
        buy_limit_price = float(ftx.convert_price_to_precision(pair, row["ema1"]))
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
    if row["EMA50"] < row["EMA200"] and row['CHOP'] >50:
        sell_limit_price = float(ftx.convert_price_to_precision(pair, row["ema"]))
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