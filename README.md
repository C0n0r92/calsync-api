# CalSync API

Flask backend for the CalSync Bubble.io plugin. Generates "Add to Calendar" links for Google, Apple, Outlook, and Yahoo calendars.

## Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
```

Server runs on `http://localhost:5001`.

## API Endpoints

### GET /health
Health check endpoint.

```json
{"status": "ok"}
```

### POST /api/calendar/add-link
Generate add-to-calendar links for all providers.

**Request:**
```json
{
  "title": "Team Meeting",
  "start": "2026-03-25T10:00:00Z",
  "end": "2026-03-25T11:00:00Z",
  "description": "Weekly sync",
  "location": "Zoom"
}
```

**Response:**
```json
{
  "google": "https://calendar.google.com/calendar/render?...",
  "apple": "https://calsync.playerdatainsights.com/ical/event/<id>.ics",
  "outlook": "https://outlook.live.com/calendar/0/deeplink/compose?...",
  "yahoo": "https://calendar.yahoo.com/?..."
}
```

### GET /ical/event/<event_id>.ics
Download .ics file for Apple Calendar.

## Testing

```bash
pytest test_api.py -v
```

## Deployment

Deploy to DigitalOcean with gunicorn:

```bash
gunicorn app:app --bind 0.0.0.0:5001
```

Or use the Procfile for process managers like systemd.

## Bubble Plugin

The `bubble-plugin/action1.js` file contains the JavaScript action code to paste into the Bubble plugin editor.
