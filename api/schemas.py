"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TodoBase(BaseModel):
    """Shared fields for todo operations."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=500)
    completed: bool = False


class TodoCreate(TodoBase):
    """Schema for creating a new todo."""


class TodoUpdate(BaseModel):
    """Schema for updating an existing todo. All fields optional."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=500)
    completed: bool | None = None


class TodoResponse(TodoBase):
    """Schema for todo responses including database-generated fields."""

    id: int
    created_at: datetime
    updated_at: datetime | None = None
    
    model_config = {"from_attributes": True}


# ============= SUBTASK SCHEMAS =============

class SubtaskBase(BaseModel):
    """Shared fields for subtask operations."""
    
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    status: str = Field(default="pending", pattern="^(pending|in_progress|completed)$")


class SubtaskCreate(SubtaskBase):
    """Schema for creating a new subtask."""
    
    blocked_by_id: Optional[int] = Field(None, description="ID of subtask this is blocked by")


class SubtaskUpdate(BaseModel):
    """Schema for updating an existing subtask. All fields optional."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|completed)$")
    blocked_by_id: Optional[int] = Field(None, description="ID of subtask this is blocked by")


class SubtaskResponse(SubtaskBase):
    """Schema for subtask responses including database-generated fields."""
    
    id: int
    todo_id: int
    blocked_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class SubtaskWithDependencies(SubtaskResponse):
    """Subtask with dependency information."""
    
    blocks: List[int] = Field(default_factory=list, description="List of subtask IDs this blocks")


# ============= REMINDER SCHEMAS =============

class ReminderBase(BaseModel):
    """Shared fields for reminder operations."""
    
    type: str = Field(..., pattern="^(deadline|recurring)$", description="Type of reminder")


class ReminderCreateForDeadline(ReminderBase):
    """Schema for creating a deadline reminder."""
    
    deadline: datetime = Field(..., description="Deadline for the reminder")
    channels: List[str] = Field(default_factory=lambda: ["in_app"], description="Notification channels")


class ReminderCreateForRecurring(ReminderBase):
    """Schema for creating a recurring reminder."""
    
    frequency: str = Field(..., pattern="^(daily|weekly|monthly)$", description="Recurrence frequency")
    channels: List[str] = Field(default_factory=lambda: ["in_app"], description="Notification channels")


class ReminderUpdate(BaseModel):
    """Schema for updating an existing reminder. All fields optional."""
    
    type: Optional[str] = Field(None, pattern="^(deadline|recurring)$")
    deadline: Optional[datetime] = None
    frequency: Optional[str] = Field(None, pattern="^(daily|weekly|monthly)$")
    channels: Optional[List[str]] = None
    state: Optional[str] = Field(None, pattern="^(active|approaching|overdue)$")


class ReminderResponse(ReminderBase):
    """Schema for reminder responses including database-generated fields."""
    
    id: int
    todo_id: int
    deadline: Optional[datetime] = None
    frequency: Optional[str] = None
    interval_days: Optional[int] = None
    channels: str = Field(default="in_app", description="Comma-separated list of channels")
    state: str = Field(default="active", pattern="^(active|approaching|overdue)$")
    snoozed_until: Optional[datetime] = None
    snooze_count: int = Field(default=0)
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class ReminderInstance(BaseModel):
    """Schema for reminder instances (recurring reminders)."""
    
    id: int
    reminder_id: int
    todo_id: int
    trigger_time: datetime
    status: str = Field(default="pending", pattern="^(pending|triggered|missed)$")
    
    model_config = {"from_attributes": True}
