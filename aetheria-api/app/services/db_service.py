"""Database service functions for plan and routine_step tables."""

from typing import Any, Dict, List, Optional, UUID
import uuid
from datetime import datetime

from app.core.db import fetch_one, fetch_all, execute, transaction
from app.core.logging import get_logger

logger = get_logger(__name__)


# Plan table operations
async def create_plan(
    session_id: str, 
    skin_profile: Dict[str, Any], 
    rationale: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Create a new plan for an assessment session."""
    try:
        query = """
        INSERT INTO plan (session_id, skin_profile, rationale, created_at)
        VALUES ($1, $2, $3, $4)
        RETURNING id, session_id, skin_profile, rationale, created_at
        """
        
        result = await fetch_one(
            query,
            session_id,
            skin_profile,
            rationale,
            datetime.utcnow()
        )
        
        logger.info("Created plan", plan_id=result['id'] if result else None, session_id=session_id)
        return result
        
    except Exception as e:
        logger.error("Failed to create plan", error=str(e), session_id=session_id)
        return None


async def get_plan_by_id(plan_id: str) -> Optional[Dict[str, Any]]:
    """Get a plan by its ID."""
    query = """
    SELECT id, session_id, skin_profile, rationale, created_at
    FROM plan 
    WHERE id = $1
    """
    return await fetch_one(query, plan_id)


async def get_plan_by_session_id(session_id: str) -> Optional[Dict[str, Any]]:
    """Get a plan by assessment session ID."""
    query = """
    SELECT id, session_id, skin_profile, rationale, created_at
    FROM plan 
    WHERE session_id = $1
    """
    return await fetch_one(query, session_id)


async def list_plans(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """List all plans with pagination."""
    query = """
    SELECT id, session_id, skin_profile, rationale, created_at
    FROM plan 
    ORDER BY created_at DESC
    LIMIT $1 OFFSET $2
    """
    return await fetch_all(query, limit, offset)


# Routine Step table operations
async def create_routine_step(
    plan_id: str,
    when: str,
    step_order: int,
    instructions: str,
    product_id: Optional[str] = None,
    day_of_week: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """Create a new routine step."""
    try:
        query = """
        INSERT INTO routine_step (plan_id, "when", step_order, product_id, instructions, day_of_week)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id, plan_id, "when", step_order, product_id, instructions, day_of_week
        """
        
        result = await fetch_one(
            query,
            plan_id,
            when,
            step_order,
            product_id,
            instructions,
            day_of_week
        )
        
        logger.info("Created routine step", 
                   step_id=result['id'] if result else None, 
                   plan_id=plan_id,
                   when=when,
                   step_order=step_order)
        return result
        
    except Exception as e:
        logger.error("Failed to create routine step", error=str(e), plan_id=plan_id)
        return None


async def get_routine_steps_by_plan_id(plan_id: str) -> List[Dict[str, Any]]:
    """Get all routine steps for a plan, ordered by when and step_order."""
    query = """
    SELECT id, plan_id, "when", step_order, product_id, instructions, day_of_week
    FROM routine_step 
    WHERE plan_id = $1
    ORDER BY "when", step_order
    """
    return await fetch_all(query, plan_id)


async def get_routine_steps_by_plan_and_when(plan_id: str, when: str) -> List[Dict[str, Any]]:
    """Get routine steps for a specific plan and time (AM/PM)."""
    query = """
    SELECT id, plan_id, "when", step_order, product_id, instructions, day_of_week
    FROM routine_step 
    WHERE plan_id = $1 AND "when" = $2
    ORDER BY step_order
    """
    return await fetch_all(query, plan_id, when)


async def delete_routine_steps_by_plan_id(plan_id: str) -> Optional[str]:
    """Delete all routine steps for a plan."""
    query = """
    DELETE FROM routine_step 
    WHERE plan_id = $1
    """
    result = await execute(query, plan_id)
    logger.info("Deleted routine steps", plan_id=plan_id, result=result)
    return result


# Complex operations using transactions
async def create_plan_with_routine_steps(
    session_id: str,
    skin_profile: Dict[str, Any],
    rationale: Dict[str, Any],
    am_steps: List[Dict[str, Any]],
    pm_steps: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """Create a plan with its routine steps in a single transaction."""
    try:
        async with transaction() as conn:
            # Create the plan
            plan_query = """
            INSERT INTO plan (session_id, skin_profile, rationale, created_at)
            VALUES ($1, $2, $3, $4)
            RETURNING id, session_id, skin_profile, rationale, created_at
            """
            
            plan_record = await conn.fetchrow(
                plan_query,
                session_id,
                skin_profile,
                rationale,
                datetime.utcnow()
            )
            
            if not plan_record:
                logger.error("Failed to create plan in transaction")
                return None
                
            plan_id = str(plan_record['id'])
            
            # Create AM routine steps
            for i, step in enumerate(am_steps):
                step_query = """
                INSERT INTO routine_step (plan_id, "when", step_order, product_id, instructions, day_of_week)
                VALUES ($1, $2, $3, $4, $5, $6)
                """
                await conn.execute(
                    step_query,
                    plan_id,
                    'AM',
                    i + 1,
                    step.get('product_id'),
                    step['instructions'],
                    step.get('day_of_week')
                )
            
            # Create PM routine steps
            for i, step in enumerate(pm_steps):
                step_query = """
                INSERT INTO routine_step (plan_id, "when", step_order, product_id, instructions, day_of_week)
                VALUES ($1, $2, $3, $4, $5, $6)
                """
                await conn.execute(
                    step_query,
                    plan_id,
                    'PM',
                    i + 1,
                    step.get('product_id'),
                    step['instructions'],
                    step.get('day_of_week')
                )
            
            logger.info("Created plan with routine steps", 
                       plan_id=plan_id, 
                       am_steps_count=len(am_steps),
                       pm_steps_count=len(pm_steps))
            
            return dict(plan_record)
            
    except Exception as e:
        logger.error("Failed to create plan with routine steps", error=str(e))
        return None


async def get_plan_with_routine_steps(plan_id: str) -> Optional[Dict[str, Any]]:
    """Get a plan with all its routine steps."""
    plan = await get_plan_by_id(plan_id)
    if not plan:
        return None
    
    routine_steps = await get_routine_steps_by_plan_id(plan_id)
    
    # Group steps by when (AM/PM)
    am_steps = [step for step in routine_steps if step['when'] == 'AM']
    pm_steps = [step for step in routine_steps if step['when'] == 'PM']
    
    return {
        **plan,
        'am_steps': am_steps,
        'pm_steps': pm_steps,
        'total_steps': len(routine_steps)
    }
