# ACE Platform - VPS Deployment Guide

This guide explains how to deploy the ACE Platform to a Virtual Private Server (VPS) using Docker Compose.

## Prerequisites

- A VPS (Ubuntu 20.04/22.04 recommended)
- Root or sudo access
- Domain name (optional, but recommended)

## 1. Install Docker & Docker Compose

Run the following commands on your VPS:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add current user to docker group (avoid sudo for docker commands)
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker compose version
```

## 2. Transfer Code

You can either clone your repository (if hosted on GitHub/GitLab) or copy files directly.

### Option A: Git Clone (Recommended)

```bash
git clone <your-repo-url> ace-platform
cd ace-platform
```

### Option B: Copy Files (SCP)

From your local machine:

```bash
scp -r c:\Projects\ace-platform user@your-vps-ip:~/ace-platform
```

## 3. Configuration

Create the environment file for the backend:

```bash
cd backend
cp .env.example .env
nano .env
```

**Critical Settings to Update:**

- `DATABASE_URL`: `postgresql://postgres:postgres@db:5432/ace_db` (Matches docker-compose.yml)
- `SECRET_KEY`: Generate a strong random string.
- `ALLOWED_ORIGINS`: `http://<your-vps-ip>,http://<your-domain>`

## 4. Deploy

Run the application in detached mode:

```bash
cd ~/ace-platform
docker compose up -d --build
```

## 5. Verify Deployment

- **Frontend**: Visit `http://<your-vps-ip>`
- **Backend API**: Visit `http://<your-vps-ip>:8000/docs`

## 6. Troubleshooting

**Check Logs:**

```bash
docker compose logs -f
```

**Restart Services:**

```bash
docker compose restart
```

**Rebuild after changes:**

```bash
docker compose up -d --build
```
