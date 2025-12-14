"""
PULSE AI Module
Hybrid AI system with Q-Learning and Deep Q-Network agents.
"""

# Q-Learning Components (Original)
from .actions import ActionType, ActionMetadata, ACTION_TYPES, get_all_actions, get_action_metadata
from .state import (
    UserState,
    StateSerializer,
    TimeBlock,
    DayOfWeek,
    EnergyLevel,
    WorkloadPressure,
    generate_all_states,
    get_state_count,
)
from .config import AIConfig
from .mood_mapper import MoodMapper
from .context_encoder import ContextEncoder
from .reward_calculator import RewardCalculator, Outcome, RewardWeights
from .implicit_feedback import ImplicitFeedbackInferencer
from .agent import ScheduleAgent
from .rule_engine import RuleEngine
from .action_masker import ActionMasker
from .task_selector import TaskSelector
from .hybrid_recommender import HybridRecommender, RecommendationResult

# DQN Components (Browser Extension) - Optional, requires PyTorch
DQN_AVAILABLE = False
try:
    from .dqn_agent import DQNAgent, DQNNetwork
    from .feature_encoder import FeatureEncoder, feature_encoder
    from .replay_buffer import ReplayBuffer, PrioritizedReplayBuffer
    DQN_AVAILABLE = True
except ImportError as e:
    # PyTorch not installed - DQN features disabled
    print(f"[AI] DQN components not available (PyTorch not installed): {e}")
    DQNAgent = None
    DQNNetwork = None
    FeatureEncoder = None
    feature_encoder = None
    ReplayBuffer = None
    PrioritizedReplayBuffer = None

__all__ = [
    # Actions
    "ActionType",
    "ActionMetadata",
    "ACTION_TYPES",
    "get_all_actions",
    "get_action_metadata",
    # State
    "UserState",
    "StateSerializer",
    "TimeBlock",
    "DayOfWeek",
    "EnergyLevel",
    "WorkloadPressure",
    "generate_all_states",
    "get_state_count",
    # Config
    "AIConfig",
    # Mood
    "MoodMapper",
    # Context
    "ContextEncoder",
    # Reward
    "RewardCalculator",
    "Outcome",
    "RewardWeights",
    # Implicit Feedback
    "ImplicitFeedbackInferencer",
    # Agent
    "ScheduleAgent",
    # Rule Engine
    "RuleEngine",
    # Action Masker
    "ActionMasker",
    # Task Selector
    "TaskSelector",
    # Hybrid Recommender
    "HybridRecommender",
    "RecommendationResult",
    # DQN Components (optional)
    "DQN_AVAILABLE",
    "DQNAgent",
    "DQNNetwork",
    "FeatureEncoder",
    "feature_encoder",
    "ReplayBuffer",
    "PrioritizedReplayBuffer",
]
