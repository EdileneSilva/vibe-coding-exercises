# Docker Monitor MCP Server

**Model Context Protocol Server for Docker Container Monitoring**

This MCP server provides comprehensive Docker container and service monitoring capabilities for the Docker To-Do App project. It enables AI agents to efficiently monitor, debug, and manage Docker containers.

---

## 🎯 Overview

The Docker Monitor MCP Server is designed to:

1. **Monitor** container and service status in real-time
2. **Retrieve** container logs for debugging
3. **Analyze** resource usage (CPU, memory, I/O)
4. **Execute** commands inside containers
5. **Manage** container lifecycle (start, stop, restart)
6. **Inspect** Docker system information

---

## 📡 Capabilities

### Core Features

| Feature | Description | Use Case |
|---------|-------------|----------|
| **System Info** | Get Docker version and system statistics | Understanding Docker environment |
| **Container Listing** | List running and stopped containers | Finding specific containers |
| **Service Listing** | List Docker Compose services | Managing multi-container apps |
| **Status Checking** | Get detailed container/service status | Debugging container issues |
| **Log Retrieval** | View container and service logs | Troubleshooting application errors |
| **Resource Monitoring** | Get CPU, memory, I/O usage | Performance analysis |
| **Command Execution** | Run commands inside containers | Debugging and administration |
| **Lifecycle Management** | Start, stop, restart containers | Managing container state |

---

## 🛠️ Tools

### `docker_get_system_info`

Get Docker system information including version, container count, images, volumes, and networks.

**Parameters:** None

**Returns:**
```json
{
  "containers": 5,
  "images": 20,
  "volumes": 3,
  "networks": 2,
  "version": "24.0.7"
}
```

**Example Usage:**
```python
system_info = call_tool("docker_get_system_info", {})
print(f"Docker version: {system_info['version']}")
print(f"Running containers: {system_info['containers']}")
```

---

### `docker_list_containers`

List all Docker containers.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `all` | boolean | No | false | Include stopped containers |

**Returns:**
```json
{
  "containers": [
    {
      "ID": "abc123...",
      "Image": "todo-api:latest",
      "Command": "uv run uvicorn main:app --host 0.0.0.0 --port 8000",
      "CreatedAt": "2026-06-23 10:00:00 +0000",
      "Status": "Up 5 minutes",
      "Ports": "0.0.0.0:8000->8000/tcp",
      "Names": "project-api-1"
    }
  ],
  "count": 3
}
```

**Example Usage:**
```python
# List running containers
containers = call_tool("docker_list_containers", {"all": false})

# List all containers including stopped
all_containers = call_tool("docker_list_containers", {"all": true})
```

---

### `docker_list_services`

List Docker Compose services.

**Parameters:** None

**Returns:**
```json
{
  "services": [
    {
      "name": "web",
      "command": "nginx -g daemon off;",
      "state": "running",
      "ports": "0.0.0.0:8080->80/tcp",
      "service": "web"
    },
    {
      "name": "api", 
      "command": "uv run uvicorn main:app --host 0.0.0.0 --port 8000",
      "state": "running",
      "ports": "0.0.0.0:8000->8000/tcp",
      "service": "api"
    },
    {
      "name": "db",
      "command": "docker-entrypoint.sh postgres",
      "state": "running",
      "ports": "",
      "service": "db"
    }
  ],
  "count": 3
}
```

**Example Usage:**
```python
services = call_tool("docker_list_services", {})
for service in services["services"]:
    print(f"{service['name']}: {service['state']}")
```

---

### `docker_get_container_status`

Get detailed status of a specific container.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `container_name` | string | Yes | Name of the container |

**Returns:**
```json
{
  "name": "project-api-1",
  "status": "running",
  "running": true,
  "exit_code": 0,
  "started_at": "2026-06-23T10:00:00Z",
  "health": {
    "Status": "healthy",
    "FailingStreak": 0
  },
  "config": {
    "image": "todo-api:latest",
    "cmd": ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
    "env": ["DATABASE_URL=postgresql://...", "..."]
  }
}
```

**Example Usage:**
```python
# Check if a container is running
status = call_tool("docker_get_container_status", {
    "container_name": "project-api-1"
})
if status["running"]:
    print(f"Container {status['name']} is running")
```

---

### `docker_get_service_status`

Get status of a specific Docker Compose service.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `service_name` | string | Yes | Name of the service |

**Returns:** Same format as container status

**Example Usage:**
```python
# Check API service status
status = call_tool("docker_get_service_status", {
    "service_name": "api"
})
print(f"API service status: {status['status']}")
```

---

### `docker_get_container_logs`

Get logs from a container.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `container_name` | string | Yes | - | Name of the container |
| `tail` | integer | No | 100 | Number of lines to show |
| `follow` | boolean | No | false | Whether to follow the logs |
| `timestamps` | boolean | No | true | Whether to include timestamps |

**Returns:**
```json
{
  "container": "project-api-1",
  "logs": "2026-06-23T10:00:00.123456789Z stdout: Starting FastAPI application...\n2026-06-23T10:00:01.234567890Z stdout: Database connection established\n",
  "error": "",
  "success": true,
  "truncated": false
}
```

**Example Usage:**
```python
# Get last 50 lines of logs
logs = call_tool("docker_get_container_logs", {
    "container_name": "project-api-1",
    "tail": 50,
    "timestamps": true
})
print(logs["logs"])

# Follow logs in real-time (limited by timeout)
live_logs = call_tool("docker_get_container_logs", {
    "container_name": "project-api-1",
    "tail": 0,
    "follow": true
})
```

---

### `docker_get_service_logs`

Get logs from a Docker Compose service.

**Parameters:** Same as container logs

**Returns:** Same format as container logs

**Example Usage:**
```python
# Get API service logs
logs = call_tool("docker_get_service_logs", {
    "service_name": "api",
    "tail": 100
})
print(logs["logs"])
```

---

### `docker_get_resource_usage`

Get resource usage for all running containers.

**Parameters:** None

**Returns:**
```json
{
  "stats": [
    {
      "ID": "abc123...",
      "Name": "project-api-1",
      "CPUPerc": "12.50",
      "MemUsage": "256MiB / 512MiB",
      "MemPerc": "50.00",
      "NetIO": "50kB / 25kB",
      "BlockIO": "200kB / 100kB",
      "PIDs": "10"
    }
  ],
  "count": 3
}
```

**Example Usage:**
```python
usage = call_tool("docker_get_resource_usage", {})
for stat in usage["stats"]:
    print(f"{stat['Name']}: CPU {stat['CPUPerc']}%, Memory {stat['MemUsage']}")
```

---

### `docker_get_container_resource_usage`

Get resource usage for a specific container.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `container_name` | string | Yes | Name of the container |

**Returns:** Same format as resource usage

---

### `docker_execute_in_container`

Execute a command in a running container.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `container_name` | string | Yes | - | Name of the container |
| `command` | array | Yes | - | Command to execute (as array) |
| `user` | string | No | "" | User to run the command as |

**Returns:**
```json
{
  "container": "project-api-1",
  "command": "python -c import os; print(os.getenv('DATABASE_URL'))",
  "success": true,
  "returncode": 0,
  "stdout": "postgresql://todouser:todopassword@db:5432/tododb",
  "stderr": ""
}
```

**Example Usage:**
```python
# Check database connection from API container
result = call_tool("docker_execute_in_container", {
    "container_name": "project-api-1",
    "command": ["python", "-c", "import psycopg2; print('DB OK')"]
})
if result["success"]:
    print(result["stdout"])

# Run migration in API container
result = call_tool("docker_execute_in_container", {
    "container_name": "project-api-1", 
    "command": ["uv", "run", "alembic", "upgrade", "head"]
})
```

---

### Container Lifecycle Tools

#### `docker_start_container`
Start a stopped container.

**Parameters:**
- `container_name` (string, required): Name of the container

**Example:**
```python
result = call_tool("docker_start_container", {
    "container_name": "project-db-1"
})
```

#### `docker_stop_container`
Stop a running container.

**Parameters:**
- `container_name` (string, required): Name of the container
- `force` (boolean, optional): Whether to force stop

**Example:**
```python
result = call_tool("docker_stop_container", {
    "container_name": "project-api-1",
    "force": false
})
```

#### `docker_restart_container`
Restart a container.

**Parameters:**
- `container_name` (string, required): Name of the container

**Example:**
```python
result = call_tool("docker_restart_container", {
    "container_name": "project-web-1"
})
```

---

### Service Management Tools

#### `docker_start_services`
Start Docker Compose services.

**Parameters:**
- `build` (boolean, optional): Whether to rebuild images
- `detach` (boolean, optional): Whether to run in detached mode

**Example:**
```python
# Start all services with build
result = call_tool("docker_start_services", {
    "build": true,
    "detach": true
})

# Start services without build
result = call_tool("docker_start_services", {
    "build": false,
    "detach": true
})
```

#### `docker_stop_services`
Stop Docker Compose services.

**Parameters:**
- `remove_volumes` (boolean, optional): Whether to remove named volumes

**Example:**
```python
# Stop services, keep volumes
result = call_tool("docker_stop_services", {
    "remove_volumes": false
})

# Stop services and remove volumes (clean slate)
result = call_tool("docker_stop_services", {
    "remove_volumes": true
})
```

#### `docker_build_services`
Build Docker Compose services.

**Parameters:**
- `service_names` (array, optional): List of services to build

**Example:**
```python
# Build all services
result = call_tool("docker_build_services", {})

# Build only API service
result = call_tool("docker_build_services", {
    "service_names": ["api"]
})
```

---

### Information Tools

#### `docker_list_images`
List Docker images.

**Parameters:**
- `all` (boolean, optional): Show all images including intermediate

**Example:**
```python
images = call_tool("docker_list_images", {"all": false})
```

#### `docker_list_volumes`
List Docker volumes.

**Parameters:** None

#### `docker_list_networks`
List Docker networks.

**Parameters:** None

---

## 🎯 Use Cases

### 1. Check Project Status

```python
# Get all service statuses
services = call_tool("docker_list_services", {})

# Check each service
for service in services["services"]:
    if service["state"] != "running":
        print(f"⚠️ Service {service['name']} is not running!")
    else:
        print(f"✅ Service {service['name']} is running")
```

### 2. Debug Container Issues

```python
# Check container logs for errors
logs = call_tool("docker_get_container_logs", {
    "container_name": "project-api-1",
    "tail": 100
})

if "Error" in logs["logs"] or "Traceback" in logs["logs"]:
    print("⚠️ Found errors in logs:")
    print(logs["logs"])
```

### 3. Monitor Resource Usage

```python
# Get resource usage and check for issues
usage = call_tool("docker_get_resource_usage", {})

for stat in usage["stats"]:
    mem_usage = float(stat["MemPerc"].rstrip("%"))
    cpu_usage = float(stat["CPUPerc"].rstrip("%"))
    
    if mem_usage > 80:
        print(f"⚠️ High memory usage: {stat['Name']} at {mem_usage}%")
    if cpu_usage > 80:
        print(f"⚠️ High CPU usage: {stat['Name']} at {cpu_usage}%")
```

### 4. Execute Debug Commands

```python
# Check database connection from API container
result = call_tool("docker_execute_in_container", {
    "container_name": "project-api-1",
    "command": ["python", "-c", "import psycopg2; conn = psycopg2.connect(host='db', user='todouser', password='todopassword', dbname='tododb'); print('✅ DB connection OK'); conn.close()"]
})

if result["success"]:
    print(result["stdout"])
else:
    print(f"❌ Error: {result['stderr']}")
```

---

## 🎯 Project-Specific Information

For the Docker To-Do App project, this MCP server works with:

### Services
- **web**: SvelteKit frontend with nginx (port 8080)
- **api**: FastAPI backend (port 8000)
- **db**: PostgreSQL database (port 5432, internal only)

### Networks
- `traefik_frontend`: For web traffic
- `traefik_backend`: For internal service communication

### Volumes
- `pgdata`: PostgreSQL data persistence

### Common Commands

```python
# Start the entire project
call_tool("docker_start_services", {"build": true, "detach": true})

# Check API service logs
call_tool("docker_get_service_logs", {"service_name": "api", "tail": 50})

# Execute command in API container
call_tool("docker_execute_in_container", {
    "container_name": "briefs-todo-app-starter-api-1",
    "command": ["bash"]
})
```

---

## 🚀 Integration

This MCP server is automatically discovered by Mistral Vibe when placed in the `.vibe/mcp/` directory.

### Manual Testing

To test the server manually:

```bash
cd /path/to/project
python .vibe/mcp/docker-monitor/server.py
```

This will:
1. Initialize the Docker monitor
2. Check Docker version
3. Count containers and services
4. Be ready to handle tool calls

---

## 🔒 Security Considerations

1. **Command Execution**: Only execute trusted commands in containers
2. **Resource Limits**: Docker stats may show sensitive resource information
3. **Environment Variables**: Container inspection may reveal environment variables
4. **Network Access**: Commands executed in containers have network access
5. **File System**: Commands have access to the container's file system

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-06-23 | Initial release | Full Docker monitoring capabilities |

---

## 🎯 Related Files

- [Root AGENTS.md](../../../AGENTS.md) - Main AI assistant guide
- [file-indexer MCP](../file-indexer/README.md) - File system indexing MCP
- [git-analyzer MCP](../git-analyzer/README.md) - Git analysis MCP
- [docker-compose.yml](../../../docker-compose.yml) - Docker Compose configuration

---

## 📚 Additional Information

- [Model Context Protocol (MCP) Specification](https://github.com/modelcontextprotocol/specification)
- [Mistral Vibe Documentation](https://docs.mistral.ai/vibe/)
- [Docker CLI Documentation](https://docs.docker.com/reference/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

---

*Last updated: 2026-06-23*
*Generated by Mistral Vibe - Docker Monitor MCP Server*