# 🚀 MCPxA2AxAgentic-RAG: Complete Production Deployment Guide

This document provides a step-by-step guide to deploying the **MCP x A2A x Agentic-RAG System** on **Render** using **Docker and GitHub**.

---

## 📌 1. Architecture & Render Fit

### Multi-Process Orchestration in One Container
When running, this application operates 3 interconnected components:
1. **Host Agent Server (`agents.host_agent.main`)**: A2A Starlette service on internal port `10001`.
2. **Agentic RAG Agent Server (`agents.agentic_rag_agent.main`)**: A2A Starlette service on internal port `10002`.
3. **MCP Stdio Subprocesses**: Spawned by Python on-demand (`web_search_server.py` and `terminal_server.py`).
4. **Streamlit UI (`app/streamlit_ui.py`)**: Web interface bound to `0.0.0.0:$PORT` (where Render sets `$PORT`, typically `10000`).

### Why It Fits Comfortably on Render's 512 MB Free Tier:
- On this branch (`chore/update-embedding-provider`), embeddings were migrated to **Google Cloud Generative AI (`gemini-embedding-001`)** via API rather than loading heavy local PyTorch / HuggingFace models into memory.
- Total memory usage is approximately **~250 MB – 300 MB**, safely within Render's 512 MB ceiling.

---

## 🛠️ 2. Core Deployment Files

- [**`start.sh`**](file:///c:/Users/shres/Desktop/proj/A2A/mcp_a2a_agentic_rag/start.sh): Starts `main.py` in the background, polls `http://127.0.0.1:10001/health` and `10002/health` until both agents are responding, then launches Streamlit on `0.0.0.0:$PORT`.
- [**`Dockerfile`**](file:///c:/Users/shres/Desktop/proj/A2A/mcp_a2a_agentic_rag/Dockerfile): Slim Python 3.11 container with `curl` and `net-tools` (for `netstat`), and automatic CRLF line-ending sanitization for `start.sh`.
- [**`.dockerignore`**](file:///c:/Users/shres/Desktop/proj/A2A/mcp_a2a_agentic_rag/.dockerignore): Protects `.env`, `venv/`, and git history from entering the public image.

---

## 🌿 3. Step 0: Commit Files to Your Branch

Run the following commands in PowerShell or terminal:

```bash
git add Dockerfile start.sh .dockerignore requirements.txt DEPLOYMENT_GUIDE.md
git commit -m "feat(deploy): configure Docker and start supervisor for Render"
git push origin chore/update-embedding-provider
```

---

## 🚀 4. Step-by-Step Render Deployment

1. Go to [dashboard.render.com](https://dashboard.render.com/) and sign in with GitHub.
2. Click **New +** ➔ **Web Service**.
3. Select **Build and deploy from a Git repository**, then choose `mcp_a2a_agentic_rag`.
4. Configure the settings:
   - **Name**: `mcp-a2a-agentic-rag` (will produce `https://mcp-a2a-agentic-rag.onrender.com`)
   - **Region**: Choose the closest region (e.g. *Singapore*, *Frankfurt*, or *Oregon*)
   - **Branch**: **`chore/update-embedding-provider`**
   - **Runtime**: **Docker** (Render will automatically detect your `Dockerfile`)
   - **Instance Type**: **Free**
5. Under **Environment Variables**, add:
   - `GOOGLE_API_KEY`: Your Gemini API key (`AIzaSy...`)
   - `SERPAPI_KEY`: Your SerpAPI search key
6. Under **Advanced**, optionally set **Health Check Path** to:
   - `/_stcore/health`
7. Click **Create Web Service**.

---

## ⚡ 5. Keeping Your Free Render App Awake (Zero Cold Starts)

Render free tier instances sleep after 15 minutes of inactivity. To keep your app responsive for recruiters:
1. Go to [cron-job.org](https://cron-job.org/en/) (100% free).
2. Set a recurring GET ping to `https://<YOUR-RENDER-APP>.onrender.com/_stcore/health` every **14 minutes**.
3. Your app will remain warm and respond instantly!
