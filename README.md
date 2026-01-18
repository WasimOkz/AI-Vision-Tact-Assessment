<<<<<<< HEAD
# AI-Vision-Tact-Assessment
=======
# AI Candidate Assessment Platform

A production-grade, multi-agent AI system for conducting intelligent candidate assessments through chat and voice-based interviews.

![Architecture](https://img.shields.io/badge/Architecture-Multi--Agent-blue)
![Backend](https://img.shields.io/badge/Backend-FastAPI-green)
![Frontend](https://img.shields.io/badge/Frontend-Next.js-black)
![AI](https://img.shields.io/badge/AI-LangGraph-purple)

## 🎯 Overview

This platform revolutionizes the hiring process with:
- **Multi-Agent AI System**: 5 specialized agents for comprehensive assessment
- **Chat-Based Interviews**: Real-time WebSocket communication
- **Voice Interviews**: STT → LLM → TTS pipeline with avatar
- **HR Dashboard**: Complete candidate management and decision tracking

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js)                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────┐ │
│  │  Landing    │ │  Candidate  │ │    Chat     │ │    HR      │ │
│  │    Page     │ │    Form     │ │  Interview  │ │ Dashboard  │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────────┘ │
│                              │                                   │
│                    WebSocket / REST API                         │
└─────────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────────┐
│                       BACKEND (FastAPI)                          │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                        API Routers                          ││
│  │  /candidates  │  /assessment  │  /voice  │  /hr            ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    WebSocket Handlers                       ││
│  │         Chat Handler         │       Voice Handler          ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────────┐
│                    AI LAYER (LangGraph)                          │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌──────────────────┐ │
│  │  Profile  │ │ Technical │ │Behavioral │ │   Evaluation     │ │
│  │ Analyzer  │ │Interviewer│ │Interviewer│ │     Agent        │ │
│  └───────────┘ └───────────┘ └───────────┘ └──────────────────┘ │
│                        ↓                                        │
│                 ┌──────────────┐                                │
│                 │  HR Handoff  │ ← Human-in-the-Loop            │
│                 └──────────────┘                                │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API Key

### Option 1: Docker (Recommended)

```bash
# Clone and setup
cd "Vision Tact Assesment"

# Create .env file
cp backend/.env.example backend/.env
# Edit .env and add your OPENAI_API_KEY

# Run with Docker
docker-compose up --build
```

### Option 2: Manual Setup

#### Backend
```bash
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🤖 Multi-Agent System

### Agent Descriptions

| Agent | Purpose |
|-------|---------|
| **Profile Analyzer** | Analyzes candidate's LinkedIn, GitHub, and resume data |
| **Technical Interviewer** | Conducts technical assessment with adaptive questions |
| **Behavioral Interviewer** | STAR method behavioral interview |
| **Evaluation Agent** | Generates comprehensive assessment reports |
| **HR Handoff Agent** | Manages human-in-the-loop transitions |

### State Machine Flow

```
Profile Analysis → Technical Interview → Behavioral Interview → Evaluation → HR Review
```

## 📁 Project Structure

```
Vision Tact Assesment/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Configuration
│   │   ├── routers/             # API endpoints
│   │   │   ├── candidates.py    # Candidate CRUD
│   │   │   ├── assessment.py    # Assessment sessions
│   │   │   ├── voice.py         # Voice endpoints
│   │   │   └── hr.py            # HR dashboard
│   │   ├── agents/              # LangGraph agents
│   │   │   ├── orchestrator.py  # Agent coordination
│   │   │   ├── profile_analyzer.py
│   │   │   ├── technical_interviewer.py
│   │   │   ├── behavioral_interviewer.py
│   │   │   ├── evaluation.py
│   │   │   └── hr_handoff.py
│   │   ├── services/            # Business logic
│   │   │   ├── ingestion.py     # Data ingestion
│   │   │   ├── knowledge_base.py
│   │   │   ├── llm_service.py
│   │   │   └── voice_service.py
│   │   ├── models/              # Pydantic models
│   │   └── websockets/          # WebSocket handlers
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx         # Landing page
│   │   │   ├── candidate/       # Candidate form
│   │   │   ├── chat/            # Chat interview
│   │   │   ├── voice/           # Voice interview
│   │   │   └── hr/              # HR dashboard
│   │   └── components/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for LLM | Yes |
| `LLM_MODEL` | LLM model to use (default: gpt-4o-mini) | No |
| `REDIS_URL` | Redis connection URL | No |
| `ELEVENLABS_API_KEY` | ElevenLabs for TTS | No |
| `DEEPGRAM_API_KEY` | Deepgram for STT | No |

## 📝 API Documentation

### Key Endpoints

- `POST /api/candidates/` - Create candidate with profile data
- `POST /api/assessment/start` - Start assessment session
- `WS /ws/chat/{session_id}` - Real-time chat WebSocket
- `WS /ws/voice/{session_id}` - Real-time voice WebSocket
- `GET /api/hr/dashboard/stats` - HR dashboard statistics
- `POST /api/hr/decision/{report_id}` - Submit HR decision

Full API documentation available at `/docs` when running the backend.

## 🔮 Features

### Implemented
- ✅ Multi-agent AI system with LangGraph-style orchestration
- ✅ Real-time chat with WebSocket
- ✅ Voice interview with STT/TTS
- ✅ HR dashboard with decision management
- ✅ Candidate profile ingestion (LinkedIn, GitHub, Resume)
- ✅ Assessment report generation
- ✅ Human-in-the-loop handoff

### Mocked Services (Documented)
- LinkedIn profile fetching (would require OAuth in production)
- GitHub profile fetching (mock data provided)
- Avatar lip-sync animation (static avatar with states)

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

## 📊 Evaluation Criteria Coverage

| Area | Weight | Implementation |
|------|--------|----------------|
| System Design & Architecture | 25% | Modular FastAPI + Next.js, clean separation |
| Multi-Agent Implementation | 25% | 5 agents with LangGraph orchestration |
| Real-Time Voice + Avatar | 20% | WebSocket STT/TTS with avatar states |
| Code Quality & Modularity | 15% | Type-safe, documented, reusable |
| UI/UX | 10% | Modern glassmorphism design |
| Documentation | 5% | Comprehensive README + API docs |

## 👨‍💻 Author



## 📄 License

MIT License
>>>>>>> f428da25 (Initial commit)
