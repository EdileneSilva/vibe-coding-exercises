# /docker

Manage Docker services for the todo application.

## Usage

```
/docker <action> [service]
```

## Actions

| Action | Description | Example |
|--------|-------------|---------|
| `up` | Start all services (build if needed) | `/docker up` |
| `down` | Stop all services | `/docker down` |
| `rebuild` | Rebuild and restart all services | `/docker rebuild` |
| `clean` | Stop and remove volumes (clean slate) | `/docker clean` |
| `status` | Show service status | `/docker status` |
| `logs [service]` | Follow service logs | `/docker logs api` |
| `exec <service>` | Enter a running container | `/docker exec api` |
| `health` | Check health of all services | `/docker health` |

## Implementation

When this command is invoked, run the appropriate `docker compose` command:

| Action | Command |
|--------|---------|
| `up` | `docker compose up --build -d` |
| `down` | `docker compose down` |
| `rebuild` | `docker compose down && docker compose up --build -d` |
| `clean` | `docker compose down -v` |
| `status` | `docker compose ps` |
| `logs [svc]` | `docker compose logs -f [svc]` |
| `exec <svc>` | `docker compose exec <svc> bash` |
| `health` | `curl -f http://localhost:8000/health && curl -f http://localhost:8080` |

## Services

| Service | Port | Description |
|---------|------|-------------|
| `api` | 8000 | FastAPI backend |
| `web` | 8080 | SvelteKit frontend (nginx) |
| `db` | internal | PostgreSQL database |

## Notes

- Always use `docker compose` (v2) not `docker-compose` (v1)
- Database is only accessible internally — never exposed to host
- Check `.env` file for required environment variables before starting
