# 🧪 Testing Guide - PastPapersDownloader

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the server:**
   ```bash
   python3 -m uvicorn app.main:app --reload
   ```

3. **Access the application:**
   - Web UI: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs
   - Health Check: http://localhost:8000/health

## Testing Checklist

### ✅ Basic Functionality
- [x] Server starts without errors
- [x] Health endpoint returns 200
- [x] Qualifications API returns data
- [x] Subjects API returns data
- [x] Seasons API returns data

### ⏳ End-to-End Testing
- [ ] Landing page loads and displays qualifications
- [ ] Click qualification → Navigate to subjects page
- [ ] Select subjects → Navigate to seasons page
- [ ] Select seasons → Start download
- [ ] Progress page shows updates
- [ ] ZIP file downloads successfully
- [ ] ZIP contains correct folder structure

### 🔍 API Testing

#### Test Qualifications
```bash
curl http://localhost:8000/api/v1/qualifications/
```

#### Test Subjects
```bash
curl "http://localhost:8000/api/v1/subjects/?qualification=AICE"
```

#### Test Seasons
```bash
curl "http://localhost:8000/api/v1/subjects/9700/seasons?qualification=AICE"
```

#### Test Bulk Download
```bash
curl -X POST http://localhost:8000/api/v1/downloads/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "qualification": "AICE",
    "subjects": ["9700"],
    "seasons": ["9700:2024-May-June"]
  }'
```

## Known Issues to Test

1. **Large Downloads**: Test with 10+ seasons
2. **Multiple Subjects**: Test with 2-3 subjects
3. **Error Handling**: Test with invalid subject codes
4. **Progress Updates**: Verify polling works correctly
5. **ZIP Download**: Verify file structure in ZIP

## Browser Testing

1. Open http://localhost:8000
2. Select a qualification
3. Select one or more subjects
4. Select one or more seasons
5. Click "Download Selected"
6. Monitor progress page
7. Download ZIP when complete
8. Verify ZIP contents
