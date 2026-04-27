
# Resume RAG

This project now runs as a strict two-tier app:

- FastAPI backend
- React (Vite) frontend

## Setup

1. Create and activate a Python virtual environment.
2. Install backend dependencies.
3. Start Qdrant.
4. Run backend and frontend separately.

## Backend

Install dependencies:

```bash
pip install -r requirements.txt
```

Run API server:

```bash
python server.py
```

The backend starts on `http://localhost:5000`.

## Frontend

From the `frontend` folder:

```bash
npm install
npm run dev
```

The frontend dev server starts on Vite's default local URL.

## Qdrant

Create local data folder:

```bash
mkdir qdrant_data
```

Start Qdrant with Docker:

```bash
docker run -d -p 6333:6333 -v $(pwd)/qdrant_data:/qdrant/storage qdrant/qdrant
```

Dashboard:

```text
http://localhost:6333/dashboard
```
