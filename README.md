# 🚀 TrackWise

**TrackWise** is a timeline-based portfolio and personal achievement tracker that brings storytelling and introspection into professional representation. Unlike static resumes, TrackWise allows users to chronologically organize their projects, experiences, milestones, and reflections—giving depth, context, and continuity to their journey.

It's ideal as:
- A public-facing **portfolio**,
- A private **progress tracker**, or
- A smart **resume generator** with upcoming GitHub/LinkedIn/Notion integrations.

## Visual Tour

### Login

<img width="1469" height="807" alt="Image" src="https://github.com/user-attachments/assets/542fa3f1-40bf-443a-96f1-4553ff75b5b6" />

### Dashboard

<img width="1470" height="809" alt="Image" src="https://github.com/user-attachments/assets/20f8138d-9fed-4615-8e46-71ffaf160b71" />

<img width="1470" height="809" alt="Image" src="https://github.com/user-attachments/assets/bbede144-54e0-4cb6-b86e-c63ee7d9a13d" />

<img width="1470" height="811" alt="Image" src="https://github.com/user-attachments/assets/c367229c-f1e9-45dc-996a-a0da516b2dcb" />

<img width="1470" height="810" alt="Image" src="https://github.com/user-attachments/assets/16140ae4-9f00-4491-bb3a-6118a306e6d2" />

### Integrations

<img width="1470" height="809" alt="Image" src="https://github.com/user-attachments/assets/cb766eb0-58b0-45c4-89c2-b9eff4295041" />

<img width="1470" height="809" alt="Image" src="https://github.com/user-attachments/assets/6a2236ca-f0ef-447f-9d32-eb2555694669" />

### Timeline

<img width="1470" height="807" alt="Image" src="https://github.com/user-attachments/assets/c4c019d2-ef97-4783-89e1-8fef7615ea22" />

<img width="1470" height="815" alt="Image" src="https://github.com/user-attachments/assets/1e4d0572-3386-4798-a0c8-b4632b04ded3" />

### Settings

<img width="1470" height="809" alt="Image" src="https://github.com/user-attachments/assets/97f7b056-2af7-4d1b-b9f9-da2a8c6ad80c" />


## Key Features
- 🏗️ Timeline Node Editor: A modular way to build and edit your achievements. Drag, drop, and refine your story.

- 🤖 AI-Powered Context: Leveraging AI to generate professional summaries and introspect on your growth.

- 🔗 GitHub Integration: Automatically sync PRs, commits, and contributions into your professional timeline.

- 🖼️ Dynamic Profile Management: High-performance avatar system using binary storage and weak ETag caching for instant load times.

- 🔒 Secure Architecture: JWT-based authentication with Redis-backed token blacklisting for secure logouts.

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
