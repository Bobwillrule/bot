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
interval = int(os.getenv("INTERVAL"))
candle = os.getenv("CANDLE")

session =requests.Session() # start the session

def public_info(linkEnd, pair, candle):
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

def get_price(pair, candle):
    """Gets the latest price of the pair"""
    data = public_info("OHLC", pair, candle)
    price = data[-1][4] # the position of the last closing price
    return price

def write_out(price):
    """Writes out the latest price to CSV file. If CSV file does not exist it creats a new onee"""
    with open("data_log.csv", "a", newline="") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(price)
        

while True:
    final_price = [get_price(pair, candle)]
    print(final_price)
    write_out(final_price)
    time.sleep(interval)






