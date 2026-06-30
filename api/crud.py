"""CRUD operations for the Todo model."""

from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session

from models import Reminder, Subtask, Todo
from schemas import (
    ReminderCreateForDeadline,
    ReminderCreateForRecurring,
    ReminderUpdate,
    SubtaskCreate,
    SubtaskUpdate,
    TodoCreate,
    TodoUpdate,
)


# ============= TODO CRUD =============

def get_todos(db: Session) -> list[Todo]:
    """Return all todos ordered by creation date (newest first)."""
    return db.query(Todo).order_by(Todo.created_at.desc()).all()


def get_todo(db: Session, todo_id: int) -> Todo | None:
    """Return a single todo by ID, or None if not found."""
    return db.query(Todo).filter(Todo.id == todo_id).first()


def create_todo(db: Session, todo: TodoCreate) -> Todo:
    """Create a new todo and return it."""
    db_todo = Todo(**todo.model_dump())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


def update_todo(db: Session, todo_id: int, todo: TodoUpdate) -> Todo | None:
    """Update an existing todo. Returns None if not found."""
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not db_todo:
        return None
    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)
    db.commit()
    db.refresh(db_todo)
    return db_todo


def delete_todo(db: Session, todo_id: int) -> bool:
    """Delete a todo by ID. Returns True if deleted, False if not found."""
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not db_todo:
        return False
    db.delete(db_todo)
    db.commit()
    return True


# ============= SUBTASK CRUD =============

def get_subtasks(db: Session, todo_id: int) -> list[Subtask]:
    """Return all subtasks for a given todo."""
    return db.query(Subtask).filter(Subtask.todo_id == todo_id).order_by(Subtask.created_at).all()


def get_subtask(db: Session, subtask_id: int) -> Subtask | None:
    """Return a single subtask by ID, or None if not found."""
    return db.query(Subtask).filter(Subtask.id == subtask_id).first()


def create_subtask(db: Session, todo_id: int, subtask: SubtaskCreate) -> Subtask:
    """Create a new subtask for a todo."""
    db_subtask = Subtask(todo_id=todo_id, **subtask.model_dump())
    db.add(db_subtask)
    db.commit()
    db.refresh(db_subtask)
    return db_subtask


def update_subtask(db: Session, subtask_id: int, subtask: SubtaskUpdate) -> Subtask | None:
    """Update an existing subtask. Returns None if not found."""
    db_subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()
    if not db_subtask:
        return None
    
    update_data = subtask.model_dump(exclude_unset=True)
    
    # Validate dependency: cannot set blocked_by_id to self
    if 'blocked_by_id' in update_data and update_data['blocked_by_id'] == subtask_id:
        raise ValueError("Subtask cannot be blocked by itself")
    
    for key, value in update_data.items():
        setattr(db_subtask, key, value)
    db.commit()
    db.refresh(db_subtask)
    return db_subtask


def delete_subtask(db: Session, subtask_id: int) -> bool:
    """Delete a subtask by ID. Returns True if deleted, False if not found."""
    db_subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()
    if not db_subtask:
        return False
    
    # Clear dependencies before deletion
    # Any subtasks that were blocked by this one should have their blocked_by_id set to None
    db.query(Subtask).filter(Subtask.blocked_by_id == subtask_id).update({"blocked_by_id": None})
    
    db.delete(db_subtask)
    db.commit()
    return True


def get_subtask_dependencies(db: Session, subtask_id: int) -> dict:
    """Get dependency graph for a subtask.
    
    Returns:
        {
            'blocked_by': Subtask | None,
            'blocks': list[Subtask],
            'can_complete': bool
        }
    """
    db_subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()
    if not db_subtask:
        return {'blocked_by': None, 'blocks': [], 'can_complete': False}
    
    blocked_by = db.query(Subtask).filter(Subtask.id == db_subtask.blocked_by_id).first()
    blocks = db.query(Subtask).filter(Subtask.blocked_by_id == subtask_id).all()
    
    # Check if can be completed (no uncompleted dependencies)
    can_complete = True
    current = db_subtask
    visited = set()
    
    while current and current.id not in visited:
        visited.add(current.id)
        if current.blocked_by_id:
            blocked_by_subtask = db.query(Subtask).filter(Subtask.id == current.blocked_by_id).first()
            if blocked_by_subtask and blocked_by_subtask.status != 'completed':
                can_complete = False
                break
            current = blocked_by_subtask
        else:
            break
    
    return {
        'blocked_by': blocked_by,
        'blocks': blocks,
        'can_complete': can_complete
    }


def check_can_complete_subtask(db: Session, subtask_id: int) -> tuple[bool, Optional[str]]:
    """Check if a subtask can be completed.
    
    Returns:
        (can_complete: bool, error_message: str | None)
    """
    db_subtask = db.query(Subtask).filter(Subtask.id == subtask_id).first()
    if not db_subtask:
        return False, "Subtask not found"
    
    # Recursively check all blocking dependencies
    current = db_subtask
    visited = set()
    
    while current and current.id not in visited:
        visited.add(current.id)
        if current.blocked_by_id:
            blocked_by = db.query(Subtask).filter(Subtask.id == current.blocked_by_id).first()
            if not blocked_by:
                break
            if blocked_by.status != 'completed':
                return False, f"Cannot complete: blocked by incomplete subtask '{blocked_by.title}'"
            current = blocked_by
    
    return True, None


def get_dependency_graph(db: Session, todo_id: int) -> dict:
    """Get the complete dependency graph for a todo's subtasks.
    
    Returns:
        {
            'subtasks': list[dict],
            'edges': list[tuple[int, int]]  # (from_id, to_id) for blocked_by relationships
        }
    """
    subtasks = db.query(Subtask).filter(Subtask.todo_id == todo_id).all()
    
    edges = []
    for subtask in subtasks:
        if subtask.blocked_by_id:
            edges.append((subtask.blocked_by_id, subtask.id))
    
    return {
        'subtasks': [
            {
                'id': s.id,
                'title': s.title,
                'status': s.status,
                'blocked_by_id': s.blocked_by_id
            }
            for s in subtasks
        ],
        'edges': edges
    }


# ============= REMINDER CRUD =============

def get_reminders(db: Session, todo_id: int) -> list[Reminder]:
    """Return all reminders for a given todo."""
    return db.query(Reminder).filter(Reminder.todo_id == todo_id).order_by(Reminder.created_at).all()


def get_reminder(db: Session, reminder_id: int) -> Reminder | None:
    """Return a single reminder by ID, or None if not found."""
    return db.query(Reminder).filter(Reminder.id == reminder_id).first()


def create_reminder_deadline(
    db: Session, 
    todo_id: int, 
    reminder: ReminderCreateForDeadline
) -> Reminder:
    """Create a new deadline reminder for a todo."""
    # Convert channels list to comma-separated string
    channels_str = ",".join(reminder.channels) if reminder.channels else "in_app"
    
    # Determine initial state
    state = "active"
    if reminder.deadline < datetime.utcnow():
        state = "overdue"
    elif (reminder.deadline - datetime.utcnow()) < timedelta(hours=48):
        state = "approaching"
    
    db_reminder = Reminder(
        todo_id=todo_id,
        type=reminder.type,
        deadline=reminder.deadline,
        channels=channels_str,
        state=state,
        interval_days=None
    )
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder


def create_reminder_recurring(
    db: Session, 
    todo_id: int, 
    reminder: ReminderCreateForRecurring
) -> Reminder:
    """Create a new recurring reminder for a todo."""
    # Map frequency to interval_days
    freq_map = {
        'daily': 1,
        'weekly': 7,
        'monthly': 30
    }
    interval_days = freq_map.get(reminder.frequency, 1)
    
    # Convert channels list to comma-separated string
    channels_str = ",".join(reminder.channels) if reminder.channels else "in_app"
    
    db_reminder = Reminder(
        todo_id=todo_id,
        type=reminder.type,
        frequency=reminder.frequency,
        interval_days=interval_days,
        channels=channels_str,
        state="active"
    )
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder


def update_reminder(db: Session, reminder_id: int, reminder: ReminderUpdate) -> Reminder | None:
    """Update an existing reminder. Returns None if not found."""
    db_reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not db_reminder:
        return None
    
    update_data = reminder.model_dump(exclude_unset=True)
    
    # Handle channels conversion
    if 'channels' in update_data and isinstance(update_data['channels'], list):
        update_data['channels'] = ",".join(update_data['channels'])
    
    # If deadline is updated, recalculate state
    if 'deadline' in update_data:
        if update_data['deadline'] < datetime.utcnow():
            update_data['state'] = 'overdue'
        elif (update_data['deadline'] - datetime.utcnow()) < timedelta(hours=48):
            update_data['state'] = 'approaching'
        else:
            update_data['state'] = 'active'
    
    for key, value in update_data.items():
        if key != 'channels' or value is not None:
            setattr(db_reminder, key, value)
    
    db.commit()
    db.refresh(db_reminder)
    return db_reminder


def delete_reminder(db: Session, reminder_id: int) -> bool:
    """Delete a reminder by ID. Returns True if deleted, False if not found."""
    db_reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not db_reminder:
        return False
    db.delete(db_reminder)
    db.commit()
    return True


def snooze_reminder(db: Session, reminder_id: int, hours: int = 1) -> Reminder | None:
    """Snooze a reminder by the specified number of hours."""
    db_reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not db_reminder:
        return None
    
    if db_reminder.type == 'deadline' and db_reminder.deadline:
        new_deadline = db_reminder.deadline + timedelta(hours=hours)
        db_reminder.deadline = new_deadline
        db_reminder.snooze_count += 1
        db_reminder.snoozed_until = new_deadline
        db.commit()
        db.refresh(db_reminder)
    
    return db_reminder


def get_reminders_due_within(db: Session, hours: int = 48) -> list[Todo]:
    """Get all todos with reminders due within the specified hours."""
    from datetime import datetime, timedelta
    
    now = datetime.utcnow()
    end_time = now + timedelta(hours=hours)
    
    # Find reminders that are due within the time window
    reminders = db.query(Reminder).filter(
        Reminder.type == 'deadline',
        Reminder.deadline >= now,
        Reminder.deadline <= end_time
    ).all()
    
    # Get unique todo_ids
    todo_ids = list({r.todo_id for r in reminders})
    
    # Return the todos
    return db.query(Todo).filter(Todo.id.in_(todo_ids)).all()


def update_reminder_states(db: Session) -> int:
    """Update all reminder states based on current time.
    
    Returns the number of reminders updated.
    """
    now = datetime.utcnow()
    updated_count = 0
    
    reminders = db.query(Reminder).filter(Reminder.type == 'deadline').all()
    
    for reminder in reminders:
        if reminder.deadline:
            time_diff = reminder.deadline - now
            
            if time_diff < timedelta(0):
                new_state = 'overdue'
            elif time_diff < timedelta(hours=48):
                new_state = 'approaching'
            else:
                new_state = 'active'
            
            if reminder.state != new_state:
                reminder.state = new_state
                updated_count += 1
    
    if updated_count > 0:
        db.commit()
    
    return updated_count
