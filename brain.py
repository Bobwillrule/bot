import torch
import torch.nn as nn
import torch.optim as optim

# main brain
class policyNetwork(nn.module):
    """nueral network for trading"""
    def __init__ (self, stateSize, actionSize):
        super().__init__
        self.layer = nn.sequential(
            nn.Linear(stateSize, 32), #first layer
            nn.reLU,
            nn.Linear(32, 16), # Second layer
            nn.reLU,
            nn.Linear(16, actionSize)
        )

    def forward(self, x):
        return self.layer(x)
    

    

    

