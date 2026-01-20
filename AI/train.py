import os
from dotenv import load_dotenv
import pandas as pd
import torch
from AI.TradingEnv import TradingEnv
from AI.brain import trainDQN
from indicators.RSIIndicators import RSI, StochRSI
from indicators.volume import zVolume

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


# def load_data(filename, RSI_period=14):
#     df = pd.read_csv(filename)
#     df = RSI(df, RSI_period)              # add RSI column
#     df = StochRSI(df, RSI_period)         # add stochastic RSI
#     df = zVolume(df)              # normalized volume for DQN
#     df = df.dropna().reset_index(drop=True)
#     return df

def load_data(filename, RSI_period=14):

    df = pd.read_csv(
        "BTTUSD_5.csv",
        names=["open", "high", "low", "close", "volume", "trades"]
    )

    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)

    df = RSI(df, RSI_period)
    df = StochRSI(df, RSI_period)
    df = zVolume(df)

    df = df.dropna().reset_index(drop=True)
    return df


def train():
    df = load_data("BTTUSD_5.csv", RSIPeriod)

    env = TradingEnv(df, lotSize=1, startBalance=startMoney)

    policy = trainDQN(env, episodes=50, gamma=0.95, lr=1e-3, epsilon=0.1)

    torch.save(policy.state_dict(), "trading_model.pth")
    print("Model saved as trading_model.pth")