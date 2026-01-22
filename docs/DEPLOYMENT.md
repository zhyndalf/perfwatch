# PerfWatch Deployment Guide

This guide walks you through deploying PerfWatch on a bare Linux machine from scratch.

---

## Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+, Debian 11+, or similar)
- **Architecture**: x86_64 (amd64) or ARM64 (aarch64)
- **RAM**: Minimum 2GB, recommended 4GB+
- **Disk**: Minimum 10GB free space
- **Network**: Internet access for initial setup
- **Privileges**: Root or sudo access

### Why Linux Only?
PerfWatch uses Linux `perf stat` (the `perf` binary) for hardware performance counters. This feature is not available on Windows or macOS.

---

## ARM64 Deployment (Raspberry Pi, AWS Graviton, etc.)

PerfWatch fully supports ARM64 Linux systems including:
- **Raspberry Pi 4/5** (64-bit Raspberry Pi OS)
- **AWS Graviton** instances (EC2 t4g, c7g, m7g, etc.)
- **Apple Silicon** with Linux VMs (UTM, Parallels)
- **NVIDIA Jetson** (Nano, Xavier, Orin)
- **Oracle Cloud** Ampere A1 instances

### Using Pre-built Multi-Arch Images

The easiest way to deploy on ARM64 is using our pre-built images from GitHub Container Registry:

```bash
# Images auto-detect your architecture (amd64 or arm64)
docker pull ghcr.io/zhyndalf/perfwatch-backend:latest
docker pull ghcr.io/zhyndalf/perfwatch-frontend:latest
```

Or simply use docker compose - it will pull the correct architecture automatically:

```bash
git clone https://github.com/zhyndalf/perfwatch.git
cd perfwatch
docker compose up -d
```

### Building Locally on ARM64

Building on ARM64 hardware works exactly the same as x86_64:

```bash
# Clone repository
git clone https://github.com/zhyndalf/perfwatch.git
cd perfwatch

# Build and start (same commands as x86_64)
docker compose build
docker compose up -d
docker compose exec backend alembic upgrade head
```

### ARM64-Specific Notes

1. **perf stat Support**: Depends on PMU exposure and kernel config
   - May require `CONFIG_ARM_PMU=y` in kernel config
   - Available counters vary by SoC (Cortex-A72, A76, X1, etc.)
   - Raspberry Pi 4/5 has full PMU support

2. **CPU Temperature**: Depends on device tree sensors
   - Works on Raspberry Pi with standard kernel
   - May show "N/A" on some ARM boards without thermal sensors

3. **Performance Expectations**: Similar to x86_64
   - Perf stat counters vary by ARM PMU/SoC
   - Cache sizes/levels vary by processor
   - All psutil-based metrics work identically

4. **Docker Requirements**:
   - Docker 20.10+ recommended
   - Use 64-bit OS (arm64/aarch64), not 32-bit (armv7l)

### Raspberry Pi Specific Setup

```bash
# Install Docker on Raspberry Pi OS (64-bit)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Reboot or re-login, then:
cd perfwatch
docker compose up -d
```

### Verifying ARM64 Support

```bash
# Check your architecture
uname -m
# Expected: aarch64

# Verify container is running ARM64
docker compose exec backend uname -m
# Expected: aarch64

# Test perf stat counters
docker compose exec backend perf stat -e cycles,instructions -a sleep 1
# Expected: Non-zero values. If <not supported>, PMU is not exposed.
```

---

## Step 1: Install Docker and Docker Compose

### Ubuntu/Debian
```bash
# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verify installation
sudo docker --version
sudo docker compose version
```

### RHEL/CentOS/Fedora
```bash
# Install Docker
sudo dnf -y install dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Verify installation
sudo docker --version
sudo docker compose version
```

### Add Current User to Docker Group (Optional)
```bash
# Avoid needing sudo for docker commands
sudo usermod -aG docker $USER

# Log out and back in for changes to take effect
# Or run: newgrp docker
```

---

## Step 2: Clone the Repository

```bash
# Install git if not present
sudo apt-get install -y git  # Ubuntu/Debian
# OR
sudo dnf install -y git      # RHEL/CentOS/Fedora

# Clone PerfWatch
git clone https://github.com/zhyndalf/perfwatch.git
cd perfwatch
```

---

## Step 3: Configure Environment Variables

### Create Production .env File
```bash
# Copy example environment file
cp .env.example .env

# Edit with your preferred editor
nano .env
# OR
vim .env
```

### Required Configuration Changes

**CRITICAL: Change these values for production!**

```bash
# Database credentials (change from defaults)
POSTGRES_USER=perfwatch_prod
POSTGRES_PASSWORD=<GENERATE_STRONG_PASSWORD>
POSTGRES_DB=perfwatch

# JWT secret (generate a strong random secret)
JWT_SECRET=<GENERATE_STRONG_SECRET>
JWT_EXPIRE_HOURS=24

# Admin credentials (change from defaults)
ADMIN_USERNAME=<YOUR_ADMIN_USERNAME>
ADMIN_PASSWORD=<YOUR_STRONG_PASSWORD>
```

### Generate Strong Secrets

```bash
# Generate JWT secret (64 random characters)
openssl rand -hex 32

# Generate strong database password
openssl rand -base64 32
```

### Example Production .env
```bash
# Database
POSTGRES_USER=perfwatch_prod
POSTGRES_PASSWORD=xK9mP2vL8qR5nT3wY7jH4fD6sA1gZ0cV
POSTGRES_DB=perfwatch

# Backend
JWT_SECRET=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
JWT_EXPIRE_HOURS=24

# Admin user
ADMIN_USERNAME=sysadmin
ADMIN_PASSWORD=MySecureP@ssw0rd!2024
```

---

## Step 4: Configure Docker Compose for Production

### Review docker-compose.yml

The default `docker-compose.yml` is configured for development. For production, consider these adjustments:

**Option A: Use as-is (simplest)**
- Suitable for single-machine deployments
- Database data persists in Docker volume

**Option B: Customize for production (recommended)**

Create `docker-compose.prod.yml`:

```yaml
services:
  db:
    image: postgres:15
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "127.0.0.1:5432:5432"  # Only expose to localhost
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: unless-stopped
    privileged: true  # Required for perf
    environment:
      - DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      - JWT_SECRET=${JWT_SECRET}
      - JWT_EXPIRE_HOURS=${JWT_EXPIRE_HOURS}
      - ADMIN_USERNAME=${ADMIN_USERNAME}
      - ADMIN_PASSWORD=${ADMIN_PASSWORD}
    ports:
      - "127.0.0.1:8000:8000"  # Only expose to localhost
    depends_on:
      db:
        condition: service_healthy

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    restart: unless-stopped
    ports:
      - "3000:80"  # Expose to network (or use reverse proxy)
    depends_on:
      - backend

volumes:
  postgres_data:
```

**Key production changes:**
- `restart: unless-stopped` - Auto-restart on failure
- `127.0.0.1:5432:5432` - Database only accessible from localhost
- `127.0.0.1:8000:8000` - Backend API only accessible from localhost
- Frontend on port 3000 (use reverse proxy for HTTPS)

---

## Step 5: Build and Start Services

### Using Default docker-compose.yml
```bash
# Build images
sudo docker compose build

# Start services in detached mode
sudo docker compose up -d

# Check service status
sudo docker compose ps
```

### Using Production docker-compose.prod.yml
```bash
# Build images
sudo docker compose -f docker-compose.prod.yml build

# Start services
sudo docker compose -f docker-compose.prod.yml up -d

# Check status
sudo docker compose -f docker-compose.prod.yml ps
```

---

## Step 6: Initialize Database

### Run Database Migrations
```bash
# Wait for services to be healthy (check logs)
sudo docker compose logs -f backend

# Run migrations (Ctrl+C after you see "Application startup complete")
sudo docker compose exec backend alembic upgrade head
```

### Verify Database Initialization
```bash
# Check that admin user was created
sudo docker compose logs backend | grep "Admin user"

# Should see: "Admin user created successfully" or "Admin user already exists"
```

---

## Step 7: Verify Deployment

### Check Service Health
```bash
# All services should be "Up" and "healthy"
sudo docker compose ps

# Check backend health endpoint
curl http://localhost:8000/health

# Expected response: {"status":"healthy"}
```

### Test Authentication
```bash
# Login with admin credentials
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"YOUR_ADMIN_USERNAME","password":"YOUR_ADMIN_PASSWORD"}'

# Should return JWT token
```

### Access Web Interface
```bash
# Open browser to:
http://<SERVER_IP>:3000

# Login with your admin credentials
```

---

## Step 8: Configure Firewall (Optional but Recommended)

### Using UFW (Ubuntu/Debian)
```bash
# Install UFW
sudo apt-get install -y ufw

# Allow SSH (IMPORTANT: do this first!)
sudo ufw allow 22/tcp

# Allow PerfWatch frontend
sudo ufw allow 3000/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### Using firewalld (RHEL/CentOS/Fedora)
```bash
# Allow PerfWatch frontend
sudo firewall-cmd --permanent --add-port=3000/tcp

# Reload firewall
sudo firewall-cmd --reload

# Check status
sudo firewall-cmd --list-all
```

---

## Step 9: Set Up Reverse Proxy with HTTPS (Production Recommended)

### Install Nginx
```bash
# Ubuntu/Debian
sudo apt-get install -y nginx

# RHEL/CentOS/Fedora
sudo dnf install -y nginx
```

### Configure Nginx for PerfWatch
```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/perfwatch
```

**Nginx configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Change to your domain

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;  # Change to your domain

    # SSL certificates (use Let's Encrypt - see below)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /api/ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Enable Nginx Site
```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/perfwatch /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### Install SSL Certificate with Let's Encrypt
```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx  # Ubuntu/Debian
# OR
sudo dnf install -y certbot python3-certbot-nginx      # RHEL/CentOS/Fedora

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Certbot will automatically configure Nginx for HTTPS
```

### Update Firewall for HTTPS
```bash
# UFW
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw delete allow 3000/tcp  # Remove direct access

# firewalld
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --remove-port=3000/tcp
sudo firewall-cmd --reload
```

---

## Step 10: Configure Automatic Startup

Docker Compose services with `restart: unless-stopped` will automatically start on system boot if Docker is enabled.

### Enable Docker on Boot
```bash
sudo systemctl enable docker
```

### Verify Auto-Start
```bash
# Reboot system
sudo reboot

# After reboot, check services
sudo docker compose ps

# All services should be running
```

---

## Maintenance Commands

### View Logs
```bash
# All services
sudo docker compose logs -f

# Specific service
sudo docker compose logs -f backend
sudo docker compose logs -f frontend
sudo docker compose logs -f db
```

### Restart Services
```bash
# Restart all
sudo docker compose restart

# Restart specific service
sudo docker compose restart backend
```

### Update Application
```bash
# Pull latest code
cd /path/to/perfwatch
git pull

# Rebuild and restart
sudo docker compose build
sudo docker compose up -d

# Run any new migrations
sudo docker compose exec backend alembic upgrade head
```

### Backup Database
```bash
# Create backup
sudo docker compose exec db pg_dump -U perfwatch_prod perfwatch > perfwatch_backup_$(date +%Y%m%d).sql

# Restore backup
sudo docker compose exec -T db psql -U perfwatch_prod perfwatch < perfwatch_backup_20240101.sql
```

### Stop Services
```bash
# Stop all services
sudo docker compose down

# Stop and remove volumes (WARNING: deletes all data)
sudo docker compose down -v
```

---

## Troubleshooting

### Services Won't Start
```bash
# Check logs for errors
sudo docker compose logs

# Check disk space
df -h

# Check Docker status
sudo systemctl status docker
```

### Database Connection Errors
```bash
# Verify database is healthy
sudo docker compose ps

# Check database logs
sudo docker compose logs db

# Manually test connection
sudo docker compose exec db psql -U perfwatch_prod -d perfwatch -c "SELECT 1;"
```

### perf stat Not Working
```bash
# Check if privileged mode is enabled in docker-compose.yml
grep "privileged" docker-compose.yml

# Check perf binary
docker compose exec backend which perf

# Check kernel support
cat /proc/sys/kernel/perf_event_paranoid
# Should be 1 or less. If higher, run:
sudo sysctl -w kernel.perf_event_paranoid=1

# Make permanent
echo "kernel.perf_event_paranoid=1" | sudo tee -a /etc/sysctl.conf

# Validate perf counters (non-zero values required)
perf stat -e cycles,instructions -a sleep 1
# If counters are <not supported>, your VM/hypervisor is not exposing PMU.
```

### Frontend Can't Connect to Backend
```bash
# Check backend is running
curl http://localhost:8000/health

# Check frontend environment
sudo docker compose exec frontend cat /usr/share/nginx/html/config.js

# Verify CORS settings in backend
sudo docker compose logs backend | grep CORS
```

---

## Security Checklist

- [ ] Changed default database password
- [ ] Changed default admin password
- [ ] Generated strong JWT secret
- [ ] Database only accessible from localhost
- [ ] Backend API only accessible from localhost (if using reverse proxy)
- [ ] Firewall configured to allow only necessary ports
- [ ] HTTPS enabled with valid SSL certificate
- [ ] Regular backups scheduled
- [ ] Docker and system packages kept up to date
- [ ] Monitoring and log review process established

---

## Production Recommendations

1. **Use a reverse proxy** (Nginx/Apache) with HTTPS
2. **Set up automated backups** (daily database dumps)
3. **Monitor disk usage** (PostgreSQL data grows over time)
4. **Configure log rotation** for Docker logs
5. **Set up monitoring alerts** (disk space, service health)
6. **Review retention policy** (default 30 days, adjust in Settings)
7. **Keep system updated** (security patches)
8. **Document your configuration** (passwords, domains, etc.)

---

## Quick Reference

| Component | Default Port | Production Port |
|-----------|--------------|-----------------|
| Frontend | 3000 | 443 (via Nginx) |
| Backend API | 8000 | 443 (via Nginx) |
| PostgreSQL | 5432 | 127.0.0.1:5432 |

| Command | Purpose |
|---------|---------|
| `docker compose up -d` | Start services |
| `docker compose down` | Stop services |
| `docker compose logs -f` | View logs |
| `docker compose ps` | Check status |
| `docker compose exec backend alembic upgrade head` | Run migrations |
| `docker compose restart backend` | Restart backend |

---

## Support

- **Documentation**: `/docs/sdd/` directory
- **GitHub Issues**: https://github.com/zhyndalf/perfwatch/issues
- **API Documentation**: http://localhost:8000/docs (when running)

---

**Deployment complete!** Access PerfWatch at `http://your-server:3000` (or your configured domain).
