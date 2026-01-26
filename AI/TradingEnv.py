import numpy as np

class TradingEnv:
    """Simulates trading of the bot using the most recent rows of data."""

    def __init__(self, df, lotSize=0.001, startBalance=1000, window=4000):
        # Keep only the last 'window' rows
        self.df = df.tail(window).reset_index(drop=True)
        self.lotSize = lotSize
        self.startBalance = startBalance
        self.reset()

    def reset(self):
        """Resets portfolio for a new episode"""
        self.t = 0
        self.balance = self.startBalance
        self.holdingNum = 0
        self.done = False
        return self._getState()

    def _getState(self):
        """Returns current state for AI"""
        row = self.df.iloc[self.t]
        return np.array([
            row["rsi"],                    # 0-100
            row["stoch_rsi"],              # 0-100
            row["zVolume"],                # roughly ~[-3,3]
            self.holdingNum / self.lotSize, # fraction of max lot held (0-1)
            self.balance / self.startBalance # normalized balance (0-1)
        ], dtype=np.float32)

    def step(self, action):
        """
        Executes a trade action
        action: 0=hold, 1=buy, 2=sell
        """
        row = self.df.iloc[self.t]
        price = row["close"]
        oldValue = self.balance + price * self.holdingNum

        # Enforce only full lot trades
        self.holding = self.holdingNum > 0

        # Buy
        if action == 1 and not self.holding and self.balance >= price * self.lotSize:
            self.balance -= price * self.lotSize
            self.holdingNum += self.lotSize

        # Sell
        elif action == 2 and self.holding:
            self.balance += price * self.lotSize
            self.holdingNum -= self.lotSize
        # Move to next candle
        self.t += 1

        # Check if done
        # Check if done
        if self.t >= len(self.df):
            self.done = True
            # Return last valid state
            last_row = self.df.iloc[-1]
            return np.array([
                last_row["rsi"],
                last_row["stoch_rsi"],
                last_row["zVolume"],
                self.holdingNum / self.lotSize,
                self.balance / self.startBalance
            ], dtype=np.float32), 0.0, self.done

        # Compute reward
        newPrice = self.df.iloc[self.t]["close"]
        newValue = self.balance + newPrice * self.holdingNum
        reward = ((newValue - oldValue) / self.startBalance) * 15_000_000

        return self._getState(), reward, self.done
