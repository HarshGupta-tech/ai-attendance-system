"""Initial setup script for the AI Attendance System.

This script:
1. Creates the database tables
2. Runs the seed script
3. Creates necessary directories

Usage:
    python scripts/setup.py
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def setup():
    print('=' * 60)
    print('AI Attendance System - Initial Setup')
    print('=' * 60)
    print()
    
    # 1. Create directories
    dirs = ['backend/uploads', 'backend/uploads/faces', 'backend/logs', 'backend/models']
    for d in dirs:
        path = os.path.join(os.path.dirname(__file__), '..', d)
        os.makedirs(path, exist_ok=True)
        print(f'  Created directory: {d}')
    
    # 2. Create database tables
    print('\nCreating database tables...')
    from app.database.session import engine, Base
    from app.models import *  # Import all models
    Base.metadata.create_all(bind=engine)
    print('  Database tables created.')
    
    # 3. Seed database
    print('\nSeeding database...')
    from seed_database import seed
    seed()
    
    print('\n' + '=' * 60)
    print('Setup complete!')
    print('\nTo start the backend:')
    print('  cd backend && uvicorn app.main:app --reload')
    print('\nTo start the frontend:')
    print('  cd frontend && npm run dev')
    print('=' * 60)

if __name__ == '__main__':
    setup()
