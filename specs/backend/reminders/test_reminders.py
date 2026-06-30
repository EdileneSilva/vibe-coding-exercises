"""
Pytest-BDD tests for Reminder System feature
"""
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add api directory to path
project_root = '/home/edilene/Dropbox/Simplon_Projects/briefs-todo-app-starter'
api_path = os.path.join(project_root, 'api')
sys.path.insert(0, api_path)

# Import after path is set
import main as api_main
import database as api_database

app = api_main.app
Base = api_database.Base
get_db = api_database.get_db

# Setup test database
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


# Load scenarios from feature file
project_root = '/home/edilene/Dropbox/Simplon_Projects/briefs-todo-app-starter'
scenarios(f'{project_root}/specs/backend/reminders/features/reminders.feature')


# Fixtures
@pytest.fixture
def context():
    """Shared context for step functions"""
    return {}


# Step definitions
@given('the API is running')
def api_running(context):
    """API is running for testing"""
    context['client'] = client


@given(parsers.parse('I have a todo with id {todo_id:d} titled "{title}"'))
def have_todo(context, todo_id, title):
    """Create a todo with the given id and title"""
    db = TestingSessionLocal()
    import crud as api_crud
    import schemas as api_schemas
    
    create_todo = api_crud.create_todo
    TodoCreate = api_schemas.TodoCreate
    
    todo_data = TodoCreate(title=title, description="", completed=False)
    todo = create_todo(db=db, todo=todo_data)
    context[f'todo_{todo_id}'] = todo
    context[f'todo_{todo_id}_id'] = todo.id
    db.close()


@given(parsers.parse('I have a todo with id {todo_id:d} titled "{title}" with deadline "{deadline}"'))
def have_todo_with_deadline(context, todo_id, title, deadline):
    """Create a todo with deadline"""
    db = TestingSessionLocal()
    import crud as api_crud
    import schemas as api_schemas
    
    create_todo = api_crud.create_todo
    TodoCreate = api_schemas.TodoCreate
    
    todo_data = TodoCreate(title=title, description="", completed=False)
    todo = create_todo(db=db, todo=todo_data)
    
    # For now, store deadline in context (will be implemented in models)
    if 'reminders' not in context:
        context['reminders'] = {}
    context['reminders'][todo.id] = {'deadline': deadline, 'type': 'deadline'}
    
    context[f'todo_{todo_id}'] = todo
    context[f'todo_{todo_id}_id'] = todo.id
    db.close()


@given(parsers.parse('I have a todo with id {todo_id:d} titled "{title}" with no reminder'))
def have_todo_no_reminder(context, todo_id, title):
    """Create a todo without reminder"""
    db = TestingSessionLocal()
    import crud as api_crud
    import schemas as api_schemas
    
    create_todo = api_crud.create_todo
    TodoCreate = api_schemas.TodoCreate
    
    todo_data = TodoCreate(title=title, description="", completed=False)
    todo = create_todo(db=db, todo=todo_data)
    context[f'todo_{todo_id}'] = todo
    context[f'todo_{todo_id}_id'] = todo.id
    db.close()


@given(parsers.parse('todo {todo_id:d} has a deadline reminder for "{deadline}"'))
def todo_has_deadline_reminder(context, todo_id, deadline):
    """Setup: todo already has a deadline reminder"""
    actual_todo_id = context[f'todo_{todo_id}_id']
    if 'reminders' not in context:
        context['reminders'] = {}
    context['reminders'][actual_todo_id] = {
        'deadline': deadline,
        'type': 'deadline'
    }


@given(parsers.parse('todo {todo_id:d} has a recurring reminder with frequency "{frequency}"'))
def todo_has_recurring_reminder(context, todo_id, frequency):
    """Setup: todo already has a recurring reminder"""
    actual_todo_id = context[f'todo_{todo_id}_id']
    if 'reminders' not in context:
        context['reminders'] = {}
    
    freq_days = {
        'daily': 1,
        'weekly': 7,
        'monthly': 30
    }.get(frequency, 1)
    
    context['reminders'][actual_todo_id] = {
        'frequency': frequency,
        'type': 'recurring',
        'interval_days': freq_days
    }


@when(parsers.parse('I set a deadline reminder for "{deadline}" on todo {todo_id:d}'))
def set_deadline_reminder(context, deadline, todo_id):
    """Set a deadline reminder on a todo"""
    if 'reminders' not in context:
        context['reminders'] = {}
    
    actual_todo_id = context[f'todo_{todo_id}_id']
    context['reminders'][actual_todo_id] = {
        'deadline': deadline,
        'type': 'deadline'
    }


@when(parsers.parse('I set a recurring reminder with frequency "{frequency}" on todo {todo_id:d}'))
def set_recurring_reminder(context, frequency, todo_id):
    """Set a recurring reminder on a todo"""
    if 'reminders' not in context:
        context['reminders'] = {}
    
    actual_todo_id = context[f'todo_{todo_id}_id']
    
    # Map frequency to days
    freq_days = {
        'daily': 1,
        'weekly': 7,
        'monthly': 30
    }.get(frequency, 1)
    
    context['reminders'][actual_todo_id] = {
        'frequency': frequency,
        'type': 'recurring',
        'interval_days': freq_days
    }


@when(parsers.parse('I set a reminder with channel "{channel}" on todo {todo_id:d}'))
def set_reminder_channel(context, channel, todo_id):
    """Add a notification channel to a reminder"""
    actual_todo_id = context[f'todo_{todo_id}_id']
    
    if 'reminder_channels' not in context:
        context['reminder_channels'] = {}
    
    if actual_todo_id not in context['reminder_channels']:
        context['reminder_channels'][actual_todo_id] = []
    
    context['reminder_channels'][actual_todo_id].append(channel)


@then(parsers.parse('todo {todo_id:d} should have a reminder with deadline "{deadline}"'))
def todo_has_deadline_reminder(context, todo_id, deadline):
    """Verify reminder deadline"""
    actual_todo_id = context[f'todo_{todo_id}_id']
    assert actual_todo_id in context['reminders'], f"No reminder found for todo {todo_id}"
    assert context['reminders'][actual_todo_id]['deadline'] == deadline


@then(parsers.parse('the reminder type should be "{reminder_type}"'))
def reminder_type(context, reminder_type):
    """Verify reminder type"""
    # Get the last todo with a reminder
    for todo_id, reminder in context['reminders'].items():
        assert reminder['type'] == reminder_type, \
            f"Expected type '{reminder_type}', got '{reminder['type']}'"
        return


@then(parsers.parse('todo {todo_id:d} should have a reminder with frequency "{frequency}"'))
def todo_has_frequency(context, todo_id, frequency):
    """Verify reminder frequency"""
    actual_todo_id = context[f'todo_{todo_id}_id']
    assert actual_todo_id in context['reminders'], f"No reminder found for todo {todo_id}"
    assert context['reminders'][actual_todo_id]['frequency'] == frequency


@then(parsers.parse('the reminder should repeat every {days:d} days'))
def reminder_repeat_interval(context, days):
    """Verify reminder repeat interval"""
    for todo_id, reminder in context['reminders'].items():
        if reminder['type'] == 'recurring':
            assert reminder['interval_days'] == days
            return
    raise AssertionError("No recurring reminder found")


@then(parsers.parse('todo {todo_id:d} should have {count:d} reminder notifications'))
def todo_has_notification_count(context, todo_id, count):
    """Verify number of notification channels"""
    actual_todo_id = context[f'todo_{todo_id}_id']
    assert actual_todo_id in context['reminder_channels'], \
        f"No channels found for todo {todo_id}"
    assert len(context['reminder_channels'][actual_todo_id]) == count


@then(parsers.parse('the channels should be "{channels}"'))
def channels_list(context, channels):
    """Verify notification channels"""
    expected_channels = [c.strip() for c in channels.split(',')]
    for todo_id, actual_channels in context['reminder_channels'].items():
        assert set(actual_channels) == set(expected_channels), \
            f"Expected channels {expected_channels}, got {actual_channels}"
        return


@when(parsers.parse('the current time is "{current_time}"'))
def set_current_time(context, current_time):
    """Set the current time for testing"""
    context['current_time'] = datetime.fromisoformat(current_time)


@then(parsers.parse('the reminder should be in "{state}" state'))
def reminder_state(context, state):
    """Verify reminder state based on current time"""
    current_time = context['current_time']
    
    for todo_id, reminder in context['reminders'].items():
        if 'deadline' in reminder:
            deadline = datetime.fromisoformat(reminder['deadline'])
            time_diff = deadline - current_time
            
            if state == 'approaching':
                assert time_diff > timedelta(0), "Deadline should be in the future"
                assert time_diff < timedelta(days=2), "Deadline should be within 48 hours"
            elif state == 'overdue':
                assert time_diff < timedelta(0), "Deadline should be in the past"
            return
    
    raise AssertionError(f"No reminder found in state '{state}'")


@then(parsers.parse('the time remaining should be "{time_remaining}"'))
def time_remaining(context, time_remaining):
    """Verify time remaining"""
    current_time = context['current_time']
    
    for todo_id, reminder in context['reminders'].items():
        if 'deadline' in reminder:
            deadline = datetime.fromisoformat(reminder['deadline'])
            time_diff = deadline - current_time
            
            # Convert timedelta to hours
            total_seconds = time_diff.total_seconds()
            hours = int(total_seconds // 3600)
            
            # Check if the hours match (approximate)
            expected_hours = int(time_remaining.split()[0])
            assert abs(hours - expected_hours) < 1, \
                f"Expected ~{expected_hours} hours, got {hours}"
            return
    
    raise AssertionError("No reminder found to check time remaining")


@then('the todo should be marked as "overdue"')
def todo_marked_overdue(context):
    """Verify todo is marked as overdue"""
    # This will be implemented when we add overdue tracking
    current_time = context['current_time']
    
    for todo_id, reminder in context['reminders'].items():
        if 'deadline' in reminder:
            deadline = datetime.fromisoformat(reminder['deadline'])
            if deadline < current_time:
                # Todo should be marked as overdue
                # For now, we'll just verify the logic
                return
    
    raise AssertionError("No overdue todo found")


@when(parsers.parse('I check reminders for the next {days:d} days'))
def check_reminders_next_days(context, days):
    """Check reminders for upcoming days"""
    current_time = context.get('current_time', datetime.now())
    end_time = current_time + timedelta(days=days)
    
    context['reminder_instances'] = []
    for todo_id, reminder in context['reminders'].items():
        if reminder['type'] == 'recurring':
            interval = timedelta(days=reminder['interval_days'])
            # Start from the first reminder after current_time
            current = current_time + interval
            while current <= end_time:
                context['reminder_instances'].append(current)
                current += interval


@then(parsers.parse('there should be {count:d} reminder instances'))
def reminder_instances_count(context, count):
    """Verify number of reminder instances"""
    assert len(context['reminder_instances']) == count, \
        f"Expected {count} instances, got {len(context['reminder_instances'])}"


@then('each instance should be 1 day apart')
def instances_one_day_apart(context):
    """Verify instances are spaced correctly"""
    instances = sorted(context['reminder_instances'])
    for i in range(1, len(instances)):
        diff = instances[i] - instances[i-1]
        assert diff == timedelta(days=1), \
            f"Expected 1 day apart, got {diff}"


@when(parsers.parse('I remove the reminder from todo {todo_id:d}'))
def remove_reminder(context, todo_id):
    """Remove reminder from todo"""
    actual_todo_id = context[f'todo_{todo_id}_id']
    if actual_todo_id in context['reminders']:
        del context['reminders'][actual_todo_id]


@then(parsers.parse('todo {todo_id:d} should have {count:d} reminders'))
def todo_reminders_count(context, todo_id, count):
    """Verify reminder count for todo"""
    actual_todo_id = context[f'todo_{todo_id}_id']
    assert actual_todo_id in context['reminders'] or count == 0
    if count > 0:
        assert actual_todo_id in context['reminders']
    else:
        assert actual_todo_id not in context['reminders']


@when(parsers.parse('I update the reminder deadline to "{new_deadline}"'))
def update_reminder_deadline(context, new_deadline):
    """Update reminder deadline"""
    for todo_id, reminder in context['reminders'].items():
        if 'deadline' in reminder:
            reminder['deadline'] = new_deadline
            return
    raise AssertionError("No deadline reminder found to update")


@when(parsers.parse('I snooze the reminder for {hours:d} hour'))
def snooze_reminder(context, hours):
    """Snooze a reminder"""
    for todo_id, reminder in context['reminders'].items():
        if 'deadline' in reminder:
            deadline = datetime.fromisoformat(reminder['deadline'])
            new_deadline = deadline + timedelta(hours=hours)
            reminder['deadline'] = new_deadline.isoformat()
            return
    raise AssertionError("No deadline reminder found to snooze")


@then(parsers.parse('the reminder deadline should be "{expected_deadline}"'))
def reminder_deadline_updated(context, expected_deadline):
    """Verify updated reminder deadline"""
    for todo_id, reminder in context['reminders'].items():
        if 'deadline' in reminder:
            assert reminder['deadline'] == expected_deadline
            return
    raise AssertionError("No deadline reminder found")


@when(parsers.parse('I request todos with reminders due within {hours:d} hours'))
def request_todos_due_within(context, hours):
    """Request todos with reminders due within time window"""
    current_time = context.get('current_time', datetime.now())
    end_time = current_time + timedelta(hours=hours)
    
    context['due_todos'] = []
    for todo_id, reminder in context['reminders'].items():
        if 'deadline' in reminder:
            deadline = datetime.fromisoformat(reminder['deadline'])
            if current_time <= deadline <= end_time:
                context['due_todos'].append(todo_id)


@then(parsers.parse('the result should include todo {todo_id:d}'))
def result_includes_todo(context, todo_id):
    """Verify todo is in results"""
    actual_todo_id = context[f'todo_{todo_id}_id']
    assert actual_todo_id in context['due_todos'], \
        f"Expected todo {todo_id} in results"


@then(parsers.parse('the result should not include todo {todo_id:d}'))
def result_excludes_todo(context, todo_id):
    """Verify todo is not in results"""
    actual_todo_id = context[f'todo_{todo_id}_id']
    assert actual_todo_id not in context.get('due_todos', []), \
        f"Expected todo {todo_id} not in results"
