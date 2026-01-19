# 📚 PastPapersDownloader - Web Application

A modern FastAPI web application for downloading CAIE past papers from PapaCambridge. Browse qualifications, select subjects and seasons, and download bulk past papers with real-time progress tracking.

---

## ✨ Features

- **Web UI**: Beautiful, intuitive interface for browsing and selecting past papers
- **Multiple Qualifications**: Support for A-Level, IGCSE, and O-Level
- **Bulk Downloads**: Download multiple subjects and seasons at once
- **Progress Tracking**: Real-time progress updates during downloads
- **Organized ZIP Files**: Downloads come in organized folder structures
- **User-Friendly**: Select download location via browser save dialog

---

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd PastPapersDownloader
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the server:**
   ```bash
   python3 -m uvicorn app.main:app --reload
   ```

4. **Open in browser:**
   ```
   http://localhost:8000
   ```

---

## 📖 Usage

### Web Interface

1. **Select Qualification**: Choose A-Level, IGCSE, or O-Level
2. **Select Subjects**: Choose one or more subjects (multi-select)
3. **Select Seasons**: Choose one or more years/seasons to download
4. **Download**: Click "Download Selected" to start bulk download
5. **Monitor Progress**: Watch real-time progress on the download page
6. **Get ZIP**: Download the organized ZIP file when complete

### API Endpoints

The application provides a REST API for programmatic access:

- **GET** `/api/v1/qualifications/` - List all qualifications
- **GET** `/api/v1/subjects/?qualification=AICE` - List subjects
- **GET** `/api/v1/subjects/{code}/seasons?qualification=AICE` - List seasons
- **POST** `/api/v1/downloads/bulk` - Start bulk download
- **GET** `/api/v1/downloads/{job_id}/progress` - Get download progress
- **GET** `/api/v1/downloads/{job_id}/zip` - Download ZIP file

**API Documentation**: Visit `http://localhost:8000/api/docs` for interactive API documentation.

---

## 🏗️ Architecture

### Technology Stack

- **Backend**: FastAPI (Python)
- **Web Scraping**: BeautifulSoup4, requests
- **Async Downloads**: aiohttp
- **Frontend**: HTML, CSS, JavaScript (vanilla)
- **Server**: Uvicorn (ASGI)

### Project Structure

```
app/
├── main.py              # FastAPI application entry point
├── api/                 # API routes
│   └── v1/
│       └── endpoints/   # API endpoint modules
├── core/                # Core modules (config, links, models)
├── models/              # Pydantic data models
├── services/            # Business logic services
├── static/              # Static files (CSS, JS)
└── templates/           # HTML templates
```

---

## ⚙️ Configuration

Create a `.env` file (see `.env.example`) to configure:

- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)
- `MAX_CONCURRENT_DOWNLOADS` - Concurrent download limit (default: 15)
- `DOWNLOAD_TIMEOUT` - Download timeout in seconds (default: 30)
- `CLEANUP_TTL_HOURS` - Temp file cleanup time (default: 1)

---

## 📝 Development

### Running in Development

```bash
# With auto-reload
python3 -m uvicorn app.main:app --reload

# Production mode
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Testing

See `docs/TESTING.md` for testing guide.

---

## 📄 License

See `LICENSE` file for details.

---

## 🤝 Contributing

This is a migrated FastAPI application. For development notes and architecture details, see the `docs/` directory.

---

## 📚 Documentation

- **API Documentation**: http://localhost:8000/api/docs (when server is running)
- **Testing Guide**: `docs/TESTING.md`
- **Architecture**: `docs/ARCHITECTURE_DIAGRAM.md`
- **Implementation Details**: `docs/IMPLEMENTATION_SUMMARY.md`

---

**Version**: 2.0.0  
**Status**: Production Ready ✅
