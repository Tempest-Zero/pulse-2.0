"""
AI Agent Tests
Tests for Q-Learning agent with concurrency and persistence.
"""

import pytest
import json
import os
import threading
import tempfile
from pathlib import Path
from unittest.mock import patch

from ai.agent import ScheduleAgent
from ai.state import UserState
from ai.actions import ActionType
from ai.config import AIConfig


@pytest.fixture
def temp_model_dir(tmp_path):
    """Create temporary directory for agent models."""
    model_dir = tmp_path / "user_models"
    model_dir.mkdir(parents=True)
    return model_dir


@pytest.fixture
def test_state():
    """Create a test state."""
    return UserState("morning", "monday", "high", "low")


@pytest.fixture
def test_agent(temp_model_dir):
    """Create a fresh agent for testing."""
    # Clear any cached instances
    ScheduleAgent.clear_cache()
    
    # Patch the model directory
    with patch.object(AIConfig, 'MODEL_DIRECTORY', str(temp_model_dir)):
        agent = ScheduleAgent(user_id=999)
        yield agent
        ScheduleAgent.clear_cache()


class TestAgentCreation:
    """Tests for agent creation and initialization."""
    
    def test_create_agent(self, test_agent):
        """Test creating a new agent."""
        assert test_agent.user_id == 999
        assert test_agent.epsilon == AIConfig.INITIAL_EPSILON
        assert test_agent.total_recommendations == 0
    
    def test_agent_has_empty_q_table(self, test_agent):
        """Test new agent has empty Q-table."""
        assert len(test_agent.q_table) == 0
    
    def test_agent_has_empty_visit_counts(self, test_agent):
        """Test new agent has empty visit counts."""
        assert len(test_agent.visit_counts) == 0


class TestAgentSingleton:
    """Tests for singleton pattern."""
    
    def test_get_instance_creates_agent(self, temp_model_dir):
        """Test get_instance creates new agent."""
        ScheduleAgent.clear_cache()
        
        with patch.object(AIConfig, 'MODEL_DIRECTORY', str(temp_model_dir)):
            agent = ScheduleAgent.get_instance(888)
            assert agent.user_id == 888
            ScheduleAgent.clear_cache()
    
    def test_get_instance_returns_same_agent(self, temp_model_dir):
        """Test get_instance returns cached instance."""
        ScheduleAgent.clear_cache()
        
        with patch.object(AIConfig, 'MODEL_DIRECTORY', str(temp_model_dir)):
            agent1 = ScheduleAgent.get_instance(777)
            agent2 = ScheduleAgent.get_instance(777)
            assert agent1 is agent2
            ScheduleAgent.clear_cache()
    
    def test_different_users_different_agents(self, temp_model_dir):
        """Test different users get different agents."""
        ScheduleAgent.clear_cache()
        
        with patch.object(AIConfig, 'MODEL_DIRECTORY', str(temp_model_dir)):
            agent1 = ScheduleAgent.get_instance(555)
            agent2 = ScheduleAgent.get_instance(556)
            assert agent1 is not agent2
            ScheduleAgent.clear_cache()


class TestAgentRecommend:
    """Tests for recommendation generation."""
    
    def test_recommend_returns_action(self, test_agent, test_state):
        """Test recommend returns an ActionType."""
        action, confidence = test_agent.recommend(test_state)
        assert isinstance(action, ActionType)
    
    def test_recommend_returns_confidence(self, test_agent, test_state):
        """Test recommend returns confidence score."""
        action, confidence = test_agent.recommend(test_state)
        assert 0.0 <= confidence <= 1.0
    
    def test_recommend_respects_valid_actions(self, test_agent, test_state):
        """Test recommend only returns valid actions."""
        valid = [ActionType.BREAK, ActionType.REFLECT]
        action, _ = test_agent.recommend(test_state, valid)
        assert action in valid
    
    def test_recommend_initializes_state(self, test_agent, test_state):
        """Test recommend initializes Q-values for new state."""
        assert len(test_agent.q_table) == 0
        test_agent.recommend(test_state)
        assert len(test_agent.q_table) == 1


class TestAgentUpdate:
    """Tests for Q-learning update."""
    
    def test_update_changes_q_value(self, test_agent, test_state):
        """Test update modifies Q-value."""
        action = ActionType.DEEP_FOCUS
        
        # Get initial Q-value
        test_agent.recommend(test_state)  # Initialize state
        initial_q = test_agent.q_table["morning|monday|high|low"][action.value]
        
        # Update with positive reward
        test_agent.update(test_state, action, 1.0)
        new_q = test_agent.q_table["morning|monday|high|low"][action.value]
        
        assert new_q > initial_q
    
    def test_update_increments_visit_count(self, test_agent, test_state):
        """Test update increments visit count."""
        action = ActionType.BREAK
        
        test_agent.update(test_state, action, 0.5)
        count = test_agent.visit_counts["morning|monday|high|low"][action.value]
        assert count == 1
        
        test_agent.update(test_state, action, 0.5)
        count = test_agent.visit_counts["morning|monday|high|low"][action.value]
        assert count == 2
    
    def test_update_increments_total_recommendations(self, test_agent, test_state):
        """Test update increments total recommendation count."""
        assert test_agent.total_recommendations == 0
        
        test_agent.update(test_state, ActionType.BREAK, 0.5)
        assert test_agent.total_recommendations == 1


class TestAgentPersistence:
    """Tests for save/load functionality."""
    
    def test_save_creates_file(self, test_agent, temp_model_dir, test_state):
        """Test save creates agent file."""
        with patch.object(AIConfig, 'MODEL_DIRECTORY', str(temp_model_dir)):
            test_agent.recommend(test_state)
            test_agent.save()
            
            filepath = temp_model_dir / f"agent_{test_agent.user_id}.json"
            assert filepath.exists()
    
    def test_save_creates_directory(self, test_agent, tmp_path, test_state):
        """Test save creates directory if missing."""
        new_dir = tmp_path / "new_dir" / "models"
        
        with patch.object(AIConfig, 'MODEL_DIRECTORY', str(new_dir)):
            test_agent.recommend(test_state)
            test_agent.save()
            assert new_dir.exists()
    
    def test_load_restores_q_table(self, temp_model_dir, test_state):
        """Test load restores Q-table correctly."""
        with patch.object(AIConfig, 'MODEL_DIRECTORY', str(temp_model_dir)):
            # Create and train agent
            agent1 = ScheduleAgent(user_id=111)
            agent1.update(test_state, ActionType.DEEP_FOCUS, 1.0)
            agent1.save()
            
            # Load into new agent
            agent2 = ScheduleAgent(user_id=111)
            agent2.load()
            
            # Verify Q-table restored
            key = "morning|monday|high|low"
            assert key in agent2.q_table
            assert agent2.q_table[key][ActionType.DEEP_FOCUS.value] > AIConfig.INITIAL_Q_VALUE
    
    def test_load_nonexistent_returns_false(self, test_agent, temp_model_dir):
        """Test loading nonexistent file returns False."""
        with patch.object(AIConfig, 'MODEL_DIRECTORY', str(temp_model_dir)):
            result = test_agent.load()
            assert result is False
    
    def test_save_json_keys_are_strings(self, test_agent, temp_model_dir, test_state):
        """Test saved JSON uses string keys (CRITICAL)."""
        with patch.object(AIConfig, 'MODEL_DIRECTORY', str(temp_model_dir)):
            test_agent.update(test_state, ActionType.BREAK, 0.5)
            test_agent.save()
            
            filepath = temp_model_dir / f"agent_{test_agent.user_id}.json"
            with open(filepath) as f:
                data = json.load(f)
            
            # All keys must be strings
            for key in data.get("q_table", {}).keys():
                assert isinstance(key, str)
                assert "|" in key  # Pipe-separated


class TestAgentPhases:
    """Tests for learning phase detection."""
    
    def test_bootstrap_phase(self, test_agent):
        """Test phase is bootstrap when recommendations < 20."""
        test_agent.total_recommendations = 10
        assert test_agent._get_phase() == "bootstrap"
    
    def test_transition_phase(self, test_agent):
        """Test phase is transition when 20 <= recommendations < 60."""
        test_agent.total_recommendations = 40
        assert test_agent._get_phase() == "transition"
    
    def test_learned_phase(self, test_agent):
        """Test phase is learned when recommendations >= 60."""
        test_agent.total_recommendations = 100
        assert test_agent._get_phase() == "learned"


class TestAgentStats:
    """Tests for statistics reporting."""
    
    def test_get_stats_returns_dict(self, test_agent):
        """Test get_stats returns dictionary."""
        stats = test_agent.get_stats()
        assert isinstance(stats, dict)
    
    def test_stats_contains_expected_keys(self, test_agent):
        """Test stats contains all expected keys."""
        stats = test_agent.get_stats()
        assert "user_id" in stats
        assert "total_recommendations" in stats
        assert "current_epsilon" in stats
        assert "phase" in stats
