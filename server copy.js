const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 3000;
const UPLOADS_DIR = path.join(__dirname, 'image');

if (!fs.existsSync(UPLOADS_DIR)) {
  fs.mkdirSync(UPLOADS_DIR, { recursive: true });
}

app.use(express.json());
app.use(express.static(__dirname));

app.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  if (req.method === 'OPTIONS') return res.sendStatus(200);
  next();
});

const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, UPLOADS_DIR);
  },
  filename: function (req, file, cb) {
    const ext = path.extname(file.originalname) || '.jpg';
    const base = path.basename(file.originalname, ext).replace(/\s+/g, '_').slice(0, 50);
    const name = base + '_' + Date.now() + ext;
    cb(null, name);
  }
});

const upload = multer({
  storage,
  limits: { fileSize: 10 * 1024 * 1024 },
  fileFilter: (req, file, cb) => {
    if (file.mimetype.startsWith('image/')) cb(null, true);
    else cb(new Error('Only images allowed'));
  }
});

app.post('/api/upload', upload.single('image'), function (req, res) {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }
  res.json({ filename: req.file.filename });
});

// บันทึกรูปทับไฟล์เดิม (ใช้จาก editimage.html Save)
const uploadOverwrite = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024 },
  fileFilter: (req, file, cb) => {
    if (file.mimetype && file.mimetype.startsWith('image/')) cb(null, true);
    else cb(new Error('Only images allowed'));
  }
});
app.post('/api/upload-overwrite', uploadOverwrite.single('image'), function (req, res) {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }
  // ใช้ชื่อเดิม: form field 'filename' หรือชื่อที่แนบมากับไฟล์ (originalname)
  const raw = (req.body && req.body.filename) || (req.file.originalname || '');
  const name = path.basename(String(raw).split('?')[0].split('#')[0].trim()).replace(/[^a-zA-Z0-9._-]/g, '_');
  if (!name || !/\.(png|jpg|jpeg|gif|webp)$/i.test(name)) {
    return res.status(400).json({ error: 'Invalid or missing filename' });
  }
  const filepath = path.join(UPLOADS_DIR, name);
  if (!path.resolve(filepath).startsWith(path.resolve(UPLOADS_DIR))) {
    return res.status(400).json({ error: 'Invalid path' });
  }
  fs.writeFile(filepath, req.file.buffer, function (err) {
    if (err) return res.status(500).json({ error: err.message });
    res.json({ ok: true, filename: name });
  });
});

app.use('/image', express.static(UPLOADS_DIR));

app.listen(PORT, () => {
  console.log('Server running at http://localhost:' + PORT);
  console.log('Open http://localhost:' + PORT + '/image-task-result.html');
});
