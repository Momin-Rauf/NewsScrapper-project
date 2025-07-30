from flask import Flask, jsonify, send_from_directory, render_template_string
import os
import json
import threading
import time
from datetime import datetime
import logging

# Add the backend directory to Python path
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import NewsScraper
from utils.logger import setup_logger

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = setup_logger(__name__)

# Global scraper instance
scraper = None
scraper_thread = None
scraper_running = False

def start_background_scraper():
    """Start the background scraper in a separate thread"""
    global scraper, scraper_running
    
    try:
        logger.info("Initializing background scraper...")
        scraper = NewsScraper(use_advanced_filter=False)
        scraper_running = True
        
        # Run scraper with free tier optimizations
        polling_interval = 300  # 5 minutes
        max_cycles_per_hour = 10
        cycle_count = 0
        
        logger.info(f"Background scraper started with {polling_interval}s intervals")
        
        while scraper_running:
            try:
                cycle_count += 1
                logger.info(f"Background cycle {cycle_count} at {datetime.now()}")
                
                # Run a single cycle
                success = scraper.run_single_cycle()
                
                if success:
                    logger.info(f"Background cycle {cycle_count} completed successfully")
                else:
                    logger.warning(f"Background cycle {cycle_count} failed")
                
                # Check hourly limit
                if cycle_count >= max_cycles_per_hour:
                    logger.info(f"Reached hourly limit, waiting for next hour...")
                    time.sleep(3600)  # Wait 1 hour
                    cycle_count = 0
                else:
                    time.sleep(polling_interval)
                    
            except Exception as e:
                logger.error(f"Error in background cycle: {e}")
                time.sleep(polling_interval)
                
    except Exception as e:
        logger.error(f"Failed to start background scraper: {e}")

def start_scraper_thread():
    """Start the scraper in a background thread"""
    global scraper_thread
    if scraper_thread is None or not scraper_thread.is_alive():
        scraper_thread = threading.Thread(target=start_background_scraper, daemon=True)
        scraper_thread.start()
        logger.info("Scraper thread started")

# Start the background scraper when the app starts
@app.before_first_request
def initialize_scraper():
    """Initialize the background scraper on first request"""
    start_scraper_thread()

# Serve static files from the root directory
@app.route('/')
def index():
    """Serve the main HTML file"""
    try:
        with open('../index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content
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
        alerts_file = 'alerts.json'
        if os.path.exists(alerts_file):
            with open(alerts_file, 'r', encoding='utf-8') as f:
                alerts = json.load(f)
            return jsonify(alerts)
        else:
            return jsonify([])
    except Exception as e:
        logger.error(f"Error reading alerts: {e}")
        return jsonify([])

@app.route('/api/status')
def get_status():
    """API endpoint to get system status"""
    try:
        alerts_file = 'alerts.json'
        if os.path.exists(alerts_file):
            with open(alerts_file, 'r', encoding='utf-8') as f:
                alerts = json.load(f)
            alert_count = len(alerts)
        else:
            alert_count = 0
        
        # Get scraper status
        scraper_status = "running" if scraper_running else "stopped"
        thread_status = "alive" if scraper_thread and scraper_thread.is_alive() else "dead"
        
        status = {
            'status': 'running',
            'timestamp': datetime.now().isoformat(),
            'alert_count': alert_count,
            'scraper_status': scraper_status,
            'thread_status': thread_status,
            'version': '1.0.0'
        }
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'scraper_running': scraper_running
    })

@app.route('/api/restart-scraper')
def restart_scraper():
    """Manually restart the scraper"""
    global scraper_running, scraper_thread
    
    try:
        # Stop current scraper
        scraper_running = False
        if scraper_thread and scraper_thread.is_alive():
            scraper_thread.join(timeout=5)
        
        # Start new scraper
        start_scraper_thread()
        
        return jsonify({
            'status': 'success',
            'message': 'Scraper restarted successfully',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error restarting scraper: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    # Start scraper immediately for local development
    start_scraper_thread()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 