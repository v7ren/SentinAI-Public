package main

import (
	"bytes"
	"crypto/md5"
	"database/sql"
	"encoding/gob"
	"encoding/hex"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
)

const (
	secretKey   = "go_gin_bench_secret_2024"
	adminAPIKey = "go_gin_admin_key_xyz"
)

var (
	db        *sql.DB
	uploadDir string
)

func initDB() {
	var err error
	db, err = sql.Open("sqlite3", "./bench.db")
	if err != nil {
		panic(err)
	}
	_, _ = db.Exec(`
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
	`)
	h := md5.Sum([]byte("Admin123!"))
	_, _ = db.Exec("INSERT OR IGNORE INTO users (id, username, password, email, role) VALUES (1, 'admin', ?, 'admin@test.com', 'admin')", hex.EncodeToString(h[:]))
}

func requireAuth(c *gin.Context) {
	uid, _ := c.Cookie("user_id")
	if uid == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
		c.Abort()
		return
	}
	c.Next()
}

func main() {
	uploadDir = filepath.Join(".", "uploads")
	_ = os.MkdirAll(uploadDir, 0755)
	initDB()
	r := gin.Default()
	r.Use(gin.Recovery())

	r.GET("/", index)
	r.POST("/api/auth/register", register)
	r.POST("/api/auth/login", login)
	r.GET("/api/profile/:id", getProfile)
	r.POST("/api/profile", requireAuth, createProfile)
	r.PUT("/api/profile/:id", requireAuth, updateProfile)
	r.GET("/api/search", search)
	r.POST("/api/upload", requireAuth, upload)
	r.GET("/api/file", readFile)
	r.POST("/api/run", runCmd)
	r.GET("/api/admin/users", adminUsers)
	r.POST("/api/config/load", configLoad)
	r.POST("/api/eval", doEval)
	r.GET("/api/echo", echo)

	_ = r.Run("0.0.0.0:5005")
}

func index(c *gin.Context) {
	c.Header("Content-Type", "text/html")
	c.String(200, `<html><head><title>Go Gin Benchmark</title></head><body><div style="background:#f00;color:#fff;padding:8px;">WARNING: This app is for SAST benchmarking only. Do not deploy publicly.</div><p>API: /api/auth/login, /api/profile, /api/search, /api/upload, /api/admin/users</p></body></html>`)
}

func register(c *gin.Context) {
	var body struct {
		Username string `json:"username"`
		Password string `json:"password"`
		Email    string `json:"email"`
		Role     string `json:"role"`
	}
	_ = c.ShouldBindJSON(&body)
	if body.Role == "" {
		body.Role = "user"
	}
	h := md5.Sum([]byte(body.Password))
	pwHash := hex.EncodeToString(h[:])
	q := fmt.Sprintf("INSERT INTO users (username, password, email, role) VALUES ('%s', '%s', '%s', '%s')",
		body.Username, pwHash, body.Email, body.Role)
	_, err := db.Exec(q)
	if err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}
	var uid int64
	_ = db.QueryRow("SELECT last_insert_rowid()").Scan(&uid)
	c.SetCookie("user_id", fmt.Sprint(uid), 3600, "/", "", false, false)
	c.SetCookie("role", body.Role, 3600, "/", "", false, false)
	c.JSON(200, gin.H{"id": uid, "role": body.Role})
}

func login(c *gin.Context) {
	var body struct {
		Username string `json:"username"`
		Password string `json:"password"`
	}
	_ = c.ShouldBindJSON(&body)
	h := md5.Sum([]byte(body.Password))
	pwHash := hex.EncodeToString(h[:])
	q := fmt.Sprintf("SELECT id, role FROM users WHERE username = '%s' AND password = '%s'", body.Username, pwHash)
	var id int
	var role string
	err := db.QueryRow(q).Scan(&id, &role)
	if err != nil {
		c.JSON(401, gin.H{"error": "Invalid credentials"})
		return
	}
	c.SetCookie("user_id", fmt.Sprint(id), 3600, "/", "", false, false)
	c.SetCookie("role", role, 3600, "/", "", false, false)
	c.JSON(200, gin.H{"id": id, "role": role})
}

func getProfile(c *gin.Context) {
	id := c.Param("id")
	q := fmt.Sprintf("SELECT p.id, p.user_id, p.display_name, p.bio, u.username FROM profiles p JOIN users u ON p.user_id = u.id WHERE p.id = '%s'", id)
	var pid, uid int
	var displayName, bio, username string
	err := db.QueryRow(q).Scan(&pid, &uid, &displayName, &bio, &username)
	if err != nil {
		c.JSON(404, gin.H{"error": "Not found"})
		return
	}
	c.JSON(200, gin.H{"id": pid, "user_id": uid, "display_name": displayName, "bio": bio, "username": username})
}

func createProfile(c *gin.Context) {
	uid, _ := c.Cookie("user_id")
	var body struct {
		DisplayName string `json:"display_name"`
		Bio         string `json:"bio"`
	}
	_ = c.ShouldBindJSON(&body)
	q := fmt.Sprintf("INSERT INTO profiles (user_id, display_name, bio) VALUES (%s, '%s', '%s')", uid, body.DisplayName, body.Bio)
	_, err := db.Exec(q)
	if err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}
	var pid int64
	_ = db.QueryRow("SELECT last_insert_rowid()").Scan(&pid)
	c.JSON(200, gin.H{"id": pid})
}

func updateProfile(c *gin.Context) {
	id := c.Param("id")
	var body struct {
		DisplayName string `json:"display_name"`
		Bio         string `json:"bio"`
	}
	_ = c.ShouldBindJSON(&body)
	q := fmt.Sprintf("UPDATE profiles SET display_name = '%s', bio = '%s' WHERE id = '%s'", body.DisplayName, body.Bio, id)
	_, _ = db.Exec(q)
	c.JSON(200, gin.H{"ok": true})
}

func search(c *gin.Context) {
	q := c.Query("q")
	sql := fmt.Sprintf("SELECT id, user_id, display_name, bio FROM profiles WHERE display_name LIKE '%%%s%%' OR bio LIKE '%%%s%%'", q, q)
	rows, err := db.Query(sql)
	if err != nil {
		c.JSON(500, gin.H{"error": err.Error()})
		return
	}
	defer rows.Close()
	var out []gin.H
	for rows.Next() {
		var id, uid int
		var displayName, bio string
		_ = rows.Scan(&id, &uid, &displayName, &bio)
		out = append(out, gin.H{"id": id, "user_id": uid, "display_name": displayName, "bio": bio})
	}
	c.JSON(200, out)
}

func upload(c *gin.Context) {
	f, err := c.FormFile("file")
	if err != nil {
		c.JSON(400, gin.H{"error": "No file"})
		return
	}
	dst := filepath.Join(uploadDir, f.Filename)
	_ = c.SaveUploadedFile(f, dst)
	info, _ := os.Stat(dst)
	c.JSON(200, gin.H{"path": f.Filename, "size": info.Size()})
}

func readFile(c *gin.Context) {
	name := c.Query("name")
	full := filepath.Join(uploadDir, name)
	if _, err := os.Stat(full); os.IsNotExist(err) {
		c.JSON(404, gin.H{"error": "Not found"})
		return
	}
	c.File(full)
}

func runCmd(c *gin.Context) {
	var body struct {
		Cmd string `json:"cmd"`
	}
	_ = c.ShouldBindJSON(&body)
	if body.Cmd == "" {
		body.Cmd = "id"
	}
	out, err := exec.Command("sh", "-c", body.Cmd).Output()
	if err != nil {
		c.JSON(200, gin.H{"output": err.Error()})
		return
	}
	c.JSON(200, gin.H{"output": string(out)})
}

func adminUsers(c *gin.Context) {
	key := c.GetHeader("X-API-Key")
	if key == "" {
		key = c.Query("api_key")
	}
	if key != adminAPIKey {
		c.JSON(403, gin.H{"error": "Forbidden"})
		return
	}
	rows, _ := db.Query("SELECT id, username, email, role FROM users")
	defer rows.Close()
	var out []gin.H
	for rows.Next() {
		var id int
		var username, email, role string
		_ = rows.Scan(&id, &username, &email, &role)
		out = append(out, gin.H{"id": id, "username": username, "email": email, "role": role})
	}
	c.JSON(200, out)
}

func configLoad(c *gin.Context) {
	body, err := io.ReadAll(c.Request.Body)
	if err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}
	var v interface{}
	dec := gob.NewDecoder(bytes.NewReader(body))
	err = dec.Decode(&v)
	if err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}
	c.JSON(200, gin.H{"config": fmt.Sprint(v)})
}

func doEval(c *gin.Context) {
	var body struct {
		Expr string `json:"expr"`
	}
	_ = c.ShouldBindJSON(&body)
	if body.Expr == "" {
		body.Expr = "1+1"
	}
	out, err := exec.Command("sh", "-c", "echo $(( "+body.Expr+" ))").Output()
	if err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}
	c.JSON(200, gin.H{"result": strings.TrimSpace(string(out))})
}

func echo(c *gin.Context) {
	msg := c.Query("msg")
	c.Header("Content-Type", "text/html")
	c.String(200, "<html><body>Message: "+msg+"</body></html>")
}
