"""
Hybrid Recommender
Main orchestrator combining RL agent, rule engine, and supporting systems.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from dataclasses import dataclass

from .actions import ActionType, ACTION_TYPES
from .state import UserState, StateSerializer
from .config import AIConfig
from .context_encoder import ContextEncoder
from .agent import ScheduleAgent
from .rule_engine import RuleEngine
from .action_masker import ActionMasker
from .task_selector import TaskSelector
from .reward_calculator import RewardCalculator, Outcome


@dataclass
class RecommendationResult:
    """Result from the hybrid recommender."""
    action: ActionType
    action_display_name: str
    suggested_duration_minutes: int
    explanation: str
    confidence: float
    strategy: str  # 'rule', 'rl', 'hybrid'
    state_key: str
    task_id: Optional[int] = None
    task_title: Optional[str] = None
    phase: str = "bootstrap"


class HybridRecommender:
    """
    Main recommendation orchestrator.
    
    Combines:
    - ContextEncoder for state extraction
    - ScheduleAgent for Q-learning decisions
    - RuleEngine for fallback/cold-start
    - ActionMasker for filtering invalid actions
    - TaskSelector for concrete task mapping
    
    Phase-based strategy:
    - Bootstrap (<20 recs): Pure rules
    - Transition (20-60 recs): Hybrid with confidence threshold
    - Learned (>60 recs): RL primary with rules fallback
    """
    
    def __init__(self):
        self.context_encoder = ContextEncoder()
        self.rule_engine = RuleEngine()
        self.action_masker = ActionMasker()
        self.task_selector = TaskSelector()
        self.reward_calculator = RewardCalculator()
    
    def get_recommendation(
        self,
        db: Session,
        user_id: Optional[int] = None,
        current_time: Optional[datetime] = None
    ) -> RecommendationResult:
        """
        Get a recommendation for the user.
        
        Main entry point for the recommendation system.
        
        Args:
            db: Database session
            user_id: User ID (uses config default in single-user mode)
            current_time: Current time (defaults to now)
            
        Returns:
            RecommendationResult with action, explanation, confidence, etc.
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc)

        user_id = AIConfig.get_user_id(user_id)
        
        # Step 1: Encode context to state
        state = self.context_encoder.encode(db, current_time, user_id)
        state_key = StateSerializer.to_key(state)
        
        # Step 2: Get valid actions (action masking)
        valid_actions = self.action_masker.get_valid_actions(state, db)
        
        # Step 3: Determine phase and get agent
        agent = ScheduleAgent.get_instance(user_id)
        phase = agent._get_phase()
        
        # Step 4: Choose strategy based on phase
        action, confidence, strategy, explanation = self._select_action(
            agent, state, valid_actions, phase
        )
        
        # Step 5: Select concrete task if applicable
        task_id = None
        task_title = None
        if action in (ActionType.DEEP_FOCUS, ActionType.LIGHT_TASK):
            task = self.task_selector.select_task(action, state, db, user_id)
            if task:
                task_id = task.id
                task_title = task.title
        
        # Step 6: Get action metadata
        meta = ACTION_TYPES[action]
        
        return RecommendationResult(
            action=action,
            action_display_name=meta.display_name,
            suggested_duration_minutes=meta.suggested_duration_minutes,
            explanation=explanation,
            confidence=confidence,
            strategy=strategy,
            state_key=state_key,
            task_id=task_id,
            task_title=task_title,
            phase=phase,
        )
    
    def _select_action(
        self,
        agent: ScheduleAgent,
        state: UserState,
        valid_actions: list[ActionType],
        phase: str
    ) -> Tuple[ActionType, float, str, str]:
        """
        Select action based on phase and confidence.
        
        Returns:
            Tuple of (action, confidence, strategy, explanation)
        """
        # Get rule-based recommendation
        rule_action, rule_explanation = self.rule_engine.get_recommendation(state)
        
        # Ensure rule action is valid
        if rule_action not in valid_actions and valid_actions:
            rule_action = valid_actions[0]
            rule_explanation = f"Recommendation adjusted based on context: {ACTION_TYPES[rule_action].description}"
        
        # Bootstrap phase: pure rules
        if phase == "bootstrap":
            return (
                rule_action,
                0.3,  # Low confidence during bootstrap
                "rule",
                f"🌱 Building your profile: {rule_explanation}"
            )
        
        # Get RL recommendation
        rl_action, rl_confidence = agent.recommend(state, valid_actions)
        
        # Transition phase: hybrid based on confidence
        if phase == "transition":
            if rl_confidence >= AIConfig.TRANSITION_CONFIDENCE:
                return (
                    rl_action,
                    rl_confidence,
                    "hybrid",
                    f"📊 Learning your patterns: {ACTION_TYPES[rl_action].description}"
                )
            else:
                return (
                    rule_action,
                    0.4,
                    "rule",
                    f"📊 Still learning: {rule_explanation}"
                )
        
        # Learned phase: RL primary with confidence check
        if rl_confidence >= AIConfig.LEARNED_CONFIDENCE:
            return (
                rl_action,
                rl_confidence,
                "rl",
                f"✨ Personalized for you: {ACTION_TYPES[rl_action].description}"
            )
        else:
            # Fall back to rules for low confidence
            return (
                rule_action,
                0.5,
                "hybrid",
                f"Suggested based on your patterns: {rule_explanation}"
            )
    
    def record_feedback(
        self,
        db: Session,
        state_key: str,
        action: ActionType,
        outcome: Outcome,
        user_id: Optional[int] = None,
        mood_before: Optional[str] = None,
        mood_after: Optional[str] = None,
        user_rating: Optional[int] = None,
        suggested_duration: Optional[int] = None,
        actual_duration: Optional[int] = None
    ) -> float:
        """
        Record feedback and update the agent.
        
        Args:
            db: Database session
            state_key: State key from the recommendation
            action: Action that was recommended
            outcome: Outcome (completed, partial, skipped, ignored)
            user_id: User ID
            mood_before/after: Mood strings for delta calculation
            user_rating: Explicit rating 1-5
            suggested_duration: Suggested duration in minutes
            actual_duration: Actual duration in minutes
            
        Returns:
            Calculated reward value
        """
        user_id = AIConfig.get_user_id(user_id)
        
        # Calculate reward
        reward = self.reward_calculator.calculate_reward(
            outcome=outcome,
            mood_before=mood_before,
            mood_after=mood_after,
            user_rating=user_rating,
            suggested_duration_minutes=suggested_duration,
            actual_duration_minutes=actual_duration,
        )
        
        # Reconstruct state and update agent
        try:
            state = StateSerializer.from_key(state_key)
            agent = ScheduleAgent.get_instance(user_id)
            agent.update(state, action, reward)
        except ValueError:
            # Invalid state key - can't update
            pass
        
        return reward
    
    def get_stats(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get statistics about the recommendation system.
        
        Returns:
            Dictionary with agent stats and system info
        """
        user_id = AIConfig.get_user_id(user_id)
        agent = ScheduleAgent.get_instance(user_id)
        
        stats = agent.get_stats()
        stats["rules"] = self.rule_engine.get_all_rules()
        stats["phase_thresholds"] = {
            "bootstrap": AIConfig.BOOTSTRAP_THRESHOLD,
            "transition": AIConfig.TRANSITION_THRESHOLD,
        }
        
        return stats
