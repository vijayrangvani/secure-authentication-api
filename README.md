# 🔐 Secure Authentication API

> A production-ready, security-hardened FastAPI authentication & authorization API featuring JWT tokens, bcrypt hashing, OAuth2 Password Flow, token refresh lifecycle, Role-Based Access Control (RBAC), and persistent PostgreSQL storage.

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15%2B-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=for-the-badge)](https://www.sqlalchemy.org/)
[![JWT](https://img.shields.io/badge/JWT-Secure_Tokens-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)](https://jwt.io/)
[![OAuth2](https://img.shields.io/badge/OAuth2-Password_Flow-EB5424?style=for-the-badge)](https://oauth.net/2/)

---

## 📌 Table of Contents

<details>
<summary><b>Click to expand</b></summary>

- [📖 Project Overview](#-project-overview)
- [✨ Core Features](#-core-features)
- [🏗️ System Architecture](#️-system-architecture)
- [🔄 Authentication & Authorization Lifecycle](#-authentication--authorization-lifecycle)
- [🛠️ Tech Stack](#️-tech-stack)
- [📁 Project Structure](#-project-structure)
- [⚙️ Setup & Installation](#️-setup--installation)
- [🔐 Environment Variables](#-environment-variables)
- [▶️ Running the Application](#️-running-the-application)
- [📡 API Endpoints & Usage](#-api-endpoints--usage)
- [🎟️ JWT & Refresh Token Mechanics](#️-jwt--refresh-token-mechanics)
- [👑 Role-Based Access Control (RBAC)](#-role-based-access-control-rbac)
- [🧪 Testing & Verification Guide](#-testing--verification-guide)
- [🎥 Project Demonstration Guide](#-project-demonstration-guide)
- [🔒 Security Practices & Implementation](#-security-practices--implementation)
- [⚠️ Limitations & Scope](#️-limitations--scope)
- [📚 Learning Outcomes](#-learning-outcomes)
- [🔮 Future Improvements](#-future-improvements)
- [👨‍💻 Author](#-author)

</details>

---

## 📖 Project Overview

Authentication and authorization are the backbone of secure web backends. This project delivers a robust, real-world authentication system built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**.

It provides complete user onboarding, deterministic password hashing using **bcrypt**, stateless authentication using dual **Access + Refresh JWTs**, compliance with FastAPI's **OAuth2 Password Flow**, and granular **Role-Based Access Control (RBAC)** protecting privileged administrative routes.

---

## ✨ Core Features

- 👤 **User Registration:** Input validation via Pydantic schemas with unique constraint checks.
- 🔑 **Bcrypt Password Hashing:** Salted, non-reversible password encryption using `passlib[bcrypt]`.
- 🎟️ **Dual-Token JWT Architecture:**
  - Short-lived **Access Tokens** (30 min) for authorized API interactions.
  - Long-lived **Refresh Tokens** (7 days) for seamless token renewals.
- 🌐 **OAuth2 Password Flow:** Standard-compliant `/token` endpoint supporting `OAuth2PasswordRequestForm`.
- 🛡️ **Protected Routes:** FastAPI dependency injection (`Depends`) validating bearer tokens and user status.
- 👑 **Role-Based Access Control (RBAC):** Distinct permission boundaries separating standard `user` and privileged `admin` accounts.
- 🗄️ **Relational Persistence:** Database abstraction via SQLAlchemy ORM with PostgreSQL backend.
- 👥 **Admin User Management:** Search, retrieve, update user roles, change passwords, and delete user records.
- 📖 **Interactive API Documentation:** Native OpenAPI Swagger UI (`/docs`) and ReDoc (`/redoc`).

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Client
        C[🌐 Client / Browser / Swagger]
    end

    subgraph FastAPI Application
        GW[🚪 FastAPI Gateway]
        
        subgraph Security Layer
            AUTH[🔐 Auth Handlers\n/login & /token & /refresh]
            DEP[🛡️ OAuth2 Bearer Dependency\nJWT Validation]
            RBAC{👑 RBAC Guard\nrole == 'admin'?}
        end
        
        subgraph Business Logic & Endpoints
            REG[POST /register]
            PROT[GET /protected]
            ADMIN[GET /admin\nUser Management APIs]
        end
    end

    subgraph Persistence Layer
        ORM[(SQLAlchemy ORM)]
        DB[(🐘 PostgreSQL Database)]
    end

    C -->|HTTP Requests| GW
    GW --> REG
    GW --> AUTH
    GW --> DEP

    DEP -->|Authenticated User| PROT
    DEP -->|Validate Role| RBAC
    RBAC -->|Admin Granted| ADMIN
    RBAC -->|Forbidden 403/401| C

    REG -->|Bcrypt Hash & Save| ORM
    AUTH -->|Verify Hash & Issue JWT| ORM
    ADMIN -->|CRUD Users| ORM
    ORM --> DB
```

---

## 🔄 Authentication & Authorization Lifecycle

### 1. Dual-Token Refresh Sequence

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant API as FastAPI /auth
    participant DB as PostgreSQL

    Client->>API: POST /login {username, password}
    API->>DB: Fetch user by username
    DB-->>API: User record (with hashed password)
    API->>API: Verify bcrypt password hash
    API-->>Client: Returns 200 OK (access_token [30m] + refresh_token [7d])

    Note over Client,API: Access Protected Endpoints
    Client->>API: GET /protected (Bearer access_token)
    API->>API: Decode & validate signature/expiry
    API-->>Client: Returns 200 OK (Protected Data)

    Note over Client,API: When Access Token Expires (30m)
    Client->>API: GET /protected (Expired access_token)
    API-->>Client: 401 Unauthorized (Token expired)

    Client->>API: POST /refresh {refresh_token}
    API->>API: Validate refresh token signature & claims
    API-->>Client: Returns 200 OK (New access_token)
```

---

## 🛠️ Tech Stack

| Technology | Purpose | Implementation Detail |
| :--- | :--- | :--- |
| **Python** | Core Language | Python 3.9+ |
| **FastAPI** | Web Framework | Async endpoints, dependency injection, auto OpenAPI docs |
| **Uvicorn** | ASGI Web Server | High-performance asynchronous runtime |
| **SQLAlchemy** | Database ORM | Declarative models, session lifecycle, and transaction management |
| **PostgreSQL** | Relational Database | ACID-compliant persistent user storage |
| **Psycopg2** | PostgreSQL Driver | Native DBAPI driver for Python |
| **Python-Jose / PyJWT** | Token Generation | Cryptographic HMAC-SHA256 (HS256) signing & claim decoding |
| **Passlib (Bcrypt)** | Password Hashing | Automated salting and cryptographic hashing |
| **OAuth2** | Auth Flow Standard | `OAuth2PasswordBearer` and `OAuth2PasswordRequestForm` integration |
| **Pydantic** | Data Validation | Request body schemas, email/password validation, response serialization |
| **Python-Dotenv** | Configuration | Environment-based secret and credential isolation |

---

## 📁 Project Structure

```text
secure-authentication-api/
│
├── main.py              # FastAPI application, route declarations, and lifecycle
├── security.py          # Password hashing utilities, JWT encoder/decoder, auth dependencies
├── database.py          # SQLAlchemy engine, session maker, and DB dependency injection
├── models.py            # Relational database models (User table definitions)
├── schemas.py           # Pydantic models for request/response serialization & validation
│
├── requirements.txt     # Pinned Python package dependencies
├── .env.example         # Template for environment variables (committed to Git)
├── .env                 # Local secrets and connection strings (ignored by Git)
├── .gitignore           # Excludes virtualenv, bytecode, and sensitive .env files
└── README.md            # Comprehensive project documentation
```

---

## ⚙️ Setup & Installation

### 1. Clone the Repository
```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd secure-authentication-api
```

### 2. Configure Python Virtual Environment
```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows (Command Prompt / PowerShell)
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in the root directory based on the `.env.example` template:

```bash
cp .env.example .env
```

Define the required parameters:

```ini
# PostgreSQL Database Connection String
DATABASE_URL=postgresql://username:password@localhost:5432/secure_auth_db

# Cryptographic JWT Secret & Algorithm
SECRET_KEY=super_secret_random_64_character_hex_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

> ⚠️ **Security Warning:** Never commit `.env` or production credentials to GitHub. Always keep `.env` in `.gitignore`.

---

## ▶️ Running the Application

### 1. Ensure PostgreSQL is Active
Make sure your PostgreSQL instance is running and the database specified in `DATABASE_URL` exists.

### 2. Start the Uvicorn ASGI Server
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Access Interactive Documentation
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📡 API Endpoints & Usage

### 🔐 Authentication Endpoints

#### 1. Register User
- **Endpoint:** `POST /register`
- **Description:** Creates a new user account with hashed password storage.
- **Request Body:**
```json
{
  "username": "vijay",
  "password": "StrongPassword@123"
}
```
- **Response (`201 Created`):**
```json
{
  "id": 1,
  "username": "vijay",
  "role": "user",
  "created_at": "2026-09-29T10:00:00"
}
```

#### 2. User Login
- **Endpoint:** `POST /login`
- **Description:** Verifies credentials and issues dual Access + Refresh tokens.
- **Request Body:**
```json
{
  "username": "vijay",
  "password": "StrongPassword@123"
}
```
- **Response (`200 OK`):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer"
}
```

#### 3. OAuth2 Password Flow
- **Endpoint:** `POST /token`
- **Content-Type:** `application/x-www-form-urlencoded`
- **Body Fields:** `username=vijay&password=StrongPassword@123`
- **Response (`200 OK`):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 4. Refresh Access Token
- **Endpoint:** `POST /refresh`
- **Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```
- **Response (`200 OK`):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer"
}
```

---

### 🛡️ Protected & Administrative Endpoints

| Method | Endpoint | Authorization | Purpose |
| :--- | :--- | :--- | :--- |
| `GET` | `/protected` | `Bearer <access_token>` | Test authenticated user access |
| `GET` | `/admin` | `Bearer <admin_token>` | Test privileged administrative access |
| `GET` | `/users` | `Bearer <admin_token>` | Retrieve user lists or search by query |
| `GET` | `/users/{id}` | `Bearer <admin_token>` | Retrieve single user record by ID |
| `GET` | `/search-users` | `Bearer <admin_token>` | Search users by specific filters |
| `PATCH` | `/update-role/{id}` | `Bearer <admin_token>` | Promote/demote a user (`user` ⇄ `admin`) |
| `PATCH` | `/password-update/` | `Bearer <access_token>` | Update authenticated user's password |
| `DELETE` | `/user-delete/{id}` | `Bearer <admin_token>` | Permanently remove user record |

---

## 🎟️ JWT & Refresh Token Mechanics

### Token Payload Structure
The issued JWT contains standard cryptographic claims along with application identity:

```json
{
  "sub": "1",
  "username": "vijay",
  "role": "user",
  "type": "access",
  "exp": 1790680000
}
```

### Dual-Token Security Model
1. **Access Token Lifespan (30 Minutes):**
   - Transmitted in HTTP headers: `Authorization: Bearer <access_token>`.
   - Evaluated statelessly without frequent database lookups.
   - Limited lifespan drastically reduces the window of vulnerability if intercepted.
2. **Refresh Token Lifespan (7 Days):**
   - Transmitted strictly to the `/refresh` endpoint when an access token expires.
   - Restores API access without forcing the user to re-enter credentials.

---

## 👑 Role-Based Access Control (RBAC)

The API enforces strict permission tiers using FastAPI dependencies:

```mermaid
flowchart TD
    REQ[HTTP Request] --> TOK{Valid Bearer JWT?}
    TOK -->|No / Invalid| E401[❌ 401 Unauthorized]
    TOK -->|Yes| USER{Resolve Current User}
    
    USER --> ROUTE{Requested Route}
    ROUTE -->|/protected| POK[✅ Access Granted]
    
    ROUTE -->|/admin & Admin APIs| CHK{User.role == 'admin'?}
    CHK -->|No| E403[⛔ 403 Forbidden / Access Denied]
    CHK -->|Yes| AOK[✅ Admin Access Granted]
```

### Dependency Implementation Pattern
```python
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Validates token signature, expiration, and resolves user record
    ...

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
```

---

## 🧪 Testing & Verification Guide

The entire API surface can be verified through Swagger UI (`http://127.0.0.1:8000/docs`) or `curl`:

<details open>
<summary><b>Click to expand validation test cases</b></summary>

| # | Test Scenario | Steps | Expected Result | Status |
| :---: | :--- | :--- | :--- | :---: |
| **01** | User Registration | Send `POST /register` with username and password | Returns `201 Created` with user ID | ✅ Passed |
| **02** | Successful Login | Send `POST /login` with registered credentials | Returns `200 OK` with Access & Refresh tokens | ✅ Passed |
| **03** | Invalid Login | Send `POST /login` with bad password | Returns `401 Unauthorized` | ✅ Passed |
| **04** | Protected Endpoint (No Auth) | Call `GET /protected` without header | Returns `401 Unauthorized` (`Not authenticated`) | ✅ Passed |
| **05** | Protected Endpoint (With Auth) | Authorize Swagger with Bearer token & call `GET /protected` | Returns `200 OK` with user payload | ✅ Passed |
| **06** | Admin Access (Regular User) | Call `GET /admin` with standard `user` token | Returns `403 Forbidden` (`Admin access required`) | ✅ Passed |
| **07** | Admin Access (Admin User) | Call `GET /admin` with `admin` role token | Returns `200 OK` (`Welcome Admin`) | ✅ Passed |
| **08** | Refresh Token Flow | Submit valid refresh token to `POST /refresh` | Returns `200 OK` with new access token | ✅ Passed |
| **09** | OAuth2 Password Form | Submit form data to `POST /token` | Returns `200 OK` with Bearer access token | ✅ Passed |
| **10** | Expiration Lifetimes | Verify token timestamps (`exp`) | Access token = 30 min, Refresh token = 7 days | ✅ Passed |

</details>

---

## 🎥 Project Demonstration Guide

When recording or presenting a walkthrough of this project, follow this structured narrative:

1. **Architecture & Schema Overview:** Introduce FastAPI, PostgreSQL, SQLAlchemy ORM, and bcrypt password hashing.
2. **User Onboarding:** Demonstrate `POST /register` and inspect the database to prove password salt and hash (no plaintext storage).
3. **Login & Dual Token Generation:** Execute `POST /login` to display the Access Token and Refresh Token payloads.
4. **Protected Route Verification:**
   - Attempt `GET /protected` unauthenticated → Demonstrate `401 Unauthorized`.
   - Attach the Bearer token in Swagger → Demonstrate `200 OK`.
5. **RBAC Demonstration:**
   - Call `GET /admin` as standard user → Show `403 Forbidden`.
   - Update user role to `admin` in database or via `/update-role/{id}`.
   - Re-authenticate and call `GET /admin` → Show `200 OK`.
6. **Token Refresh Lifecycle:** Submit the refresh token to `POST /refresh` and use the resulting new access token to continue making authenticated requests.
7. **FastAPI OAuth2 Standard:** Show native integration with Swagger's **Authorize** button using the `/token` endpoint.

---

## 🔒 Security Practices & Implementation

- 🛡️ **No Plaintext Passwords:** Passwords are mathematically transformed using salted bcrypt hashing prior to SQL insertion.
- ⏳ **Limited Token Exposure:** 30-minute access token limit bounds the blast radius of compromised tokens.
- 🔑 **Cryptographic Signing:** HS256 algorithm with 256-bit secret key validates token authenticity and prevents tampering.
- 🧱 **Least Privilege Enforcement:** Strict separation between standard user capabilities and administrative APIs.
- ⚙️ **Strict Environment Isolation:** No hardcoded database credentials or keys; configurations are injected at runtime via `.env`.

---

## ⚠️ Limitations & Scope

- **Logout Token Blacklisting (Bonus):**
  - **Status:** *Not Implemented.*
  - **Reason:** In standard stateless JWTs, tokens remain valid until expiration unless tracked in a fast in-memory blacklist (such as Redis). This project maintains stateless tokens without Redis infrastructure dependencies.

---

## 📚 Learning Outcomes

Through building and testing this project, the following core software engineering competencies were developed:
- Implementing clean RESTful authentication patterns in **FastAPI**.
- Structuring relational database operations using **SQLAlchemy** models, engines, and sessions.
- Generating, validating, and signing **JSON Web Tokens (JWT)**.
- Implementing the official **OAuth2 Password Bearer** specification.
- Engineering granular **Role-Based Access Control** via reusable dependency injection.
- Managing database connections and configuration securely through environment variables.
- Performing API validation and end-to-end regression testing via Swagger UI.

---

## 🔮 Future Improvements

- [ ] Implement token revocation/blacklist using **Redis** key-value TTLs.
- [ ] Add email verification on registration using background tasks.
- [ ] Implement rate-limiting on `/login` and `/token` endpoints (slow-down brute force attacks).
- [ ] Add automated unit and integration tests using `pytest` and `httpx`.
- [ ] Containerize application and PostgreSQL service using `docker-compose`.

---

## 👨‍💻 Author

**Vijay Rangvani**  
*Backend & AI Engineering Learner*

---

> *Built with FastAPI, PostgreSQL, and SQLAlchemy.*