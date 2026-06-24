#!/usr/bin/env python3
"""
Docker Command Handler

Handles /docker slash commands for Docker operations.
"""

import argparse
import subprocess
import sys
from typing import Optional


def run_command(command: list[str], cwd: Optional[str] = None) -> tuple[bool, str]:
    """Run a shell command and return success status and output."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, f"Error: {e.stderr or e.stdout}"


def docker_status() -> str:
    """Show status of Docker containers."""
    # Use docker compose ps to show service status
    success, output = run_command(["docker", "compose", "ps", "-a"])
    if not success:
        return output
    
    # Also show container status
    success2, output2 = run_command(["docker", "ps", "-a", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"])
    
    return f"=== Docker Compose Services ===\n{output}\n\n=== All Containers ===\n{output2}"


def docker_start() -> str:
    """Start all Docker containers."""
    success, output = run_command(["docker", "compose", "up", "-d"])
    if success:
        return "✅ Containers started successfully\n" + output
    return "❌ Failed to start containers:\n" + output


def docker_stop() -> str:
    """Stop all Docker containers."""
    success, output = run_command(["docker", "compose", "down"])
    if success:
        return "✅ Containers stopped successfully\n" + output
    return "❌ Failed to stop containers:\n" + output


def docker_restart() -> str:
    """Restart all Docker containers."""
    # Stop then start
    stop_success, stop_output = run_command(["docker", "compose", "down"])
    if not stop_success:
        return "❌ Failed to stop containers:\n" + stop_output
    
    start_success, start_output = run_command(["docker", "compose", "up", "-d"])
    if not start_success:
        return "❌ Failed to start containers:\n" + start_output
    
    return "✅ Containers restarted successfully"


def docker_logs(service: Optional[str] = None, follow: bool = False, tail: int = 100) -> str:
    """Show Docker container logs."""
    cmd = ["docker", "compose", "logs"]
    if service:
        cmd.extend(["--no-deps", service])
    if follow:
        cmd.append("--follow")
    cmd.extend(["--tail", str(tail)])
    
    success, output = run_command(cmd)
    if success:
        return output
    return "❌ Failed to get logs:\n" + output


def docker_ps(all_containers: bool = False) -> str:
    """List Docker containers."""
    cmd = ["docker", "ps"]
    if all_containers:
        cmd.append("-a")
    cmd.extend(["--format", "table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Ports}}"])
    
    success, output = run_command(cmd)
    if success:
        return output
    return "❌ Failed to list containers:\n" + output


def docker_build(no_cache: bool = False, pull: bool = False) -> str:
    """Build Docker images."""
    cmd = ["docker", "compose", "build"]
    if no_cache:
        cmd.append("--no-cache")
    if pull:
        cmd.append("--pull")
    
    success, output = run_command(cmd)
    if success:
        return "✅ Images built successfully\n" + output
    return "❌ Failed to build images:\n" + output


def docker_up(build: bool = False, detach: bool = False) -> str:
    """Start Docker services with compose."""
    cmd = ["docker", "compose", "up"]
    if build:
        cmd.append("--build")
    if detach:
        cmd.append("-d")
    
    success, output = run_command(cmd)
    if success:
        return "✅ Services started\n" + output
    return "❌ Failed to start services:\n" + output


def docker_down(volumes: bool = False, rmi: bool = False) -> str:
    """Stop Docker services with compose."""
    cmd = ["docker", "compose", "down"]
    if volumes:
        cmd.append("-v")
    if rmi:
        cmd.append("--rmi", "all")
    
    success, output = run_command(cmd)
    if success:
        return "✅ Services stopped\n" + output
    return "❌ Failed to stop services:\n" + output


def show_help() -> str:
    """Show help message."""
    return """
Docker Command Usage:

  /docker status
      Show status of all containers

  /docker start
      Start all containers

  /docker stop
      Stop all running containers

  /docker restart
      Restart all containers

  /docker logs [service] [--follow] [--tail N]
      Show container logs (default: tail 100 lines)
      Example: /docker logs api --follow --tail 50

  /docker ps [--all]
      List containers (--all: show all, including stopped)

  /docker build [--no-cache] [--pull]
      Build Docker images

  /docker up [--build] [--detach]
      Start services with compose
      Example: /docker up --build -d

  /docker down [--volumes] [--rmi]
      Stop services with compose
      Example: /docker down -v

  /docker help
      Show this help message
"""


def parse_args(args: list[str]) -> tuple[str, dict]:
    """Parse command arguments."""
    if not args:
        return "help", {}
    
    action = args[0].lower()
    
    if action == "status":
        return "status", {}
    elif action == "start":
        return "start", {}
    elif action == "stop":
        return "stop", {}
    elif action == "restart":
        return "restart", {}
    elif action == "logs":
        parser = argparse.ArgumentParser(description="Show container logs")
        parser.add_argument("service", nargs="?", default=None, help="Service name")
        parser.add_argument("--follow", "-f", action="store_true", help="Follow log output")
        parser.add_argument("--tail", "-n", type=int, default=100, help="Number of lines")
        parsed = parser.parse_args(args[1:])
        return "logs", {
            "service": parsed.service,
            "follow": parsed.follow,
            "tail": parsed.tail
        }
    elif action == "ps":
        parser = argparse.ArgumentParser(description="List containers")
        parser.add_argument("--all", "-a", action="store_true", help="Show all containers")
        parsed = parser.parse_args(args[1:])
        return "ps", {"all": parsed.all}
    elif action == "build":
        parser = argparse.ArgumentParser(description="Build images")
        parser.add_argument("--no-cache", action="store_true", help="No cache")
        parser.add_argument("--pull", action="store_true", help="Pull base images")
        parsed = parser.parse_args(args[1:])
        return "build", {
            "no_cache": parsed.no_cache,
            "pull": parsed.pull
        }
    elif action == "up":
        parser = argparse.ArgumentParser(description="Start services")
        parser.add_argument("--build", "-b", action="store_true", help="Build images")
        parser.add_argument("--detach", "-d", action="store_true", help="Detached mode")
        parsed = parser.parse_args(args[1:])
        return "up", {
            "build": parsed.build,
            "detach": parsed.detach
        }
    elif action == "down":
        parser = argparse.ArgumentParser(description="Stop services")
        parser.add_argument("--volumes", "-v", action="store_true", help="Remove volumes")
        parser.add_argument("--rmi", action="store_true", help="Remove images")
        parsed = parser.parse_args(args[1:])
        return "down", {
            "volumes": parsed.volumes,
            "rmi": parsed.rmi
        }
    elif action in ("help", "-h", "--help"):
        return "help", {}
    else:
        return "help", {}


def main():
    """Main entry point for the docker command."""
    # Skip the first argument (command name)
    args = sys.argv[1:]
    
    try:
        action, kwargs = parse_args(args)
        
        if action == "help":
            print(show_help())
        elif action == "status":
            print(docker_status())
        elif action == "start":
            print(docker_start())
        elif action == "stop":
            print(docker_stop())
        elif action == "restart":
            print(docker_restart())
        elif action == "logs":
            print(docker_logs(
                service=kwargs.get("service"),
                follow=kwargs.get("follow", False),
                tail=kwargs.get("tail", 100)
            ))
        elif action == "ps":
            print(docker_ps(all_containers=kwargs.get("all", False)))
        elif action == "build":
            print(docker_build(
                no_cache=kwargs.get("no_cache", False),
                pull=kwargs.get("pull", False)
            ))
        elif action == "up":
            print(docker_up(
                build=kwargs.get("build", False),
                detach=kwargs.get("detach", False)
            ))
        elif action == "down":
            print(docker_down(
                volumes=kwargs.get("volumes", False),
                rmi=kwargs.get("rmi", False)
            ))
        else:
            print(show_help())
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
