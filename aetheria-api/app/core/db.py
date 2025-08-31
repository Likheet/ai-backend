"""Database connection and configuration."""

import asyncpg
from asyncpg import Pool, Connection, Record
from typing import Optional, Dict, List, Any, AsyncGenerator
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

# Global connection pool
_pool: Optional[Pool] = None


async def create_db_pool() -> Pool:
    """Create and return database connection pool."""
    global _pool
    
    if _pool is None:
        logger.info("Creating database connection pool")
        _pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=5,
            max_size=20,
            command_timeout=60,
            server_settings={
                "jit": "off",
                "timezone": "UTC",  # Always store in UTC
            }
        )
        logger.info("Database connection pool created")
    
    return _pool


async def get_db_pool() -> Pool:
    """Get the database connection pool."""
    if _pool is None:
        return await create_db_pool()
    return _pool


async def close_db_pool() -> None:
    """Close the database connection pool."""
    global _pool
    
    if _pool is not None:
        logger.info("Closing database connection pool")
        await _pool.close()
        _pool = None
        logger.info("Database connection pool closed")


def record_to_dict(record: Optional[Record]) -> Optional[Dict[str, Any]]:
    """Convert asyncpg Record to dictionary."""
    if record is None:
        return None
    return dict(record)


def records_to_dicts(records: List[Record]) -> List[Dict[str, Any]]:
    """Convert list of asyncpg Records to list of dictionaries."""
    return [dict(record) for record in records]


async def fetch_one(query: str, *args) -> Optional[Dict[str, Any]]:
    """Execute query and return single record as dictionary."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        logger.debug("Executing fetch_one", query=query[:100])
        record = await conn.fetchrow(query, *args)
        return record_to_dict(record)


async def fetch_all(query: str, *args) -> List[Dict[str, Any]]:
    """Execute query and return all records as list of dictionaries."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        logger.debug("Executing fetch_all", query=query[:100])
        records = await conn.fetch(query, *args)
        return records_to_dicts(records)


async def execute(query: str, *args) -> Optional[str]:
    """Execute query and return command tag."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        logger.debug("Executing command", query=query[:100])
        result = await conn.execute(query, *args)
        return result


@asynccontextmanager
async def transaction() -> AsyncGenerator[Connection, None]:
    """Create a database transaction context manager."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            logger.debug("Started database transaction")
            yield conn
            logger.debug("Committed database transaction")


async def check_db_connection() -> bool:
    """Check if database connection is healthy."""
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return True
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        return False


async def check_existing_tables() -> Dict[str, bool]:
    """Check which tables exist in the database."""
    try:
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('customer', 'assessment_session', 'intake_form', 'machine_scan', 'machine_metric', 'plan', 'routine_step')
        """
        records = await fetch_all(query)
        existing_tables = {record['table_name'] for record in records}
        
        expected_tables = ['customer', 'assessment_session', 'intake_form', 'machine_scan', 'machine_metric', 'plan', 'routine_step']
        return {table: table in existing_tables for table in expected_tables}
    except Exception as e:
        logger.error("Failed to check existing tables", error=str(e))
        return {}
