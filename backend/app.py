from flask import Flask, jsonify, send_from_directory
import os
import json
import threading
import time
import sys
from datetime import datetime
import logging

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import original scraping modules
from main import NewsScraper
from utils.logger import setup_logger

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = setup_logger(__name__)

# Global variables
alerts = []
last_update = None
scraper_running = False
scraper_instance = None

def run_original_scraper():
    """Run the original complex scraper system"""
    global alerts, last_update, scraper_running, scraper_instance
    
    scraper_running = True
    logger.info("Original scraper system started")
    
    try:
        # Initialize the original scraper with basic filter for free tier
        scraper_instance = NewsScraper(use_advanced_filter=False)
        logger.info("Original NewsScraper initialized successfully")
        
        # Run scraper with free tier optimizations
        polling_interval = 300  # 5 minutes instead of 30 seconds
        max_cycles_per_hour = 10
        cycle_count = 0
        
        logger.info(f"Original scraper running with {polling_interval}s intervals")
        
        while scraper_running:
            try:
                cycle_count += 1
                logger.info(f"Original scraper cycle {cycle_count} at {datetime.now()}")
                
                # Run a single cycle using the original scraper
                success = scraper_instance.run_single_cycle()
                
                if success:
                    logger.info(f"Original scraper cycle {cycle_count} completed successfully")
                    
                    # Load the generated alerts from the original system
                    try:
                        if os.path.exists('alerts.json'):
                            with open('alerts.json', 'r', encoding='utf-8') as f:
                                alerts = json.load(f)
                            last_update = datetime.now().isoformat()
                            logger.info(f"Loaded {len(alerts)} alerts from original system")
                    except Exception as e:
                        logger.error(f"Error loading alerts: {e}")
                else:
                    logger.warning(f"Original scraper cycle {cycle_count} failed")
                
                # Check hourly limit for free tier
                if cycle_count >= max_cycles_per_hour:
                    logger.info(f"Reached hourly limit ({max_cycles_per_hour} cycles), waiting for next hour...")
                    time.sleep(3600)  # Wait 1 hour
                    cycle_count = 0
                else:
                    time.sleep(polling_interval)
                    
            except Exception as e:
                logger.error(f"Error in original scraper cycle: {e}")
                time.sleep(polling_interval)
                
    except Exception as e:
        logger.error(f"Failed to start original scraper: {e}")

def start_background_scraper():
    """Start the original scraper in a background thread"""
    thread = threading.Thread(target=run_original_scraper, daemon=True)
    thread.start()
    logger.info("Original scraper thread started")

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
            with open('alerts.json', 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        else:
            return jsonify([])
    except Exception as e:
        logger.error(f"Error reading alerts: {e}")
        return jsonify([])

@app.route('/api/status')
def get_status():
    """API endpoint to get system status"""
    try:
        # Get scraper statistics if available
        scraper_stats = {}
        if scraper_instance:
            try:
                scraper_stats = scraper_instance.get_system_stats()
            except:
                scraper_stats = {'status': 'running'}
        
        status = {
            'status': 'running',
            'timestamp': datetime.now().isoformat(),
            'alert_count': len(alerts),
            'last_update': last_update,
            'scraper_running': scraper_running,
            'scraper_stats': scraper_stats,
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
    """Manually restart the original scraper"""
    global scraper_running, scraper_instance
    
    try:
        # Stop current scraper
        scraper_running = False
        if scraper_instance:
            scraper_instance.running = False
        
        # Wait a moment for cleanup
        time.sleep(2)
        
        # Start new scraper
        start_background_scraper()
        
        return jsonify({
            'status': 'success',
            'message': 'Original scraper restarted successfully',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error restarting scraper: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 