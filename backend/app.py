from flask import Flask, jsonify, send_from_directory
import os
import json
import threading
import time
from datetime import datetime
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
alerts = []
last_update = None
scraper_running = False

def simple_scraper():
    """Simple scraper that works on free tier"""
    global alerts, last_update, scraper_running
    
    scraper_running = True
    logger.info("Simple scraper started")
    
    # Sample alerts for demonstration
    sample_alerts = [
        {
            "title": "Police incident in Central London",
            "description": "Traffic disruption due to police activity",
            "location": "Central London",
            "lat": 51.5074,
            "lon": -0.1278,
            "type": "crime",
            "time": datetime.now().isoformat(),
            "source": "Metropolitan Police"
        },
        {
            "title": "Security alert at London Bridge",
            "description": "Increased security presence reported",
            "location": "London Bridge",
            "lat": 51.5055,
            "lon": -0.0864,
            "type": "emergency",
            "time": datetime.now().isoformat(),
            "source": "BBC News"
        }
    ]
    
    while scraper_running:
        try:
            # Update alerts every 5 minutes (free tier friendly)
            alerts = sample_alerts.copy()
            last_update = datetime.now().isoformat()
            
            # Save to file
            with open('alerts.json', 'w') as f:
                json.dump(alerts, f, indent=2)
            
            logger.info(f"Updated {len(alerts)} alerts")
            
            # Wait 5 minutes
            time.sleep(300)
            
        except Exception as e:
            logger.error(f"Scraper error: {e}")
            time.sleep(300)

def start_background_scraper():
    """Start the background scraper thread"""
    thread = threading.Thread(target=simple_scraper, daemon=True)
    thread.start()
    logger.info("Background scraper thread started")

# Start scraper when app starts
start_background_scraper()

@app.route('/')
def index():
    """Serve the main HTML file"""
    try:
        with open('../index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Frontend files not found", 404

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (CSS, JS, etc.)"""
    try:
        return send_from_directory('..', filename)
    except FileNotFoundError:
        return "File not found", 404

@app.route('/api/alerts')
def get_alerts():
    """API endpoint to get alerts data"""
    try:
        if os.path.exists('alerts.json'):
            with open('alerts.json', 'r') as f:
                return jsonify(json.load(f))
        else:
            return jsonify([])
    except Exception as e:
        logger.error(f"Error reading alerts: {e}")
        return jsonify([])

@app.route('/api/status')
def get_status():
    """API endpoint to get system status"""
    status = {
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'alert_count': len(alerts),
        'last_update': last_update,
        'scraper_running': scraper_running,
        'version': '1.0.0'
    }
    return jsonify(status)

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 