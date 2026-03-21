# How to log in as admin

The **Admin** page (`/admin`) shows worker nodes, scan activity, and live agent blocks. Access is restricted to admins. You can become an admin in either of two ways.

**Where to configure:** copy `backend/.env.example` to `backend/.env` (next to `mainflask.py`) and set the Admin section.

---

## Option 1: Use your normal login email (recommended)

If you sign in to the app with an email that the backend treats as admin, you can open `/admin` after signing in and it will work.

### Steps

1. **Backend `.env`** (or environment) — add your email to the comma‑separated list:
   ```env
   ADMIN_EMAILS=your@email.com,other-admin@example.com
   ```
2. **Sign in** to the app (Clerk or whatever sets the backend session) with that email.
3. Open **`/admin`**. The page will load; worker activity and agent blocks will work.

The backend checks that the session email is in `ADMIN_EMAILS`. The proxy forwards your cookies, so no extra login step is needed.

---

## Option 2: Dedicated admin account (backend-only login)

The backend also supports a separate admin account/password stored in env. This uses the Flask session and is intended for back-office use.

### Steps

1. **Backend `.env`** — set:
   ```env
   ADMIN_ACCOUNT=admin
   ADMIN_PASSWORD=your-secure-password
   ```
   - In production, avoid default pairs like `admin`/`admin` or `admin123`/`admin123` or the backend may reject login.

2. **Call the admin login endpoint** (so the backend sets the admin session and cookie):
   ```bash
   curl -X POST "http://localhost:5001/auth/admin-login" \
     -H "Content-Type: application/json" \
     -d '{"account":"admin","password":"your-secure-password"}' \
     -c cookies.txt -b cookies.txt -v
   ```
   Replace host/port if your backend is elsewhere (e.g. `https://5001.renestj.xyz`).

3. **Use the same cookie when opening the app**  
   For the browser to send the backend session cookie to the Next.js app, the cookie must be for a domain that includes both the frontend and the backend (e.g. `SESSION_COOKIE_DOMAIN=.renestj.xyz`). Then:
   - Either visit the backend origin first and log in there (so the cookie is set), then go to the frontend and open `/admin` (same parent domain).
   - Or implement a small “Admin login” form in the frontend that POSTs to a **proxy** that forwards to `BACKEND_URL/auth/admin-login` and returns the `Set-Cookie` from the backend so the browser stores it.

If the backend and frontend are on different hosts/ports and no shared cookie domain is set, Option 1 (ADMIN_EMAILS + normal sign-in) is the one that will work without extra setup.

---

## Summary

| Method              | Env vars              | How you “log in”        | Best when                          |
|---------------------|-----------------------|--------------------------|------------------------------------|
| **Option 1**        | `ADMIN_EMAILS`        | Sign in as usual with that email, then open `/admin` | Using Clerk/normal auth; want one login for everything. |
| **Option 2**        | `ADMIN_ACCOUNT`, `ADMIN_PASSWORD` | POST to `/auth/admin-login`; session cookie set by backend | Back-office or scripts; frontend and backend share a cookie domain. |

The `/api/admin/worker-activity` and `/api/admin/worker-activity/stream` endpoints accept **either**:
- a session whose email is in `ADMIN_EMAILS`, or  
- a session set by the dedicated admin login (`admin_authenticated`).

So both options can be used to access the admin page once the backend has the right env and session.
