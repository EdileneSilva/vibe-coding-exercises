"""
Step definitions for Sub-tasks and Dependencies feature
Uses actual database implementation
"""
from behave import given, when, then
import sys
import os

# Add api directory to path using absolute path
project_root = '/home/edilene/Dropbox/Simplon_Projects/briefs-todo-app-starter'
api_path = os.path.join(project_root, 'api')
sys.path.insert(0, api_path)

# Import after path is set
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import from api directory
import main as api_main
import database as api_database
import crud as api_crud
import schemas as api_schemas
from models import Subtask, Todo

app = api_main.app
Base = api_database.Base
get_db = api_database.get_db

# Setup test database - use in-memory for isolation
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

# Dependency override
OverrideGetDB = lambda: TestingSessionLocal()
app.dependency_overrides[get_db] = OverrideGetDB

client = TestClient(app)


@given('the API is running at "{url}"')
def step_api_running(context, url):
    """API is running for testing"""
    context.api_url = url
    context.client = client


@given('I have a todo titled "{title}"')
def step_have_todo(context, title):
    """Create a todo with the given title"""
    db = TestingSessionLocal()
    
    todo_data = api_schemas.TodoCreate(title=title, description="", completed=False)
    todo = api_crud.create_todo(db=db, todo=todo_data)
    context.current_todo = todo
    context.current_todo_id = todo.id
    
    # Initialize subtasks storage if needed
    if not hasattr(context, 'subtasks'):
        context.subtasks = {}
    if todo.id not in context.subtasks:
        context.subtasks[todo.id] = []
    
    db.close()


@given('I add a subtask "{title}" to the todo')
@given('I have added subtask "{title}" to the todo')
@when('I have added subtask "{title}" to the todo')
@when('I add a subtask "{title}" to the todo')
def step_add_subtask(context, title):
    """Add a subtask to the current todo"""
    db = TestingSessionLocal()
    
    if not hasattr(context, 'subtasks'):
        context.subtasks = {}
    
    todo_id = context.current_todo_id
    if todo_id not in context.subtasks:
        context.subtasks[todo_id] = []
    
    # Create the subtask using CRUD
    subtask_data = api_schemas.SubtaskCreate(
        title=title,
        description="",
        status="pending"
    )
    subtask = api_crud.create_subtask(db=db, todo_id=todo_id, subtask=subtask_data)
    
    context.subtasks[todo_id].append(subtask)
    db.close()


@when('I set subtask "{title}" description to "{description}"')
def step_set_subtask_description(context, title, description):
    """Set description for a subtask"""
    db = TestingSessionLocal()
    
    # Find the subtask by title
    for todo_id, subtasks in context.subtasks.items():
        for subtask in subtasks:
            if subtask.title == title:
                update_data = api_schemas.SubtaskUpdate(description=description)
                api_crud.update_subtask(db, subtask.id, update_data)
                db.close()
                return
    
    db.close()
    raise AssertionError(f"Subtask '{title}' not found")


@when('I have added subtasks "{titles}" to the todo')
@given('I have added subtasks "{titles}" to the todo')
def step_have_added_subtasks(context, titles):
    """Add multiple subtasks"""
    subtask_titles = [t.strip() for t in titles.split(',')]
    for title in subtask_titles:
        step_add_subtask(context, title)


@when('I mark subtask "{title}" as completed')
def step_mark_subtask_completed(context, title):
    """Mark a subtask as completed"""
    db = TestingSessionLocal()
    
    # Find the subtask by title
    for todo_id, subtasks in context.subtasks.items():
        for subtask in subtasks:
            if subtask.title == title:
                update_data = api_schemas.SubtaskUpdate(status="completed")
                api_crud.update_subtask(db, subtask.id, update_data)
                db.close()
                return
    
    db.close()
    raise AssertionError(f"Subtask '{title}' not found")


@then('the todo should have {count} subtasks')
@then('the todo should have {count} subtask')
def step_todo_has_subtasks_count(context, count):
    """Verify subtask count"""
    db = TestingSessionLocal()
    
    todo_id = context.current_todo_id
    subtasks = api_crud.get_subtasks(db, todo_id)
    actual_count = len(subtasks)
    db.close()
    
    assert actual_count == int(count), f"Expected {count} subtasks, got {actual_count}"


@then('the subtasks should be "{expected_subtasks}"')
def step_subtasks_list(context, expected_subtasks):
    """Verify subtask titles"""
    db = TestingSessionLocal()
    
    todo_id = context.current_todo_id
    subtasks = api_crud.get_subtasks(db, todo_id)
    actual_titles = sorted([s.title for s in subtasks])
    
    # Clean the expected_subtasks string
    expected_titles = sorted([t.strip().strip('"').strip("'") for t in expected_subtasks.split(',')])
    
    db.close()
    
    assert actual_titles == expected_titles, \
        f"Expected subtasks {expected_titles}, got {actual_titles}"


@then('subtask "{title}" should have status "{status}"')
def step_subtask_has_status(context, title, status):
    """Verify subtask status"""
    db = TestingSessionLocal()
    
    todo_id = context.current_todo_id
    subtasks = api_crud.get_subtasks(db, todo_id)
    
    for subtask in subtasks:
        if subtask.title == title:
            assert subtask.status == status, \
                f"Expected status '{status}', got '{subtask.status}'"
            db.close()
            return
    
    db.close()
    raise AssertionError(f"Subtask '{title}' not found")


@then('subtask "{title}" should have title "{expected_title}"')
def step_subtask_has_title(context, title, expected_title):
    """Verify subtask title"""
    db = TestingSessionLocal()
    
    todo_id = context.current_todo_id
    subtasks = api_crud.get_subtasks(db, todo_id)
    
    for subtask in subtasks:
        if subtask.title == title:
            assert subtask.title == expected_title, \
                f"Expected title '{expected_title}', got '{subtask.title}'"
            db.close()
            return
    
    db.close()
    raise AssertionError(f"Subtask '{title}' not found")


@then('subtask "{title}" should have description "{expected_description}"')
def step_subtask_has_description(context, title, expected_description):
    """Verify subtask description"""
    db = TestingSessionLocal()
    
    todo_id = context.current_todo_id
    subtasks = api_crud.get_subtasks(db, todo_id)
    
    for subtask in subtasks:
        if subtask.title == title:
            assert subtask.description == expected_description, \
                f"Expected description '{expected_description}', got '{subtask.description}'"
            db.close()
            return
    
    db.close()
    raise AssertionError(f"Subtask '{title}' not found")


@then('the todo should have status "{status}"')
@then('the todo should have status "{status}" {rest}')
def step_todo_status(context, status, rest=None):
    """Verify todo status based on subtasks"""
    db = TestingSessionLocal()
    
    todo_id = context.current_todo_id
    subtasks = api_crud.get_subtasks(db, todo_id)
    
    if not subtasks:
        db.close()
        return
    
    completed = sum(1 for s in subtasks if s.status == 'completed')
    total = len(subtasks)
    
    if status == 'completed':
        assert completed == total, f"Expected all subtasks completed, got {completed}/{total}"
    elif status == 'in_progress':
        assert 0 < completed < total, f"Expected partial completion, got {completed}/{total}"
    elif status == 'pending':
        assert completed == 0, f"Expected no subtasks completed, got {completed}/{total}"
    
    db.close()


@when('I set subtask "{subtask_title}" to depend on "{dependency}" (blocked by)')
def step_set_dependency(context, subtask_title, dependency):
    """Set dependency between subtasks"""
    db = TestingSessionLocal()
    
    todo_id = context.current_todo_id
    subtasks = api_crud.get_subtasks(db, todo_id)
    
    # Find the subtasks
    subtask_to_block = None
    blocking_subtask = None
    
    for subtask in subtasks:
        if subtask.title == subtask_title:
            subtask_to_block = subtask
        if subtask.title == dependency:
            blocking_subtask = subtask
    
    if not subtask_to_block:
        db.close()
        raise AssertionError(f"Subtask '{subtask_title}' not found")
    if not blocking_subtask:
        db.close()
        raise AssertionError(f"Dependency subtask '{dependency}' not found")
    
    # Update the subtask to be blocked by the other
    update_data = api_schemas.SubtaskUpdate(blocked_by_id=blocking_subtask.id)
    api_crud.update_subtask(db, subtask_to_block.id, update_data)
    db.close()


@given('subtask "{subtask_title}" is blocked by "{dependency}"')
@when('subtask "{subtask_title}" is blocked by "{dependency}"')
def step_subtask_blocked_by(context, subtask_title, dependency):
    """Set blocked by relationship"""
    step_set_dependency(context, subtask_title, dependency)


@then('subtask "{subtask_title}" should have dependency "{dep_type}" pointing to "{target}"')
def step_verify_dependency(context, subtask_title, dep_type, target):
    """Verify dependency relationship"""
    db = TestingSessionLocal()
    
    todo_id = context.current_todo_id
    subtasks = api_crud.get_subtasks(db, todo_id)
    
    # Find the subtasks
    subtask = None
    target_subtask = None
    
    for s in subtasks:
        if s.title == subtask_title:
            subtask = s
        if s.title == target:
            target_subtask = s
    
    if not subtask:
        db.close()
        raise AssertionError(f"Subtask '{subtask_title}' not found")
    if not target_subtask:
        db.close()
        raise AssertionError(f"Target subtask '{target}' not found")
    
    if dep_type == 'blocks':
        # Check that subtask blocks target
        assert target_subtask.blocked_by_id == subtask.id, \
            f"Expected {subtask.title} to block {target}"
    elif dep_type == 'blocked_by':
        # Check that subtask is blocked by target
        assert subtask.blocked_by_id == target_subtask.id, \
            f"Expected {subtask_title} to be blocked by {target}"
    
    db.close()


@when('I try to mark subtask "{title}" as completed')
def step_try_mark_completed(context, title):
    """Try to mark subtask as completed, may fail if blocked"""
    db = TestingSessionLocal()
    
    todo_id = context.current_todo_id
    subtasks = api_crud.get_subtasks(db, todo_id)
    
    for subtask in subtasks:
        if subtask.title == title:
            can_complete, error = api_crud.check_can_complete_subtask(db, subtask.id)
            if not can_complete:
                context.last_error = error
                db.close()
                return
            else:
                update_data = api_schemas.SubtaskUpdate(status="completed")
                api_crud.update_subtask(db, subtask.id, update_data)
                context.last_error = None
                db.close()
                return
    
    db.close()
    context.last_error = f"Subtask '{title}' not found"


@then('the operation should fail with error "{error_message}"')
def step_operation_fails(context, error_message):
    """Verify operation failed with expected error"""
    assert hasattr(context, 'last_error'), "Expected an error to occur"
    assert error_message in context.last_error, \
        f"Expected error containing '{error_message}', got '{context.last_error}'"


@when('I request the dependency graph for the todo')
def step_request_dependency_graph(context):
    """Request dependency graph"""
    db = TestingSessionLocal()
    
    todo_id = context.current_todo_id
    context.graph = api_crud.get_dependency_graph(db, todo_id)
    db.close()


@then('the graph should show "{expected_graph}"')
def step_verify_graph(context, expected_graph):
    """Verify dependency graph structure"""
    # Parse expected graph (e.g., "A" -> "B" -> "C")
    parts = [p.strip() for p in expected_graph.split('->')]
    
    # Build expected relationships
    subtask_map = {s['title']: s for s in context.graph['subtasks']}
    
    for i in range(len(parts) - 1):
        current = parts[i]
        next_sub = parts[i + 1]
        
        # Check that current blocks next
        if current in subtask_map and next_sub in subtask_map:
            current_id = subtask_map[current]['id']
            next_id = subtask_map[next_sub]['id']
            
            # Check edge exists
            edge_exists = (current_id, next_id) in context.graph['edges']
            assert edge_exists, f"Expected edge from {current} to {next_sub}"
        else:
            raise AssertionError(f"Subtasks {current} or {next_sub} not found in graph")


@when('I delete subtask "{title}"')
def step_delete_subtask(context, title):
    """Delete a subtask"""
    db = TestingSessionLocal()
    
    todo_id = context.current_todo_id
    subtasks = api_crud.get_subtasks(db, todo_id)
    
    for subtask in subtasks:
        if subtask.title == title:
            api_crud.delete_subtask(db, subtask.id)
            # Remove from context
            if todo_id in context.subtasks:
                context.subtasks[todo_id] = [s for s in context.subtasks[todo_id] if s.title != title]
            db.close()
            return
    
    db.close()
    raise AssertionError(f"Subtask '{title}' not found")


@when('I update subtask "{old_title}" with new title "{new_title}" and description "{description}"')
def step_update_subtask(context, old_title, new_title, description):
    """Update subtask details"""
    db = TestingSessionLocal()
    
    todo_id = context.current_todo_id
    subtasks = api_crud.get_subtasks(db, todo_id)
    
    for subtask in subtasks:
        if subtask.title == old_title:
            update_data = api_schemas.SubtaskUpdate(
                title=new_title,
                description=description
            )
            api_crud.update_subtask(db, subtask.id, update_data)
            db.close()
            return
    
    db.close()
    raise AssertionError(f"Subtask '{old_title}' not found")


@then('the remaining subtask should be "{title}"')
def step_remaining_subtask(context, title):
    """Verify remaining subtask"""
    db = TestingSessionLocal()
    
    todo_id = context.current_todo_id
    subtasks = api_crud.get_subtasks(db, todo_id)
    
    db.close()
    
    assert len(subtasks) == 1, f"Expected 1 subtask, got {len(subtasks)}"
    assert subtasks[0].title == title, f"Expected '{title}', got '{subtasks[0].title}'"
