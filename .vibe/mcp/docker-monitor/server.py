#!/usr/bin/env python3
"""
Docker Monitor MCP Server

A Model Context Protocol server that provides Docker container and service
monitoring capabilities for the Docker To-Do App project.

This MCP server allows AI agents to:
- Monitor Docker container status and health
- View and follow container logs
- Check container resource usage
- Execute commands in containers
- Manage container lifecycle
"""

import subprocess
import json
import re
from typing import Any, Optional
from datetime import datetime
from pathlib import Path

# MCP Server metadata
MCP_SERVER_NAME = "docker-monitor"
MCP_SERVER_VERSION = "1.0.0"

# Docker commands
DOCKER_CMD = "docker"
DOCKER_COMPOSE_CMD = "docker compose"


class DockerMonitor:
    """Main docker monitor class that provides Docker-related functionality."""
    
    def __init__(self):
        self.compose_file = "docker-compose.yml"
        self.project_name = "briefs-todo-app-starter"
    
    def _run_command(self, command: list[str], cwd: Optional[str] = None) -> dict[str, Any]:
        """Execute a shell command and return the result."""
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "command": " ".join(command)
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": "Command timed out",
                "command": " ".join(command),
                "timeout": True
            }
        except Exception as e:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "command": " ".join(command)
            }
    
    def get_system_info(self) -> dict[str, Any]:
        """Get Docker system information."""
        result = self._run_command([DOCKER_CMD, "info", "--format", "{{json .}}"])
        if result["success"]:
            try:
                return json.loads(result["stdout"])
            except json.JSONDecodeError:
                pass
        
        # Fallback to basic info
        return {
            "containers": self._get_container_count(),
            "images": self._get_image_count(),
            "volumes": self._get_volume_count(),
            "networks": self._get_network_count(),
            "version": self._get_docker_version()
        }
    
    def _get_container_count(self) -> int:
        """Get the number of containers."""
        result = self._run_command([DOCKER_CMD, "ps", "-a", "--format", "{{.Names}}"])
        if result["success"]:
            return len([line for line in result["stdout"].split('\n') if line.strip()])
        return 0
    
    def _get_image_count(self) -> int:
        """Get the number of images."""
        result = self._run_command([DOCKER_CMD, "images", "--format", "{{.Repository}}"])
        if result["success"]:
            return len([line for line in result["stdout"].split('\n') if line.strip()])
        return 0
    
    def _get_volume_count(self) -> int:
        """Get the number of volumes."""
        result = self._run_command([DOCKER_CMD, "volume", "ls", "--format", "{{.Name}}"])
        if result["success"]:
            return len([line for line in result["stdout"].split('\n') if line.strip()])
        return 0
    
    def _get_network_count(self) -> int:
        """Get the number of networks."""
        result = self._run_command([DOCKER_CMD, "network", "ls", "--format", "{{.Name}}"])
        if result["success"]:
            return len([line for line in result["stdout"].split('\n') if line.strip()])
        return 0
    
    def _get_docker_version(self) -> str:
        """Get the Docker version."""
        result = self._run_command([DOCKER_CMD, "--version"])
        if result["success"]:
            match = re.search(r'version\s+(\d+\.\d+\.\d+)', result["stdout"], re.IGNORECASE)
            if match:
                return match.group(1)
        return "unknown"
    
    def list_containers(self, all: bool = False, format: str = "json") -> dict[str, Any]:
        """List Docker containers.
        
        Args:
            all: If True, include stopped containers
            format: Output format
            
        Returns:
            Dictionary with container list
        """
        cmd = [DOCKER_CMD, "ps"]
        if all:
            cmd.append("-a")
        cmd.extend(["--format", "{{json .}}"])
        
        result = self._run_command(cmd)
        if result["success"] and result["stdout"]:
            try:
                containers = []
                for line in result["stdout"].strip().split('\n'):
                    if line.strip():
                        containers.append(json.loads(line))
                return {"containers": containers, "count": len(containers)}
            except json.JSONDecodeError:
                pass
        
        return {"containers": [], "count": 0, "error": result.get("stderr", "")}
    
    def list_services(self) -> dict[str, Any]:
        """List Docker Compose services.
        
        Returns:
            Dictionary with service list
        """
        result = self._run_command([DOCKER_COMPOSE_CMD, "ps", "--format", "json"])
        if result["success"] and result["stdout"]:
            try:
                services = json.loads(result["stdout"])
                return {"services": services, "count": len(services)}
            except json.JSONDecodeError:
                pass
        
        # Fallback to text parsing
        result = self._run_command([DOCKER_COMPOSE_CMD, "ps"])
        services = []
        if result["success"]:
            for line in result["stdout"].strip().split('\n')[1:]:  # Skip header
                parts = re.split(r'\s{2,}', line.strip())
                if len(parts) >= 4:
                    services.append({
                        "name": parts[0],
                        "status": parts[1],
                        "ports": parts[2] if len(parts) > 2 else "",
                        "service": parts[3] if len(parts) > 3 else ""
                    })
        
        return {"services": services, "count": len(services)}
    
    def get_container_status(self, container_name: str) -> dict[str, Any]:
        """Get the status of a specific container.
        
        Args:
            container_name: Name of the container
            
        Returns:
            Dictionary with container status
        """
        result = self._run_command([DOCKER_CMD, "inspect", "--format", "{{json .}}", container_name])
        if result["success"]:
            try:
                container = json.loads(result["stdout"])
                if isinstance(container, list):
                    container = container[0]
                return {
                    "name": container_name,
                    "status": container.get("State", {}).get("Status", "unknown"),
                    "running": container.get("State", {}).get("Running", False),
                    "exit_code": container.get("State", {}).get("ExitCode", -1),
                    "started_at": container.get("State", {}).get("StartedAt", ""),
                    "finished_at": container.get("State", {}).get("FinishedAt", ""),
                    "health": container.get("State", {}).get("Health", {}),
                    "config": {
                        "image": container.get("Config", {}).get("Image", ""),
                        "cmd": container.get("Config", {}).get("Cmd", []),
                        "env": container.get("Config", {}).get("Env", []),
                    },
                    "network_settings": container.get("NetworkSettings", {}),
                    "raw": container
                }
            except json.JSONDecodeError:
                pass
        
        return {"name": container_name, "status": "unknown", "error": result.get("stderr", "Container not found")}
    
    def get_service_status(self, service_name: str) -> dict[str, Any]:
        """Get the status of a specific Docker Compose service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Dictionary with service status
        """
        result = self._run_command([DOCKER_COMPOSE_CMD, "ps", service_name, "--format", "json"])
        if result["success"] and result["stdout"]:
            try:
                services = json.loads(result["stdout"])
                if services:
                    return services[0]
                return {"name": service_name, "status": "not running", "error": "Service not found"}
            except json.JSONDecodeError:
                pass
        
        # Fallback
        return {"name": service_name, "status": "unknown", "error": result.get("stderr", "Service not found")}
    
    def get_container_logs(self, container_name: str, tail: int = 100, follow: bool = False, 
                           timestamps: bool = True) -> dict[str, Any]:
        """Get logs from a container.
        
        Args:
            container_name: Name of the container
            tail: Number of lines to show
            follow: Whether to follow the logs
            timestamps: Whether to include timestamps
            
        Returns:
            Dictionary with container logs
        """
        cmd = [DOCKER_CMD, "logs"]
        if tail > 0:
            cmd.extend(["--tail", str(tail)])
        if timestamps:
            cmd.append("--timestamps")
        if follow:
            cmd.append("--follow")
        cmd.append(container_name)
        
        result = self._run_command(cmd)
        return {
            "container": container_name,
            "logs": result.get("stdout", ""),
            "error": result.get("stderr", ""),
            "success": result.get("success", False),
            "truncated": False
        }
    
    def get_service_logs(self, service_name: str, tail: int = 100, follow: bool = False) -> dict[str, Any]:
        """Get logs from a Docker Compose service.
        
        Args:
            service_name: Name of the service
            tail: Number of lines to show
            follow: Whether to follow the logs
            
        Returns:
            Dictionary with service logs
        """
        cmd = [DOCKER_COMPOSE_CMD, "logs"]
        if tail > 0:
            cmd.extend(["--tail", str(tail)])
        if follow:
            cmd.append("--follow")
        cmd.append(service_name)
        
        result = self._run_command(cmd)
        return {
            "service": service_name,
            "logs": result.get("stdout", ""),
            "error": result.get("stderr", ""),
            "success": result.get("success", False),
            "truncated": False
        }
    
    def get_resource_usage(self) -> dict[str, Any]:
        """Get resource usage for all running containers.
        
        Returns:
            Dictionary with resource usage data
        """
        result = self._run_command([DOCKER_CMD, "stats", "--no-stream", "--format", "json"])
        if result["success"] and result["stdout"]:
            try:
                lines = result["stdout"].strip().split('\n')
                stats = []
                for line in lines:
                    if line.strip():
                        try:
                            stats.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
                return {"stats": stats, "count": len(stats)}
            except json.JSONDecodeError:
                pass
        
        return {"stats": [], "count": 0, "error": result.get("stderr", "")}
    
    def get_container_resource_usage(self, container_name: str) -> dict[str, Any]:
        """Get resource usage for a specific container.
        
        Args:
            container_name: Name of the container
            
        Returns:
            Dictionary with resource usage data
        """
        result = self._run_command([
            DOCKER_CMD, "stats", "--no-stream", "--format", "json", container_name
        ])
        if result["success"] and result["stdout"]:
            try:
                return json.loads(result["stdout"].strip())
            except json.JSONDecodeError:
                pass
        
        return {"container": container_name, "error": result.get("stderr", "Container not found")}
    
    def execute_in_container(self, container_name: str, command: list[str], 
                             user: str = "") -> dict[str, Any]:
        """Execute a command in a running container.
        
        Args:
            container_name: Name of the container
            command: Command to execute
            user: User to run the command as
            
        Returns:
            Dictionary with execution result
        """
        cmd = [DOCKER_CMD, "exec"]
        if user:
            cmd.extend(["--user", user])
        cmd.extend([container_name] + command)
        
        result = self._run_command(cmd)
        return {
            "container": container_name,
            "command": " ".join(command),
            "success": result.get("success", False),
            "returncode": result.get("returncode", -1),
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", "")
        }
    
    def start_container(self, container_name: str) -> dict[str, Any]:
        """Start a stopped container.
        
        Args:
            container_name: Name of the container
            
        Returns:
            Dictionary with operation result
        """
        result = self._run_command([DOCKER_CMD, "start", container_name])
        return {
            "container": container_name,
            "success": result.get("success", False),
            "message": result.get("stdout", ""),
            "error": result.get("stderr", "")
        }
    
    def stop_container(self, container_name: str, force: bool = False) -> dict[str, Any]:
        """Stop a running container.
        
        Args:
            container_name: Name of the container
            force: Whether to force stop
            
        Returns:
            Dictionary with operation result
        """
        cmd = [DOCKER_CMD, "stop"]
        if force:
            cmd.append("--time=0")
        cmd.append(container_name)
        
        result = self._run_command(cmd)
        return {
            "container": container_name,
            "success": result.get("success", False),
            "message": result.get("stdout", ""),
            "error": result.get("stderr", "")
        }
    
    def restart_container(self, container_name: str) -> dict[str, Any]:
        """Restart a container.
        
        Args:
            container_name: Name of the container
            
        Returns:
            Dictionary with operation result
        """
        result = self._run_command([DOCKER_CMD, "restart", container_name])
        return {
            "container": container_name,
            "success": result.get("success", False),
            "message": result.get("stdout", ""),
            "error": result.get("stderr", "")
        }
    
    def start_services(self, build: bool = False, detach: bool = True) -> dict[str, Any]:
        """Start Docker Compose services.
        
        Args:
            build: Whether to rebuild images
            detach: Whether to run in detached mode
            
        Returns:
            Dictionary with operation result
        """
        cmd = [DOCKER_COMPOSE_CMD, "up"]
        if build:
            cmd.append("--build")
        if detach:
            cmd.append("-d")
        
        result = self._run_command(cmd)
        return {
            "services": "all",
            "build": build,
            "detach": detach,
            "success": result.get("success", False),
            "message": result.get("stdout", ""),
            "error": result.get("stderr", "")
        }
    
    def stop_services(self, remove_volumes: bool = False) -> dict[str, Any]:
        """Stop Docker Compose services.
        
        Args:
            remove_volumes: Whether to remove named volumes
            
        Returns:
            Dictionary with operation result
        """
        cmd = [DOCKER_COMPOSE_CMD, "down"]
        if remove_volumes:
            cmd.append("-v")
        
        result = self._run_command(cmd)
        return {
            "services": "all",
            "remove_volumes": remove_volumes,
            "success": result.get("success", False),
            "message": result.get("stdout", ""),
            "error": result.get("stderr", "")
        }
    
    def build_services(self, service_names: list[str] = None) -> dict[str, Any]:
        """Build Docker Compose services.
        
        Args:
            service_names: Optional list of services to build
            
        Returns:
            Dictionary with operation result
        """
        cmd = [DOCKER_COMPOSE_CMD, "build"]
        if service_names:
            cmd.extend(service_names)
        
        result = self._run_command(cmd)
        return {
            "services": service_names or "all",
            "success": result.get("success", False),
            "message": result.get("stdout", ""),
            "error": result.get("stderr", "")
        }
    
    def list_images(self, all: bool = False) -> dict[str, Any]:
        """List Docker images.
        
        Args:
            all: If True, show all images including intermediate
            
        Returns:
            Dictionary with image list
        """
        cmd = [DOCKER_CMD, "images"]
        if all:
            cmd.append("-a")
        cmd.extend(["--format", "json"])
        
        result = self._run_command(cmd)
        if result["success"] and result["stdout"]:
            try:
                images = []
                for line in result["stdout"].strip().split('\n'):
                    if line.strip():
                        images.append(json.loads(line))
                return {"images": images, "count": len(images)}
            except json.JSONDecodeError:
                pass
        
        return {"images": [], "count": 0, "error": result.get("stderr", "")}
    
    def list_volumes(self) -> dict[str, Any]:
        """List Docker volumes.
        
        Returns:
            Dictionary with volume list
        """
        result = self._run_command([DOCKER_CMD, "volume", "ls", "--format", "json"])
        if result["success"] and result["stdout"]:
            try:
                volumes = json.loads(result["stdout"])
                return {"volumes": volumes, "count": len(volumes)}
            except json.JSONDecodeError:
                pass
        
        return {"volumes": [], "count": 0, "error": result.get("stderr", "")}
    
    def list_networks(self) -> dict[str, Any]:
        """List Docker networks.
        
        Returns:
            Dictionary with network list
        """
        result = self._run_command([DOCKER_CMD, "network", "ls", "--format", "json"])
        if result["success"] and result["stdout"]:
            try:
                networks = json.loads(result["stdout"])
                return {"networks": networks, "count": len(networks)}
            except json.JSONDecodeError:
                pass
        
        return {"networks": [], "count": 0, "error": result.get("stderr", "")}


# Initialize the docker monitor
monitor = DockerMonitor()


def get_tools() -> list[dict[str, Any]]:
    """Get the list of MCP tools provided by this server."""
    return [
        {
            "name": "docker_get_system_info",
            "description": "Get Docker system information (version, container count, etc.)",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "docker_list_containers",
            "description": "List all Docker containers",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "all": {
                        "type": "boolean",
                        "description": "Include stopped containers",
                        "default": False,
                    },
                },
            },
        },
        {
            "name": "docker_list_services",
            "description": "List Docker Compose services",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "docker_get_container_status",
            "description": "Get status of a specific container",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "container_name": {
                        "type": "string",
                        "description": "Name of the container",
                    },
                },
                "required": ["container_name"],
            },
        },
        {
            "name": "docker_get_service_status",
            "description": "Get status of a specific Docker Compose service",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": "Name of the service",
                    },
                },
                "required": ["service_name"],
            },
        },
        {
            "name": "docker_get_container_logs",
            "description": "Get logs from a container",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "container_name": {
                        "type": "string",
                        "description": "Name of the container",
                    },
                    "tail": {
                        "type": "integer",
                        "description": "Number of lines to show",
                        "default": 100,
                        "minimum": 1,
                        "maximum": 10000,
                    },
                    "follow": {
                        "type": "boolean",
                        "description": "Whether to follow the logs",
                        "default": False,
                    },
                    "timestamps": {
                        "type": "boolean",
                        "description": "Whether to include timestamps",
                        "default": True,
                    },
                },
                "required": ["container_name"],
            },
        },
        {
            "name": "docker_get_service_logs",
            "description": "Get logs from a Docker Compose service",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": "Name of the service",
                    },
                    "tail": {
                        "type": "integer",
                        "description": "Number of lines to show",
                        "default": 100,
                        "minimum": 1,
                        "maximum": 10000,
                    },
                    "follow": {
                        "type": "boolean",
                        "description": "Whether to follow the logs",
                        "default": False,
                    },
                },
                "required": ["service_name"],
            },
        },
        {
            "name": "docker_get_resource_usage",
            "description": "Get resource usage for all running containers",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "docker_get_container_resource_usage",
            "description": "Get resource usage for a specific container",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "container_name": {
                        "type": "string",
                        "description": "Name of the container",
                    },
                },
                "required": ["container_name"],
            },
        },
        {
            "name": "docker_execute_in_container",
            "description": "Execute a command in a running container",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "container_name": {
                        "type": "string",
                        "description": "Name of the container",
                    },
                    "command": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Command to execute",
                    },
                    "user": {
                        "type": "string",
                        "description": "User to run the command as",
                        "default": "",
                    },
                },
                "required": ["container_name", "command"],
            },
        },
        {
            "name": "docker_start_container",
            "description": "Start a stopped container",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "container_name": {
                        "type": "string",
                        "description": "Name of the container",
                    },
                },
                "required": ["container_name"],
            },
        },
        {
            "name": "docker_stop_container",
            "description": "Stop a running container",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "container_name": {
                        "type": "string",
                        "description": "Name of the container",
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Whether to force stop",
                        "default": False,
                    },
                },
                "required": ["container_name"],
            },
        },
        {
            "name": "docker_restart_container",
            "description": "Restart a container",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "container_name": {
                        "type": "string",
                        "description": "Name of the container",
                    },
                },
                "required": ["container_name"],
            },
        },
        {
            "name": "docker_start_services",
            "description": "Start Docker Compose services",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "build": {
                        "type": "boolean",
                        "description": "Whether to rebuild images",
                        "default": False,
                    },
                    "detach": {
                        "type": "boolean",
                        "description": "Whether to run in detached mode",
                        "default": True,
                    },
                },
            },
        },
        {
            "name": "docker_stop_services",
            "description": "Stop Docker Compose services",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "remove_volumes": {
                        "type": "boolean",
                        "description": "Whether to remove named volumes",
                        "default": False,
                    },
                },
            },
        },
        {
            "name": "docker_build_services",
            "description": "Build Docker Compose services",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "service_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of services to build",
                        "default": None,
                    },
                },
            },
        },
        {
            "name": "docker_list_images",
            "description": "List Docker images",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "all": {
                        "type": "boolean",
                        "description": "Show all images including intermediate",
                        "default": False,
                    },
                },
            },
        },
        {
            "name": "docker_list_volumes",
            "description": "List Docker volumes",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "docker_list_networks",
            "description": "List Docker networks",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
    ]


def call_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Call an MCP tool by name with arguments.
    
    Args:
        tool_name: Name of the tool to call
        arguments: Dictionary of arguments
        
    Returns:
        Dictionary with the tool result
    """
    tool_handlers = {
        "docker_get_system_info": lambda args: {
            "system": monitor.get_system_info()
        },
        "docker_list_containers": lambda args: monitor.list_containers(
            all=args.get("all", False)
        ),
        "docker_list_services": lambda args: monitor.list_services(),
        "docker_get_container_status": lambda args: monitor.get_container_status(
            args.get("container_name", "")
        ),
        "docker_get_service_status": lambda args: monitor.get_service_status(
            args.get("service_name", "")
        ),
        "docker_get_container_logs": lambda args: monitor.get_container_logs(
            container_name=args.get("container_name", ""),
            tail=args.get("tail", 100),
            follow=args.get("follow", False),
            timestamps=args.get("timestamps", True)
        ),
        "docker_get_service_logs": lambda args: monitor.get_service_logs(
            service_name=args.get("service_name", ""),
            tail=args.get("tail", 100),
            follow=args.get("follow", False)
        ),
        "docker_get_resource_usage": lambda args: monitor.get_resource_usage(),
        "docker_get_container_resource_usage": lambda args: monitor.get_container_resource_usage(
            args.get("container_name", "")
        ),
        "docker_execute_in_container": lambda args: monitor.execute_in_container(
            container_name=args.get("container_name", ""),
            command=args.get("command", []),
            user=args.get("user", "")
        ),
        "docker_start_container": lambda args: monitor.start_container(
            args.get("container_name", "")
        ),
        "docker_stop_container": lambda args: monitor.stop_container(
            container_name=args.get("container_name", ""),
            force=args.get("force", False)
        ),
        "docker_restart_container": lambda args: monitor.restart_container(
            args.get("container_name", "")
        ),
        "docker_start_services": lambda args: monitor.start_services(
            build=args.get("build", False),
            detach=args.get("detach", True)
        ),
        "docker_stop_services": lambda args: monitor.stop_services(
            remove_volumes=args.get("remove_volumes", False)
        ),
        "docker_build_services": lambda args: monitor.build_services(
            service_names=args.get("service_names")
        ),
        "docker_list_images": lambda args: monitor.list_images(
            all=args.get("all", False)
        ),
        "docker_list_volumes": lambda args: monitor.list_volumes(),
        "docker_list_networks": lambda args: monitor.list_networks(),
    }
    
    if tool_name in tool_handlers:
        try:
            return {
                "content": tool_handlers[tool_name](arguments),
                "isError": False,
            }
        except Exception as e:
            return {
                "content": {"error": str(e)},
                "isError": True,
            }
    else:
        return {
            "content": {"error": f"Unknown tool: {tool_name}"},
            "isError": True,
        }


# MCP Server initialization
if __name__ == "__main__":
    print("Docker Monitor MCP Server")
    print(f"Docker version: {monitor._get_docker_version()}")
    
    # Test connection
    result = monitor.list_containers()
    print(f"Found {result['count']} containers")
    
    result = monitor.list_services()
    print(f"Found {result['count']} services")
    
    print("Ready!")
