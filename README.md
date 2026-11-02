# AI Placement Copilot

AI-powered resume analysis, job matching, learning roadmaps, and adaptive
Gemini-powered skill assessments.

## Project structure

```text
.
├── backend/       FastAPI API, authentication, MongoDB adapter, and services
├── frontend/      React + TypeScript + Vite web application
├── db/            MongoDB setup and database documentation
└── .github/       Repository automation and modernization configuration
```

## Requirements

- Python 3.12+
- Node.js 20+
- MongoDB 7+
- A Gemini API key for AI-generated assessment questions

## Run locally

### 1. Configure the backend

```powershell
cd backend
Copy-Item .env.example .env
```

Set `GEMINI_API_KEY`, `SECRET_KEY`, and Google OAuth values in
`backend/.env`. Never commit `.env`.

### 2. Start the backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

The API runs at `http://127.0.0.1:8000`.

### 3. Start the frontend

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

The web app runs at `http://127.0.0.1:5173`.

## GitHub safety

Commit source code, dependency manifests, and `.env.example` files only.
Do not commit API keys, OAuth secrets, virtual environments, `node_modules`,
build output, uploaded resumes, or database dumps.
