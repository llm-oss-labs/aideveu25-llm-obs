#!/bin/bash

# Start ollama service in the background
echo "Starting Ollama service..."
ollama serve &>/dev/null &

# Wait for the service to be ready
echo "Waiting for Ollama service to start..."
sleep 5

# Pull the phi3 model
echo "Pulling phi3:latest model..."
ollama pull phi3:latest

# Test the model with a simple prompt
echo "Testing model with a simple prompt..."
ollama run phi3:latest 'Hello' > /dev/null

echo "Ollama setup completed successfully!"