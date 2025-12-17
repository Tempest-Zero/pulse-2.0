"""
Q-Learning Schedule Agent
Core RL agent with thread-safe singleton pattern and atomic persistence.
"""

import json
import os
import random
import threading
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from .actions import ActionType, get_all_actions
from .state import UserState, StateSerializer
from .config import AIConfig


class ScheduleAgent:
    """
    Q-Learning agent for task recommendation.
    
    Features:
    - Thread-safe singleton per user
    - Epsilon-greedy action selection with decay
    - Adaptive learning rate based on visit counts
    - Atomic file persistence
    - Optimistic initialization
    
    Critical implementation notes:
    - State keys MUST be pipe-separated strings (JSON-safe)
    - Uses os.replace() for atomic writes
    - Instance caching with threading.Lock
    """
    
    # Class-level cache and lock
    _instances: Dict[int, "ScheduleAgent"] = {}
    _lock: threading.Lock = threading.Lock()
    _last_persist: Dict[int, datetime] = {}
    
    def __init__(self, user_id: int):
        """
        Initialize a new agent instance.
        
        Note: Use get_instance() instead of direct construction.
        """
        self.user_id = user_id
        self.q_table: Dict[str, Dict[str, float]] = {}  # state_key -> {action: q_value}
        self.visit_counts: Dict[str, Dict[str, int]] = {}  # state_key -> {action: count}
        self.epsilon = AIConfig.INITIAL_EPSILON
        self.total_recommendations = 0
        self._initialized = False
    
    @classmethod
    def get_instance(cls, user_id: int) -> "ScheduleAgent":
        """
        Get or create a singleton agent instance for a user.
        
        Thread-safe with locking.
        
        Args:
            user_id: User ID
            
        Returns:
            ScheduleAgent instance for this user
        """
        with cls._lock:
            if user_id not in cls._instances:
                agent = cls(user_id)
                agent.load()
                cls._instances[user_id] = agent
            return cls._instances[user_id]
    
    def recommend(
        self,
        state: UserState,
        valid_actions: Optional[List[ActionType]] = None
    ) -> Tuple[ActionType, float]:
        """
        Get a recommendation using epsilon-greedy policy.
        
        Args:
            state: Current user state
            valid_actions: List of allowed actions (for masking)
            
        Returns:
            Tuple of (recommended action, confidence score)
        """
        state_key = StateSerializer.to_key(state)
        
        if valid_actions is None:
            valid_actions = get_all_actions()
        
        if not valid_actions:
            # Safety fallback
            valid_actions = [ActionType.BREAK]
        
        # Initialize Q-values for new state if needed
        if state_key not in self.q_table:
            self._initialize_state(state_key)
        
        # Epsilon-greedy selection
        if random.random() < self.epsilon:
            # Explore: random valid action
            action = random.choice(valid_actions)
            confidence = 0.0  # Low confidence for exploration
        else:
            # Exploit: best Q-value among valid actions
            action, confidence = self._get_best_action(state_key, valid_actions)
        
        return action, confidence
    
    def _get_best_action(
        self, 
        state_key: str, 
        valid_actions: List[ActionType]
    ) -> Tuple[ActionType, float]:
        """
        Get the best action based on Q-values.
        
        Returns:
            Tuple of (best action, confidence)
        """
        state_q = self.q_table.get(state_key, {})
        
        best_action = valid_actions[0]
        best_q = state_q.get(best_action.value, AIConfig.INITIAL_Q_VALUE)
        
        for action in valid_actions[1:]:
            q_value = state_q.get(action.value, AIConfig.INITIAL_Q_VALUE)
            if q_value > best_q:
                best_q = q_value
                best_action = action
        
        # Calculate confidence based on visit count
        visit_count = self.visit_counts.get(state_key, {}).get(best_action.value, 0)
        confidence = min(1.0, visit_count / 10.0)  # Max confidence at 10 visits
        
        return best_action, confidence
    
    def _initialize_state(self, state_key: str) -> None:
        """Initialize Q-values for a new state (optimistic initialization)."""
        self.q_table[state_key] = {
            action.value: AIConfig.INITIAL_Q_VALUE
            for action in get_all_actions()
        }
        self.visit_counts[state_key] = {
            action.value: 0
            for action in get_all_actions()
        }
    
    def update(
        self,
        state: UserState,
        action: ActionType,
        reward: float
    ) -> None:
        """
        Update Q-value using the Q-learning update rule.
        
        Q(s,a) ← Q(s,a) + α(r - Q(s,a))
        
        Uses adaptive learning rate based on visit count.
        
        Args:
            state: State where action was taken
            action: Action that was taken
            reward: Observed reward
        """
        state_key = StateSerializer.to_key(state)
        action_key = action.value
        
        # Initialize if needed
        if state_key not in self.q_table:
            self._initialize_state(state_key)
        
        # Get current Q-value and visit count
        current_q = self.q_table[state_key].get(action_key, AIConfig.INITIAL_Q_VALUE)
        visit_count = self.visit_counts[state_key].get(action_key, 0)
        
        # Adaptive learning rate
        alpha = self._get_learning_rate(visit_count)
        
        # Q-learning update (stateless - no next state discount)
        # Q(s,a) ← Q(s,a) + α(r - Q(s,a))
        new_q = current_q + alpha * (reward - current_q)
        
        # Update Q-table and visit counts
        self.q_table[state_key][action_key] = new_q
        self.visit_counts[state_key][action_key] = visit_count + 1
        
        # Increment total and update epsilon
        self.total_recommendations += 1
        self._update_epsilon()
    
    def _get_learning_rate(self, visit_count: int) -> float:
        """
        Get adaptive learning rate based on visit count.
        
        Higher rate for less-visited state-action pairs.
        """
        if visit_count < 5:
            return AIConfig.LEARNING_RATE_HIGH  # 0.3
        elif visit_count < 20:
            return AIConfig.LEARNING_RATE_MED   # 0.1
        else:
            return AIConfig.LEARNING_RATE_LOW   # 0.05
    
    def _update_epsilon(self) -> None:
        """
        Update epsilon with linear decay after transition threshold.
        
        Decays from INITIAL_EPSILON to MIN_EPSILON.
        """
        if self.total_recommendations < AIConfig.EPSILON_DECAY_START:
            return
        
        # Linear decay
        decay_steps = self.total_recommendations - AIConfig.EPSILON_DECAY_START
        decay_rate = (AIConfig.INITIAL_EPSILON - AIConfig.MIN_EPSILON) / 100
        
        self.epsilon = max(
            AIConfig.MIN_EPSILON,
            AIConfig.INITIAL_EPSILON - (decay_steps * decay_rate)
        )
    
    def save(self) -> None:
        """
        Save agent state to disk with atomic write.
        
        Uses .tmp file + os.replace() to prevent corruption.
        """
        filepath = self._get_filepath()
        tmp_filepath = f"{filepath}.tmp"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Prepare data (all keys are strings for JSON)
        data = {
            "user_id": self.user_id,
            "q_table": self.q_table,
            "visit_counts": self.visit_counts,
            "epsilon": self.epsilon,
            "total_recommendations": self.total_recommendations,
            "saved_at": datetime.now().isoformat(),
        }
        
        # Write to temp file first
        with open(tmp_filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        # Atomic rename
        os.replace(tmp_filepath, filepath)
        
        # Update last persist time
        ScheduleAgent._last_persist[self.user_id] = datetime.now()
    
    def load(self) -> bool:
        """
        Load agent state from disk.
        
        Returns:
            True if loaded successfully, False if initialized fresh
        """
        filepath = self._get_filepath()
        
        if not os.path.exists(filepath):
            self._initialized = True
            return False
        
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            
            self.q_table = data.get("q_table", {})
            self.visit_counts = data.get("visit_counts", {})
            self.epsilon = data.get("epsilon", AIConfig.INITIAL_EPSILON)
            self.total_recommendations = data.get("total_recommendations", 0)
            self._initialized = True
            return True
            
        except (json.JSONDecodeError, KeyError, IOError) as e:
            # Corrupted file - start fresh
            self._initialized = True
            return False
    
    def _get_filepath(self) -> str:
        """Get the file path for this agent's model."""
        base_dir = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(
            base_dir, 
            AIConfig.MODEL_DIRECTORY, 
            f"agent_{self.user_id}.json"
        )
    
    def get_stats(self) -> Dict:
        """Get agent statistics for monitoring."""
        total_states = len(self.q_table)
        total_visits = sum(
            sum(counts.values()) 
            for counts in self.visit_counts.values()
        )
        
        return {
            "user_id": self.user_id,
            "total_states_visited": total_states,
            "total_visits": total_visits,
            "total_recommendations": self.total_recommendations,
            "current_epsilon": round(self.epsilon, 4),
            "phase": self._get_phase(),
        }
    
    def _get_phase(self) -> str:
        """Determine current learning phase."""
        if self.total_recommendations < AIConfig.BOOTSTRAP_THRESHOLD:
            return "bootstrap"
        elif self.total_recommendations < AIConfig.TRANSITION_THRESHOLD:
            return "transition"
        else:
            return "learned"
    
    @classmethod
    def persist_all(cls) -> int:
        """
        Persist all cached agents that haven't been saved recently.
        
        Returns:
            Number of agents saved
        """
        saved_count = 0
        current_time = datetime.now()
        persist_threshold = AIConfig.PERSIST_INTERVAL_SECONDS
        
        with cls._lock:
            for user_id, agent in cls._instances.items():
                last_save = cls._last_persist.get(user_id)
                
                if last_save is None or \
                   (current_time - last_save).total_seconds() >= persist_threshold:
                    try:
                        agent.save()
                        saved_count += 1
                    except IOError:
                        pass  # Log error in production
        
        return saved_count
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear all cached instances (for testing)."""
        with cls._lock:
            cls._instances.clear()
            cls._last_persist.clear()
