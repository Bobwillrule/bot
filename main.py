import math
import requests
import os
from dotenv import load_dotenv
import time
import csv
import pandas as pd
from RSIIndicators import RSI, StochRSI


from datetime import datetime, timezone, timedelta

load_dotenv() 

url_public = os.getenv("KRAKEN_PUBLIC")
pair = os.getenv("PAIR")
interval = int(os.getenv("INTERVAL")) # in seconds
candle = os.getenv("CANDLE") # in minutes
RSIPeriod = int(os.getenv("RSIPERIOD"))
sellThreshold = int(os.getenv("SELLTHRESHOLD"))
buyThreshold = int(os.getenv("BUYTHRESHOLD"))
startMoney = int(os.getenv("INITIALPAPERMONEY"))
lotSize = int(os.getenv("HOWMANYYOUWANT"))

session =requests.Session() # start the session

def WhatTime():
    """returns the current date and time"""
    print("hello world!")
    return f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}/" \
           f"{datetime.now(timezone(timedelta(hours=-7))).strftime('%m-%d %H:%M:%S')}"


def PublicInfo(linkEnd, pair, candle):
    """Gets the public info of the kraken API. Link end appends to the end of the link
    to send the right request and the pair is the pair of coins we wish to get"""
    url = f"{url_public}/{linkEnd}"
    response = session.get(url, params={"pair": pair, "interval": candle}, timeout=10) # get the session and the API request
    response.raise_for_status() # Check for status, 200 is good
    data = response.json() # make the json into a map

    candles = data["result"].get(pair)
    if candles is None:
        raise ValueError(f"No OHLC data found for pair '{pair}'") # if get returns none
    return candles

def GetCandle(pair, candle):
    """Gets the latest price of the pair"""
    data = PublicInfo("OHLC", pair, candle) # Get the candle info 
    df = pd.DataFrame(data, columns=["time","open","high","low","close","vwap","volume","count"]) # Put in dataframe
    df["close"] = df["close"].astype(float)
    return df


import csv
import os

def WriteOut(df):
    """Writes out the latest price to CSV file. Writes header only if file does not exist."""

    file_exists = os.path.isfile("data_log.csv")

    with open("data_log.csv", "a", newline="") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        
        if not file_exists:  # File doesn't exist , write header
            writer.writerow(["Time", "Closing Price", "RSI Value", "Stochastic RSI", "Score"])
        
        # Write latest data row
        writer.writerow([df["timeStamp"].iloc[-1],
                         df["close"].iloc[-1],
                         df["RSI"].iloc[-1],
                         df["stochRSI"].iloc[-1],
                         df["Score"].iloc[-1]])
    
    print(f'{df["timeStamp"].iloc[-1]}, {df["close"].iloc[-1]}, {df["RSI"].iloc[-1]:.2f}, {df["stochRSI"].iloc[-1]:.2f}, {df["Score"].iloc[-1]:.2f}')


def addWeight(df):
    df = RSI(df, RSIPeriod)
    df = StochRSI(df, RSIPeriod)

    score = 0
    if df["RSI"].iloc[-1] < 30:
        score += 30
    elif df["RSI"].iloc[-1] > 70:
        score -= 30

    if df["stochRSI"].iloc[-1] < 30:
        score += 30
    elif df["stochRSI"].iloc[-1] > 70:
        score -= 30

    # set score only for the last row
    df.loc[df.index[-1], "Score"] = score

    return df

def evaluation(df, buyThreshold, sellThreshold):
    df = addWeight(df)
    if (df["Score"] == buyThreshold): # If score is above threshold
        PaperTrade(df)
        df["decision"] = f"Buy @ {df["close"].iloc[-1]}" 
    elif (df["Score"] == sellThreshold): # If score is below seel threshold
        PaperTrade(df)
        df["decision"] = f"Sell @ {df["close"].iloc[-1]}"
    else: # Hold what you have 
        df["decision"] = "Hold"
    return df

def PaperTrade(df, buy, lotSize):
    """Practice trading updating only the last row (no history added)"""

    if buy:
        # Calculate cost of purchase
        price = lotSize * df["close"].iloc[-1]

        # Check that we have enough money to buy
        if price <= df["Balance"].iloc[-1]:
            # Deduct cost from balance
            df.loc[df.index[-1], "Balance"] -= price
            # Add coins to our holdings
            df.loc[df.index[-1], "Amount"]  += lotSize

    else:
        # Check that we have enough coins to sell
        if df["Amount"].iloc[-1] >= lotSize:
            # Calculate proceeds of sale
            price = lotSize * df["close"].iloc[-1]
            # Add money to balance
            df.loc[df.index[-1], "Balance"] += price
            # Subtract coins from holdings
            df.loc[df.index[-1], "Amount"]  -= lotSize
    return df

while True:
    df = GetCandle(pair, candle)
    df["timeStamp"] = WhatTime()
    df = addWeight(df)
    df["Balance"] = startMoney
    WriteOut(df) # get the latest price at index [-1]
    time.sleep(interval)






