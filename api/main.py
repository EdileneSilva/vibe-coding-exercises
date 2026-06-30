"""FastAPI application entry point."""

import logging
from datetime import datetime
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import crud
import schemas
from database import Base, engine, get_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="To-Do API",
    description="REST API for managing to-do tasks",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoints
@app.get("/health")
async def health_check() -> dict[str, Any]:
    """
    Basic health check endpoint.
    Returns 200 OK if the API is running.
    """
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "todo-api",
        "version": "0.1.0",
    }


@app.get("/health/db")
async def database_health_check(db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    Database health check endpoint.
    Verifies database connectivity by executing a simple query.
    """
    try:
        # Execute a simple query to verify database connectivity
        db.execute("SELECT 1")
        logger.info("Database health check passed")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(e)}",
        )


@app.get("/metrics")
async def metrics() -> dict[str, Any]:
    """
    Simple metrics endpoint.
    Provides basic operational metrics.
    """
    import crud
    from database import SessionLocal
    
    try:
        db = SessionLocal()
        todo_count = len(crud.get_todos(db))
        db.close()
        
        return {
            "metrics": {
                "todos_total": todo_count,
                "api_uptime": "up",
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"Metrics endpoint error: {e}")
        return {
            "metrics": {
                "error": str(e),
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests for monitoring."""
    logger.info(f"Incoming request: {request.method} {request.url}")
    start_time = datetime.utcnow()
    
    response = await call_next(request)
    
    process_time = (datetime.utcnow() - start_time).total_seconds() * 1000
    logger.info(
        f"Request completed: {request.method} {request.url} "
        f"- Status: {response.status_code} "
        f"- Duration: {process_time:.2f}ms"
    )
    
    return response


@app.get("/todos", response_model=list[schemas.TodoResponse])
def list_todos(db: Session = Depends(get_db)):
    """List all todos."""
    return crud.get_todos(db)


@app.get("/todos/{todo_id}", response_model=schemas.TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    """Get a single todo by ID."""
    todo = crud.get_todo(db, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.post("/todos", response_model=schemas.TodoResponse, status_code=201)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    """Create a new todo."""
    return crud.create_todo(db, todo)


@app.put("/todos/{todo_id}", response_model=schemas.TodoResponse)
def update_todo(todo_id: int, todo: schemas.TodoUpdate, db: Session = Depends(get_db)):
    """Update an existing todo."""
    updated = crud.update_todo(db, todo_id, todo)
    if not updated:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    """Delete a todo."""
    if not crud.delete_todo(db, todo_id):
        raise HTTPException(status_code=404, detail="Todo not found")


# ============= SUBTASK ENDPOINTS =============

@app.get("/todos/{todo_id}/subtasks", response_model=list[schemas.SubtaskResponse])
def list_subtasks(todo_id: int, db: Session = Depends(get_db)):
    """List all subtasks for a todo."""
    # Verify todo exists
    if not crud.get_todo(db, todo_id):
        raise HTTPException(status_code=404, detail="Todo not found")
    return crud.get_subtasks(db, todo_id)


@app.get("/subtasks/{subtask_id}", response_model=schemas.SubtaskResponse)
def get_subtask(subtask_id: int, db: Session = Depends(get_db)):
    """Get a single subtask by ID."""
    subtask = crud.get_subtask(db, subtask_id)
    if not subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")
    return subtask


@app.post("/todos/{todo_id}/subtasks", response_model=schemas.SubtaskResponse, status_code=201)
def create_subtask(todo_id: int, subtask: schemas.SubtaskCreate, db: Session = Depends(get_db)):
    """Create a new subtask for a todo."""
    # Verify todo exists
    if not crud.get_todo(db, todo_id):
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # Verify blocked_by_id exists if provided
    if subtask.blocked_by_id:
        if not crud.get_subtask(db, subtask.blocked_by_id):
            raise HTTPException(status_code=404, detail=f"Blocking subtask {subtask.blocked_by_id} not found")
    
    return crud.create_subtask(db, todo_id, subtask)


@app.put("/subtasks/{subtask_id}", response_model=schemas.SubtaskResponse)
def update_subtask(subtask_id: int, subtask: schemas.SubtaskUpdate, db: Session = Depends(get_db)):
    """Update an existing subtask."""
    updated = crud.update_subtask(db, subtask_id, subtask)
    if not updated:
        raise HTTPException(status_code=404, detail="Subtask not found")
    return updated


@app.delete("/subtasks/{subtask_id}", status_code=204)
def delete_subtask(subtask_id: int, db: Session = Depends(get_db)):
    """Delete a subtask."""
    if not crud.delete_subtask(db, subtask_id):
        raise HTTPException(status_code=404, detail="Subtask not found")


@app.get("/todos/{todo_id}/subtasks/dependencies", response_model=dict)
def get_dependency_graph(todo_id: int, db: Session = Depends(get_db)):
    """Get the dependency graph for a todo's subtasks."""
    # Verify todo exists
    if not crud.get_todo(db, todo_id):
        raise HTTPException(status_code=404, detail="Todo not found")
    return crud.get_dependency_graph(db, todo_id)


@app.post("/subtasks/{subtask_id}/complete", response_model=schemas.SubtaskResponse)
def complete_subtask(subtask_id: int, db: Session = Depends(get_db)):
    """Mark a subtask as completed, checking dependencies."""
    subtask = crud.get_subtask(db, subtask_id)
    if not subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")
    
    # Check if can be completed
    can_complete, error = crud.check_can_complete_subtask(db, subtask_id)
    if not can_complete:
        raise HTTPException(status_code=400, detail=error or "Cannot complete subtask")
    
    # Update status
    subtask.status = "completed"
    db.commit()
    db.refresh(subtask)
    
    return subtask


# ============= REMINDER ENDPOINTS =============

@app.get("/todos/{todo_id}/reminders", response_model=list[schemas.ReminderResponse])
def list_reminders(todo_id: int, db: Session = Depends(get_db)):
    """List all reminders for a todo."""
    # Verify todo exists
    if not crud.get_todo(db, todo_id):
        raise HTTPException(status_code=404, detail="Todo not found")
    return crud.get_reminders(db, todo_id)


@app.get("/reminders/{reminder_id}", response_model=schemas.ReminderResponse)
def get_reminder(reminder_id: int, db: Session = Depends(get_db)):
    """Get a single reminder by ID."""
    reminder = crud.get_reminder(db, reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder


@app.post("/todos/{todo_id}/reminders/deadline", response_model=schemas.ReminderResponse, status_code=201)
def create_deadline_reminder(todo_id: int, reminder: schemas.ReminderCreateForDeadline, db: Session = Depends(get_db)):
    """Create a new deadline reminder for a todo."""
    # Verify todo exists
    if not crud.get_todo(db, todo_id):
        raise HTTPException(status_code=404, detail="Todo not found")
    
    return crud.create_reminder_deadline(db, todo_id, reminder)


@app.post("/todos/{todo_id}/reminders/recurring", response_model=schemas.ReminderResponse, status_code=201)
def create_recurring_reminder(todo_id: int, reminder: schemas.ReminderCreateForRecurring, db: Session = Depends(get_db)):
    """Create a new recurring reminder for a todo."""
    # Verify todo exists
    if not crud.get_todo(db, todo_id):
        raise HTTPException(status_code=404, detail="Todo not found")
    
    return crud.create_reminder_recurring(db, todo_id, reminder)


@app.put("/reminders/{reminder_id}", response_model=schemas.ReminderResponse)
def update_reminder(reminder_id: int, reminder: schemas.ReminderUpdate, db: Session = Depends(get_db)):
    """Update an existing reminder."""
    updated = crud.update_reminder(db, reminder_id, reminder)
    if not updated:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return updated


@app.delete("/reminders/{reminder_id}", status_code=204)
def delete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    """Delete a reminder."""
    if not crud.delete_reminder(db, reminder_id):
        raise HTTPException(status_code=404, detail="Reminder not found")


@app.post("/reminders/{reminder_id}/snooze", response_model=schemas.ReminderResponse)
def snooze_reminder(reminder_id: int, hours: int = 1, db: Session = Depends(get_db)):
    """Snooze a reminder by the specified number of hours."""
    reminder = crud.snooze_reminder(db, reminder_id, hours)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder


@app.get("/reminders/due", response_model=list[schemas.TodoResponse])
def get_reminders_due(hours: int = 48, db: Session = Depends(get_db)):
    """Get all todos with reminders due within the specified hours."""
    return crud.get_reminders_due_within(db, hours)


@app.post("/reminders/update-states")
def update_reminder_states(db: Session = Depends(get_db)):
    """Update all reminder states based on current time."""
    updated_count = crud.update_reminder_states(db)
    return {"updated_count": updated_count, "message": f"Updated {updated_count} reminder states"}
