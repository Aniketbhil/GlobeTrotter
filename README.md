# GlobeTrotter 🌍

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-0.141.1+-009688?style=flat&logo=fastapi&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16--alpine-4169E1?style=flat&logo=postgresql&logoColor=white) ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F0E?style=flat&logo=sqlalchemy&logoColor=white) ![Alembic](https://img.shields.io/badge/Alembic-1.19+-6C757D?style=flat) ![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white) ![React](https://img.shields.io/badge/React-19.2-61DAFB?style=flat&logo=react&logoColor=black) ![Vite](https://img.shields.io/badge/Vite-8.2-646CFF?style=flat&logo=vite&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-ES--Modules-F7DF1E?style=flat&logo=javascript&logoColor=black) ![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4.3-06B6D4?style=flat&logo=tailwindcss&logoColor=white) ![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=flat&logo=jsonwebtokens&logoColor=white) ![uv](https://img.shields.io/badge/uv-Package_Manager-DE5E57?style=flat) ![Zustand](https://img.shields.io/badge/Zustand-5.0-443E38?style=flat) ![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

GlobeTrotter is a full-stack multi-city travel planning platform that combines a Python FastAPI backend built with a modular vertical-slice architecture and PostgreSQL database with a React 19 single-page frontend styled with Tailwind CSS v4. The system enables users to create and manage multi-destination travel itineraries, discover cities and activities, build day-by-day travel schedules, calculate estimated category expenses with custom per-stop budget overrides, visualize trip timelines on a month calendar, upload profile and trip cover images, and publish public read-only share links that other registered users can clone directly into their accounts. It also provides a dedicated administration interface for tracking platform statistics, popular destinations, and user activity.

---

## 🛠️ Tech Stack

| Domain | Technology / Library | Version / Requirement | Role & Purpose |
| :--- | :--- | :--- | :--- |
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) | `>= 0.141.1` | High-performance asynchronous REST API framework |
| **Python Runtime** | Python | `>= 3.12` | Programming language for backend API services |
| **Package Manager** | [uv](https://github.com/astral-sh/uv) | Latest | Modern, fast Python package and virtual environment manager |
| **Database** | PostgreSQL | `16-alpine` | Relational database engine run via Docker Compose |
| **ORM** | [SQLAlchemy](https://www.sqlalchemy.org/) | `>= 2.0.52` | Relational database mapping and query engine |
| **Migrations** | [Alembic](https://alembic.sqlalchemy.org/) | `>= 1.19.1` | Database schema migration management |
| **Authentication & Security** | Passlib (bcrypt) & Python-Jose | Passlib `>= 1.7.4`, Jose `>= 3.5.0` | Password hashing and JWT Bearer token generation/validation |
| **Data Validation** | Pydantic & Pydantic Settings | Pydantic `>= 2.13.4` | Request/response schema validation & environment configuration |
| **Frontend UI** | [React](https://react.dev/) | `^19.2.8` | Declarative UI component framework (JSX) |
| **Build Tool** | [Vite](https://vitejs.dev/) | `^8.2.0` | Fast frontend dev server and production builder |
| **Styling** | [Tailwind CSS](https://tailwindcss.com/) | `^4.3.3` | Utility-first CSS framework using custom theme variables |
| **State Management** | [Zustand](https://zustand-demo.pmnd.rs/) | `^5.0.15` | Lightweight client state management for auth and theme |
| **Form & Validation** | React Hook Form & Zod | Form `^7.86.0`, Zod `^3.25.76` | Client-side form handling and validation schemas |
| **HTTP Client** | Axios | `^1.19.0` | Client-side REST API calls with JWT request interceptors |
| **Icons** | Lucide React | `^1.33.0` | Modern SVG icon set |

---

## 📂 Project Structure

GlobeTrotter is organized as a monorepo containing two decoupled projects: `globetrotter-backend/` and `globetrotter-frontend/`.

```text
GlobeTrotter/
├── README.md                      # Master monorepo documentation
├── globetrotter-backend/           # FastAPI backend service
│   ├── README.md                  # Backend quickstart guide
│   ├── pyproject.toml             # Python dependencies and tool settings
│   ├── docker-compose.yaml        # PostgreSQL 16 & pgAdmin services
│   ├── alembic.ini                # Alembic migration configuration
│   ├── seed_data/                 # CSV reference data (cities.csv, activities.csv)
│   ├── migrations/                # Alembic migration scripts
│   └── app/                       # Application root (Vertical Slice Architecture)
│       ├── main.py                # FastAPI app initialization, middleware, routes
│       ├── core/                  # Core config, DB session, security, storage
│       ├── common/                # Base schemas, exception handlers, pagination
│       ├── scripts/               # Operational scripts (seed_reference_data.py)
│       └── features/              # Modular feature slices
│           ├── activities/        # Reference activities lookup & admin CRUD
│           ├── admin/             # System overview stats, top metrics, user management
│           ├── auth/              # Signup, login, password reset, profile & avatar
│           ├── budget/            # Category cost calculations & per-stop overrides
│           ├── cities/            # Reference cities search, pagination & admin CRUD
│           ├── itinerary/         # Day-wise itinerary assembler & calendar view
│           ├── sharing/           # Public share link creation & trip cloning
│           ├── stops/             # Trip stops management & sequence reordering
│           ├── trip_activities/   # Scheduling activities inside stops & reordering
│           ├── trips/             # Trip CRUD, status filtering & cover photo upload
│           └── users/             # User resource routes
└── globetrotter-frontend/          # React 19 + Vite single-page application
    ├── README.md                  # Frontend quickstart guide
    ├── package.json               # Node.js dependencies and npm scripts
    ├── vite.config.js             # Vite development server configuration
    ├── index.html                 # Application HTML entry point
    └── src/                       # Frontend source files (React JSX)
        ├── main.jsx               # React DOM root entry point
        ├── App.jsx                # Application router configuration & routes
        ├── config/                # Axios instance configuration (api.js)
        ├── store/                 # Zustand stores (authStore.js, themeStore.js)
        ├── styles/                # Tailwind CSS v4 design tokens and theme CSS
        ├── components/            # Shared UI components (Button, Card, Input, Modal, Badge, Layout)
        └── features/              # Feature-based pages and API client handlers
            ├── admin/             # Admin dashboard page & admin API client
            ├── auth/              # Login, Signup, Forgot/Reset Password pages
            ├── budget/            # Trip budget breakdown page & budget API client
            ├── calendar/          # Trip calendar page & calendar API client
            ├── explore/           # City and activity discovery search page
            ├── itinerary/         # Itinerary builder, stop/activity modals & API client
            ├── profile/           # User profile management page
            ├── sharing/           # Public shared itinerary viewer page & share modals
            └── trips/             # Dashboard, Create Trip, My Trips pages & API client
```

---

## 📋 Prerequisites

Ensure the following runtimes and tools are installed on your host machine:

- **Python**: `3.12` or higher
- **uv**: Fast Python package manager ([installation instructions](https://github.com/astral-sh/uv))
- **Node.js**: `18.0` or higher (with `npm`)
- **Docker & Docker Compose**: For running local PostgreSQL and pgAdmin containers

---

## ⚙️ Setup & Installation

Follow these steps in order to set up and run both backend and frontend services locally.

### 1. Backend Setup

Open a terminal and navigate to the backend folder:

```bash
cd globetrotter-backend
```

#### Environment Configuration

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

The application settings defined in `app/core/config.py` accept the following environment variables:

| Variable | Description | Default Value |
| :--- | :--- | :--- |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg://globetrotter:globetrotter@localhost:5432/globetrotter` |
| `JWT_SECRET_KEY` | Secret key used for signing JWT tokens | `change-me-in-production` |
| `JWT_ALGORITHM` | Algorithm for signing JWTs | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token validity duration in minutes | `60` |
| `ENVIRONMENT` | Deployment environment (`development` or `production`) | `development` |
| `UPLOAD_DIR` | Directory for uploaded profile/cover photos | `uploads/photos` |
| `MAX_UPLOAD_SIZE_MB` | Maximum allowed upload size in MB | `5` |
| `PUBLIC_BASE_URL` | Base public URL of backend service | `http://localhost:8000` |
| `TRANSPORT_COST_MULTIPLIER` | Estimated travel transport cost multiplier | `15.0` |
| `STAY_COST_MULTIPLIER` | Estimated accommodation stay cost multiplier | `25.0` |
| `MEAL_COST_PER_DAY` | Estimated daily meal expense multiplier | `30.0` |
| `ADMIN_EMAIL` | Optional initial admin email for automatic user creation | *None* |
| `ADMIN_PASSWORD` | Optional initial admin password for automatic user creation | *None* |

#### Start Database Services

Spin up PostgreSQL 16 and pgAdmin 4 containers:

```bash
docker compose up -d
```

- **PostgreSQL**: Accessible at `localhost:5432` (User: `globetrotter`, Password: `globetrotter`, Database: `globetrotter`)
- **pgAdmin**: Accessible at `http://localhost:5050` (Email: `admin@globetrotter.local`, Password: `admin`)

#### Database Migrations & Reference Data Seeding

Apply Alembic database migrations:

```bash
uv run alembic upgrade head
```

Seed initial reference cities and activities into PostgreSQL:

```bash
uv run python -m app.scripts.seed_reference_data
```

> **Note on Seeding & Admin Bootstrap**: 
> - The reference data seed script reads `seed_data/cities.csv` and `seed_data/activities.csv` and is idempotent (updates existing records, inserts new ones).
> - On backend server startup, if `ADMIN_EMAIL` and `ADMIN_PASSWORD` are configured in `.env`, an administrative user account is automatically bootstrapped if it does not already exist.

#### Start Backend Server

Run the FastAPI development server with live reload:

```bash
uv run uvicorn app.main:app --reload
```

The API server runs at `http://localhost:8000`. You can inspect the health check at `http://localhost:8000/health` or open the interactive OpenAPI docs at `http://localhost:8000/docs`.

---

### 2. Frontend Setup

Open a separate terminal window and navigate to the frontend directory:

```bash
cd globetrotter-frontend
```

#### Install Dependencies

Install Node.js packages via `npm`:

```bash
npm install
```

#### API Configuration

The frontend API client (`src/config/api.js`) defaults to connecting to the backend at `http://localhost:8000`. Ensure the backend server is running before launching the dev server.

#### Start Development Server

Run the Vite development server:

```bash
npm run dev
```

The frontend application will be accessible at `http://localhost:5173`.

---

## 📡 API Endpoint Reference

The backend API routes are structured around vertical feature slices:

### Authentication (`/api/auth`)
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/signup` | Public | Register a new user account |
| `POST` | `/api/auth/login` | Public | Authenticate user and receive Bearer JWT |
| `POST` | `/api/auth/forgot-password` | Public | Request password reset token |
| `POST` | `/api/auth/reset-password` | Public | Reset password using valid token |
| `GET` | `/api/auth/me` | Authenticated | Fetch authenticated user profile |
| `PATCH` | `/api/auth/me` | Authenticated | Update user profile information |
| `DELETE` | `/api/auth/me` | Authenticated | Permanently delete user account |
| `POST` | `/api/auth/me/photo` | Authenticated | Upload user profile photo |
| `DELETE` | `/api/auth/me/photo` | Authenticated | Delete user profile photo |

### Reference Cities (`/api/cities`)
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/cities` | Authenticated | Search, filter, and list paginated cities |
| `GET` | `/api/cities/{city_id}` | Authenticated | Retrieve city details |
| `POST` | `/api/cities` | Admin Only | Create a new reference city |
| `PATCH` | `/api/cities/{city_id}` | Admin Only | Update city information |
| `DELETE` | `/api/cities/{city_id}` | Admin Only | Delete reference city |

### Reference Activities (`/api/activities`)
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/activities` | Authenticated | Search, filter, and list paginated activities |
| `GET` | `/api/activities/{activity_id}` | Authenticated | Retrieve activity details |
| `POST` | `/api/activities` | Admin Only | Create a new reference activity |
| `PATCH` | `/api/activities/{activity_id}` | Admin Only | Update activity details |
| `DELETE` | `/api/activities/{activity_id}` | Admin Only | Delete reference activity |

### Trips (`/api/trips`)
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/trips` | Authenticated | Create a new trip |
| `GET` | `/api/trips` | Authenticated | List user trips (flat or grouped by status) |
| `GET` | `/api/trips/{trip_id}` | Authenticated | Get full trip details with stops and budget summary |
| `PATCH` | `/api/trips/{trip_id}` | Authenticated | Update trip title, dates, or description |
| `DELETE` | `/api/trips/{trip_id}` | Authenticated | Delete trip and all related stops/activities |
| `POST` | `/api/trips/{trip_id}/cover-photo` | Authenticated | Upload trip cover photo |
| `DELETE` | `/api/trips/{trip_id}/cover-photo` | Authenticated | Remove trip cover photo |

### Trip Stops (`/api/trips/{trip_id}/stops`)
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/trips/{trip_id}/stops` | Authenticated | Add a city stop to a trip |
| `GET` | `/api/trips/{trip_id}/stops` | Authenticated | List all stops for a trip in order |
| `GET` | `/api/trips/{trip_id}/stops/{stop_id}` | Authenticated | Get stop details |
| `PATCH` | `/api/trips/{trip_id}/stops/{stop_id}` | Authenticated | Update stop travel dates |
| `DELETE` | `/api/trips/{trip_id}/stops/{stop_id}` | Authenticated | Delete stop from trip |
| `PATCH` | `/api/trips/{trip_id}/stops/reorder` | Authenticated | Reorder stop sequence numbers |

### Trip Activities (`/api/trips/{trip_id}/stops/{stop_id}/activities`)
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `.../activities` | Authenticated | Schedule an activity within a stop |
| `GET` | `.../activities` | Authenticated | List stop activities grouped chronologically by day |
| `GET` | `.../activities/{trip_activity_id}` | Authenticated | Get scheduled activity details |
| `PATCH` | `.../activities/{trip_activity_id}` | Authenticated | Update activity custom date/time/cost |
| `DELETE` | `.../activities/{trip_activity_id}` | Authenticated | Remove activity from stop |
| `PATCH` | `.../activities/reorder` | Authenticated | Reorder activities schedule |

### Trip Budget & Overrides (`/api/trips`)
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/trips/{trip_id}/budget` | Authenticated | Get full category breakdown, per-stop costs & alerts |
| `PUT` | `/api/trips/{trip_id}/stops/{stop_id}/budget-override` | Authenticated | Upsert custom budget override for a stop |

### Itinerary & Calendar (`/api/trips`)
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/trips/{trip_id}/itinerary` | Authenticated | Retrieve day-wise structured itinerary plan |
| `GET` | `/api/trips/calendar` | Authenticated | Retrieve month calendar view of scheduled stops/activities |

### Sharing (`/api`)
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/trips/{trip_id}/share` | Authenticated | Publish trip and generate public share slug |
| `DELETE` | `/api/trips/{trip_id}/share` | Authenticated | Unpublish trip share link |
| `GET` | `/api/public/itinerary/{slug}` | Public | View public read-only shared trip itinerary |
| `POST` | `/api/public/itinerary/{slug}/copy` | Authenticated | Clone shared trip into current user's account |

### System Administration (`/api/admin`)
| Method | Endpoint | Access | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/admin/stats/overview` | Admin Only | View system-wide counts (users, trips, shares) |
| `GET` | `/api/admin/stats/top-cities` | Admin Only | View top visited cities metrics |
| `GET` | `/api/admin/stats/top-activities` | Admin Only | View top scheduled activities metrics |
| `GET` | `/api/admin/stats/users` | Admin Only | Search and list paginated user accounts |
| `GET` | `/api/admin/stats/users/{user_id}/trips` | Admin Only | View all trips belonging to a specific user |

---

## 🧪 Running Tests

### Backend Unit & Integration Tests

The backend test suite is built using `pytest` and `pytest-asyncio`, with test files organized alongside each feature slice.

Run the test suite from `globetrotter-backend/`:

```bash
uv run pytest
```

### Frontend Code Quality

The frontend uses ESLint to enforce code style and formatting across JSX files.

Run code linting from `globetrotter-frontend/`:

```bash
npm run lint
```

---

## 📌 Implementation Notes & Known Limitations

- **Frontend Codebase Format**: The frontend is implemented in React 19 JSX (`.jsx`) using standard ES modules and Zustand state management.
- **Frontend API Base URL**: `src/config/api.js` points directly to `http://localhost:8000`. For custom host or deployment setup, update the `baseURL` property in `src/config/api.js`.
- **Password Reset Delivery**: Password reset token generation via `POST /api/auth/forgot-password` records reset tokens in the database, but email dispatch is mocked locally.
- **Static File Storage**: Uploaded user avatars and trip cover photos are saved locally to `uploads/photos/`.
- **Frontend Testing**: Automated linting is configured via `npm run lint`; unit/integration test runners (Vitest/Jest) are not included.

---

## 📝 Version Control Note

Version control operations (git repository initialization, commits, branching, and remote synchronization) are managed manually by the project maintainer. Setup and build scripts do not perform automated git commands.

---

## 📄 License

This project is licensed under the terms of the MIT License. See the [LICENSE](LICENSE) file for details.
