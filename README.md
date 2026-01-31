
# Mini Expense Tracker (Full Stack)

A production‑grade **full‑stack expense tracking application** with a resilient frontend and a robust backend.
The system is designed to handle **real‑world concerns** such as authentication, idempotency, network retries,
timezone consistency (IST), and clean API contracts.

---

## 📖 Overview

**Mini Expense Tracker** helps users securely record, view, update, and analyze personal expenses.

This is not a simple CRUD app:
- The **frontend** focuses on UX, resilience, and idempotent operations.
- The **backend** focuses on correctness, security, clean architecture, and production readiness.

The application supports **multiple users**, **JWT‑based authentication**, and **IST‑consistent timestamps** stored at the database level.

---

## 🛠️ Tech Stack

### Frontend
- React 18 + Vite
- Tailwind CSS v4
- Axios
- React Context API
- Framer Motion
- Lucide React
- date-fns
- uuid
- react-toastify

### Backend
- FastAPI
- Python 3.11+
- SQLAlchemy 2.x (Async)
- PostgreSQL
- asyncpg
- Pydantic v2
- JWT Authentication
- Passlib (Argon2 hashing)
- Pytest (unit + integration tests)

---

## ✨ Features

### Authentication
- Secure user registration & login
- JWT‑based authentication
- Automatic logout on token expiry (401)

### Expense Management
- Create, Read, Update, Delete expenses
- Filter by category
- Sort by date (newest / oldest)
- Real‑time total calculation

### Resilience & Reliability
- **Idempotent Create Expense** using `client_id` (UUID)
- Prevents duplicate records on retries or network failures

### Timezone Correctness
- All timestamps stored and displayed in **IST (Asia/Kolkata)**
- Database session timezone enforced
- DB‑level defaults (`timezone('Asia/Kolkata', now())`)

### UI & UX
- Responsive layout (mobile + desktop)
- Modal‑based workflows
- Toast notifications
- Glassmorphism UI (Teal & Emerald theme)

---

## 🧠 Design Decisions

### Why Idempotency?
Network retries and double‑clicks are common in real apps.
Each expense creation includes a **client‑generated UUID**, ensuring:
- Multiple retries create **only one record**
- Backend remains safe under flaky networks

### Why Argon2 for Password Hashing?
- OWASP‑recommended
- No bcrypt 72‑byte limit
- Memory‑hard (more resistant to GPU attacks)
- Avoids native dependency issues

### Why DB‑level IST handling?
- PostgreSQL `timestamptz` stores UTC internally
- Session timezone is set to `Asia/Kolkata`
- Prevents mixed timezone display issues
- Ensures consistency across all queries

---


## Application Workflow

This document describes the **core runtime workflow** of the Mini Expense Tracker application,
focusing on **authentication/session handling** and the **expense lifecycle**.

---

## 1️⃣ Authentication & Session Lifecycle

### Registration
1. User submits email and password from the frontend.
2. Backend validates input (email format, password length).
3. Password is securely hashed using **Argon2**.
4. User record is created with `created_at` stored in **IST (Asia/Kolkata)** at the database level.

### Login
1. User submits email and password.
2. Backend verifies credentials against the stored Argon2 hash.
3. Backend issues a **JWT access token** containing:
   - `sub` → user ID
   - `exp` → token expiry timestamp
4. Token is returned to the frontend.

### Session Management (Frontend)
1. JWT is stored in `localStorage`.
2. A centralized Axios interceptor:
   - Attaches `Authorization: Bearer <token>` to all protected requests.
   - Ensures no manual token wiring is needed in individual API calls.

### Authorization & Expiry Handling
1. Every protected backend route validates the JWT.
2. If the token is:
   - Missing
   - Invalid
   - Expired  
   → Backend responds with `401 Unauthorized`.
3. Axios interceptor detects `401` responses and:
   - Clears stored token
   - Resets auth state
   - Redirects user to the login screen

This guarantees a clean and predictable session lifecycle across refreshes and deployments.

---

## 2️⃣ Expense Lifecycle (Create → Read → Update → Delete)

### Create Expense (Idempotent & Network-Safe)
1. When the **Add Expense** modal opens, the frontend generates a unique `client_id` (UUID).
2. User fills in expense details and submits the form.
3. Frontend sends the payload including `client_id` to the backend.
4. Backend checks `(user_id, client_id)`:
   - If it already exists → returns the existing expense.
   - If not → creates a new expense.
5. This ensures **exactly-once creation**, even if:
   - Network requests are retried
   - The submit button is clicked multiple times
6. On success, the frontend:
   - Closes the modal
   - Refreshes the expense list
   - Generates a new `client_id` for the next create operation

---

### Read Expenses (Filtered & Sorted)
1. Frontend fetches expenses with optional query parameters:
   - `category`
   - `sort=date_desc | date_asc`
2. Backend:
   - Restricts data to the authenticated user
   - Applies filtering and sorting at the query level
   - Computes aggregate totals
3. Frontend updates:
   - Expense list
   - Total spend summary
   - Category-wise breakdown

---

### Update Expense
1. User opens the **Edit Expense** modal.
2. Existing expense data is pre-filled.
3. User submits changes.
4. Backend:
   - Verifies ownership
   - Applies partial or full updates
   - Persists changes with IST-consistent timestamps
5. Frontend refreshes state to reflect updates.

---

### Delete Expense
1. User initiates delete action with confirmation.
2. Backend verifies ownership and deletes the expense.
3. Frontend refreshes state to remove the deleted record.

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000
```

---

### 🔐 Auth APIs

#### Register
**POST** `/auth/register`

Request:
```json
{
  "email": "user@example.com",
  "password": "strongpassword123"
}
```

Response `201`:
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2026-01-31T20:30:12+05:30"
}
```

---

#### Login
**POST** `/auth/login`

Request:
```json
{
  "email": "user@example.com",
  "password": "strongpassword123"
}
```

Response `200`:
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer"
}
```

---

### 💰 Expense APIs
> All endpoints require:
```
Authorization: Bearer <JWT>
```

#### Create Expense (Idempotent)
**POST** `/expenses`

Request:
```json
{
  "amount": 250.75,
  "category": "Food",
  "description": "Lunch",
  "date": "2026-01-31T13:00:00Z",
  "client_id": "c1b5c9b1-9a7f-4b6b-9a3f-8e0e8a6e4a21"
}
```

Response `201`:
```json
{
  "id": 10,
  "user_id": 1,
  "amount": 250.75,
  "category": "Food",
  "description": "Lunch",
  "date": "2026-01-31T18:30:00+05:30",
  "created_at": "2026-01-31T20:30:45+05:30",
  "client_id": "c1b5c9b1-9a7f-4b6b-9a3f-8e0e8a6e4a21"
}
```

---

#### List Expenses
**GET** `/expenses?sort=date_desc&category=Food`

Response:
```json
{
  "items": [...],
  "total": 1250.50,
  "count": 5
}
```

---

#### Update Expense
**PUT / PATCH** `/expenses/{id}`

Request:
```json
{
  "amount": 300,
  "description": "Updated lunch"
}
```

---

#### Delete Expense
**DELETE** `/expenses/{id}`

Response:
```
204 No Content
```

---

## ⚙️ Local Setup

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at:
```
http://localhost:8000
```

---

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:
```
http://localhost:5173
```

---

## 🔐 Environment Variables

### Backend (`backend/.env`)
```
DATABASE_URL=postgresql://...
SECRET_KEY=super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60
LOG_LEVEL=INFO
```

### Frontend
```
VITE_API_BASE_URL=http://localhost:8000
```

---

