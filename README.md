# 🎫 Lakebase-Powered AI Support Operations Hub

An operational, multi-tier ticketing application built to run natively inside Databricks Apps, backed by a serverless Lakebase PostgreSQL database engine.

## 📁 Repository Structure

* **`backend/`**: Core API application layer.
  * `main.py`: FastAPI backend endpoint routing and Pydantic validation schemas.
  * `lakebase.py`: Centralized Databricks SDK secret managers and database connection pools.
* **`frontend/`**: Interactive user UI layer.
  * `app.py`: Streamlit dashboard handling live operation states, validation streams, and ticket threads.
* **`archive/`**: Preserved original bootcamp boilerplate files (`massive_client.py`, `setup_secrets.py`) for reference.
* **`app.yaml`**: Databricks platform deployment orchestration manifest.
* **`startup.sh`**: Startup execution hook designed to sequence backend and frontend microservices seamlessly.

## 🚀 Key Built-in Capabilities
* Dynamic multi-state filtering (Open / In Progress / Resolved).
* Strict Pydantic email and text-length input validation layers.
* Multi-step safe record deletion protection streams.
* Overhauled interactive chat-style UI threads.
