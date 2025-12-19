# IELTS Mock Test Platform - Docker Setup

## Quick Start

### Prerequisites

- Docker Desktop installed and running
- Git (optional)

### Running the Application

1. **Start all services:**

   ```bash
   docker-compose up -d
   ```

2. **Check service status:**

   ```bash
   docker-compose ps
   ```

3. **View logs:**

   ```bash
   # All services
   docker-compose logs -f

   # Specific service
   docker-compose logs -f backend
   docker-compose logs -f frontend
   docker-compose logs -f db
   ```

4. **Access the application:**

   - **Frontend**: http://localhost:5173
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs

5. **Initialize the database** (first time only):

   ```bash
   docker-compose exec backend python -m app
   ```

   This will create:

   - All database tables
   - Default admin user: `admin@example.com` / `admin123`
   - Question type templates

### Stopping the Application

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clears database)
docker-compose down -v
```

### Rebuilding Services

```bash
# Rebuild all services
docker-compose build

# Rebuild specific service
docker-compose build backend
docker-compose build frontend

# Rebuild and restart
docker-compose up -d --build
```

## Services

### Database (PostgreSQL)

- **Port**: 5432
- **Username**: ielts_user
- **Password**: password
- **Database**: ielts_db

### Backend (FastAPI)

- **Port**: 8000
- **Auto-reload**: Enabled (code changes reload automatically)
- **Volumes**: `./backend` mounted for live code updates

### Frontend (React + Vite)

- **Port**: 5173
- **Auto-reload**: Enabled (HMR - Hot Module Replacement)
- **Volumes**: `./frontend` mounted for live code updates

## Development Workflow

### Backend Development

```bash
# Enter backend container
docker-compose exec backend bash

# Run migrations (when available)
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"
```

### Frontend Development

```bash
# Enter frontend container
docker-compose exec frontend sh

# Install new package
docker-compose exec frontend npm install package-name

# Run linter
docker-compose exec frontend npm run lint
```

### Database Access

```bash
# Connect to PostgreSQL
docker-compose exec db psql -U ielts_user -d ielts_db

# Example queries
SELECT * FROM users;
SELECT * FROM test_templates;
```

## Environment Variables

### Backend (.env)

Located at `backend/.env`:

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key
- `ALLOWED_ORIGINS`: CORS allowed origins

### Frontend (.env.local)

Located at `frontend/.env.local`:

- `VITE_API_URL`: Backend API URL

## Troubleshooting

### Database connection errors

```bash
# Check database is running
docker-compose ps db

# Restart database
docker-compose restart db
```

### Frontend not loading

```bash
# Check logs
docker-compose logs frontend

# Rebuild frontend
docker-compose up -d --build frontend
```

### Backend errors

```bash
# View logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

### Clear everything and start fresh

```bash
docker-compose down -v
docker-compose up -d --build
docker-compose exec backend python -m app
```

## Production Deployment

For production, modify `docker-compose.yml`:

1. Change `SECRET_KEY` to a strong random value
2. Update `POSTGRES_PASSWORD`
3. Set `DEBUG: false` in backend
4. Remove volume mounts for code
5. Use `CMD` without `--reload`
6. Add nginx reverse proxy
7. Enable HTTPS

Example production command:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Network Architecture

```
Browser
   ↓
Frontend (Port 5173)
   ↓
Backend API (Port 8000)
   ↓
PostgreSQL Database (Port 5432)
```

All services communicate via the `ielts-network` bridge network.

## Data Persistence

- **Database**: Data stored in `postgres_data` volume
- **Uploads**: Files stored in `backend_uploads` volume

To backup data:

```bash
# Backup database
docker-compose exec db pg_dump -U ielts_user ielts_db > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T db psql -U ielts_user -d ielts_db
```
