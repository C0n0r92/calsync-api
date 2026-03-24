# CalSync for Bubble — Full Product Spec
*Written: 2026-03-24*

---

## What It Is
A Bubble.io plugin that lets any Bubble app sync events to Google Calendar, Apple Calendar, and Outlook. Two core features:
1. **Add to Calendar** — generates "Add to Calendar" links/buttons for any event
2. **Google Calendar Sync** — creates/updates/deletes events in a user's Google Calendar from Bubble workflows

No AI, no expensive APIs. iCal is an open standard. Google Calendar API has a generous free tier.

---

## Target Customer
Bubble developers building:
- Booking/scheduling apps
- Event management platforms
- Course/class enrollment systems
- Appointment booking tools
- Any app where users need to remember an event

---

## Pricing
- **Free tier**: Add to Calendar links only (no Google sync), up to 100 events/month
- **Pro: $8/mo** or $80 one-time: Full Google Calendar sync, unlimited events
- Bubble takes 25% → developer keeps $6/mo or $60 one-time

---

## Features (v1)

### Feature 1: Add to Calendar Links (Free)
Generates direct "Add to Calendar" URLs for:
- Google Calendar
- Apple Calendar (.ics download)
- Outlook (live.com URL)
- Yahoo Calendar

**Input:** Event title, start datetime, end datetime, description (optional), location (optional)
**Output:** 4 URLs the Bubble developer can attach to buttons

### Feature 2: iCal Feed URL (Free)
Generates a static .ics file URL that users can subscribe to in any calendar app. Auto-updates when events change.

**Input:** List of events from Bubble database
**Output:** A subscribable .ics URL

### Feature 3: Google Calendar Sync (Pro)
Creates, updates, and deletes events in a user's Google Calendar via OAuth.

**Input:** Event data + user's Google OAuth token
**Output:** Google Calendar event ID (for future updates/deletes)

---

## Architecture

```
Bubble App
    │
    │ (Plugin JS action — ~20 lines)
    │
    ▼
CalSync API (Flask on DO)
    │
    ├── /api/ical/generate     → Returns .ics content
    ├── /api/calendar/add-link → Returns Add to Calendar URLs
    ├── /api/gcal/create       → Creates Google Calendar event
    ├── /api/gcal/update       → Updates Google Calendar event
    ├── /api/gcal/delete       → Deletes Google Calendar event
    └── /api/auth/google       → Google OAuth flow
```

**Stack:**
- Flask (Python) on existing DO droplet
- New subdomain: `api.calsync.io` or `calsync.playerdatainsights.com` (short term)
- Supabase: store API keys, usage counts, subscription status
- Google Calendar API (free tier: 1M requests/day)
- icalendar Python library (open source, no cost)
- Stripe for billing (via Bubble's marketplace checkout)

---

## Bubble Plugin Structure

### Actions (what Bubble developers use in workflows):

**Action 1: Generate Add-to-Calendar Links**
- Inputs: `event_title` (text), `start_datetime` (date), `end_datetime` (date), `description` (text, optional), `location` (text, optional)
- Outputs: `google_url` (text), `apple_url` (text), `outlook_url` (text), `yahoo_url` (text)
- Tier: Free

**Action 2: Create Google Calendar Event**
- Inputs: `event_title`, `start_datetime`, `end_datetime`, `description`, `location`, `google_access_token`
- Outputs: `event_id` (text), `success` (boolean), `error_message` (text)
- Tier: Pro

**Action 3: Delete Google Calendar Event**
- Inputs: `event_id`, `google_access_token`
- Outputs: `success` (boolean), `error_message` (text)
- Tier: Pro

**Action 4: Generate iCal Feed**
- Inputs: `api_key` (from plugin settings), list of event data
- Outputs: `ical_url` (subscribable URL)
- Tier: Free

### Plugin Settings (per Bubble app):
- `api_key`: CalSync API key (generated on signup at calsync.io dashboard)
- `plan`: auto-detected from API key

---

## API Endpoints (Flask)

### POST /api/calendar/add-link
```json
Request:
{
  "title": "Team Meeting",
  "start": "2026-03-25T10:00:00Z",
  "end": "2026-03-25T11:00:00Z",
  "description": "Weekly sync",
  "location": "Zoom"
}

Response:
{
  "google": "https://calendar.google.com/calendar/render?action=TEMPLATE&...",
  "apple": "https://api.calsync.io/ical/event/abc123.ics",
  "outlook": "https://outlook.live.com/calendar/0/deeplink/compose?...",
  "yahoo": "https://calendar.yahoo.com/?v=60&..."
}
```

### POST /api/gcal/create
```json
Request:
{
  "api_key": "csk_xxx",
  "access_token": "ya29.xxx",
  "title": "Team Meeting",
  "start": "2026-03-25T10:00:00Z",
  "end": "2026-03-25T11:00:00Z",
  "description": "Weekly sync",
  "location": "Zoom"
}

Response:
{
  "event_id": "abc123xyz",
  "success": true
}
```

### GET /ical/feed/:api_key
Returns a valid .ics file with all events for that API key. Subscribable URL.

---

## Bubble Plugin JavaScript (Action 1 — Add to Calendar)

```javascript
function(properties, context) {
  const payload = {
    title: properties.event_title,
    start: properties.start_datetime,
    end: properties.end_datetime,
    description: properties.description || '',
    location: properties.location || ''
  };

  return fetch('https://api.calsync.io/api/calendar/add-link', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  .then(r => r.json())
  .then(data => {
    return {
      google_url: data.google,
      apple_url: data.apple,
      outlook_url: data.outlook,
      yahoo_url: data.yahoo
    };
  });
}
```

---

## Build Plan

### Day 1 (tonight — sub-agent builds while Skipper sleeps):
- [ ] Set up new Flask service: `~/calsync-api/`
- [ ] Implement `/api/calendar/add-link` endpoint
- [ ] Implement iCal .ics generation
- [ ] Basic API key validation
- [ ] Deploy to DO on port 5001 (behind nginx)
- [ ] Set up subdomain (use `calsync.playerdatainsights.com` for now)

### Day 2:
- [ ] Google Calendar OAuth flow
- [ ] `/api/gcal/create`, `/api/gcal/update`, `/api/gcal/delete`
- [ ] Supabase table for API keys + usage tracking
- [ ] Test end to end with a real Bubble app

### Day 3:
- [ ] Bubble plugin JS for all 4 actions
- [ ] Plugin settings page
- [ ] Submit to Bubble marketplace
- [ ] Simple landing page / docs at calsync.playerdatainsights.com

---

## Minimum Viable Plugin (what we ship first)
Just Feature 1 — Add to Calendar links. No Google OAuth, no sync, no database.

A Bubble developer drops in the plugin, passes event data, gets 4 URLs back. That's it. Free to use. Gets installs and reviews. Pro tier (Google sync) added in v1.1.

**This MVP can be built and submitted in 2 days.**

---

## Domain
- Short term: `calsync.playerdatainsights.com`
- Long term: register `calsyncapp.io` or `getcalsync.io` (~$10/year)

---

## Success Metrics
- Week 1: Plugin live in Bubble marketplace
- Month 1: 50 installs
- Month 3: 500 installs, 15% paying = 75 paying × $8 = $600/mo
- Month 6: 2,000 installs, 15% paying = 300 × $8 = $2,400/mo
