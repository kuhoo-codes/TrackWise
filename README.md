# 🚀 TrackWise

**TrackWise** is a timeline-based portfolio and personal achievement tracker that brings storytelling and introspection into professional representation. Unlike static resumes, TrackWise allows users to chronologically organize their projects, experiences, milestones, and reflections—giving depth, context, and continuity to their journey.

It's ideal as:
- A public-facing **portfolio**,
- A private **progress tracker**, or
- A smart **resume generator** with upcoming GitHub/LinkedIn/Notion integrations.

## Project Structure

```
TrackWise/
├── api/            # Backend (FastAPI)
└── client/         # Frontend (React + Vite)
```

## Prerequisites

- Node.js 16 or higher
- PostgreSQL

## Setup

1. To initialize both the backend and frontend environments, run:
```bash
sh ./tools/init
```

## Backend Setup

1. Navigate to the backend directory:
```bash
cd api
```

2. Activate the virtual environment:
On macOS/Linux:
```bash
source .venv/bin/activate
```

On Windows:
```bash
.\.venv\Scripts\activate
```

3. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

The backend will be running at http://localhost:8000

API Documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Frontend Setup

1. Navigate to the frontend directory:
```bash
cd client
```

2. Start the development server:
```bash
pnpm run dev
```

The frontend will be running at http://localhost:5173

## Database

The application uses PostgreSQL as its database. Make sure you have PostgreSQL installed and running on your system.
