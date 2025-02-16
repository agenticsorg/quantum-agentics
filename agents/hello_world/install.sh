#!/bin/bash

# Install the package in development mode
pip install -e .

# Check if .env file exists, if not create it
if [ ! -f .env ]; then
    echo "Creating .env file..."
    echo "OPENROUTER_API_KEY=" > .env
    echo "Please add your OpenRouter API key to the .env file"
fi

echo "Installation complete!"
