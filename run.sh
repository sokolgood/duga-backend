#!/bin/bash

# Start the FastAPI application with Uvicorn
echo "Starting FastAPI application..."
poetry run uvicorn src.main:app --host 127.0.0.1 --port 8080