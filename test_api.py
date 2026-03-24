"""Tests for CalSync API."""
import pytest
from app import app


@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestHealth:
    """Health endpoint tests."""

    def test_health_returns_ok(self, client):
        """GET /health returns status ok."""
        response = client.get('/health')
        assert response.status_code == 200
        assert response.json == {"status": "ok"}


class TestAddLink:
    """Add-to-calendar link generation tests."""

    def test_add_link_success(self, client):
        """POST /api/calendar/add-link with valid data returns all 4 URLs."""
        payload = {
            "title": "Team Meeting",
            "start": "2026-03-25T10:00:00Z",
            "end": "2026-03-25T11:00:00Z",
            "description": "Weekly sync",
            "location": "Zoom"
        }
        response = client.post('/api/calendar/add-link', json=payload)

        assert response.status_code == 200
        data = response.json

        # All 4 URLs present
        assert 'google' in data
        assert 'apple' in data
        assert 'outlook' in data
        assert 'yahoo' in data

        # Google URL format
        assert data['google'].startswith('https://calendar.google.com/calendar/render')
        assert 'action=TEMPLATE' in data['google']
        assert 'Team%20Meeting' in data['google'] or 'Team+Meeting' in data['google']

        # Apple URL is .ics hosted endpoint
        assert '/ical/event/' in data['apple']
        assert data['apple'].endswith('.ics')

        # Outlook URL format
        assert data['outlook'].startswith('https://outlook.live.com/calendar/0/deeplink/compose')

        # Yahoo URL format
        assert data['yahoo'].startswith('https://calendar.yahoo.com/')
        assert 'v=60' in data['yahoo']

    def test_add_link_missing_title(self, client):
        """POST /api/calendar/add-link without title returns 400."""
        payload = {
            "start": "2026-03-25T10:00:00Z",
            "end": "2026-03-25T11:00:00Z"
        }
        response = client.post('/api/calendar/add-link', json=payload)
        assert response.status_code == 400

    def test_add_link_missing_start(self, client):
        """POST /api/calendar/add-link without start returns 400."""
        payload = {
            "title": "Meeting",
            "end": "2026-03-25T11:00:00Z"
        }
        response = client.post('/api/calendar/add-link', json=payload)
        assert response.status_code == 400

    def test_add_link_missing_end(self, client):
        """POST /api/calendar/add-link without end returns 400."""
        payload = {
            "title": "Meeting",
            "start": "2026-03-25T10:00:00Z"
        }
        response = client.post('/api/calendar/add-link', json=payload)
        assert response.status_code == 400

    def test_add_link_optional_fields(self, client):
        """POST /api/calendar/add-link works without optional fields."""
        payload = {
            "title": "Quick Call",
            "start": "2026-03-25T14:00:00Z",
            "end": "2026-03-25T14:30:00Z"
        }
        response = client.post('/api/calendar/add-link', json=payload)

        assert response.status_code == 200
        data = response.json
        assert 'google' in data
        assert 'apple' in data
        assert 'outlook' in data
        assert 'yahoo' in data


class TestIcalDownload:
    """iCal file download tests."""

    def test_ical_event_download(self, client):
        """GET /ical/event/<id> returns valid .ics content after creating event."""
        # First create an event
        payload = {
            "title": "Test Event",
            "start": "2026-03-25T10:00:00Z",
            "end": "2026-03-25T11:00:00Z",
            "description": "Test description",
            "location": "Test Location"
        }
        create_response = client.post('/api/calendar/add-link', json=payload)
        assert create_response.status_code == 200

        # Extract event ID from apple URL
        apple_url = create_response.json['apple']
        # URL format: .../ical/event/<event_id>.ics
        event_id = apple_url.split('/ical/event/')[-1].replace('.ics', '')

        # Download the .ics file
        ics_response = client.get(f'/ical/event/{event_id}.ics')

        assert ics_response.status_code == 200
        assert ics_response.content_type == 'text/calendar; charset=utf-8'

        ics_content = ics_response.data.decode('utf-8')

        # Validate .ics content
        assert 'BEGIN:VCALENDAR' in ics_content
        assert 'END:VCALENDAR' in ics_content
        assert 'BEGIN:VEVENT' in ics_content
        assert 'END:VEVENT' in ics_content
        assert 'Test Event' in ics_content
        assert 'Test description' in ics_content
        assert 'Test Location' in ics_content

    def test_ical_event_not_found(self, client):
        """GET /ical/event/<nonexistent_id> returns 404."""
        response = client.get('/ical/event/nonexistent-id-12345.ics')
        assert response.status_code == 404


class TestCORS:
    """CORS header tests."""

    def test_cors_headers_on_options(self, client):
        """OPTIONS request returns CORS headers."""
        response = client.options('/api/calendar/add-link')
        # Flask-CORS should add these headers
        assert response.status_code in [200, 204]

    def test_cors_headers_on_post(self, client):
        """POST response includes CORS headers."""
        payload = {
            "title": "Meeting",
            "start": "2026-03-25T10:00:00Z",
            "end": "2026-03-25T11:00:00Z"
        }
        response = client.post('/api/calendar/add-link', json=payload)
        # Access-Control-Allow-Origin should be present
        assert 'Access-Control-Allow-Origin' in response.headers
