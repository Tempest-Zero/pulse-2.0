"""
AI Module Configuration
Configurable settings for the Q-Learning recommender.
"""


class AIConfig:
    """Configuration for the AI recommendation system."""

    # Multi-user mode (SINGLE_USER_MODE is disabled for proper data isolation)
    SINGLE_USER_MODE: bool = False
    DEFAULT_USER_ID: int = 1  # Only used as fallback

    # Agent parameters
    INITIAL_EPSILON: float = 0.25  # Exploration rate
    MIN_EPSILON: float = 0.05  # Minimum exploration
    EPSILON_DECAY_START: int = 60  # Start decaying after N recommendations
    INITIAL_Q_VALUE: float = 0.5  # Optimistic initialization

    # Learning rate (adaptive)
    LEARNING_RATE_HIGH: float = 0.3  # visits < 5
    LEARNING_RATE_MED: float = 0.1   # visits < 20
    LEARNING_RATE_LOW: float = 0.05  # visits >= 20

    # Phase thresholds
    BOOTSTRAP_THRESHOLD: int = 20   # recommendations < 20 → rule-based
    TRANSITION_THRESHOLD: int = 60  # recommendations < 60 → hybrid

    # Confidence thresholds
    TRANSITION_CONFIDENCE: float = 0.5
    LEARNED_CONFIDENCE: float = 0.7

    # Persistence
    PERSIST_INTERVAL_SECONDS: int = 300  # Save every 5 minutes
    MODEL_DIRECTORY: str = "data/user_models"

    # Implicit feedback
    SKIP_DETECTION_MINUTES: int = 10  # Quick next rec = skip
    IGNORE_DETECTION_HOURS: int = 2   # No activity = ignore

    @classmethod
    def get_user_id(cls, user_id: int | None = None) -> int:
        """Get effective user ID (multi-user mode requires a user_id)."""
        if user_id is None:
            raise ValueError("user_id is required in multi-user mode")
        return user_id
