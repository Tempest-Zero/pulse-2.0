"""
Deep Q-Network (DQN) Agent
Lightweight neural network for personalized task recommendation.
Uses continuous features instead of tabular Q-learning for better generalization.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from typing import List, Tuple, Optional
import os

from .replay_buffer import ReplayBuffer
from .feature_encoder import FeatureEncoder


class DQNNetwork(nn.Module):
    """
    Deep Q-Network architecture.

    Input: 12 continuous features
    Hidden: 2 layers × 64 neurons (ReLU activation)
    Output: Q-values for each possible action (task)
    Total parameters: ~5,000
    """

    def __init__(self, state_dim: int = 12, action_dim: int = 10, hidden_dim: int = 64):
        """
        Initialize DQN network.

        Args:
            state_dim: Dimensionality of state features (12)
            action_dim: Number of possible actions (tasks)
            hidden_dim: Hidden layer dimension (64)
        """
        super(DQNNetwork, self).__init__()

        self.fc1 = nn.Linear(state_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, action_dim)

        # Initialize weights
        self._init_weights()

    def _init_weights(self):
        """
        Initialize network weights using Xavier initialization.
        """
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                nn.init.constant_(module.bias, 0.0)

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the network.

        Args:
            state: State tensor (batch_size, state_dim)

        Returns:
            Q-values for each action (batch_size, action_dim)
        """
        x = F.relu(self.fc1(state))
        x = F.relu(self.fc2(x))
        q_values = self.fc3(x)

        return q_values


class DQNAgent:
    """
    DQN Agent for task recommendation.

    Learns to recommend tasks based on user context and behavior.
    Uses experience replay and target network for stable learning.
    """

    def __init__(
        self,
        state_dim: int = 12,
        action_dim: int = 10,
        hidden_dim: int = 64,
        lr: float = 0.001,
        gamma: float = 0.95,
        epsilon: float = 1.0,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.1,
        buffer_capacity: int = 10000,
        batch_size: int = 32,
        target_update_freq: int = 10
    ):
        """
        Initialize DQN agent.

        Args:
            state_dim: Dimensionality of state features
            action_dim: Number of possible actions
            hidden_dim: Hidden layer dimension
            lr: Learning rate
            gamma: Discount factor
            epsilon: Initial exploration rate
            epsilon_decay: Epsilon decay rate
            epsilon_min: Minimum epsilon
            buffer_capacity: Replay buffer capacity
            batch_size: Mini-batch size for training
            target_update_freq: Frequency of target network updates
        """
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq

        # Device (CPU or GPU)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Networks
        self.policy_net = DQNNetwork(state_dim, action_dim, hidden_dim).to(self.device)
        self.target_net = DQNNetwork(state_dim, action_dim, hidden_dim).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()

        # Optimizer
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=lr)

        # Replay buffer
        self.replay_buffer = ReplayBuffer(capacity=buffer_capacity)

        # Feature encoder
        self.feature_encoder = FeatureEncoder()

        # Training metrics
        self.training_step = 0
        self.episode_rewards = []
        self.losses = []

    def select_action(
        self,
        state: np.ndarray,
        available_actions: Optional[List[int]] = None,
        epsilon: Optional[float] = None
    ) -> int:
        """
        Select an action using epsilon-greedy policy.

        Args:
            state: Current state features
            available_actions: List of available action indices
            epsilon: Exploration rate (uses self.epsilon if None)

        Returns:
            Selected action index
        """
        if epsilon is None:
            epsilon = self.epsilon

        # Epsilon-greedy exploration
        if np.random.random() < epsilon:
            # Random action
            if available_actions:
                return np.random.choice(available_actions)
            else:
                return np.random.randint(0, self.action_dim)

        # Greedy action (exploit)
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.policy_net(state_tensor).cpu().numpy()[0]

            # Mask unavailable actions
            if available_actions:
                masked_q = np.full(self.action_dim, -np.inf)
                masked_q[available_actions] = q_values[available_actions]
                return np.argmax(masked_q)
            else:
                return np.argmax(q_values)

    def get_q_values(self, state: np.ndarray) -> np.ndarray:
        """
        Get Q-values for all actions in given state.

        Args:
            state: State features

        Returns:
            Q-values for all actions
        """
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.policy_net(state_tensor).cpu().numpy()[0]

        return q_values

    def store_transition(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool
    ):
        """
        Store a transition in the replay buffer.

        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode ended
        """
        self.replay_buffer.push(state, action, reward, next_state, done)

    def train_step(self) -> Optional[float]:
        """
        Perform one training step.

        Returns:
            Loss value, or None if buffer not ready
        """
        # Check if buffer has enough samples
        if not self.replay_buffer.is_ready(self.batch_size):
            return None

        # Sample mini-batch
        states, actions, rewards, next_states, dones = self.replay_buffer.sample(self.batch_size)

        # Convert to tensors
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)

        # Compute current Q-values
        current_q_values = self.policy_net(states).gather(1, actions.unsqueeze(1)).squeeze(1)

        # Compute target Q-values
        with torch.no_grad():
            next_q_values = self.target_net(next_states).max(1)[0]
            target_q_values = rewards + (1 - dones) * self.gamma * next_q_values

        # Compute loss (Huber loss for stability)
        loss = F.smooth_l1_loss(current_q_values, target_q_values)

        # Optimize
        self.optimizer.zero_grad()
        loss.backward()

        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), max_norm=1.0)

        self.optimizer.step()

        # Update target network
        self.training_step += 1
        if self.training_step % self.target_update_freq == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())

        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

        # Record loss
        loss_value = loss.item()
        self.losses.append(loss_value)

        return loss_value

    def save(self, path: str):
        """
        Save model to disk.

        Args:
            path: File path to save model
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)

        torch.save({
            'policy_net_state_dict': self.policy_net.state_dict(),
            'target_net_state_dict': self.target_net.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'training_step': self.training_step
        }, path)

        print(f"Model saved to {path}")

    def load(self, path: str):
        """
        Load model from disk.

        Args:
            path: File path to load model from
        """
        checkpoint = torch.load(path, map_location=self.device)

        self.policy_net.load_state_dict(checkpoint['policy_net_state_dict'])
        self.target_net.load_state_dict(checkpoint['target_net_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint['epsilon']
        self.training_step = checkpoint['training_step']

        print(f"Model loaded from {path}")

    def get_training_stats(self) -> dict:
        """
        Get training statistics.

        Returns:
            Dictionary with training metrics
        """
        return {
            'training_step': self.training_step,
            'epsilon': self.epsilon,
            'buffer_size': len(self.replay_buffer),
            'avg_loss': np.mean(self.losses[-100:]) if self.losses else 0.0,
            'total_episodes': len(self.episode_rewards),
            'avg_reward': np.mean(self.episode_rewards[-100:]) if self.episode_rewards else 0.0
        }
