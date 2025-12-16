"""
AI Module Configuration
Configurable settings for the Q-Learning recommender.

All "magic numbers" are centralized here with explanations for each value.
"""


class AIConfig:
    """Configuration for the AI recommendation system."""

    # =============================================================================
    # MULTI-USER MODE
    # =============================================================================
    # When False, all queries filter by user_id for proper data isolation.
    # When True (legacy), all data is shared across users.
    SINGLE_USER_MODE: bool = False
    DEFAULT_USER_ID: int = 1  # Only used as fallback if user_id somehow missing

    # =============================================================================
    # EXPLORATION PARAMETERS (Epsilon-Greedy)
    # =============================================================================
    # Initial exploration rate - 25% random actions at start
    # Higher = more exploration, slower convergence but better coverage
    INITIAL_EPSILON: float = 0.25

    # Minimum exploration rate - never go below 5% random
    # Ensures agent keeps discovering new patterns even after convergence
    MIN_EPSILON: float = 0.05

    # Start decaying epsilon after N recommendations
    # Matches TRANSITION_THRESHOLD - don't decay during bootstrap phase
    EPSILON_DECAY_START: int = 60

    # Number of steps to decay from INITIAL to MIN epsilon
    # 100 steps = decay by 0.002 per recommendation after threshold
    EPSILON_DECAY_STEPS: int = 100

    # =============================================================================
    # Q-VALUE INITIALIZATION
    # =============================================================================
    # Optimistic initialization encourages exploration of unvisited state-actions
    # 0.5 = neutral (rewards range from -0.8 to 2.0)
    INITIAL_Q_VALUE: float = 0.5

    # =============================================================================
    # ADAPTIVE LEARNING RATES
    # =============================================================================
    # Higher learning rates for less-visited state-action pairs
    # Allows quick adaptation to new situations while stabilizing known ones

    # High rate for very new state-actions (< 5 visits)
    # Learn quickly from early experiences
    LEARNING_RATE_HIGH: float = 0.3
    LEARNING_RATE_HIGH_THRESHOLD: int = 5

    # Medium rate for somewhat explored state-actions (5-19 visits)
    LEARNING_RATE_MED: float = 0.1
    LEARNING_RATE_MED_THRESHOLD: int = 20

    # Low rate for well-explored state-actions (>= 20 visits)
    # Stable learning, resistant to noise
    LEARNING_RATE_LOW: float = 0.05

    # =============================================================================
    # LEARNING PHASE THRESHOLDS
    # =============================================================================
    # Bootstrap phase: < 20 recommendations
    # Pure rule-based - not enough data for RL to be meaningful
    BOOTSTRAP_THRESHOLD: int = 20

    # Transition phase: 20-59 recommendations
    # Hybrid approach - RL with rule-based fallback if confidence too low
    TRANSITION_THRESHOLD: int = 60

    # Learned phase: >= 60 recommendations
    # RL primary with rule fallback only for very low confidence

    # =============================================================================
    # CONFIDENCE THRESHOLDS
    # =============================================================================
    # Minimum confidence to use RL in transition phase
    # Below this, fall back to rules
    TRANSITION_CONFIDENCE: float = 0.5

    # Minimum confidence to use RL in learned phase
    # Higher bar since we expect better learning by now
    LEARNED_CONFIDENCE: float = 0.7

    # =============================================================================
    # FALLBACK CONFIDENCE VALUES
    # =============================================================================
    # Confidence reported when using rule-based recommendations
    # Lower values during bootstrap, higher as we transition

    # Confidence for pure rule-based (bootstrap phase)
    RULE_CONFIDENCE_BOOTSTRAP: float = 0.3

    # Confidence for rule fallback (transition phase)
    RULE_CONFIDENCE_TRANSITION: float = 0.4

    # Confidence for rule fallback (learned phase - RL failed confidence check)
    RULE_CONFIDENCE_LEARNED: float = 0.5

    # =============================================================================
    # VARIANCE-BASED CONFIDENCE PARAMETERS
    # =============================================================================
    # Instead of naive visit_count/10, use variance of observed rewards
    # to estimate how confident we are in Q-value estimates

    # Minimum visits before variance is meaningful
    MIN_VISITS_FOR_VARIANCE: int = 3

    # Maximum confidence even with high visits and low variance
    MAX_CONFIDENCE: float = 0.95

    # Base confidence with no variance data (falls back to visit-based)
    BASE_CONFIDENCE_PER_VISIT: float = 0.08  # ~12 visits for max without variance

    # Variance penalty factor - higher variance = lower confidence
    # confidence = base - (variance * VARIANCE_PENALTY)
    VARIANCE_PENALTY: float = 0.3

    # =============================================================================
    # TIME BLOCK BOUNDARIES (24-hour format)
    # =============================================================================
    # Define when each time period starts and ends
    # These affect energy calculations and action masking

    # Morning: Fresh start, high energy, good for focus
    TIME_BLOCK_MORNING_START: int = 6
    TIME_BLOCK_MORNING_END: int = 12

    # Afternoon: Post-lunch, moderate energy
    TIME_BLOCK_AFTERNOON_START: int = 12
    TIME_BLOCK_AFTERNOON_END: int = 18

    # Evening: Winding down, declining energy
    TIME_BLOCK_EVENING_START: int = 18
    TIME_BLOCK_EVENING_END: int = 22

    # Night: Rest time, very low energy (only BREAK allowed)
    TIME_BLOCK_NIGHT_START: int = 22
    TIME_BLOCK_NIGHT_END: int = 6  # Wraps to next day

    # =============================================================================
    # ENERGY LEVEL CALCULATION ADJUSTMENTS
    # =============================================================================
    # These modify the base mood score to calculate energy level
    # Based on research on circadian rhythms and cognitive fatigue

    # Morning boost when few tasks completed (fresh and motivated)
    MORNING_ENERGY_BOOST: int = 1
    MORNING_BOOST_MAX_TASKS: int = 2  # Only boost if < 2 tasks done

    # Fatigue penalty after many tasks (cognitive depletion)
    FATIGUE_PENALTY: int = 1
    FATIGUE_THRESHOLD_TASKS: int = 5  # Penalty kicks in at >= 5 tasks

    # Evening energy decline (natural circadian dip)
    EVENING_ENERGY_PENALTY: int = 1

    # Night energy decline (should be resting)
    NIGHT_ENERGY_PENALTY: int = 2

    # Default mood score when no mood logged (neutral)
    DEFAULT_MOOD_SCORE: int = 5

    # Energy level thresholds (mood score ranges)
    ENERGY_HIGH_THRESHOLD: int = 8   # >= 8 = high energy
    ENERGY_MEDIUM_THRESHOLD: int = 5  # >= 5 = medium energy, < 5 = low

    # =============================================================================
    # PERSISTENCE SETTINGS
    # =============================================================================
    # Save agent models every 5 minutes
    PERSIST_INTERVAL_SECONDS: int = 300

    # Directory for saved agent models (relative to backend/)
    MODEL_DIRECTORY: str = "data/user_models"

    # =============================================================================
    # IMPLICIT FEEDBACK DETECTION
    # =============================================================================
    # Skip detection: User requested new recommendation very quickly
    # Indicates they didn't like the previous one
    SKIP_DETECTION_MINUTES: int = 10

    # Ignore detection: No activity for extended period
    # User likely ignored the recommendation
    IGNORE_DETECTION_HOURS: int = 2

    # =============================================================================
    # HELPER METHODS
    # =============================================================================

    @classmethod
    def get_user_id(cls, user_id: int | None = None) -> int:
        """Get effective user ID (multi-user mode requires a user_id)."""
        if user_id is None:
            raise ValueError("user_id is required in multi-user mode")
        return user_id

    @classmethod
    def get_time_block(cls, hour: int) -> str:
        """Map hour of day to time block name."""
        if cls.TIME_BLOCK_MORNING_START <= hour < cls.TIME_BLOCK_MORNING_END:
            return "morning"
        elif cls.TIME_BLOCK_AFTERNOON_START <= hour < cls.TIME_BLOCK_AFTERNOON_END:
            return "afternoon"
        elif cls.TIME_BLOCK_EVENING_START <= hour < cls.TIME_BLOCK_EVENING_END:
            return "evening"
        else:
            return "night"

    @classmethod
    def get_learning_rate(cls, visit_count: int) -> float:
        """Get adaptive learning rate based on visit count."""
        if visit_count < cls.LEARNING_RATE_HIGH_THRESHOLD:
            return cls.LEARNING_RATE_HIGH
        elif visit_count < cls.LEARNING_RATE_MED_THRESHOLD:
            return cls.LEARNING_RATE_MED
        else:
            return cls.LEARNING_RATE_LOW

    @classmethod
    def get_rule_confidence(cls, phase: str) -> float:
        """Get confidence value for rule-based recommendations by phase."""
        if phase == "bootstrap":
            return cls.RULE_CONFIDENCE_BOOTSTRAP
        elif phase == "transition":
            return cls.RULE_CONFIDENCE_TRANSITION
        else:
            return cls.RULE_CONFIDENCE_LEARNED
