"""Test database functionality."""

import pytest
from unittest.mock import AsyncMock, patch
from app.services.db_service import (
    create_plan,
    get_plan_by_id,
    create_routine_step,
    get_routine_steps_by_plan_id,
    create_plan_with_routine_steps
)


@pytest.mark.asyncio
async def test_create_plan():
    """Test creating a plan."""
    session_id = "test-session-123"
    skin_profile = {"skin_type": "combination", "concerns": ["acne", "dryness"]}
    rationale = {"reason": "AI-generated plan", "confidence": 0.85}
    
    # Mock the database call
    with patch('app.services.db_service.fetch_one') as mock_fetch:
        mock_fetch.return_value = {
            'id': 'plan-123',
            'session_id': session_id,
            'skin_profile': skin_profile,
            'rationale': rationale,
            'created_at': '2024-01-01T12:00:00Z'
        }
        
        result = await create_plan(session_id, skin_profile, rationale)
        
        assert result is not None
        assert result['session_id'] == session_id
        assert result['skin_profile'] == skin_profile
        assert result['rationale'] == rationale


@pytest.mark.asyncio
async def test_create_routine_step():
    """Test creating a routine step."""
    plan_id = "plan-123"
    when = "AM"
    step_order = 1
    instructions = "Apply gentle cleanser to damp skin"
    
    with patch('app.services.db_service.fetch_one') as mock_fetch:
        mock_fetch.return_value = {
            'id': 'step-123',
            'plan_id': plan_id,
            'when': when,
            'step_order': step_order,
            'product_id': None,
            'instructions': instructions,
            'day_of_week': None
        }
        
        result = await create_routine_step(
            plan_id, when, step_order, instructions
        )
        
        assert result is not None
        assert result['plan_id'] == plan_id
        assert result['when'] == when
        assert result['step_order'] == step_order
        assert result['instructions'] == instructions


@pytest.mark.asyncio
async def test_get_routine_steps_by_plan_id():
    """Test retrieving routine steps by plan ID."""
    plan_id = "plan-123"
    
    with patch('app.services.db_service.fetch_all') as mock_fetch:
        mock_fetch.return_value = [
            {
                'id': 'step-1',
                'plan_id': plan_id,
                'when': 'AM',
                'step_order': 1,
                'product_id': None,
                'instructions': 'Step 1',
                'day_of_week': None
            },
            {
                'id': 'step-2',
                'plan_id': plan_id,
                'when': 'AM',
                'step_order': 2,
                'product_id': None,
                'instructions': 'Step 2',
                'day_of_week': None
            }
        ]
        
        result = await get_routine_steps_by_plan_id(plan_id)
        
        assert len(result) == 2
        assert result[0]['when'] == 'AM'
        assert result[0]['step_order'] == 1
        assert result[1]['step_order'] == 2


def test_database_helper_imports():
    """Test that database helpers can be imported."""
    from app.core.db import fetch_one, fetch_all, execute, transaction
    
    # Just test that imports work
    assert fetch_one is not None
    assert fetch_all is not None
    assert execute is not None
    assert transaction is not None
