#!/usr/bin/env python3
"""Demo script to show the Aetheria API structure and test basic functionality."""

import os
import subprocess
import sys
from pathlib import Path


def print_tree(directory: Path, prefix: str = "", max_depth: int = 3, current_depth: int = 0) -> None:
    """Print directory tree structure."""
    if current_depth >= max_depth:
        return
    
    items = list(directory.iterdir())
    items.sort(key=lambda x: (x.is_file(), x.name.lower()))
    
    for i, item in enumerate(items):
        # Skip certain files/directories
        skip_items = {
            '__pycache__', '.git', '.pytest_cache', '.mypy_cache', 
            '.ruff_cache', 'node_modules', '.venv', 'venv'
        }
        if item.name in skip_items:
            continue
            
        is_last = i == len(items) - 1
        current_prefix = "└── " if is_last else "├── "
        print(f"{prefix}{current_prefix}{item.name}")
        
        if item.is_dir() and current_depth < max_depth - 1:
            extension = "    " if is_last else "│   "
            print_tree(item, prefix + extension, max_depth, current_depth + 1)


def show_key_files():
    """Show content of key configuration files."""
    key_files = [
        "pyproject.toml",
        "app/main.py",
        "app/core/config.py",
        "docker-compose.yml",
        "Dockerfile",
        "Makefile"
    ]
    
    for file_path in key_files:
        full_path = Path(file_path)
        if full_path.exists():
            print(f"\n{'='*60}")
            print(f"📄 {file_path}")
            print('='*60)
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Show first 30 lines to avoid too much output
                for i, line in enumerate(lines[:30], 1):
                    print(f"{i:3d}: {line.rstrip()}")
                if len(lines) > 30:
                    print(f"... ({len(lines) - 30} more lines)")


def main():
    """Main demo function."""
    print("🚀 Aetheria Salon AI Backend - Project Overview")
    print("=" * 60)
    
    # Show project structure
    print("\n📁 Project Structure:")
    print("-" * 30)
    current_dir = Path(".")
    print_tree(current_dir)
    
    # Show key files
    print("\n📋 Key Configuration Files:")
    show_key_files()
    
    print("\n" + "="*60)
    print("🎯 Quick Start Commands:")
    print("="*60)
    print()
    print("1. Install dependencies:")
    print("   pip install -e .[dev]")
    print()
    print("2. Setup environment:")
    print("   cp .env.example .env")
    print("   # Edit .env with your database URL")
    print()
    print("3. Run the API:")
    print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8080")
    print()
    print("4. Test health endpoint:")
    print("   curl http://localhost:8080/healthz")
    print()
    print("5. View API documentation:")
    print("   http://localhost:8080/docs")
    print()
    print("6. Run with Docker:")
    print("   docker-compose up --build")
    print()
    print("7. Run tests:")
    print("   pytest -v")
    print()
    print("🌟 Happy coding with Aetheria API!")


if __name__ == "__main__":
    main()
