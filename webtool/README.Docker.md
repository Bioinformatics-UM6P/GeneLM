## GeneLM Web Tool – Docker Deployment Guide

This guide explains how to install and run the GeneLM web interface using Docker with GPU acceleration (NVIDIA).

### Requirements

- Docker and Docker Compose installed
- NVIDIA GPU + NVIDIA drivers
- [nvidia-docker2](https://github.com/NVIDIA/nvidia-docker) installed (see below)

### Step 1: Install NVIDIA Container Toolkit
Run the following script **on your host machine**:

```bash
chmod +x NVIDIA_Toolkit.sh
./NVIDIA_Toolkit.sh
```

This script:
- Adds the NVIDIA Docker repository
- Installs `nvidia-docker2`
- Restarts the Docker daemon

### Step 2: Build and Run with Docker Compose

```bash
docker-compose up --build -d
```

### Access the App

- **Webtool UI**: http://localhost:8501  
- **Webtool API**: http://localhost:8000/docs

### Directory Overview

```
├── Dockerfile
├── docker-compose.yml
├── NVIDIA_Toolkit.sh
├── requirements.txt
├── postinstall.sh
├── ui/
│   └── app.py
├── api/
│   └── app.py
├── .dockerignore
└── README.Docker.md
```

### Stopping the App

```bash
docker compose down
```
