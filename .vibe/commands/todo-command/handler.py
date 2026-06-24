#!/usr/bin/env python3
"""
Todo Command Handler

Handles /todo slash commands for managing todo items.
"""

import argparse
import sys
import requests
from typing import Optional

# API base URL - in production this would be configured via environment
API_BASE_URL = "http://localhost:8000"


def add_todo(title: str, description: Optional[str] = None, completed: bool = False) -> dict:
    """Add a new todo item via API."""
    payload = {
        "title": title,
        "description": description or "",
        "completed": completed
    }
    response = requests.post(f"{API_BASE_URL}/todos", json=payload)
    response.raise_for_status()
    return response.json()


def list_todos(filter_type: Optional[str] = None) -> list[dict]:
    """List todos with optional filtering."""
    response = requests.get(f"{API_BASE_URL}/todos")
    response.raise_for_status()
    todos = response.json()
    
    if filter_type == "active":
        return [t for t in todos if not t["completed"]]
    elif filter_type == "completed":
        return [t for t in todos if t["completed"]]
    return todos


def complete_todo(todo_id: int) -> dict:
    """Mark a todo as completed."""
    payload = {"completed": True}
    response = requests.put(f"{API_BASE_URL}/todos/{todo_id}", json=payload)
    response.raise_for_status()
    return response.json()


def delete_todo(todo_id: int) -> bool:
    """Delete a todo item."""
    response = requests.delete(f"{API_BASE_URL}/todos/{todo_id}")
    if response.status_code == 204:
        return True
    response.raise_for_status()
    return False


def show_help() -> str:
    """Show help message."""
    return """
Todo Command Usage:

  /todo add <title> [--description <desc>] [--completed]
      Add a new todo item
      Example: /todo add Buy milk --description "Get milk from store"

  /todo list [--all|--active|--completed]
      List todos (default: all)
      Example: /todo list --active

  /todo complete <id>
      Mark a todo as completed
      Example: /todo complete 1

  /todo delete <id>
      Delete a todo item
      Example: /todo delete 2

  /todo help
      Show this help message
"""


def parse_args(args: list[str]) -> tuple[str, dict]:
    """Parse command arguments."""
    if not args:
        return "help", {}
    
    action = args[0].lower()
    
    if action == "add":
        parser = argparse.ArgumentParser(description="Add a new todo")
        parser.add_argument("title", help="Todo title")
        parser.add_argument("--description", "-d", help="Todo description", default=None)
        parser.add_argument("--completed", "-c", action="store_true", help="Mark as completed")
        parsed = parser.parse_args(args[1:])
        return "add", {
            "title": parsed.title,
            "description": parsed.description,
            "completed": parsed.completed
        }
    
    elif action == "list":
        parser = argparse.ArgumentParser(description="List todos")
        group = parser.add_mutually_exclusive_group()
        group.add_argument("--all", action="store_true", help="Show all todos")
        group.add_argument("--active", action="store_true", help="Show active todos")
        group.add_argument("--completed", action="store_true", help="Show completed todos")
        parsed = parser.parse_args(args[1:])
        filter_type = None
        if parsed.active:
            filter_type = "active"
        elif parsed.completed:
            filter_type = "completed"
        return "list", {"filter": filter_type}
    
    elif action == "complete":
        parser = argparse.ArgumentParser(description="Complete a todo")
        parser.add_argument("id", type=int, help="Todo ID to complete")
        parsed = parser.parse_args(args[1:])
        return "complete", {"id": parsed.id}
    
    elif action == "delete":
        parser = argparse.ArgumentParser(description="Delete a todo")
        parser.add_argument("id", type=int, help="Todo ID to delete")
        parsed = parser.parse_args(args[1:])
        return "delete", {"id": parsed.id}
    
    elif action in ("help", "-h", "--help"):
        return "help", {}
    
    else:
        return "help", {}


def main():
    """Main entry point for the todo command."""
    # Skip the first argument (command name)
    args = sys.argv[1:]
    
    try:
        action, kwargs = parse_args(args)
        
        if action == "help":
            print(show_help())
        elif action == "add":
            todo = add_todo(
                title=kwargs["title"],
                description=kwargs.get("description"),
                completed=kwargs.get("completed", False)
            )
            print(f"✅ Added todo #{todo['id']}: {todo['title']}")
        elif action == "list":
            todos = list_todos(kwargs.get("filter"))
            if not todos:
                print("No todos found.")
            else:
                for todo in todos:
                    status = "✓" if todo["completed"] else "○"
                    print(f"{status} #{todo['id']}: {todo['title']}")
                    if todo.get("description"):
                        print(f"   {todo['description']}")
        elif action == "complete":
            todo = complete_todo(kwargs["id"])
            print(f"✅ Completed todo #{todo['id']}: {todo['title']}")
        elif action == "delete":
            if delete_todo(kwargs["id"]):
                print(f"🗑️ Deleted todo #{kwargs['id']}")
            else:
                print(f"❌ Todo #{kwargs['id']} not found")
        else:
            print(show_help())
    except requests.exceptions.RequestException as e:
        print(f"❌ API Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
