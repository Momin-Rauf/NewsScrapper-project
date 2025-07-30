Scope of Work

Frontend Map Interface (JavaScript/Leaflet.js)

Map with live markers (OpenStreetMap or Google Maps)

Auto-refresh every 30 seconds

Filters, legend, status bar

Logo overlay

Hosted on Netlify

Backend Feed Integration (Python)

Polls live data every 30 seconds from:

(BBC News RSS

Met Police News site

GOV.UK Atom feeds)

Filters for security-related terms (e.g. stabbing, protest, terror)

Matches locations to known coordinates (Oxford Circus, Soho, Westminster, etc.)

Outputs a valid alerts.json file for the frontend

Deploys the file using Netlify CLI (or alternative)

Automation

Self-running script loop on a Mac or VPS

Option to expand later to serverless/cloud deployment



1. Project Objective

Build and maintain a live, auto-updating intelligence map for Greater London that:
• Displays real-time alerts from trusted public sources
• Updates the frontend map every 30 seconds without simulations
• Can be deployed via Netlify (static hosting)

2. Frontend Requirements
• Built using HTML, CSS, and JavaScript (Leaflet.js)
• Load map using OpenStreetMap tiles (or Google Maps if licensed)
• Auto-refresh markers every 30 seconds
• Must include:
• Logo overlay (top-left)
• Legend for marker types (Police, News, Emergency)
• Status bar showing “Last updated” and number of alerts
• Reads alerts.json from the project root

3. Alert Feed Specification

Frontend reads alerts from:
[
{
"type": "crime",
"location": "Oxford Circus",
"time": "2025-07-15T14:33:00",
"lat": 51.5154,
"lon": -0.1411,
"title": "Stabbing near Oxford Circus",
"link": "https://news.met.police.uk/...";
}
]
• Alerts must be geolocated to appear on the map
• Colours:
• red = police/crime
• orange = news/media
• green = emergency/public safety


4. Backend Requirements (Python Script)

A Python script should:
• Run every 30 seconds on a local Mac or server
• Pull data from:
• BBC News RSS → https://feeds.bbci.co.uk/news/rss.xml
• Met Police → https://news.met.police.uk/news
• GOV.UK Alerts → https://www.gov.uk/foreign-travel-advice.atom
• Filter for serious incidents (e.g. “stabbing”, “explosion”, “protest”)
• Match against known London area names (Oxford Circus, Westminster, Camden, etc.)
• If no location match → skip the alert (no default coordinates)
• Output alerts.json in correct structure (see #3)

5. Automation & Deployment
• alerts.json is copied into the frontend folder


6. Deliverables
• fetch_live_alerts.py with commented code
• Full deployable Netlify folder (HTML, JS, CSS, alerts.json)
• A working map at [Netlify domain] showing only real incidents
• Option to log skipped alerts for review
