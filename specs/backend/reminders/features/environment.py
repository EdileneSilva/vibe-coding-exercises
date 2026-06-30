"""
Environment setup and cleanup for behave tests
"""
import sys
import os
from sqlalchemy import create_engine

# Add api directory to path
project_root = '/home/edilene/Dropbox/Simplon_Projects/briefs-todo-app-starter'
api_path = os.path.join(project_root, 'api')
sys.path.insert(0, api_path)

from models import Base
from database import get_db
from fastapi.testclient import TestClient
import main as api_main

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = None

app = api_main.app


def before_all(context):
    """Setup before all tests"""
    global TestingSessionLocal
    
    from sqlalchemy.orm import sessionmaker
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Dependency override
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    context.client = TestClient(app)


def before_scenario(context, scenario):
    """Clean up before each scenario"""
    # Clear all tables
    with engine.connect() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.commit()
    
    # Reset context state
    context.reminders = {}
    context.subtasks = {}
    if hasattr(context, 'current_todo'):
        delattr(context, 'current_todo')
    if hasattr(context, 'current_todo_id'):
        delattr(context, 'current_todo_id')
    if hasattr(context, 'last_created_reminder'):
        delattr(context, 'last_created_reminder')
    if hasattr(context, 'reminder_instances'):
        delattr(context, 'reminder_instances')
    if hasattr(context, 'current_time'):
        delattr(context, 'current_time')
    if hasattr(context, 'last_error'):
        delattr(context, 'last_error')
    if hasattr(context, 'filtered_todos'):
        delattr(context, 'filtered_todos')


def after_scenario(context, scenario):
    """Clean up after each scenario"""
    # Clear all tables
    with engine.connect() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.commit()


def after_all(context):
    """Cleanup after all tests"""
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
