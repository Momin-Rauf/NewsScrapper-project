# London Security Alerts Map

A real-time security alerts mapping system for London that scrapes multiple news sources and displays alerts on an interactive map.

## Features

- **Real-time News Scraping**: Automatically fetches security-related news from multiple sources
- **Interactive Map**: Displays alerts on a map with location-based filtering
- **Multiple Sources**: BBC, Metropolitan Police, GOV.UK, Evening Standard
- **Smart Filtering**: Advanced content filtering to identify security-related news
- **Location Matching**: Automatically geocodes and maps alert locations
- **Auto-refresh**: Updates every 30 seconds with visual countdown timer

## Project Structure

```
NewsScrapper/
├── backend/                 # Python backend
│   ├── feeds/              # News feed scrapers
│   ├── processors/         # Content processing and filtering
│   ├── utils/              # Utility functions
│   ├── config/             # Configuration files
│   ├── app.py              # Flask web server with integrated scraper
│   └── main.py             # Main scraper orchestrator
├── index.html              # Frontend HTML
├── script.js               # Frontend JavaScript
├── styles.css              # Frontend CSS
└── render.yaml             # Render deployment configuration
```

## Local Development

### Prerequisites

- Python 3.9+
- pip

### Setup

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   cd backend
   python app.py
   ```

3. **Access the application:**
   - Open http://localhost:5000 in your browser

## Deployment on Render (Free Tier)

This project is optimized for Render's free tier with a **single-service architecture**:

### Single Web Service:

The application combines both the web server and background scraper into one service using threading, which works perfectly with Render's free tier limitations.

### Deployment Steps:

1. **Fork/Clone this repository** to your GitHub account

2. **Connect to Render:**
   - Go to [render.com](https://render.com)
   - Sign up/Login with your GitHub account
   - Click "New +" and select "Blueprint"

3. **Deploy using Blueprint:**
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` file
   - Click "Apply" to deploy the service

4. **Access your application:**
   - The service will be available at: `https://your-app-name.onrender.com`
   - The scraper runs automatically in the background

### Free Tier Optimizations:

- **Single service**: Combines web server and scraper to stay within limits
- **Reduced polling frequency**: 5 minutes instead of 30 seconds
- **Limited cycles per hour**: Maximum 10 cycles to stay within limits
- **Basic content filtering**: Uses simpler filtering to reduce resource usage
- **Threading**: Background scraper runs in a separate thread within the web process

### Environment Variables:

The following environment variables are automatically set:
- `PYTHON_VERSION`: 3.9.16
- `RENDER_ENVIRONMENT`: production
- `PORT`: Automatically set by Render

## API Endpoints

- `GET /` - Main application page
- `GET /api/alerts` - Get all alerts in JSON format
- `GET /api/status` - Get system status and statistics
- `GET /health` - Health check endpoint
- `POST /api/restart-scraper` - Manually restart the background scraper

## Configuration

### Polling Intervals

- **Local development**: 30 seconds
- **Render free tier**: 5 minutes (optimized for limits)

### Content Sources

The system scrapes from:
- BBC News
- Metropolitan Police
- GOV.UK
- Evening Standard

### Alert Types

- **Police/Crime**: Red markers
- **News/Media**: Blue markers  
- **Emergency/Public Safety**: Orange markers

## Monitoring

- **Health checks**: Automatic health monitoring via `/health` endpoint
- **Logs**: View logs in Render dashboard
- **Status**: Check system status via `/api/status` endpoint
- **Scraper status**: Monitor background scraper via status endpoint

## Troubleshooting

### Common Issues:

1. **No alerts showing**: Check `/api/status` to verify scraper is running
2. **Scraper not working**: Use `/api/restart-scraper` to restart the background process
3. **Map not loading**: Ensure static files are being served correctly

### Logs:

- All logs: Available in Render dashboard
- Local logs: Check console output

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## License

This project is open source and available under the MIT License. 