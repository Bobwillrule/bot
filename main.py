import math
import requests
import os
from dotenv import load_dotenv

load_dotenv() 

url_public = os.getenv("KRAKEN_PUBLIC")
pair = os.getenv("PAIR")

session =requests.Session() # start the session

def public_info(linkEnd, pair):
    """Gets the public info of the kraken API. Link end appends to the end of the link
    to send the right request and the pair is the pair of coins we wish to get"""
    url = f"{url_public}/{linkEnd}"
    response = session.get(url, params={"pair": pair}, timeout=10) # get the session and the API request
    response.raise_for_status() # Check for status, 200 is good
    data = response.json() # make the json into a map

    candles = data["result"].get(pair)
    if candles is None:
        raise ValueError(f"No OHLC data found for pair '{pair}'")
    return candles

def get_price(pair):
    data = public_info("OHLC", pair)
    price = data[-1][4]
    return price

print(get_price(pair))






