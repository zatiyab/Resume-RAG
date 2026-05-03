
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

Configure environment variables (example using `.env`):

```bash
# Example .env
DB_URL="postgresql://<user>:<password>@<host>:5432/<database>"
SECRET_KEY="your_secret_key"
COHERE_API_KEY="your_cohere_key"
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run Alembic to ensure the database schema matches the models (applies pending migrations):

```bash
alembic upgrade head
```

Create a new migration after changing models (autogenerate):

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

Run API server (backend):

```bash
python server.py
```

The backend defaults to `http://localhost:5000` unless configured otherwise.

## Frontend

From the `frontend` folder:

```bash
npm install
npm run dev
```

The frontend dev server starts on Vite's default local URL.

## Qdrant
We use Qdrant Cloud for vector storage by default. Configure the following environment variables (example `.env` entries):

```bash
# Qdrant Cloud
QDRANT_URL="https://<your-cloud-endpoint>"        # e.g. https://xyz123.qdrant.cloud
QDRANT_API_KEY="your_qdrant_api_key"
```

How to obtain credentials:

- Sign in to Qdrant Cloud and create a project/cluster.
- Copy the cluster URL and an API key (service or access key) into your `.env`.



