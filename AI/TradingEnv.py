class TradingEnv:
    """Simulates Trading of the bot"""

    #Initilizes empty porfolio
    def __init__ (self, df, lotSize = 1, startBalance =1000):
        self.df = df.reset_index(drop = True)
        self.lotSize = lotSize
        self.startBalance = startBalance
        self.holding = False
        self.holdingNum = 0
        self.reset()

    def reset(self): #Resets the portfolio
        self.t = 0
        self.balance = self.startBalance
        self.holding = False
        self.holdingNum = 0
        self.done=False
        return self._getState()
    
    def _getState(self):
        row = self.df.iloc[self.t]
        return np.array([
            row["RSI"],
            row["stochRSI"],
            row["z_volume"],
            self.holdingNum,
            self.balance
        ], dtype=np.float32)
    
    
    def step(self, action):
        "trades the simulation. 0=hold, 1 = buy, 2 = sell"

        ## get current row
        row = self.df.iloc[self.t]
        price = row["close"]
        oldValue = self.balance + price * self.holdingNum #compute old value

        ## Ensure that we are only holding one positione everytime
        if self.holdingNum == 0:
            self.holding = False
        elif self.holdingNum == self.lotSize:
            self.holding = True
        else:
            raise ValueError("holding size cannot exceed lot size every time")
        
        ## Determine if we are buying or selling
        if action == 1 and not self.holding and self.balance >= price*self.lotSize: #Buy
            self.balance -= price*self.lotSize 
            self.holdingNum += self.lotSize

        elif action == 2 and self.holding: #Sell
            self.balance += price*self.lotSize
            self.holdingNum -= self.lotSize

        ## Compute the rewards
        self.t += 1 #go to next candle

        if self.t >= len(self.df): # Check if we are at the end of training data
            self.done = True
            return self._getState(), 0.0, self.done
        

        newPrice = self.df.iloc[self.t]["close"]
        newValue = self.balance + newPrice * self.holdingNum
        reward = newValue - oldValue

        return self._getState(), reward, self.done