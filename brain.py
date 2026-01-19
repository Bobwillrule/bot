import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

# main brain
class policyNetwork(nn.Module):
    """nueral network for trading"""
    def __init__ (self, stateSize, actionSize):
        super().__init__()
        self.layer = nn.Sequential(
            nn.Linear(stateSize, 32), #first layer
            nn.reLU(),
            nn.Linear(32, 16), # Second layer
            nn.reLU(),
            nn.Linear(16, actionSize)
        )

    def forward(self, x):
        return self.layer(x)
    
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
    
def trainDQN(env, episodes = 50, gamma=0.95, lr=1e-3, epsilon=0.1, stateSize = 5, actionSize = 3):
    """trains the ai using reinforcement learning"""
    policy = policyNetwork(stateSize, actionSize)
    optimizer = optim.Adam(policy.parameters(), lr=lr)
    lossFunc = nn.MSELoss()

    ## loops through each episode
    for episode in range(episodes):
        state = torch.tensor(env.reset(), dtype = torch.float32)
        totalReward = 0

        #Loop through data set once
        while not env.done:
            if np.random.rand() < epsilon: #Epsilon greedy for exploration
                action = np.random.randint(actionSize)
            else: # normal no exploration
                qvals = policy(state)
                action = torch.argmax(qvals).item()
            
            nextState, reward, done = env.step(action)
            nextState_t = torch.tensor(nextState, dtype = torch.float32)
            totalReward += reward

            #Compute target
            with torch.no_grad(): #save memory
                qNext = policy(nextState_t)
                maxQNext = torch.max(qNext)
                target = reward + gamma*maxQNext *(0 if done else 1)

            #update qValue
            qPrediction = policy(state)[action] 
            target_t = torch.tensor([target], dtype=torch.float32)
            loss = lossFunc(qPrediction, target_t)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            state = nextState_t

        print(f"Episode {episode+1}/{episodes}, Total Reward: {totalReward:.2f}")

    return policy



            
    


        

        
    
    

    

    

