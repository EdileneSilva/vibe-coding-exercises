# Docker Helper Skill

**Auto-triggered Skill for Docker Operations and Container Management**

This skill is automatically triggered when the user mentions Docker, containers, or related concepts. It provides specialized assistance for Docker operations, debugging, and deployment.

---

## 🎯 Purpose

The `docker-helper` skill provides specialized assistance for:
- Docker container lifecycle management (start, stop, restart, remove)
- Docker image building and management
- Docker Compose operations
- Container debugging and troubleshooting
- Docker network and volume management
- Performance monitoring and optimization
- Docker security best practices

---

## 🔍 Trigger Patterns

This skill activates when the user message contains:

### Primary Triggers (High Confidence)
- "docker"
- "container"
- "containers"
- "image"
- "images"
- "docker compose"
- "docker-compose"
- "compose"
- "build"
- "run"
- "start"
- "stop"
- "restart"
- "kill"
- "rm"
- "rmi"
- "ps"
- "logs"

### Secondary Triggers (Medium Confidence)
- "port"
- "ports"
- "volume"
- "volumes"
- "network"
- "networks"
- "service"
- "services"
- "stack"
- "deployment"
- "deploy"
- "scaling"
- "orchestration"

### Contextual Triggers
- User is in a directory with Dockerfile or docker-compose.yml
- User mentions specific container names from the project
- User asks about service status or health
- Docker-related error messages in user input

---

## 🚀 Capabilities

### Container Management
- Start, stop, restart, pause, unpause containers
- View running and stopped containers
- Inspect container details (processes, ports, mounts)
- Execute commands inside containers
- Export and import containers
- View container logs and statistics

### Image Management
- Build images from Dockerfiles
- Pull and push images from registries
- List and remove images
- Inspect image layers and history
- Tag and manage image versions

### Docker Compose
- Start, stop, and manage multi-container applications
- Build and rebuild services
- View service status and logs
- Execute commands in service containers
- Scale services
- Manage environment variables and secrets

### Networking
- Create, list, and remove networks
- Inspect network configuration
- Connect and disconnect containers to networks
- Troubleshoot network connectivity

### Volumes
- Create, list, and remove volumes
- Inspect volume contents
- Backup and restore volumes
- Manage volume permissions

### Debugging
- Diagnose container startup issues
- Analyze container logs
- Inspect container processes and resource usage
- Check port mappings and network connectivity
- Debug Dockerfile build issues

### Performance
- Monitor container resource usage (CPU, memory, I/O)
- Analyze performance metrics
- Identify performance bottlenecks
- Optimize container resource allocation
- Recommend performance improvements

---

## 📋 Workflows

### Workflow 1: Start Development Environment

**Trigger:** User says "start docker" or "docker compose up"

**Steps:**
1. Check if Docker is running
2. Navigate to project directory
3. Check for docker-compose.yml file
4. Validate Dockerfile and configuration
5. Start containers with appropriate flags
6. Verify all services are running
7. Display access information (URLs, ports)

**Example Interaction:**
```
User: "Start the development environment with docker"

AI (docker-helper skill active):
1. Checking Docker status... ✅ Docker is running
2. Found docker-compose.yml in /path/to/project
3. Validating configuration... ✅ Valid
4. Starting containers...

Executing: docker compose up --build -d

Building api service... ✅ Done
Building web service... ✅ Done
Building db service... ✅ Done

✅ All services started successfully!

Access your application at:
- Web UI: http://localhost:8080
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

Services:
- web: Up (healthy) - Port 8080
- api: Up (healthy) - Port 8000
- db: Up (healthy) - Port 5432 (internal)

Would you like me to:
- View the logs?
- Run a specific command in a container?
- Check resource usage?
```

### Workflow 2: Debug Container Issues

**Trigger:** User says "container not starting" or "docker error"

**Steps:**
1. Identify the problematic container
2. Check container status and exit code
3. View container logs
4. Inspect container configuration
5. Check resource constraints
6. Analyze Dockerfile for issues
7. Provide troubleshooting recommendations

**Example Interaction:**
```
User: "The api container keeps crashing"

AI (docker-helper skill active):
Debugging api container...

1. Container status: Exited (137)
   - Exit code 137 typically indicates OOM kill (Out of Memory)

2. Last logs:
   ```
   2026-06-23 10:00:00 Starting FastAPI application...
   2026-06-23 10:00:05 Loaded 1000 records from database
   2026-06-23 10:00:10 MemoryError: Unable to allocate memory
   ```

3. Resource usage before crash:
   - Memory: 1.2GB / 1.5GB limit (80% usage)
   - CPU: 45%

🔍 **Diagnosis:** Container hitting memory limit

💡 **Solutions:**
1. Increase memory limit in docker-compose.yml:
   ```yaml
   deploy:
     resources:
       limits:
         memory: 2G
   ```
2. Optimize application memory usage
3. Reduce batch processing size

Would you like me to apply fix #1?
```

### Workflow 3: Build and Deploy New Image

**Trigger:** User says "build docker image" or "deploy new version"

**Steps:**
1. Identify which service to build
2. Check for Dockerfile
3. Validate Dockerfile syntax
4. Build the image with appropriate tags
5. Test the image locally
6. Push to registry if requested
7. Deploy to production if requested

**Example Interaction:**
```
User: "Build a new api image with the latest changes"

AI (docker-helper skill active):
1. Found Dockerfile in api/ directory
2. Validating Dockerfile... ✅ Valid
3. Building image...

Executing: docker build -t todo-api:1.0.0 -t todo-api:latest ./api

Step 1/8: FROM python:3.12-slim
Step 2/8: WORKDIR /app
...
Step 8/8: CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
✅ Build completed successfully

Image created:
- todo-api:1.0.0
- todo-api:latest

Would you like to:
1. Test the new image locally?
2. Push to Docker Hub?
3. Deploy to production?
4. Run the container?

User: "Test it locally"

AI:
Running container from new image...
Executing: docker run -d -p 8000:8000 --name test-api todo-api:1.0.0

✅ Container running on port 8000
Test endpoint: curl http://localhost:8000/todos

Would you like me to verify the API is working?
```

### Workflow 4: Monitor Resource Usage

**Trigger:** User says "docker stats" or "check container resources"

**Steps:**
1. Identify running containers
2. Display real-time resource usage
3. Analyze usage patterns
4. Provide optimization recommendations
5. Offer to adjust resource limits

**Example Interaction:**
```
User: "Show me docker resource usage"

AI (docker-helper skill active):
Real-time resource usage:

┌─────────────────────────────────────────────────────────────┐
│ Container  │ CPU %  │ Memory    │ Network I/O │ Disk I/O │ Status │
├────────────┼────────┼──────────┼─────────────┼──────────┼────────┤
│ web        │ 5.2%   │ 128Mi/256Mi │ 10kb/5kb   │ 100kb/50kb │ Up    │
│ api        │ 12.5%  │ 256Mi/512Mi │ 50kb/25kb  │ 200kb/100kb│ Up    │
│ db         │ 3.1%   │ 64Mi/128Mi  │ 1kb/1kb     │ 50kb/50kb  │ Up    │
└─────────────────────────────────────────────────────────────┘

💡 **Recommendations:**
1. ✅ All containers within resource limits
2. ⚠️ API container using 50% of memory - consider increasing limit
3. ✅ Low CPU usage across all containers

Would you like me to:
- View detailed stats for a specific container?
- Adjust resource limits?
- Set up resource alerts?
```

---

## 🛠️ Project-Specific Knowledge

### Project Docker Architecture

This project uses Docker Compose with the following services:

```yaml
# docker-compose.yml
services:
  web:
    build: ./web
    ports:
      - "8080:80"
    networks:
      - traefik_frontend
      - traefik_backend
    depends_on:
      - api

  api:
    build: ./api
    ports:
      - "8000:8000"
    networks:
      - traefik_backend
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16
    environment:
      POSTGRES_USER: todouser
      POSTGRES_PASSWORD: todopassword
      POSTGRES_DB: tododb
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - traefik_backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U todouser -d tododb"]
      interval: 5s
      timeout: 5s
      retries: 5

networks:
  traefik_frontend:
    driver: bridge
  traefik_backend:
    driver: bridge

volumes:
  pgdata:
    driver: local
```

### Common Commands for This Project

| Action | Command | Description |
|--------|---------|-------------|
| Start all services | `docker compose up --build -d` | Build and start in background |
| Stop all services | `docker compose down` | Stop containers, keep volumes |
| Stop and clean | `docker compose down -v` | Stop containers and remove volumes |
| View logs | `docker compose logs -f` | Follow all service logs |
| View API logs | `docker compose logs -f api` | Follow API service logs |
| View web logs | `docker compose logs -f web` | Follow web service logs |
| Enter API container | `docker compose exec api bash` | Get shell in API container |
| Enter web container | `docker compose exec web bash` | Get shell in web container |
| Build API image | `docker compose build api` | Rebuild API image |
| Build web image | `docker compose build web` | Rebuild web image |
| Check status | `docker compose ps` | Show service status |
| Pull latest images | `docker compose pull` | Update base images |

### Service Details

| Service | Port | Health Check | Purpose |
|---------|------|--------------|---------|
| web | 8080 | HTTP 200 on / | SvelteKit frontend with nginx |
| api | 8000 | HTTP 200 on /todos | FastAPI backend |
| db | 5432 | pg_isready | PostgreSQL database |

### Networks

| Network | Services | Purpose |
|---------|----------|---------|
| `traefik_frontend` | web | Frontend network for web traffic |
| `traefik_backend` | api, db | Backend network for internal communication |

### Volumes

| Volume | Mount Point | Purpose |
|--------|-------------|---------|
| `pgdata` | `/var/lib/postgresql/data` | PostgreSQL data persistence |

---

## 🎯 Best Practices

### Dockerfile Best Practices

1. **Use specific base image tags**
   ```dockerfile
   FROM python:3.12-slim  # Good
   FROM python:latest    # Bad - not specific
   ```

2. **Minimize layers**
   ```dockerfile
   RUN apt-get update && \
       apt-get install -y build-essential && \
       rm -rf /var/lib/apt/lists/*  # Good - combined commands
   ```

3. **Use multi-stage builds**
   ```dockerfile
   FROM node:20-slim AS builder
   # Build stage
   
   FROM nginx:alpine
   # Runtime stage
   COPY --from=builder /app/build /usr/share/nginx/html
   ```

4. **Copy dependency files first**
   ```dockerfile
   COPY package.json bun.lock ./
   RUN bun install --frozen-lockfile
   COPY . .
   ```

5. **Create non-root users**
   ```dockerfile
   RUN useradd -m -u 1000 appuser
   USER appuser
   ```

### Docker Compose Best Practices

1. **Use environment variable substitution**
   ```yaml
   environment:
     - DATABASE_URL=${DATABASE_URL:-postgresql://localhost:5432/db}
   ```

2. **Set resource limits**
   ```yaml
   deploy:
     resources:
       limits:
         memory: 512M
         cpus: '1.0'
   ```

3. **Configure restart policies**
   ```yaml
   restart: unless-stopped
   ```

4. **Use healthchecks**
   ```yaml
   healthcheck:
     test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
     interval: 30s
     timeout: 10s
     retries: 3
   ```

5. **Define explicit networks**
   ```yaml
   networks:
     - frontend
     - backend
   ```

### Security Best Practices

1. **Never expose database ports**
   ```yaml
   # Bad
   ports:
     - "5432:5432"
   
   # Good - internal only
   # (no ports mapping for db service)
   ```

2. **Use secrets for sensitive data**
   ```yaml
   secrets:
     - db_password
   
   environment:
     POSTGRES_PASSWORD_FILE: /run/secrets/db_password
   ```

3. **Set read-only filesystems**
   ```yaml
   volumes:
     - ./config:/app/config:ro
   ```

4. **Use .dockerignore**
   ```text
   .git
   .env
   *.md
   node_modules
   __pycache__
   ```

5. **Scan images for vulnerabilities**
   ```bash
   docker scan todo-api:latest
   ```

---

## 🔧 Configuration

### Skill Configuration

```yaml
# .vibe/skills/docker-helper/config.yaml
name: docker-helper
version: 1.0.0
description: Docker operations and container management skill
author: Mistral Vibe
enabled: true

triggers:
  primary:
    - docker
    - container
    - containers
    - image
    - images
    - compose
  secondary:
    - port
    - volume
    - network
    - service
    - deploy

settings:
  project_name: briefs-todo-app-starter
  compose_file: docker-compose.yml
  default_network: bridge
  default_timeout: 30
  max_log_lines: 100
  auto_cleanup: false
```

---

## 📝 Examples

### Example 1: Simple Container Start
```
User: "Start the database container"

AI Response:
Starting PostgreSQL container from docker-compose.yml...

Executing: docker compose up -d db

✅ Database container started
- Service: db
- Image: postgres:16
- Port: 5432 (internal only)
- Volume: pgdata
- Status: healthy

The database is now available for the API service to connect.
```

### Example 2: Debug Network Connectivity
```
User: "Why can't the api container connect to the database?"

AI Response:
Debugging network connectivity between api and db containers...

1. Checking if both containers are running:
   - api: Up (healthy)
   - db: Up (healthy)
   ✅ Both containers are running

2. Checking network configuration:
   - Both containers on network: traefik_backend
   ✅ Same network

3. Testing connectivity from api container:
   Executing: docker compose exec api ping db
   
   ```
   PING db (172.20.0.2): 56 data bytes
   64 bytes from 172.20.0.2: icmp_seq=0 ttl=64 time=0.123 ms
   ```
   ✅ Network connectivity OK

4. Testing database connection:
   Executing: docker compose exec api python -c "import psycopg2; psycopg2.connect(host='db', port=5432, user='todouser', password='todopassword', dbname='tododb')"
   
   ✅ Database connection successful

💡 The connectivity is working! The issue might be:
- Database not ready when API starts (add retry logic)
- Incorrect connection string in API configuration
- Database user permissions

Would you like me to check the API connection string?
```

### Example 3: View Service Logs
```
User: "Show me the last 50 lines of the api logs"

AI Response:
Last 50 lines of api container logs:

```
2026-06-23 10:00:00 Starting FastAPI application...
2026-06-23 10:00:01 Database connection established
2026-06-23 10:00:02 API server started on 0.0.0.0:8000
2026-06-23 10:00:05 GET /todos - 200 OK
2026-06-23 10:00:08 POST /todos - 201 Created
2026-06-23 10:00:10 GET /todos/1 - 200 OK
2026-06-23 10:00:15 PUT /todos/1 - 200 OK
2026-06-23 10:00:20 DELETE /todos/1 - 204 No Content
```

Would you like me to:
- Follow the logs in real-time?
- Filter for specific messages?
- Check for errors only?
```

### Example 4: Clean Up Unused Resources
```
User: "Clean up unused docker images and containers"

AI Response:
Cleaning up Docker resources...

1. Removing stopped containers:
   Executing: docker container prune -f
   ✅ Removed 5 stopped containers

2. Removing unused networks:
   Executing: docker network prune -f
   ✅ Removed 3 unused networks

3. Removing dangling images:
   Executing: docker image prune -f
   ✅ Removed 2 dangling images

4. Removing unused volumes:
   ⚠️ WARNING: This will remove all unused volumes, including data!
   
   Executing: docker volume prune -f
   ✅ Removed 1 unused volume

5. Removing unused images:
   Executing: docker image prune -a -f
   ⚠️ This removes all images not used by at least one container
   
   Would you like to proceed? (y/N)

Summary:
- Containers cleaned: 5
- Networks cleaned: 3
- Dangling images cleaned: 2
- Unused volumes cleaned: 1
- Total space reclaimed: ~1.2GB

Would you like me to also clean up build cache?
```

---

## 🔍 Related Files

- [Root AGENTS.md](../../../AGENTS.md) - Main AI assistant guide
- [api/AGENTS.md](../../../api/AGENTS.md) - API-specific context
- [web/AGENTS.md](../../../web/AGENTS.md) - Frontend-specific context
- [docs/TECHNICAL_GUIDE.md](../../../docs/TECHNICAL_GUIDE.md) - Technical implementation
- [docker-compose.yml](../../../docker-compose.yml) - Docker Compose configuration

---

*Last updated: 2026-06-23*
*Generated by Mistral Vibe - Docker Helper Skill*