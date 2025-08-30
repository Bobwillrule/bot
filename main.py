import math
import requests

response = requests.get("https://api.kraken.com/0/public/Ticker")

def public_info(linkEnd, pair):
    """Gets the public info of the kraken API. Link end appends to the end of the link
    to send the right request and the pair is the pair of coins we wish to get"""

    
