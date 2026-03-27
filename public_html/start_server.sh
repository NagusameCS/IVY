#!/bin/bash
set -e
# Start IVYSTUDY development server

echo "Starting IVYSTUDY development server..."

# Check if we're in the right directory
if [ ! -f "dev_server.py" ]; then
    echo "Error: Please run this script from the public_html directory"
    echo "Expected to find dev_server.py in current directory"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found"
    echo "Please install Python 3 to run the development server"
    exit 1
fi

# Make sure the API directory exists and has proper structure
if [ ! -d "api" ]; then
    echo "Warning: api directory not found"
fi

# Start the server
echo "Starting server on http://localhost:8080"
echo "Press Ctrl+C to stop"
python3 dev_server.py