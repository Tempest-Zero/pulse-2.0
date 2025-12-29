"""
Graphiti client module for memory layer.

Provides:
- Resilient client with Neo4j fallback
- Pattern extraction and constraint conversion
- Storage functions
"""

from .resilient_client import resilient_client, patterns_to_constraints
from .pattern_extractor import (
    get_user_context,
    get_user_defaults,
    extract_patterns,
    store_user_defaults,
    store_edit,
    fetch_preferences
)
from .store import store_cold_start, store_acceptance

__all__ = [
    "resilient_client",
    "patterns_to_constraints",
    "get_user_context",
    "get_user_defaults",
    "extract_patterns",
    "store_user_defaults",
    "store_edit",
    "store_cold_start",
    "store_acceptance",
    "fetch_preferences"
]
