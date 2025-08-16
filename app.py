"""Flask server for Illini Prompt Nurse prototype."""
from __future__ import annotations

import os
from flask import Flask, request, jsonify
from flask_cors import CORS

from core import run_gpt

app = Flask(__name__)
CORS(app)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/api/ask")
def api_ask():
    data = request.get_json(force=True)
    student_id = data.get("student_id", "")
    message = data.get("message", "")
    result = run_gpt(student_id, message)
    return jsonify(result)


@app.post("/api/upload-doc")
def upload_doc():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "no file"}), 400
    path = os.path.join(UPLOAD_DIR, file.filename)
    file.save(path)
    return jsonify({"status": "File received", "filename": file.filename})


@app.post("/api/schedule")
def schedule():
    # In a real system this would trigger a scheduling workflow
    return jsonify({"status": "Appointment request sent"})


@app.get("/")
def root():
    return jsonify({"message": "Illini Prompt Nurse API"})


if __name__ == "__main__":
    app.run(debug=True)
