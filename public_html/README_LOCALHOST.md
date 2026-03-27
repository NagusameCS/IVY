# IVYSTUDY Development Server

## Quick Start

### Option 1: Run the start script
```bash
# On macOS/Linux:
chmod +x start_server.sh
./start_server.sh

# On Windows:
start_server.bat
```

### Option 2: Run directly
```bash
python3 dev_server.py
```

## What it does

The development server provides:

- **Static file serving** for all HTML, CSS, JS, and images
- **View counter API** at `/api/` (fully functional with rate limiting)
- **Directory routing** (e.g., `/timer/` automatically serves `/timer/index.html`)
- **Homepage routing** (`/` serves the home page at `/home/index.html`)

## URLs

Once running on `http://localhost:8080`:

- **Home page**: http://localhost:8080/
- **Main lessons**: http://localhost:8080/index.html
- **Exam Timer**: http://localhost:8080/timer/
- **Class Overview**: http://localhost:8080/overview/
- **IA/EE Exemplars**: http://localhost:8080/exemplars/
- **For Educators**: http://localhost:8080/teachers/
- **Stats**: http://localhost:8080/info/
- **View Counter API**: http://localhost:8080/api/

## Requirements

- Python 3.6+ (no additional packages needed - uses built-in modules only)
- All files should be in the `public_html` directory structure

## Features

- **WSGI integration**: The `/api/` endpoints use the same `application.py` code as production
- **CORS support**: API endpoints include proper CORS headers
- **Rate limiting**: View counter includes the same DDoS protection as production
- **Automatic routing**: Handles directory-style URLs cleanly
- **Error handling**: Graceful fallbacks for missing files or API errors

## Stopping

Press `Ctrl+C` in the terminal to stop the server.

## Troubleshooting

**Port already in use**: If port 8080 is busy, edit `dev_server.py` and change the `PORT = 8080` line.

**API not working**: Check that `api/application.py` exists and has no syntax errors.

**Files not found**: Ensure you're running from the `public_html` directory.