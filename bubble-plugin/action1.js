function(properties, context) {
  var payload = {
    title: properties.event_title,
    start: properties.start_datetime,
    end: properties.end_datetime,
    description: properties.description || "",
    location: properties.location || ""
  };

  return fetch("https://player-predictions-api-kicvq.ondigitalocean.app/calsync/api/calendar/add-link", {
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
