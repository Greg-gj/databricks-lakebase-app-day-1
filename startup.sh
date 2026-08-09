#!/bin/bash
# Start FastAPI backend on port 8001 pointing to the backend subfolder
uvicorn backend.main:app --host 0.0.0.0 --port 8001 &

# Wait a moment for backend to start
sleep 3

# Start Streamlit frontend on DATABRICKS_APP_PORT pointing to the frontend subfolder
streamlit run frontend/app.py --server.port "${DATABRICKS_APP_PORT:-8000}" --server.address 0.0.0.0