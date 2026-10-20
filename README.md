# AI Placement Copilot

This project consists of a FastAPI backend and a Vite+React frontend that allows users to upload a resume, parses it, extracts skills, and provides AI-powered job recommendations, skill gap analyses, and interview prep questions.

## Requirements
- Node.js (v18+)
- Python 3.12+

## Installation & Startup Commands

### 1. Backend (FastAPI)
Open a terminal in the `backend` directory.

```bash
cd backend
python -m venv venv
# Activate venv:
# Windows: .\venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```

**Start the Backend:**
```bash
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```
*The API will be running at http://127.0.0.1:8000*
*Swagger Testing UI available at: http://127.0.0.1:8000/docs*

### 2. Frontend (React + Vite)
Open a second terminal in the `frontend` directory.

```bash
cd frontend
npm install
```

**Start the Frontend:**
```bash
npm run dev
```
*The frontend will run at http://localhost:5173*

## End-to-End Testing Instructions
1. Ensure both the backend and frontend servers are running.
2. Open http://localhost:5173 in your browser.
3. Click "Choose File" and select a sample resume (e.g. a `.docx` or `.txt` file).
4. Click **Upload & Analyze**.
5. You will see the extracted details, simulated top job matches, skill gaps, and interview questions appear on the page!

## Common Error Fixes
- **CORS Error:** Ensure `backend/config.py` has `http://localhost:5173` in `BACKEND_CORS_ORIGINS`.
- **Model Download Delay:** The first time you upload a resume, the backend downloads the `sentence-transformers` model. This might take a few minutes and may cause a timeout. Check the backend console to see the download progress.
- **Port Conflicts:** Ensure ports 8000 (backend) and 5173 (frontend) are free.
