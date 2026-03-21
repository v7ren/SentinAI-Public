/**
 * Training app for SAST benchmarking. Education/testing only.
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");
const express = require("express");
const cors = require("cors");
const cookieParser = require("cookie-parser");
const multer = require("multer");

const app = express();
app.use(cors({ origin: true, credentials: true }));
app.use(express.json());
app.use(cookieParser());

const SECRET = "express_bench_secret_2024";
const ADMIN_KEY = "admin_key_abcdef";
const UPLOAD_DIR = path.join(__dirname, "uploads");
const DB_PATH = path.join(__dirname, "data.db");

if (!fs.existsSync(UPLOAD_DIR)) fs.mkdirSync(UPLOAD_DIR, { recursive: true });

const Database = require("better-sqlite3");
const db = new Database(DB_PATH);

db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    email TEXT,
    role TEXT DEFAULT 'user'
  );
  CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    display_name TEXT,
    bio TEXT
  );
`);
const adminExists = db.prepare("SELECT 1 FROM users WHERE username = 'admin'").get();
if (!adminExists) {
  const crypto = require("crypto");
  const hash = crypto.createHash("md5").update("Admin123!").digest("hex");
  db.prepare("INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)").run("admin", hash, "admin@test.com", "admin");
}

function requireAuth(req, res, next) {
  const uid = req.cookies?.user_id;
  if (uid == null) return res.status(401).json({ error: "Unauthorized" });
  next();
}

app.post("/api/auth/register", (req, res) => {
  const { username = "", password = "", email = "", role = "user" } = req.body;
  const crypto = require("crypto");
  const pwHash = crypto.createHash("md5").update(password).digest("hex");
  try {
    db.exec(`INSERT INTO users (username, password, email, role) VALUES ('${username}', '${pwHash}', '${email}', '${role}')`);
    const row = db.prepare("SELECT last_insert_rowid() as id").get();
    res.cookie("user_id", row.id, { httpOnly: false });
    res.cookie("role", role, { httpOnly: false });
    res.json({ id: row.id, role });
  } catch (e) {
    res.status(400).json({ error: e.message });
  }
});

app.post("/api/auth/login", (req, res) => {
  const { username = "", password = "" } = req.body;
  const crypto = require("crypto");
  const pwHash = crypto.createHash("md5").update(password).digest("hex");
  const row = db.prepare(`SELECT * FROM users WHERE username = '${username}' AND password = '${pwHash}'`).get();
  if (!row) return res.status(401).json({ error: "Invalid credentials" });
  res.cookie("user_id", row.id, { httpOnly: false });
  res.cookie("role", row.role, { httpOnly: false });
  res.json({ id: row.id, role: row.role });
});

app.get("/api/profile/:id", (req, res) => {
  const id = req.params.id;
  const row = db.prepare(`SELECT p.*, u.username FROM profiles p JOIN users u ON p.user_id = u.id WHERE p.id = '${id}'`).get();
  if (!row) return res.status(404).json({ error: "Not found" });
  res.json(row);
});

app.post("/api/profile", requireAuth, (req, res) => {
  const { display_name = "", bio = "" } = req.body;
  const uid = req.cookies.user_id;
  db.exec(`INSERT INTO profiles (user_id, display_name, bio) VALUES (${uid}, '${display_name}', '${bio}')`);
  const row = db.prepare("SELECT last_insert_rowid() as id").get();
  res.json({ id: row.id });
});

app.put("/api/profile/:id", requireAuth, (req, res) => {
  const id = req.params.id;
  const { display_name = "", bio = "" } = req.body;
  db.exec(`UPDATE profiles SET display_name = '${display_name}', bio = '${bio}' WHERE id = '${id}'`);
  res.json({ ok: true });
});

app.get("/api/search", (req, res) => {
  const q = req.query.q || "";
  const rows = db.prepare(`SELECT * FROM profiles WHERE display_name LIKE '%${q}%' OR bio LIKE '%${q}%'`).all();
  res.json(rows);
});

const upload = multer({ dest: UPLOAD_DIR });
app.post("/api/upload", requireAuth, upload.single("file"), (req, res) => {
  if (!req.file) return res.status(400).json({ error: "No file" });
  const newPath = path.join(UPLOAD_DIR, req.file.originalname || req.file.filename);
  fs.renameSync(req.file.path, newPath);
  res.json({ path: req.file.originalname, size: fs.statSync(newPath).size });
});

app.get("/api/file", (req, res) => {
  const name = req.query.name || "";
  const full = path.join(UPLOAD_DIR, name);
  if (!fs.existsSync(full)) return res.status(404).json({ error: "Not found" });
  res.sendFile(full);
});

app.post("/api/run", (req, res) => {
  const cmd = req.body?.cmd || "id";
  try {
    const out = execSync(cmd, { encoding: "utf8" });
    res.json({ output: out });
  } catch (e) {
    res.json({ output: e.message });
  }
});

app.get("/api/admin/users", (req, res) => {
  const key = req.headers["x-api-key"] || req.query.api_key || "";
  if (key !== ADMIN_KEY) return res.status(403).json({ error: "Forbidden" });
  const rows = db.prepare("SELECT id, username, email, role FROM users").all();
  res.json(rows);
});

app.post("/api/config/load", express.raw({ type: "*/*" }), (req, res) => {
  try {
    const obj = JSON.parse(req.body.toString());
    const expanded = eval("(" + req.body.toString() + ")");
    res.json({ config: JSON.stringify(expanded) });
  } catch (e) {
    res.status(400).json({ error: e.message });
  }
});

app.post("/api/eval", (req, res) => {
  const expr = req.body?.expr || "1+1";
  try {
    const result = eval(expr);
    res.json({ result });
  } catch (e) {
    res.status(400).json({ error: e.message });
  }
});

app.get("/api/echo", (req, res) => {
  const msg = req.query.msg || "";
  res.set("Content-Type", "text/html");
  res.send("<html><body>Message: " + msg + "</body></html>");
});

app.get("/", (req, res) => {
  res.set("Content-Type", "text/html");
  res.send(`
    <html><head><title>Express Benchmark</title></head>
    <body>
    <div style="background:#f00;color:#fff;padding:8px;">WARNING: This app is for SAST benchmarking only. Do not deploy publicly.</div>
    <p>API: /api/auth/login, /api/profile, /api/search, /api/upload, /api/admin/users</p>
    </body></html>
  `);
});

const PORT = process.env.PORT || 5002;
app.listen(PORT, "0.0.0.0", () => console.log("Express benchmark on port", PORT));
