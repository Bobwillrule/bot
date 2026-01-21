import time
from datetime import datetime, timezone, timedelta

def WhatTime():
    """returns the current date and time"""
    return f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}/" \
           f"{datetime.now(timezone(timedelta(hours=-7))).strftime('%m-%d %H:%M:%S')}"