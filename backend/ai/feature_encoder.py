"""
Feature Encoder
Converts browsing session data into continuous features for DQN input.
Replaces discrete state encoding with continuous features for better generalization.
"""

import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple
import math


class FeatureEncoder:
    """
    Encodes browsing session data into a continuous feature vector.

    Features (12 dimensions):
    - time_of_day_sin, time_of_day_cos: Cyclical time encoding
    - day_of_week: Normalized day (0-1)
    - work_ratio: Work time / total time
    - focus_score: Normalized focus duration
    - distraction_rate: Normalized tab switches per hour
    - session_duration: Log-normalized minutes
    - tab_switches_norm: Normalized tab switches
    - unique_domains_norm: Normalized unique domains
    - is_weekday: Binary (0 or 1)
    - is_working_hours: Binary (0 or 1)
    - workload_pressure: Estimated pressure (0-1)
    """

    def __init__(self):
        # Normalization constants
        self.MAX_FOCUS_MINUTES = 30.0
        self.MAX_DISTRACTION_RATE = 60.0
        self.MAX_SESSION_MINUTES = 120.0
        self.MAX_TAB_SWITCHES = 50.0
        self.MAX_UNIQUE_DOMAINS = 20.0

    def encode_session(self, session_data: Dict) -> np.ndarray:
        """
        Encode a browsing session into a feature vector.

        Args:
            session_data: Dictionary containing session information

        Returns:
            numpy array of shape (12,) with continuous features
        """
        # Extract timestamp
        timestamp = session_data.get('timestamp', datetime.now())
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

        hour = timestamp.hour
        day_of_week = timestamp.weekday()

        # Time features (cyclical encoding)
        time_of_day_norm = hour / 24.0
        time_of_day_sin = math.sin(2 * math.pi * time_of_day_norm)
        time_of_day_cos = math.cos(2 * math.pi * time_of_day_norm)
        day_of_week_norm = day_of_week / 7.0

        # Category distribution
        category_dist = session_data.get('category_distribution', {})
        work_time = category_dist.get('work', 0)
        leisure_time = category_dist.get('leisure', 0)
        social_time = category_dist.get('social', 0)
        neutral_time = category_dist.get('neutral', 0)
        total_time = work_time + leisure_time + social_time + neutral_time

        # Work-life balance ratio
        work_ratio = work_time / total_time if total_time > 0 else 0.0

        # Behavioral metrics
        metrics = session_data.get('metrics', {})
        avg_focus_duration = metrics.get('avg_focus_duration_minutes', 0.0)
        distraction_rate = metrics.get('distraction_rate_per_hour', 0.0)
        tab_switches = metrics.get('tab_switches', 0)
        unique_domains = metrics.get('unique_domains', 0)

        # Session duration
        session_duration = session_data.get('duration_minutes', 60)

        # Normalize features
        focus_score = min(avg_focus_duration / self.MAX_FOCUS_MINUTES, 1.0)
        distraction_rate_norm = min(distraction_rate / self.MAX_DISTRACTION_RATE, 1.0)
        session_duration_norm = math.log(session_duration + 1) / math.log(self.MAX_SESSION_MINUTES)
        tab_switches_norm = min(tab_switches / self.MAX_TAB_SWITCHES, 1.0)
        unique_domains_norm = min(unique_domains / self.MAX_UNIQUE_DOMAINS, 1.0)

        # Context features
        is_weekday = 1.0 if 0 <= day_of_week <= 4 else 0.0
        is_working_hours = 1.0 if 9 <= hour <= 17 else 0.0

        # Workload pressure (combination of work ratio and distraction)
        workload_pressure = min((work_ratio * 0.6) + (tab_switches_norm * 0.4), 1.0)

        # Construct feature vector
        features = np.array([
            time_of_day_sin,
            time_of_day_cos,
            day_of_week_norm,
            work_ratio,
            focus_score,
            distraction_rate_norm,
            session_duration_norm,
            tab_switches_norm,
            unique_domains_norm,
            is_weekday,
            is_working_hours,
            workload_pressure
        ], dtype=np.float32)

        return features

    def encode_batch(self, sessions: List[Dict]) -> np.ndarray:
        """
        Encode multiple sessions into a batch of feature vectors.

        Args:
            sessions: List of session dictionaries

        Returns:
            numpy array of shape (batch_size, 12)
        """
        return np.array([self.encode_session(session) for session in sessions])

    def get_feature_names(self) -> List[str]:
        """
        Get the names of all features in order.

        Returns:
            List of feature names
        """
        return [
            'time_of_day_sin',
            'time_of_day_cos',
            'day_of_week',
            'work_ratio',
            'focus_score',
            'distraction_rate',
            'session_duration',
            'tab_switches_norm',
            'unique_domains_norm',
            'is_weekday',
            'is_working_hours',
            'workload_pressure'
        ]

    def get_feature_dim(self) -> int:
        """
        Get the dimensionality of the feature vector.

        Returns:
            Feature dimension (12)
        """
        return 12


# Singleton instance
feature_encoder = FeatureEncoder()


# Helper function for backward compatibility
def encode_context(session_data: Dict) -> np.ndarray:
    """
    Legacy function for encoding session context.
    Calls the new FeatureEncoder.

    Args:
        session_data: Session information dictionary

    Returns:
        Feature vector
    """
    return feature_encoder.encode_session(session_data)
