# Elite Trading Web App

A web interface for searching Elite Dangerous commodity prices via EDSM API.

## Quick Start (Local)

```bash
pip install -r requirements.txt
python app.py
```

Then open: http://localhost:5000

## Deploy Options

### 1. Railway (Recommended - Free Tier)

1. Push to GitHub
2. Go to https://railway.app
3. "New Project" → "Deploy from GitHub"
4. Select your repo
5. Railway auto-detects Python and deploys

### 2. Render (Free Tier)

1. Push to GitHub
2. Go to https://render.com
3. "New" → "Web Service"
4. Connect GitHub repo
5. Use `render.yaml` or set:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`

### 3. Heroku (Free Tier Available)

1. Push to GitHub
2. Go to https://heroku.com
3. Create new app
4. Connect GitHub repo
5. Deploy branch

### 4. Docker

```bash
docker build -t elite-trading .
docker run -p 5000:5000 elite-trading
```

### 5. DigitalOcean App Platform

1. Push to GitHub
2. Create App on DigitalOcean
3. Select GitHub repo
4. Choose Python environment
5. Set start command: `gunicorn app:app --bind 0.0.0.0:$PORT`

## Features

- Search any commodity in any system
- Shows all stations selling the commodity
- Highlights stations with prices below average
- Quick commodity selection buttons
- Mobile responsive

## API Endpoints

- `GET /search?system=Sol&commodity=Gold` - Search commodity
- `GET /api/stations/<system>` - Get system stations
- `GET /api/market/<system>/<station>` - Get station market data

## Tech Stack

- Flask (Python web framework)
- EDSM API (Elite Dangerous Star Map)
- Gunicorn (production WSGI server)
