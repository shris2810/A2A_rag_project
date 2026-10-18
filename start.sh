#!/usr/bin/env bash
set -e

# Render assigns a dynamic port via the $PORT environment variable (usually 10000).
# Fall back to 10000 for local Docker testing if $PORT is unset.
RENDER_PORT="${PORT:-10000}"

echo "=========================================================="
echo "🚀 Starting SmartQuery on Render"
echo "=========================================================="
echo "Target Web Port: $RENDER_PORT"

# Validate required API keys
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "WARNING: GOOGLE_API_KEY environment variable is missing!"
    echo "   Ensure GOOGLE_API_KEY is configured in your Render Environment settings."
fi

if [ -z "$SERPAPI_KEY" ]; then
    echo " WARNING: SERPAPI_KEY environment variable is missing!"
    echo "   Web search functionality will fail without SERPAPI_KEY."
fi

# 1. Start Host Agent (10001) and Agentic RAG Agent (10002) in the background
echo "📦 Starting Agent Backend Servers via main.py..."
python main.py &
BACKEND_PID=$!

# Trap signals for graceful container shutdown on Render
cleanup() {
    echo "Received shutdown signal. Terminating backend (PID: $BACKEND_PID)..."
    kill -TERM "$BACKEND_PID" 2>/dev/null || true
    wait "$BACKEND_PID" 2>/dev/null || true
    exit 0
}
trap cleanup SIGTERM SIGINT

# 2. Probe backend agents until healthy before starting Streamlit
echo "⏳ Waiting for Host Agent (10001) and RAG Agent (10002) to become healthy..."
MAX_ATTEMPTS=30
ATTEMPT=0
READY=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -s -f http://127.0.0.1:10001/health >/dev/null 2>&1 && \
       curl -s -f http://127.0.0.1:10002/health >/dev/null 2>&1; then
        echo "✅ Both Host Agent (10001) and RAG Agent (10002) are healthy!"
        READY=1
        break
    fi
    ATTEMPT=$((ATTEMPT + 1))
    echo "   ...waiting for backend agents ($ATTEMPT/$MAX_ATTEMPTS)"
    sleep 2
done

if [ $READY -eq 0 ]; then
    echo "⚠️  Warning: Backend health check timed out after 60s. Launching UI anyway..."
fi

# 3. Launch Streamlit UI on Render's exposed port
echo "🌟 Launching Streamlit UI on 0.0.0.0:$RENDER_PORT..."
exec streamlit run app/streamlit_ui.py \
    --server.port="$RENDER_PORT" \
    --server.address="0.0.0.0" \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    --browser.gatherUsageStats=false \
    --browser.serverAddress="0.0.0.0"
