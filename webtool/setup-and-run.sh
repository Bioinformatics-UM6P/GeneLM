#!/bin/bash
# Script: setup_and_run.sh
# Purpose: Setup environment and start web UI + API server


# Create Python environment
if [ ! -d "venv" ]; then
  echo "Creating Python virtual environment..."
  python3 -m venv venv
fi

# Activate the environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
bash postinstall.sh

# Launch Streamlit UI in the background
echo "Starting Streamlit UI..."
nohup streamlit run ui/app.py --server.headless true > __files__/streamlit.log 2>&1 &

# Launch FastAPI server in the background
echo "Starting FastAPI server..."
nohup uvicorn --app-dir api api:app --host 127.0.0.1 --port 8000 --reload > __files__/api.log 2>&1 &

echo "✅ All services started! Access the web UI at http://localhost:8501 and API at http://localhost:8000"
