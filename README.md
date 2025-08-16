# Illini Prompt Nurse

Prototype student triage assistant for McKinley Health Center.

## Running the demo
1. Install dependencies (Flask backend):
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   python app.py
   ```
3. Open `index2.html` in your browser and try the Ask, Upload, and Schedule forms.

The `index.html` file remains untouched as a backup of the original landing page.

The Flask backend exposes CORS-enabled `/api/ask`, `/api/upload-doc`, and `/api/schedule` routes.  Incoming
messages are processed by `core.py` which injects legal disclaimers, detects crisis language, and returns
priority and confidence metadata for the front-end display.
