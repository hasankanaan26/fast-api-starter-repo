# Deployment Guide

This guide covers how to deploy the Task Assistant API to production.

---

## Choosing a Platform

Not every hosting platform works for every type of project. Here's a quick breakdown:

### Platforms that work for this project

| Platform | How It Works | Best For |
|----------|-------------|----------|
| **Any VPS/cloud server** (AWS EC2, DigitalOcean, Linode, etc.) | You get a full Linux server. Install Docker, run your container. Full control. | Production APIs that need to run 24/7 |
| **Railway** | Connect your GitHub repo, it auto-detects the Dockerfile and deploys. Very beginner-friendly. | Quick deploys without managing servers |
| **Render** | Similar to Railway — connect your repo, picks up the Dockerfile, deploys automatically. Has a free tier. | Small projects, free hosting for demos |
| **Fly.io** | Deploys Docker containers to servers close to your users. Great CLI tool. | APIs that need low latency globally |

### Platforms that do NOT work for this project

| Platform | Why Not |
|----------|---------|
| **Vercel** | Designed for frontend apps and serverless functions (Next.js, React, etc.). FastAPI is a long-running server — it needs to stay alive between requests to keep tasks in memory. Vercel's serverless functions spin up and down per-request, so your in-memory task list would be lost after every call. |
| **Netlify** | Same issue as Vercel — built for static sites and serverless functions. It can't run a persistent Python server process. |
| **GitHub Pages** | Only serves static files (HTML, CSS, JS). It can't run any backend code at all — no Python, no servers, no APIs. Great for documentation sites, not for APIs. |

> **In short:** This project is a **backend API server** that needs to stay running continuously. Platforms designed for static sites or serverless functions won't work. You need a platform that can run a Docker container or a long-lived Python process.

---

## Deploy with Docker (Any Server)

These steps work on any Linux server — AWS EC2, DigitalOcean Droplets, Linode, Hetzner, etc.

### Step 1: Set up Docker on your server

```bash
# SSH into your server
ssh -i "your-key.pem" your-user@your-server-ip

# Install Docker (Ubuntu/Debian)
sudo apt update && sudo apt install -y docker.io

# Or on Amazon Linux / RHEL:
# sudo yum update -y && sudo yum install -y docker

# Start Docker and enable it on boot
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to the docker group (so you don't need "sudo" every time)
# Log out and back in after this for it to take effect
sudo usermod -aG docker $USER
```

### Step 2: Get your image onto the server

**Option A: Pull from a container registry (recommended)**

```bash
# If you've pushed your image to Docker Hub:
docker pull your-dockerhub-username/task-assistant:latest
```

**Option B: Build directly on the server**

```bash
# Clone your repo and build there.
# You do NOT need to install uv on the server — Docker handles everything.
# The Dockerfile copies uv from its official image automatically.
git clone https://github.com/YOUR_USERNAME/TaskAssistant.git
cd TaskAssistant
docker build -t task-assistant .
```

### Step 3: Run the container

```bash
# Run the container in the background, mapping port 8000
# --restart unless-stopped = if the container crashes or the server reboots,
#   Docker will automatically restart it (unless you manually stopped it)
docker run -d -p 8000:8000 --restart unless-stopped --name task-assistant-app task-assistant
```

### Step 4: Open the port

Make sure your server's firewall / security group allows inbound traffic on **port 8000**.

- **AWS EC2**: Go to Security Groups → Add Inbound Rule → Custom TCP, Port 8000, Source 0.0.0.0/0
- **DigitalOcean**: Go to Networking → Firewalls → Add an inbound rule for port 8000
- **UFW (Ubuntu)**: `sudo ufw allow 8000`

Your API is now live at `http://your-server-ip:8000`.

---

## Deploy to Railway (Easiest Option)

[Railway](https://railway.app/) auto-detects Dockerfiles and deploys with zero configuration.

1. Push your code to GitHub
2. Go to [railway.app](https://railway.app/) and sign in with GitHub
3. Click **"New Project"** → **"Deploy from GitHub Repo"**
4. Select your TaskAssistant repository
5. Railway detects the Dockerfile and deploys automatically
6. It gives you a public URL — your API is live!

---

## Deploy to Render

[Render](https://render.com/) has a generous free tier and also auto-detects Dockerfiles.

1. Push your code to GitHub
2. Go to [render.com](https://render.com/) and sign in with GitHub
3. Click **"New"** → **"Web Service"**
4. Connect your TaskAssistant repository
5. Render detects the Dockerfile — confirm the settings:
   - **Environment:** Docker
   - **Port:** 8000
6. Click **"Create Web Service"** — your API is live!

> **Free tier note:** Render's free tier spins down after 15 minutes of inactivity. The first request after a spin-down takes ~30 seconds. Upgrade to a paid plan to keep it always-on.
