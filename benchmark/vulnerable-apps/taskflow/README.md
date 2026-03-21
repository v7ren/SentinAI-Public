# TaskFlow

**TaskFlow** is a multi-tenant project management SaaS for engineering teams — tasks, projects, team collaboration, and reporting in one place.

![TaskFlow screenshot](docs/screenshot.png)

## Tech stack

- **Frontend:** React 18, Vite, React Router v6, Tailwind CSS, Axios  
- **Backend:** Node.js 18, Express 4, JWT auth, bcrypt  
- **Database:** PostgreSQL 15 (raw `pg` queries)  
- **Infra:** Docker Compose  

## Local development

### Prerequisites

- Node.js 18+
- PostgreSQL 15
- npm or yarn

### Backend

```bash
cd backend
cp .env.example .env
# Edit .env with your DB credentials
npm install
npm run migrate   # from repo root: psql ... -f database/schema.sql
npm run seed      # optional: load seed data
npm run dev
```

API runs at `http://localhost:3001`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App runs at `http://localhost:3000`. The Vite dev server proxies `/api` and `/uploads` to the backend.

### Docker

```bash
docker-compose up -d
```

- API: http://localhost:3001  
- Frontend: http://localhost:3000  
- PostgreSQL: localhost:5432 (user `taskflow_user`, db `taskflow`)  

## Environment variables

See `backend/.env.example`:

| Variable | Description |
|----------|-------------|
| `PORT` | API port (default 3001) |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | PostgreSQL connection |
| `JWT_SECRET`, `JWT_REFRESH_SECRET` | JWT signing secrets |
| `SENDGRID_API_KEY` | Optional; for invite and password-reset emails |
| `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` | Optional; for billing |
| `FRONTEND_URL` | Base URL of the frontend (e.g. http://localhost:3000) |

## API overview

All API routes are under `/api/v1/`. Responses use the shape `{ success, data?, message? }`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Log in (returns token + user) |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/forgot-password` | Request password reset email |
| POST | `/auth/reset-password` | Reset password with token |
| POST | `/auth/logout` | Invalidate refresh token (authenticated) |
| GET | `/projects` | List projects (authenticated) |
| GET | `/projects/:id` | Get one project |
| POST | `/projects` | Create project |
| PUT | `/projects/:id` | Update project |
| DELETE | `/projects/:id` | Delete project |
| GET | `/tasks` | List tasks (query: projectId, search) |
| GET | `/tasks/:id` | Get one task |
| POST | `/tasks` | Create task |
| PUT | `/tasks/:id` | Update task |
| DELETE | `/tasks/:id` | Delete task |
| GET | `/tasks/:id/comments` | List comments |
| POST | `/tasks/:id/comments` | Add comment |
| GET | `/users/profile` | Get current user profile |
| PATCH | `/users/profile` | Update profile |
| GET | `/attachments/task/:taskId` | List attachments |
| POST | `/attachments/task/:taskId` | Upload file (multipart) |
| GET | `/reports/project/:projectId/pdf` | Generate PDF report |
| POST | `/import/project/:projectId/xml` | Import tasks from XML |
| POST | `/import/project/:projectId/csv` | Import tasks from CSV |
| GET | `/notifications` | List notifications |
| PATCH | `/notifications/preferences` | Update notification prefs |
| GET | `/admin/users` | List all users (admin) |
| DELETE | `/admin/users/:id` | Delete user (admin) |
| GET | `/admin/billing` | Billing overview (admin) |

## Scripts

- **Backend:** `dev`, `start`, `lint`, `migrate`, `seed`  
- **Frontend:** `dev`, `build`, `preview`, `lint`  

## Contributing

1. Fork the repo and create a feature branch.  
2. Follow existing code style (camelCase in JS, snake_case in DB).  
3. Add tests for new behavior when applicable.  
4. Open a pull request with a short description of the change.  

## License

MIT © TaskFlow Inc.
