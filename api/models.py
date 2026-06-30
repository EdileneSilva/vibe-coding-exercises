"""SQLAlchemy ORM models."""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Todo(Base):
    """Represents a to-do task in the database."""

    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    subtasks = relationship("Subtask", back_populates="todo", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="todo", cascade="all, delete-orphan")


class Subtask(Base):
    """Represents a subtask of a todo with dependency tracking."""

    __tablename__ = "subtasks"

    id = Column(Integer, primary_key=True, index=True)
    todo_id = Column(Integer, ForeignKey("todos.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="pending", nullable=False)  # pending, in_progress, completed
    
    # Dependency: subtask can be blocked by another subtask
    blocked_by_id = Column(Integer, ForeignKey("subtasks.id", ondelete="SET NULL"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    todo = relationship("Todo", back_populates="subtasks")
    blocked_by = relationship("Subtask", remote_side=[id], backref="blocks")


class Reminder(Base):
    """Represents a reminder for a todo."""

    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    todo_id = Column(Integer, ForeignKey("todos.id", ondelete="CASCADE"), nullable=False)
    
    # Reminder types: deadline, recurring
    type = Column(String(20), nullable=False)
    
    # For deadline reminders
    deadline = Column(DateTime(timezone=True), nullable=True)
    
    # For recurring reminders
    frequency = Column(String(20), nullable=True)  # daily, weekly, monthly
    interval_days = Column(Integer, nullable=True)
    
    # Notification channels (comma-separated list)
    channels = Column(String(200), nullable=True)  # e.g., "email,in_app,sms"
    
    # State: approaching, overdue, active
    state = Column(String(20), default="active", nullable=False)
    
    # Snooze information
    snoozed_until = Column(DateTime(timezone=True), nullable=True)
    snooze_count = Column(Integer, default=0, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    todo = relationship("Todo", back_populates="reminders")
