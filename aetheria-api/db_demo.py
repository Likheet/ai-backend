#!/usr/bin/env python3
"""Database demo script showing the new plan and routine_step functionality."""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


async def demo_database_operations():
    """Demonstrate database operations (mock version)."""
    print("\n" + "="*60)
    print("🗄️  DATABASE OPERATIONS DEMO")
    print("="*60)
    
    print("\n📋 New Tables Added:")
    print("-" * 30)
    
    print("1. PLAN TABLE:")
    print("   ├── id: UUID (Primary Key)")
    print("   ├── session_id: UUID (Unique, FK to assessment_session)")
    print("   ├── skin_profile: JSONB (skin analysis data)")
    print("   ├── rationale: JSONB (AI reasoning)")
    print("   └── created_at: TIMESTAMPTZ")
    
    print("\n2. ROUTINE_STEP TABLE:")
    print("   ├── id: UUID (Primary Key)")
    print("   ├── plan_id: UUID (FK to plan)")
    print("   ├── when: TEXT ('AM' or 'PM')")
    print("   ├── step_order: INTEGER")
    print("   ├── product_id: UUID (nullable)")
    print("   ├── instructions: TEXT")
    print("   └── day_of_week: INTEGER (0-6, nullable)")
    
    print("\n🔧 Database Helper Functions:")
    print("-" * 35)
    
    helpers = [
        "fetch_one(query, *args) -> Optional[Dict]",
        "fetch_all(query, *args) -> List[Dict]", 
        "execute(query, *args) -> Optional[str]",
        "transaction() -> AsyncContextManager[Connection]"
    ]
    
    for helper in helpers:
        print(f"   • {helper}")
    
    print("\n📊 Service Functions Available:")
    print("-" * 35)
    
    service_functions = [
        "create_plan(session_id, skin_profile, rationale)",
        "get_plan_by_id(plan_id)",
        "get_plan_by_session_id(session_id)",
        "create_routine_step(plan_id, when, step_order, instructions, ...)",
        "get_routine_steps_by_plan_id(plan_id)",
        "create_plan_with_routine_steps(session_id, skin_profile, rationale, am_steps, pm_steps)",
        "get_plan_with_routine_steps(plan_id)"
    ]
    
    for func in service_functions:
        print(f"   • {func}")
    
    print("\n💡 Example Usage:")
    print("-" * 20)
    
    example_skin_profile = {
        "skin_type": "combination",
        "concerns": ["acne", "dryness", "sensitivity"],
        "age_group": "20-30",
        "current_routine": "basic"
    }
    
    example_rationale = {
        "reasoning": "Based on combination skin with acne concerns, recommend gentle cleansing with hydrating products",
        "confidence_score": 0.87,
        "ai_model": "aetheria-v1.0"
    }
    
    example_am_steps = [
        {
            "instructions": "Apply gentle foam cleanser to damp skin, massage for 30 seconds",
            "product_id": None,
            "day_of_week": None
        },
        {
            "instructions": "Pat dry and apply lightweight moisturizer with SPF 30",
            "product_id": None,
            "day_of_week": None
        }
    ]
    
    example_pm_steps = [
        {
            "instructions": "Remove makeup with micellar water",
            "product_id": None,
            "day_of_week": None
        },
        {
            "instructions": "Apply salicylic acid toner (every other day)",
            "product_id": None,
            "day_of_week": None
        },
        {
            "instructions": "Apply night moisturizer",
            "product_id": None,
            "day_of_week": None
        }
    ]
    
    print("\n1. Create Plan with Routine Steps:")
    print(f"   session_id: 'session-123'")
    print(f"   skin_profile: {json.dumps(example_skin_profile, indent=14)}")
    print(f"   rationale: {json.dumps(example_rationale, indent=14)}")
    print(f"   am_steps: {len(example_am_steps)} steps")
    print(f"   pm_steps: {len(example_pm_steps)} steps")
    
    print("\n2. Query Example:")
    print("   SELECT p.*, COUNT(rs.id) as step_count")
    print("   FROM plan p")
    print("   LEFT JOIN routine_step rs ON p.id = rs.plan_id")
    print("   WHERE p.session_id = $1")
    print("   GROUP BY p.id;")
    
    print("\n📝 Migration Commands:")
    print("-" * 25)
    print("   # Run migration")
    print("   alembic upgrade head")
    print()
    print("   # Check current migration")  
    print("   alembic current")
    print()
    print("   # Rollback migration")
    print("   alembic downgrade -1")
    print()
    print("   # SQL sanity check")
    print("   SELECT count(*) FROM plan;")
    print("   SELECT count(*) FROM routine_step;")


def show_migration_file():
    """Show the migration file content."""
    print("\n" + "="*60)
    print("🔄 ALEMBIC MIGRATION FILE")
    print("="*60)
    
    migration_file = Path("alembic/versions/001_add_plan_routine_step.py")
    if migration_file.exists():
        print(f"\n📄 {migration_file}")
        print("-" * 60)
        
        with open(migration_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines, 1):
                print(f"{i:3d}: {line.rstrip()}")
    else:
        print("\n❌ Migration file not found!")


def show_db_service():
    """Show the database service file highlights."""
    print("\n" + "="*60)
    print("🔧 DATABASE SERVICE HIGHLIGHTS")
    print("="*60)
    
    service_file = Path("app/services/db_service.py")
    if service_file.exists():
        print(f"\n📄 Key functions in {service_file}:")
        print("-" * 50)
        
        with open(service_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract function definitions
        import re
        functions = re.findall(r'^async def (\w+)\(.*?\):', content, re.MULTILINE)
        
        for func in functions[:10]:  # Show first 10 functions
            print(f"   • {func}()")
            
        print(f"\n   ... and {len(functions) - 10} more functions" if len(functions) > 10 else "")
    else:
        print("\n❌ Database service file not found!")


async def main():
    """Main demo function."""
    print("🗄️  Aetheria API - Database Layer Demo")
    print("=" * 60)
    
    await demo_database_operations()
    show_migration_file()
    show_db_service()
    
    print("\n" + "="*60)
    print("🚀 NEXT STEPS")
    print("="*60)
    print()
    print("1. Set DATABASE_URL in .env file")
    print("2. Install dependencies: pip install -e .[dev]")
    print("3. Run migration: alembic upgrade head")
    print("4. Test connection: python -c \"from app.core.db import check_db_connection; import asyncio; print(asyncio.run(check_db_connection()))\"")
    print("5. Start API: uvicorn app.main:app --reload")
    print("6. Test: curl http://localhost:8000/healthz")
    print()
    print("🌟 Database layer ready for Supabase integration!")


if __name__ == "__main__":
    asyncio.run(main())
