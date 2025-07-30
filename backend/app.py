from flask import Flask, jsonify, send_from_directory, render_template_string
import os
import json
from datetime import datetime
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        
        status = {
            'status': 'running',
            'timestamp': datetime.now().isoformat(),
            'alert_count': alert_count,
            'version': '1.0.0'
        }
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 