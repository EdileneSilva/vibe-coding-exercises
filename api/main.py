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
