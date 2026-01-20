# Past Papers Downloader

A web application for downloading CAIE (Cambridge Assessment International Education) past papers from PapaCambridge. Built with FastAPI, featuring a clean web UI for selecting qualifications, subjects, seasons, and bulk downloading papers as organized ZIP files.

## Features

- 🎓 **Multiple Qualifications**: Support for AICE (AS and A Level), IGCSE, and O Level
- 📚 **Subject Selection**: Browse and search through available subjects
- 📅 **Season Selection**: Select multiple years/seasons for bulk downloads
- 📦 **Bulk Downloads**: Download multiple seasons as organized ZIP files
- ⚡ **Fast Performance**: Caching system for faster page loads
- 📊 **Progress Tracking**: Real-time progress updates during downloads
- 🎨 **Clean UI**: Simple, user-friendly interface

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Web Scraping**: BeautifulSoup4, Requests
- **Async Downloads**: aiohttp
- **Templating**: Jinja2

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd PastPapersDownloader
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Local Development

1. **Start the server**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Access the application**
   - Open your browser and go to: `http://localhost:8000`
   - The app will be available at the root URL

3. **API Documentation**
   - Swagger UI: `http://localhost:8000/api/docs`
   - ReDoc: `http://localhost:8000/api/redoc`

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Usage

1. **Select Qualification**: Choose AICE, IGCSE, or O Level
2. **Select Subjects**: Browse and select one or more subjects
3. **Select Seasons**: Choose the years/seasons you want to download
4. **Download**: Click "Download Selected" to start the download
5. **Monitor Progress**: Watch real-time progress on the download page
6. **Download ZIP**: Once complete, download the organized ZIP file

## Project Structure

```
PastPapersDownloader/
├── app/
│   ├── api/              # API endpoints
│   │   └── v1/
│   │       └── endpoints/ # Qualification, Subject, Season, Download endpoints
│   ├── core/              # Core configuration and models
│   ├── models/            # Pydantic models
│   ├── services/          # Business logic (scraping, downloads, caching)
│   ├── static/            # Static files (CSS, JS, images)
│   ├── templates/         # HTML templates
│   └── main.py            # FastAPI application entry point
├── temp_downloads/        # Temporary download storage (local)
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Environment Variables

Optional environment variables (defaults are provided):

- `DEBUG`: Set to `true` for debug mode (default: `false`)
- `HOST`: Server host (default: `0.0.0.0`)
- `PORT`: Server port (default: `8000`)
- `MAX_CONCURRENT_DOWNLOADS`: Max concurrent downloads (default: `15`)
- `DOWNLOAD_TIMEOUT`: Download timeout in seconds (default: `30`)

## Caching

The application uses in-memory caching to improve performance:

- **Qualifications**: Cached for 1 hour
- **Subjects**: Cached for 1 hour
- **Seasons**: Cached for 1 hour
- **File Counts**: Cached for 24 hours

This means:
- First visit: Normal speed (scrapes data)
- Return visits: Instant (from cache)

## API Endpoints

- `GET /api/v1/qualifications` - List all qualifications
- `GET /api/v1/subjects?qualification={id}` - List subjects for a qualification
- `GET /api/v1/subjects/{code}/seasons?qualification={id}` - List seasons for a subject
- `POST /api/v1/downloads/bulk` - Start a bulk download
- `GET /api/v1/downloads/{job_id}/progress` - Get download progress
- `GET /api/v1/downloads/{job_id}/zip` - Download completed ZIP file

## Troubleshooting

### Common Issues

**Port already in use**
```bash
# Use a different port
uvicorn app.main:app --port 8001
```

**Import errors**
```bash
# Make sure you're in the project root directory
# And virtual environment is activated
```

**Download fails**
- Check internet connection
- Verify PapaCambridge website is accessible
- Check server logs for errors

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest

# Run tests
pytest
```

### Code Structure

- **Services**: Business logic and web scraping
- **API Endpoints**: REST API routes
- **Models**: Data validation with Pydantic
- **Templates**: Frontend HTML/CSS/JS

## License

This project is for educational purposes. Please respect PapaCambridge's terms of service when using this tool.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review server logs for backend errors
3. Check browser console for frontend errors

---

**Note**: This tool is not affiliated with Cambridge Assessment or PapaCambridge. Use responsibly and in accordance with their terms of service.
