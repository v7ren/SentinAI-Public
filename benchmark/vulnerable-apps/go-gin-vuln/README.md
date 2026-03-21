# go-gin-vuln

**WARNING: For education and SAST benchmarking only. This application contains intentional security vulnerabilities. Do not deploy publicly or expose to the internet.**

## Folder tree

```
go-gin-vuln/
├── main.go
├── go.mod
├── README.md
├── SAFE_VARIANT.md
└── uploads/   (created at runtime)
```

## Features

- Auth: register, login (cookies)
- Profile CRUD
- File upload and download
- Search
- Admin route: list users (X-API-Key)

## Run

```bash
cd benchmark/vulnerable-apps/go-gin-vuln
go mod tidy
go run main.go
```

API base: `http://localhost:5005`

## Compare vulnerable vs fixed

Use the `safe` branch or follow `SAFE_VARIANT.md`. Exact vulnerability locations and exploit steps: see `../go-gin-vuln.md` in the `benchmark/vulnerable-apps` root.

## Warning

This app must never be deployed publicly. Use only in isolated test environments for SAST tool evaluation.
