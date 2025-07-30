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
│   ├── app.py              # Flask web server
│   ├── worker.py           # Background worker for scraping
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

2. **Run the web server:**
   ```bash
   cd backend
   python app.py
   ```

3. **Run the scraper worker (in a separate terminal):**
   ```bash
   cd backend
   python worker.py
   ```

4. **Access the application:**
   - Open http://localhost:5000 in your browser

## Deployment on Render (Free Tier)

This project is optimized for Render's free tier with the following setup:

### Two Services:

1. **Web Service** (`newsscrapper-web`): Serves the frontend and API endpoints
2. **Background Worker** (`newsscrapper-worker`): Runs the news scraper

### Deployment Steps:

1. **Fork/Clone this repository** to your GitHub account

2. **Connect to Render:**
   - Go to [render.com](https://render.com)
   - Sign up/Login with your GitHub account
   - Click "New +" and select "Blueprint"

3. **Deploy using Blueprint:**
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` file
   - Click "Apply" to deploy both services

4. **Access your application:**
   - The web service will be available at: `https://your-app-name.onrender.com`
   - The worker will run in the background automatically

### Free Tier Optimizations:

- **Reduced polling frequency**: 5 minutes instead of 30 seconds
- **Limited cycles per hour**: Maximum 10 cycles to stay within limits
- **Basic content filtering**: Uses simpler filtering to reduce resource usage
- **Single worker process**: Optimized for free tier constraints

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

## Troubleshooting

### Common Issues:

1. **Worker not running**: Check logs in Render dashboard
2. **No alerts showing**: Verify worker is running and check API endpoint
3. **Map not loading**: Ensure static files are being served correctly

### Logs:

- Web service logs: Available in Render dashboard
- Worker logs: Available in Render dashboard
- Local logs: Check console output

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## License

This project is open source and available under the MIT License. 