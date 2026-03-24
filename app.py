"""CalSync API - Add to Calendar link generator for Bubble.io plugin."""
import uuid
from datetime import datetime, timezone
from urllib.parse import quote, urlencode

from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from icalendar import Calendar, Event, vText
from dateutil import parser as dateparser

app = Flask(__name__)
CORS(app)

# In-memory event storage (keyed by event_id)
events_store = {}

# Base URL for hosted .ics files (configurable for production)
BASE_URL = "https://calsync.playerdatainsights.com"


def parse_datetime(dt_string):
    """Parse ISO datetime string to datetime object."""
    return dateparser.parse(dt_string)


def format_google_date(dt):
    """Format datetime for Google Calendar URL (YYYYMMDDTHHMMSSZ)."""
    return dt.strftime('%Y%m%dT%H%M%SZ')


def format_yahoo_date(dt):
    """Format datetime for Yahoo Calendar URL (YYYYMMDDTHHMMSS)."""
    return dt.strftime('%Y%m%dT%H%M%S')


def generate_google_url(title, start, end, description, location):
    """Generate Google Calendar add event URL."""
    start_dt = parse_datetime(start)
    end_dt = parse_datetime(end)

    params = {
        'action': 'TEMPLATE',
        'text': title,
        'dates': f"{format_google_date(start_dt)}/{format_google_date(end_dt)}",
        'details': description,
        'location': location
    }

    return f"https://calendar.google.com/calendar/render?{urlencode(params)}"


def generate_outlook_url(title, start, end, description, location):
    """Generate Outlook Calendar add event URL."""
    params = {
        'subject': title,
        'startdt': start,
        'enddt': end,
        'body': description,
        'location': location,
        'path': '/calendar/action/compose',
        'rru': 'addevent'
    }

    return f"https://outlook.live.com/calendar/0/deeplink/compose?{urlencode(params)}"


def generate_yahoo_url(title, start, end, description, location):
    """Generate Yahoo Calendar add event URL."""
    start_dt = parse_datetime(start)
    end_dt = parse_datetime(end)

    params = {
        'v': '60',
        'title': title,
        'st': format_yahoo_date(start_dt),
        'et': format_yahoo_date(end_dt),
        'desc': description,
        'in_loc': location
    }

    return f"https://calendar.yahoo.com/?{urlencode(params)}"


def generate_ics_content(event_data):
    """Generate iCal (.ics) file content for an event."""
    cal = Calendar()
    cal.add('prodid', '-//CalSync//calsync.playerdatainsights.com//')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')

    event = Event()
    event.add('summary', event_data['title'])
    event.add('dtstart', parse_datetime(event_data['start']))
    event.add('dtend', parse_datetime(event_data['end']))

    if event_data.get('description'):
        event.add('description', event_data['description'])

    if event_data.get('location'):
        event['location'] = vText(event_data['location'])

    event.add('uid', f"{event_data['id']}@calsync.playerdatainsights.com")
    event.add('dtstamp', datetime.now(timezone.utc))

    cal.add_component(event)

    return cal.to_ical()


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


@app.route('/api/calendar/add-link', methods=['POST'])
def add_link():
    """Generate add-to-calendar links for all major calendar providers."""
    data = request.get_json()

    # Validate required fields
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    if not data.get('title'):
        return jsonify({"error": "Missing required field: title"}), 400

    if not data.get('start'):
        return jsonify({"error": "Missing required field: start"}), 400

    if not data.get('end'):
        return jsonify({"error": "Missing required field: end"}), 400

    title = data['title']
    start = data['start']
    end = data['end']
    description = data.get('description', '')
    location = data.get('location', '')

    # Generate unique event ID for .ics hosting
    event_id = str(uuid.uuid4())

    # Store event data for .ics download
    events_store[event_id] = {
        'id': event_id,
        'title': title,
        'start': start,
        'end': end,
        'description': description,
        'location': location
    }

    # Generate URLs for each calendar provider
    google_url = generate_google_url(title, start, end, description, location)
    outlook_url = generate_outlook_url(title, start, end, description, location)
    yahoo_url = generate_yahoo_url(title, start, end, description, location)

    # For Apple, we host the .ics file
    # Use request.host_url in production, fallback to BASE_URL
    host_url = request.host_url.rstrip('/')
    if 'localhost' in host_url or '127.0.0.1' in host_url:
        apple_url = f"{host_url}/ical/event/{event_id}.ics"
    else:
        apple_url = f"{BASE_URL}/ical/event/{event_id}.ics"

    return jsonify({
        "google": google_url,
        "apple": apple_url,
        "outlook": outlook_url,
        "yahoo": yahoo_url,
        "event_id": event_id
    })


@app.route('/ical/event/<event_id>.ics', methods=['GET'])
def download_ics(event_id):
    """Serve .ics file for Apple Calendar download."""
    if event_id not in events_store:
        return jsonify({"error": "Event not found"}), 404

    event_data = events_store[event_id]
    ics_content = generate_ics_content(event_data)

    return Response(
        ics_content,
        mimetype='text/calendar',
        headers={
            'Content-Type': 'text/calendar; charset=utf-8',
            'Content-Disposition': f'attachment; filename="{event_data["title"]}.ics"'
        }
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
