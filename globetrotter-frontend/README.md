# GlobeTrotter Frontend 🎨

![React](https://img.shields.io/badge/React-19.2-61DAFB?style=flat&logo=react&logoColor=black) ![Vite](https://img.shields.io/badge/Vite-8.2-646CFF?style=flat&logo=vite&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-ES--Modules-F7DF1E?style=flat&logo=javascript&logoColor=black) ![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4.3-06B6D4?style=flat&logo=tailwindcss&logoColor=white) ![Zustand](https://img.shields.io/badge/Zustand-5.0-443E38?style=flat)

React 19 single-page frontend application for **GlobeTrotter** built with Vite and Tailwind CSS v4.

For full project architecture, API endpoint reference, and overall monorepo setup, refer to the [Top-Level Monorepo README](../README.md).

---

## 🎨 Getting Started

### 1. Prerequisites
- Node.js `>= 18.0`
- `npm` package manager

### 2. Installation
Install project dependencies:

```bash
npm install
```

### 3. API Configuration
The frontend API client (`src/config/api.js`) points to `http://localhost:8000` by default. Ensure the backend FastAPI server is running.

### 4. Running Development Server
Start Vite dev server with Hot Module Replacement (HMR):

```bash
npm run dev
```

The application will open at `http://localhost:5173`.

---

## 📜 Available Scripts

- `npm run dev`: Launch development server on port 5173
- `npm run build`: Build production artifacts into `dist/`
- `npm run preview`: Preview built production app locally
- `npm run lint`: Run ESLint checks across JavaScript/JSX code

---

## 🧭 Application Routes

- `/login` - User login page
- `/signup` - New account registration
- `/forgot-password` & `/reset-password` - Password recovery flow
- `/dashboard` - Overview dashboard showing user trips and quick stats
- `/trips/new` - Create trip workflow
- `/trips/:tripId/itinerary` - Itinerary builder with stops and activity management
- `/trips/:tripId/budget` - Trip category budget breakdown & custom overrides
- `/calendar` - Month calendar timeline view of trips & activities
- `/explore` - Search and discover cities and activities
- `/profile` - Profile settings, avatar photo upload, and account deletion
- `/shared/:slug` - Public read-only itinerary viewer
- `/admin` - Platform administrative dashboard (Admin users only)
