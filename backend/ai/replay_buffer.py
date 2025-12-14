"""
Replay Buffer
Experience replay buffer for DQN training.
Stores transitions and samples mini-batches for training.
"""

import numpy as np
from collections import deque
import random
from typing import Tuple, List


class ReplayBuffer:
    """
    Experience replay buffer for DQN.

    Stores transitions (state, action, reward, next_state, done)
    and provides random sampling for breaking correlation in training data.
    """

    def __init__(self, capacity: int = 10000):
        """
        Initialize replay buffer.

        Args:
            capacity: Maximum number of transitions to store
        """
        self.capacity = capacity
        self.buffer = deque(maxlen=capacity)
        self.position = 0

    def push(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool
    ):
        """
        Add a transition to the buffer.

        Args:
            state: Current state (feature vector)
            action: Action taken (task ID)
            reward: Reward received
            next_state: Next state after action
            done: Whether episode ended
        """
        transition = (state, action, reward, next_state, done)
        self.buffer.append(transition)

    def sample(self, batch_size: int) -> Tuple[np.ndarray, ...]:
        """
        Sample a random mini-batch from the buffer.

        Args:
            batch_size: Number of transitions to sample

        Returns:
            Tuple of (states, actions, rewards, next_states, dones)
        """
        if len(self.buffer) < batch_size:
            batch_size = len(self.buffer)

        batch = random.sample(self.buffer, batch_size)

        states = np.array([t[0] for t in batch], dtype=np.float32)
        actions = np.array([t[1] for t in batch], dtype=np.int64)
        rewards = np.array([t[2] for t in batch], dtype=np.float32)
        next_states = np.array([t[3] for t in batch], dtype=np.float32)
        dones = np.array([t[4] for t in batch], dtype=np.float32)

        return states, actions, rewards, next_states, dones

    def __len__(self) -> int:
        """
        Get the current size of the buffer.

        Returns:
            Number of transitions in buffer
        """
        return len(self.buffer)

    def clear(self):
        """
        Clear all transitions from the buffer.
        """
        self.buffer.clear()
        self.position = 0

    def is_ready(self, min_size: int = 100) -> bool:
        """
        Check if buffer has enough samples for training.

        Args:
            min_size: Minimum number of samples required

        Returns:
            True if buffer size >= min_size
        """
        return len(self.buffer) >= min_size


class PrioritizedReplayBuffer(ReplayBuffer):
    """
    Prioritized Experience Replay buffer.

    Samples transitions based on their TD error, giving more importance
    to transitions with higher learning potential.
    """

    def __init__(self, capacity: int = 10000, alpha: float = 0.6):
        """
        Initialize prioritized replay buffer.

        Args:
            capacity: Maximum number of transitions
            alpha: Prioritization exponent (0 = uniform, 1 = full prioritization)
        """
        super().__init__(capacity)
        self.alpha = alpha
        self.priorities = deque(maxlen=capacity)
        self.max_priority = 1.0

    def push(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
        priority: float = None
    ):
        """
        Add a transition with priority.

        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode ended
            priority: Priority value (defaults to max priority)
        """
        super().push(state, action, reward, next_state, done)

        if priority is None:
            priority = self.max_priority

        self.priorities.append(priority)

    def sample(
        self,
        batch_size: int,
        beta: float = 0.4
    ) -> Tuple[np.ndarray, ...]:
        """
        Sample a mini-batch based on priorities.

        Args:
            batch_size: Number of transitions to sample
            beta: Importance sampling exponent (0 = no correction, 1 = full correction)

        Returns:
            Tuple of (states, actions, rewards, next_states, dones, weights, indices)
        """
        if len(self.buffer) < batch_size:
            batch_size = len(self.buffer)

        # Calculate sampling probabilities
        priorities = np.array(list(self.priorities), dtype=np.float32)
        probabilities = priorities ** self.alpha
        probabilities /= probabilities.sum()

        # Sample indices based on probabilities
        indices = np.random.choice(
            len(self.buffer),
            batch_size,
            replace=False,
            p=probabilities
        )

        # Get transitions
        batch = [self.buffer[idx] for idx in indices]

        states = np.array([t[0] for t in batch], dtype=np.float32)
        actions = np.array([t[1] for t in batch], dtype=np.int64)
        rewards = np.array([t[2] for t in batch], dtype=np.float32)
        next_states = np.array([t[3] for t in batch], dtype=np.float32)
        dones = np.array([t[4] for t in batch], dtype=np.float32)

        # Calculate importance sampling weights
        weights = (len(self.buffer) * probabilities[indices]) ** (-beta)
        weights /= weights.max()  # Normalize
        weights = weights.astype(np.float32)

        return states, actions, rewards, next_states, dones, weights, indices

    def update_priorities(self, indices: List[int], priorities: np.ndarray):
        """
        Update priorities for sampled transitions.

        Args:
            indices: Indices of sampled transitions
            priorities: New priority values
        """
        for idx, priority in zip(indices, priorities):
            self.priorities[idx] = priority
            self.max_priority = max(self.max_priority, priority)

    def clear(self):
        """
        Clear all transitions and priorities.
        """
        super().clear()
        self.priorities.clear()
        self.max_priority = 1.0
