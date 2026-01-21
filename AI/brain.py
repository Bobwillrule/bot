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
            nn.ReLU(),
            nn.Linear(32, 16), # Second layer
            nn.ReLU(),
            nn.Linear(16, actionSize)
        )

    def forward(self, x):
        return self.layer(x)
    
    
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



            
    


        

        
    
    

    

    

