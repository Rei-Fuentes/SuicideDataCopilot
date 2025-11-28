#!/bin/bash

# Exit on error
set -e

echo "=== Setting up CUIDAR IA Local Environment ==="

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment (.venv)..."
    python3 -m venv .venv
else
    echo "Virtual environment (.venv) already exists."
fi

# Activate environment
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
if [ -f "app_streamlit/requirements.txt" ]; then
    echo "Installing requirements from app_streamlit/requirements.txt..."
    pip install -r app_streamlit/requirements.txt
else
    echo "Error: app_streamlit/requirements.txt not found!"
    exit 1
fi

# Download spacy model if needed (common for presidio)
# echo "Downloading spacy model..."
# python -m spacy download es_core_news_md

echo "=== Setup Complete! ==="
echo "To activate the environment, run: source .venv/bin/activate"
echo "To run the app, use: streamlit run app_streamlit/app.py"
