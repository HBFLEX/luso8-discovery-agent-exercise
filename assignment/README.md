# Luso8 Lead Discovery Agent


This project implements a complete AI-powered lead qualification system that helps African B2B companies discover and rank potential buyers using only the provided seed dataset.

---

## Features

- FastAPI backend with LangGraph agent for lead discovery and scoring
- Strict zero-hallucination enforcement — every justification references only real fields from the seed record
- PostgreSQL persistence for discovery jobs and leads with Alembic migrations
- Next.js frontend with form submission, live polling, and results display
- Fully Dockerized setup — everything runs with a single `docker compose up --build`
- Clean, readable, and maintainable code structure

---

## Tech Stack

- **Backend**: Python 3.11 + FastAPI + LangGraph + LangChain + SQLAlchemy 2.0 + Alembic
- **Database**: PostgreSQL 16
- **Frontend**: Next.js 16 (App Router) + TypeScript + Tailwind CSS
- **LLM**: Anthropic Claude (using the provided API key)
- **Containerization**: Docker + Docker Compose

---

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- The Anthropic API key

### 1. Setup

```bash
cd assignment
```

Create a `.env` file in the root folder:

```env
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_MODEL=claude-sonnet-4-6
```

### 2. Run the Full Application

```bash
docker compose up --build
```

Once running:

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

---

## Testing

The project includes both **backend** and **frontend** test workflows that can be executed inside Docker.

### Frontend Tests

Run the Next.js / Vitest frontend test suite:

```bash
docker compose run --rm frontend-test
```

This runs:

- Component tests
- User interaction flow tests
- Discovery submission → polling → results rendering validation

---

### Backend Tests

Run the backend test suite from the server container:

```bash
docker compose run --rm backend-test
```

This validates:

- API endpoints
- Agent logic
- Lead scoring workflow
- Database interactions
- Schema validation

---

### Run All Tests

To execute frontend and backend tests together:

```bash
docker compose run --rm backend-test
docker compose run --rm frontend-test
```

---

## Project Structure

```text
assignment/
├── docker-compose.yml
├── .env
├── server/                  # FastAPI + LangGraph backend
│   ├── app/
│   │   ├── agent/           # prompts, nodes, graph
│   │   ├── api/
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── services/
│   │   ├── database.py
│   │   └── ...
│   ├── data/leads_seed.json
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/                # Next.js frontend
│   ├── app/page.tsx
│   ├── Dockerfile
│   ├── next.config.ts
│   └── ...
├── README.md
└── PROMPTS.md
```

---

## API Endpoints

### `POST /api/discovery`

Start a new discovery job.

### `GET /api/discovery/{job_id}`

Get current job status.

### `GET /api/discovery/{job_id}/leads`

Retrieve ranked leads (when status is `"done"`).

---

## How the Agent Works

1. Filters the seed dataset by target market and buyer types
2. Uses Claude to score each candidate (`0.0–1.0`) with structured JSON output
3. Generates short, factual justifications referencing only existing seed fields
4. Saves results to PostgreSQL
5. Frontend polls the job until it completes

All scoring strictly follows the task requirements:

- No invented information
- Grounded justifications only
- Uses only available seed data

---

## Notes

- Uses only the provided `leads_seed.json`
- Job processing runs synchronously inside the request *(as permitted by the task specification)*
- Database schema is managed via Alembic for consistent, reproducible deployments
