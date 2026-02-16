"""
Python API backend: upload images, save report. Data แยกระดับ Project + Passkey.
"""
import hashlib
import os
import re
import json
import uuid
from datetime import datetime
from pathlib import Path

from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type"]}})

BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / "image"
REPORTS_DIR = BASE_DIR / "reports"
DATA_JSON_PATH = BASE_DIR / "data.json"

DEFAULT_PROJECT_DATA = {
    "savedAt": "",
    "imageIndex": {},
    "tasks": [
        {"taskImage": "task_0", "resultImage": "result_0", "taskComments": [], "resultComments": []}
    ],
}


def passkey_hash(passkey):
    return hashlib.sha256((passkey or "").encode("utf-8")).hexdigest()


def read_data_file():
    """อ่าน data.json และแปลงรูปแบบเก่า (ไม่มี projects) เป็นรูปแบบใหม่"""
    if not DATA_JSON_PATH.exists():
        return {"projects": []}
    with open(DATA_JSON_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)
    if not isinstance(raw, dict):
        return {"projects": []}
    if "projects" in raw and isinstance(raw["projects"], list):
        return raw
    data = {
        "savedAt": raw.get("savedAt", ""),
        "imageIndex": raw.get("imageIndex") or {},
        "tasks": raw.get("tasks") if isinstance(raw.get("tasks"), list) else DEFAULT_PROJECT_DATA["tasks"].copy(),
    }
    return {
        "projects": [
            {"id": "proj_default", "name": "Default", "passkeyHash": passkey_hash(""), "data": data}
        ],
    }


def write_data_file(obj):
    with open(DATA_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def ensure_data_and_image():
    """เมื่อ deploy: ถ้า data.json หรือโฟลเดอร์ image ไม่มี ให้สร้างไว้ใช้ได้เลย"""
    if not IMAGE_DIR.exists():
        IMAGE_DIR.mkdir(parents=True)
        print("Created image/ folder")
    else:
        print("image/ exists, using it")
    if not DATA_JSON_PATH.exists():
        write_data_file({
            "projects": [
                {"id": "proj_default", "name": "Default", "passkeyHash": passkey_hash(""), "data": DEFAULT_PROJECT_DATA.copy()}
            ]
        })
        print("Created data.json (with Default project)")
    else:
        print("data.json exists, using it")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


ensure_data_and_image()

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_SIZE = 50 * 1024 * 1024  # 50 MB (สำหรับ Save image จาก editor ที่ canvas ใหญ่)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def safe_filename(original):
    name = secure_filename(original) or "image"
    base, ext = os.path.splitext(name)
    if not ext or ext.lower() not in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
        ext = ".jpg"
    base = re.sub(r"\s+", "_", base)[:50]
    return f"{base}_{int(datetime.now().timestamp())}{ext}"


@app.route("/api/upload-overwrite", methods=["OPTIONS"])
def upload_overwrite_options():
    resp = make_response("", 200)
    resp.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Max-Age"] = "86400"
    return resp


@app.route("/api/upload-overwrite", methods=["POST"])
def upload_overwrite():
    """บันทึกรูปทับไฟล์เดิม (ใช้จาก editimage.html Save)"""
    if "image" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["image"]
    if not file or file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    raw_filename = (request.form.get("filename") or "").strip()
    if not raw_filename:
        return jsonify({"error": "filename required"}), 400
    raw_filename = raw_filename.split("?")[0].split("#")[0].strip()
    name = secure_filename(os.path.basename(raw_filename))
    if not name:
        return jsonify({"error": "Invalid filename"}), 400
    if not allowed_file(name):
        base, ext = os.path.splitext(name)
        if not ext or ext.lower() not in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
            name = (base or "image") + ".png"
    if not allowed_file(name):
        return jsonify({"error": "Only image files allowed"}), 400
    path = IMAGE_DIR / name
    try:
        if not path.resolve().is_relative_to(IMAGE_DIR.resolve()):
            return jsonify({"error": "Invalid path"}), 400
    except AttributeError:
        if not os.path.realpath(path).startswith(os.path.realpath(IMAGE_DIR)):
            return jsonify({"error": "Invalid path"}), 400
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > MAX_SIZE:
        return jsonify({"error": "File too large"}), 400
    ct = (file.content_type or "").strip().lower()
    if not ct.startswith("image/"):
        return jsonify({"error": "Only images allowed"}), 400
    file.save(path)
    return jsonify({"ok": True, "filename": name})


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "image-task-result.html")


@app.route("/image-task-result.html")
def page():
    return send_from_directory(BASE_DIR, "image-task-result.html")


@app.route("/api/upload", methods=["POST"])
def upload():
    if "image" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["image"]
    if not file or file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    if not file.content_type or not file.content_type.startswith("image/"):
        return jsonify({"error": "Only images allowed"}), 400
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > MAX_SIZE:
        return jsonify({"error": "File too large"}), 400
    filename = safe_filename(file.filename)
    file.save(IMAGE_DIR / filename)
    return jsonify({"filename": filename})


@app.route("/api/projects", methods=["GET"])
def api_list_projects():
    """รายการ Project (id, name) สำหรับให้ User เลือก"""
    try:
        data = read_data_file()
        projects = data.get("projects") or []
        out = [{"id": p.get("id"), "name": p.get("name", "Unnamed")} for p in projects if p.get("id")]
        return jsonify({"projects": out})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/load-project", methods=["POST"])
def api_load_project():
    """โหลด Project หลังใส่ Passkey ถูกต้อง"""
    body = request.get_json(force=True, silent=True) or {}
    project_id = body.get("projectId")
    passkey = body.get("passkey", "")
    if not project_id:
        return jsonify({"error": "projectId required"}), 400
    try:
        data = read_data_file()
        projects = data.get("projects") or []
        for p in projects:
            if p.get("id") == project_id:
                if p.get("passkeyHash") != passkey_hash(passkey):
                    return jsonify({"error": "Invalid passkey"}), 403
                return jsonify({"ok": True, "data": p.get("data") or DEFAULT_PROJECT_DATA})
        return jsonify({"error": "Project not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/create-project", methods=["POST"])
def api_create_project():
    """สร้าง Project ใหม่ (name + passkey)"""
    body = request.get_json(force=True, silent=True) or {}
    name = (body.get("name") or "").strip() or "New Project"
    passkey = body.get("passkey", "")
    try:
        data = read_data_file()
        projects = data.get("projects") or []
        new_id = "proj_" + uuid.uuid4().hex[:12]
        projects.append({
            "id": new_id,
            "name": name,
            "passkeyHash": passkey_hash(passkey),
            "data": DEFAULT_PROJECT_DATA.copy(),
        })
        write_data_file({"projects": projects})
        return jsonify({"ok": True, "projectId": new_id, "name": name})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/save", methods=["POST"])
def save_report():
    """บันทึกข้อมูลของ Project (ต้องส่ง projectId + passkey)"""
    data = request.get_json(force=True, silent=True)
    if not data and request.data:
        try:
            data = json.loads(request.get_data(as_text=True))
        except Exception:
            pass
    if not data:
        return jsonify({"error": "JSON body required"}), 400
    project_id = data.get("projectId")
    passkey = data.get("passkey", "")
    if not project_id:
        return jsonify({"error": "projectId required"}), 400
    try:
        if not isinstance(data.get("tasks"), list):
            return jsonify({"ok": False, "error": "Invalid data: tasks required"}), 400
        payload = {
            "savedAt": data.get("savedAt", ""),
            "imageIndex": data.get("imageIndex") if isinstance(data.get("imageIndex"), dict) else {},
            "tasks": data["tasks"],
        }
        full = read_data_file()
        projects = full.get("projects") or []
        found = False
        for p in projects:
            if p.get("id") == project_id:
                if p.get("passkeyHash") != passkey_hash(passkey):
                    return jsonify({"error": "Invalid passkey"}), 403
                p["data"] = payload
                found = True
                break
        if not found:
            return jsonify({"error": "Project not found"}), 404
        write_data_file(full)
        print("[Save] data.json updated, project=%s, tasks=%s" % (project_id, len(payload["tasks"])))
        return jsonify({"ok": True, "saved": "data.json", "dataJsonUpdated": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/image/<path:filename>")
def serve_image(filename):
    return send_from_directory(IMAGE_DIR, filename)


@app.route("/data.json")
def serve_data_json():
    return send_from_directory(BASE_DIR, "data.json")


@app.route("/api/data", methods=["GET"])
@app.route("/api/data/", methods=["GET"])
def api_get_data():
    """โหลดข้อมูล (backward compat: คืน project แรกถ้ามีเดียว ไม่ตรวจ passkey)"""
    try:
        data = read_data_file()
        projects = data.get("projects") or []
        if len(projects) == 1:
            return jsonify(projects[0].get("data") or DEFAULT_PROJECT_DATA)
        return jsonify(DEFAULT_PROJECT_DATA)
    except Exception as e:
        print("[Load data] Error:", e)
        return jsonify(DEFAULT_PROJECT_DATA)


if __name__ == "__main__":
    print("Server: http://localhost:5000")
    print("Open in browser: http://localhost:5000  (py + html work together)")
    app.run(host="0.0.0.0", port=5000, debug=False)
