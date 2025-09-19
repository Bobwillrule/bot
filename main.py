import math
import requests
import os
from dotenv import load_dotenv
import time
import csv
import pandas as pd

load_dotenv() 

url_public = os.getenv("KRAKEN_PUBLIC")
pair = os.getenv("PAIR")
interval = int(os.getenv("INTERVAL")) # in seconds
candle = os.getenv("CANDLE") # in minutes
RSIPeriod = int(os.getenv("RSIPERIOD"))

session =requests.Session() # start the session

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


def WriteOut(price):
    """Writes out the latest price to CSV file. If CSV file does not exist it creats a new onee"""
    with open("data_log.csv", "a", newline="") as csv_file:
        writer = csv.writer(csv_file, delimiter=',') # split into comma seperated
        writer.writerow(price)
        
def RSI(df, period=14):
    """Calculate RSI with Wilder's Smoothing/exponential moving average"""
    delta = df['close'].diff()
    gain = delta.clip(lower=0) # pos values
    loss = -delta.clip(upper=0)
    period = 14 # Change this to change RSI length
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean() #ewm for exp moving average
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()

    rs = avg_gain / avg_loss # RSI calculation
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

def StochRSI(df, period=14):
    """ Calculates Stochastic RSI based on RSI"""
    rsi = df['RSI']
    min_rsi = rsi.rolling(window=period).min()
    max_rsi = rsi.rolling(window=period).max()
    df['stochRSI'] = ((rsi - min_rsi) / (max_rsi - min_rsi))*100
    return df

while True:
    df = GetCandle(pair, candle)
    df = RSI(df, RSIPeriod)
    df = StochRSI(df, RSIPeriod)
    print(df["close"].iloc[-1], df["RSI"].iloc[-1], df["stochRSI"].iloc[-1])
    WriteOut([df["close"].iloc[-1]]) # get the latest price at index [-1]
    time.sleep(interval) 






