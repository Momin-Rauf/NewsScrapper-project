// London Security Alerts Map
class LondonAlertsMap {
    constructor() {
        this.map = null;
        this.markers = [];
        this.alerts = [];
        this.refreshInterval = 30000; // 30 seconds
        this.refreshTimer = null;
        this.countdownTimer = null;
        this.timeRemaining = 30; // seconds
        this.isLoading = false;
        
        this.init();
    }
    
    init() {
        this.initMap();
        this.loadAlerts();
        this.startAutoRefresh();
        this.startCountdownTimer();
        this.setupEventListeners();
    }
    
    initMap() {
        // Initialize the map centered on London
        this.map = L.map('map').setView([51.5074, -0.1278], 11);
        
        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18
        }).addTo(this.map);
        
        console.log('Map initialized');
    }
    
    async loadAlerts() {
        if (this.isLoading) {
            console.log('Already loading alerts, skipping...');
            return;
        }
        
        this.isLoading = true;
        this.showLoading(true);
        
        try {
            console.log('Fetching alerts from API...');
            const response = await fetch('/api/alerts');
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const alerts = await response.json();
            console.log(`Received ${alerts.length} alerts from server`);
            this.updateAlerts(alerts);
            this.resetTimer(); // Reset countdown after successful refresh
            
        } catch (error) {
            console.error('Error loading alerts:', error);
            this.showError('Failed to load alerts. Please try again.');
        } finally {
            this.isLoading = false;
            this.showLoading(false);
        }
    }
    
    updateAlerts(newAlerts) {
        // Update alerts array
        this.alerts = newAlerts || [];
        
        // Clear existing markers
        this.clearMarkers();
        
        // Add new markers
        this.addMarkers();
        
        // Update status
        this.updateStatus();
        
        console.log(`Updated ${this.alerts.length} alerts`);
        
        // Force map to refresh if needed
        if (this.map) {
            this.map.invalidateSize();
        }
        
        // Debug map state
        this.debugMapState();
    }
    
    clearMarkers() {
        if (this.markers && this.markers.length > 0) {
            this.markers.forEach(marker => {
                if (marker && this.map.hasLayer(marker)) {
                    this.map.removeLayer(marker);
                }
            });
        }
        this.markers = [];
        console.log('Cleared all markers');
    }
    
    addMarkers() {
        if (!this.map) {
            console.error('Map not initialized, cannot add markers');
            return;
        }
        
        let addedCount = 0;
        let coordinateCount = {}; // Track how many markers at each coordinate
        
        this.alerts.forEach(alert => {
            if (alert.lat && alert.lon) {
                try {
                    // Create a unique key for this coordinate
                    const coordKey = `${alert.lat},${alert.lon}`;
                    coordinateCount[coordKey] = (coordinateCount[coordKey] || 0) + 1;
                    
                    // Add small offset for overlapping markers
                    const offset = coordinateCount[coordKey] - 1;
                    const lat = alert.lat + (offset * 0.0001); // Small offset
                    const lon = alert.lon + (offset * 0.0001);
                    
                    const marker = this.createMarker({
                        ...alert,
                        lat: lat,
                        lon: lon,
                        markerCount: coordinateCount[coordKey]
                    });
                    
                    this.markers.push(marker);
                    marker.addTo(this.map);
                    addedCount++;
                } catch (error) {
                    console.error('Error adding marker for alert:', alert.title, error);
                }
            } else {
                console.warn('Alert missing coordinates:', alert.title);
            }
        });
        console.log(`Added ${addedCount} markers to map`);
        console.log('Coordinate distribution:', coordinateCount);
    }
    
    createMarker(alert) {
        // Calculate marker size based on number of alerts at this location
        const baseSize = 30;
        const size = baseSize + (alert.markerCount || 1) * 5; // Larger if more alerts
        
        // Create custom marker icon
        const icon = L.divIcon({
            className: `custom-marker ${alert.type}`,
            html: alert.markerCount > 1 ? `<span class="marker-count">${alert.markerCount}</span>` : '',
            iconSize: [size, size],
            iconAnchor: [size/2, size/2]
        });
        
        // Create marker
        const marker = L.marker([alert.lat, alert.lon], { icon: icon });
        
        // Create popup content
        const popupContent = this.createPopupContent(alert);
        marker.bindPopup(popupContent);
        
        // Add click event for detailed view
        marker.on('click', () => {
            this.showAlertDetails(alert);
        });
        
        // Debug marker creation
        console.log(`Created marker for "${alert.title}" - Type: ${alert.type}, Location: ${alert.location}, Coords: ${alert.lat}, ${alert.lon}, Size: ${size}px`);
        
        return marker;
    }
    
    createPopupContent(alert) {
        const time = this.formatTime(alert.time);
        
        return `
            <div class="popup-content">
                <h3>${this.escapeHtml(alert.title)}</h3>
                <p><strong>Location:</strong> ${this.escapeHtml(alert.location)}</p>
                <p><strong>Time:</strong> ${time}</p>
                <p><strong>Type:</strong> ${this.capitalizeFirst(alert.type)}</p>
                ${alert.description ? `<p>${this.escapeHtml(alert.description)}</p>` : ''}
                ${alert.link ? `<a href="${alert.link}" target="_blank">Read More</a>` : ''}
            </div>
        `;
    }
    
    showAlertDetails(alert) {
        const panel = document.getElementById('alert-panel');
        const title = document.getElementById('alert-title');
        const description = document.getElementById('alert-description');
        const location = document.getElementById('alert-location');
        const time = document.getElementById('alert-time');
        const source = document.getElementById('alert-source');
        const link = document.getElementById('alert-link');
        
        title.textContent = alert.title;
        description.textContent = alert.description || 'No description available';
        location.textContent = alert.location;
        time.textContent = this.formatTime(alert.time);
        source.textContent = alert.source || 'Unknown';
        
        if (alert.link) {
            link.href = alert.link;
            link.style.display = 'inline-block';
        } else {
            link.style.display = 'none';
        }
        
        panel.classList.remove('hidden');
    }
    
    hideAlertDetails() {
        const panel = document.getElementById('alert-panel');
        panel.classList.add('hidden');
    }
    
    updateStatus() {
        const lastUpdated = document.getElementById('last-updated');
        const alertCount = document.getElementById('alert-count');
        
        const now = new Date();
        lastUpdated.textContent = `Last updated: ${now.toLocaleTimeString()}`;
        alertCount.textContent = `Alerts: ${this.alerts.length}`;
    }
    
    startAutoRefresh() {
        this.refreshTimer = setInterval(() => {
            this.loadAlerts();
        }, this.refreshInterval);
        
        console.log(`Auto-refresh started (${this.refreshInterval / 1000}s interval)`);
    }
    
    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
            console.log('Auto-refresh stopped');
        }
    }
    
    startCountdownTimer() {
        this.timeRemaining = this.refreshInterval / 1000; // Convert to seconds
        this.updateTimerDisplay();
        
        this.countdownTimer = setInterval(() => {
            this.timeRemaining--;
            this.updateTimerDisplay();
            
            if (this.timeRemaining <= 0) {
                this.timeRemaining = this.refreshInterval / 1000; // Reset
            }
        }, 1000);
        
        console.log('Countdown timer started');
    }
    
    stopCountdownTimer() {
        if (this.countdownTimer) {
            clearInterval(this.countdownTimer);
            this.countdownTimer = null;
            console.log('Countdown timer stopped');
        }
    }
    
    updateTimerDisplay() {
        const timerElement = document.getElementById('timer');
        if (timerElement) {
            const minutes = Math.floor(this.timeRemaining / 60);
            const seconds = this.timeRemaining % 60;
            const formattedTime = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            timerElement.textContent = `⏰ ${formattedTime}`;
        }
    }
    
    resetTimer() {
        this.timeRemaining = this.refreshInterval / 1000;
        this.updateTimerDisplay();
    }
    
    setupEventListeners() {
        // Close alert panel
        document.getElementById('close-alert').addEventListener('click', () => {
            this.hideAlertDetails();
        });
        
        // Manual refresh button
        document.getElementById('refresh-btn').addEventListener('click', () => {
            console.log('Manual refresh triggered');
            this.loadAlerts();
            this.resetTimer(); // Reset countdown when manually refreshed
        });
        
        // Close panel when clicking outside
        document.addEventListener('click', (e) => {
            const panel = document.getElementById('alert-panel');
            if (!panel.contains(e.target) && !panel.classList.contains('hidden')) {
                this.hideAlertDetails();
            }
        });
        
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.stopAutoRefresh();
                this.stopCountdownTimer();
            } else {
                this.startAutoRefresh();
                this.startCountdownTimer();
                this.loadAlerts(); // Refresh immediately when page becomes visible
            }
        });
        
        // Handle window focus/blur
        window.addEventListener('focus', () => {
            this.loadAlerts();
            this.resetTimer(); // Reset countdown when window regains focus
        });
    }
    
    showLoading(show) {
        const loading = document.getElementById('loading');
        if (show) {
            loading.classList.remove('hidden');
        } else {
            loading.classList.add('hidden');
        }
    }
    
    showError(message) {
        // Create a temporary error notification
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
            position: fixed;
            top: 80px;
            left: 50%;
            transform: translateX(-50%);
            background: #dc3545;
            color: white;
            padding: 10px 20px;
            border-radius: 4px;
            z-index: 2000;
            font-size: 0.9rem;
        `;
        errorDiv.textContent = message;
        
        document.body.appendChild(errorDiv);
        
        // Remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 5000);
    }
    
    // Debug function to check map state
    debugMapState() {
        console.log('=== Map Debug Info ===');
        console.log('Map object:', this.map ? 'exists' : 'null');
        console.log('Current alerts:', this.alerts.length);
        console.log('Current markers:', this.markers.length);
        console.log('Map bounds:', this.map ? this.map.getBounds() : 'N/A');
        console.log('Map center:', this.map ? this.map.getCenter() : 'N/A');
        console.log('Map zoom:', this.map ? this.map.getZoom() : 'N/A');
        console.log('=====================');
    }
    
    // Utility functions
    formatTime(timeString) {
        try {
            const date = new Date(timeString);
            return date.toLocaleString('en-GB', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (error) {
            return timeString || 'Unknown time';
        }
    }
    
    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the map when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new LondonAlertsMap();
});

// Handle page unload
window.addEventListener('beforeunload', () => {
    // Cleanup if needed
}); 