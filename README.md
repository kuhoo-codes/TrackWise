# 🚀 TrackWise

**TrackWise** is a timeline-based portfolio and personal achievement tracker that brings storytelling and introspection into professional representation. Unlike static resumes, TrackWise allows users to chronologically organize their projects, experiences, milestones, and reflections—giving depth, context, and continuity to their journey.

It's ideal as:
- A public-facing **portfolio**,
- A private **progress tracker**, or
- A smart **resume generator** with upcoming GitHub/LinkedIn/Notion integrations.

## Project Structure

```
TrackWise/
├── api/            # FastAPI backend with PostgreSQL & Redis
├── client/         # React + Vite frontend
└── tools/          # Development scripts and utilities
```

## Prerequisites

- **Node.js** 16+ 
- **PostgreSQL** 14+
- **Redis** 8+

## Setup

1. Initialize the Project
```bash
sh ./tools/init
```
*This sets up both backend and frontend environments in one command.*

2. Start Development Servers
```bash
./tools/run-dev
```

That's it! Your application will be running at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Redis**: http://localhost:6379
- **API Documentation**: 
  - Swagger UI: http://localhost:8000/docs
  - ReDoc: http://localhost:8000/redoc

## 🔧 Manual Setup (Alternative)

If you prefer to set up components individually:

### Backend Setup
```bash
cd api
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
```

### Frontend Setup
```bash
cd client
pnpm install
pnpm run dev
```

## Database

TrackWise uses PostgreSQL for reliable data storage and Redis for caching. The initialization script handles database setup automatically, but ensure both services are running on your system.
