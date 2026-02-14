# Image Task & Result

Upload images to the server and save one JSON file with image index and comments. **Python (Flask) API** handles uploads and saving report data.

## Run the Python API (recommended)

1. Create a virtual environment (optional):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the server:
   ```bash
   python app.py
   ```
4. Open in browser: **http://localhost:5000** (Python serves the HTML; upload and save use the same server.)

**API:**
- **POST /api/upload** – upload image (form field `image`) → saved to `image/` folder, returns `{ "filename": "..." }`
- **POST /api/save** – save report (JSON body: `savedAt`, `imageIndex`, `tasks` with comments) → saved to `reports/report_YYYYMMDD_HHMMSS.json`

## Save as JSON

Click **Save as JSON** to:
1. Send the report (image index + comments) to the server → saved in `reports/`
2. Download the same JSON file to your computer

## JSON structure

- **savedAt** – save time
- **imageIndex** – all image names (key = slot id, value = filename on server)
- **tasks** – each task has `taskImage`, `resultImage`, `taskComments`, `resultComments`

## Node.js server (alternative)

You can still use the Node server on port 3000: run `npm install` and `npm start`, then set `API_BASE` in the HTML to `http://localhost:3000` (and add a save endpoint there if needed).
