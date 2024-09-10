import torch
import random
import numpy as np
from collections import deque
from model import Linear_QNet, QTrainer
from game import BlackjackGame
import torch.nn as nn
import torch.nn.functional as F

MAX_MEMORY = 100_000  # Define the constants here
BATCH_SIZE = 10000
LR = 0.001

class Agent:
    def __init__(self):
        self.model = Linear_QNet(21, 256, 6)
        self.epsilon = 0  # randomness
        self.gamma = 0.9  # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        self.n_games = 0  # track the number of games played

    def get_state(self, game):
        state_tensors = game.get_state()
        state_tensors = [torch.tensor(tensor, dtype=torch.float).unsqueeze(0) if tensor.ndim == 0 else torch.tensor(tensor, dtype=torch.float) for tensor in state_tensors]
        state = torch.cat(state_tensors, dim=0).numpy()
        return state
    
    def print_state(self, state):
        print("State Information")
        print("Player Hand:", state[0])
        print("Player Ace Count:", state[1])
        print("Player2 Hand:", state[2])
        print("Player2 Ace Count:", state[3])
        print("Dealer Hand:", state[4])
        print("Dealer Ace Count:", state[5])
        print("Count:", state[6])
        print("Decks Remainding:", state[7])
        print("Can Split:", state[8])
        print("Can Double1:", state[9])
        print("Can Double2:", state[10])
        print("Cards Left:", state[11:20])

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def reset_model(self):
        # Reinitialize the model with random weights
        self.model.apply(self._reset_weights)

    @staticmethod
    def _reset_weights(layer):
        if isinstance(layer, nn.Linear):
            nn.init.xavier_uniform_(layer.weight)
            nn.init.constant_(layer.bias, 0)

    def get_action(self, state):
        # Epsilon decay: Ensure epsilon is non-negative
        self.epsilon = max(300 - self.n_games, 0)
        
        if random.randint(0, 600) < self.epsilon:
            # Exploration: Random action
            action = random.randint(0, 6)  # Ensure action is within valid range (0 to 5)
        else:
            # Exploitation: use the model to predict the best action
            state_tensor = torch.tensor(state, dtype=torch.float).unsqueeze(0)  # Add batch dimension
            prediction = self.model(state_tensor)
            action = torch.argmax(prediction).item()
        
        return action


