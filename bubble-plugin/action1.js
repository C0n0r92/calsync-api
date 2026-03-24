/**
 * CalSync - Generate Add-to-Calendar Links
 * Bubble.io Plugin Action
 *
 * Inputs:
 *   - event_title (text, required)
 *   - start_datetime (date, required)
 *   - end_datetime (date, required)
 *   - description (text, optional)
 *   - location (text, optional)
 *
 * Outputs:
 *   - google_url (text)
 *   - apple_url (text)
 *   - outlook_url (text)
 *   - yahoo_url (text)
 */
function(properties, context) {
  var payload = {
    title: properties.event_title,
    start: properties.start_datetime,
    end: properties.end_datetime,
    description: properties.description || "",
    location: properties.location || ""
  };

  return fetch("https://calsync.playerdatainsights.com/api/calendar/add-link", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  })
  .then(function(r) { return r.json(); })
  .then(function(data) {
    return {
      google_url: data.google,
      apple_url: data.apple,
      outlook_url: data.outlook,
      yahoo_url: data.yahoo
    };
  });
}
