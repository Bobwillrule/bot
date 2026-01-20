import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

import torch
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

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
    """trains the AI using reinforcement learning"""
    policy = policyNetwork(stateSize, actionSize).to(device)
    optimizer = optim.Adam(policy.parameters(), lr=lr)
    lossFunc = nn.MSELoss()

    for episode in range(episodes):
        state = torch.tensor(env.reset(), dtype=torch.float32).unsqueeze(0).to(device)  # shape [1, stateSize]
        totalReward = 0

        while not env.done:
            if np.random.rand() < epsilon:
                action = np.random.randint(actionSize)
            else:
                qvals = policy(state)  # shape [1, actionSize]
                action = torch.argmax(qvals).item()

            nextState, reward, done = env.step(action)
            nextState_t = torch.tensor(nextState, dtype=torch.float32).unsqueeze(0).to(device)  # shape [1, stateSize]
            totalReward += reward

            # Compute target
            with torch.no_grad():
                qNext = policy(nextState_t)           # [1, actionSize]
                maxQNext = torch.max(qNext, dim=1)[0] # [1]
                target = reward + gamma * maxQNext * (0 if done else 1)  # [1]

            # Update Q-value
            qPrediction = policy(state)[0, action].unsqueeze(0)  # shape [1]
            loss = lossFunc(qPrediction, target)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            state = nextState_t

        print(f"Episode {episode+1}/{episodes}, Total Reward: {totalReward}")

    return policy
