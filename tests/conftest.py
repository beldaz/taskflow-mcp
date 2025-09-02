"""Pytest configuration and fixtures for taskflow-mcp tests."""

import os
import tempfile
import shutil
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_base_dir(temp_dir: Path) -> Generator[Path, None, None]:
    """Create a mock .tasks directory for testing."""
    base_dir = temp_dir / ".tasks"
    base_dir.mkdir()
    yield base_dir


@pytest.fixture
def sample_checklist() -> list[dict]:
    """Sample checklist data for testing."""
    return [
        {
            "label": "Set up project structure",
            "status": "done",
            "notes": "Completed initial setup",
        },
        {
            "label": "Write tests",
            "status": "in-progress",
            "notes": "Working on test coverage",
        },
        {"label": "Add documentation", "status": "pending", "notes": None},
    ]


@pytest.fixture
def sample_investigation_content() -> str:
    """Sample investigation content for testing."""
    return """# Investigation

## Problem
The application is experiencing performance issues.

## Root Cause
After analysis, we found that the database queries are not optimized.

## Impact
Users are experiencing slow response times.
"""


@pytest.fixture
def sample_solution_plan_content() -> str:
    """Sample solution plan content for testing."""
    return """# Solution Plan

## Approach
Implement database query optimization and caching.

## Implementation Steps
1. Add database indexes
2. Implement query caching
3. Optimize slow queries

## Timeline
Expected completion: 2 weeks
"""
