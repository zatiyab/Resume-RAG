# HireMind Project Setup

To run this project, follow these steps:

## Prerequisites

* Python 3.8+
* Node.js (LTS version) & npm
* Git
* Qdrant Vector Database (running locally, default: `http://localhost:6333`)

    **To run Qdrant via Docker:**
    ```bash
    docker pull qdrant/qdrant
    docker run -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant
    ```


### Node.js Installation (If not already installed)

This project requires Node.js, which includes `npm` (Node Package Manager) and `npx`.
If you don't have Node.js installed, download the recommended LTS (Long Term Support) version from the official website:
[https://nodejs.org/en/download/current](https://nodejs.org/en/download/current)
Follow the installer instructions for your operating system. `npm` and `npx` will be installed automatically with Node.js.


## Running the Application

### 1. Backend (Python/Flask)

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Create a `.env` file in the `backend/` directory with your API keys:
    ```
    COHERE_API_KEY="YOUR_COHERE_API_KEY"
    GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
    ```
4.  Start the Flask server:
    ```bash
    python server.py
    ```
    (Server will run on `http://localhost:5000`)

### 2. Frontend (React/Vite)

1.  Open a **new terminal** and navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2.  Install Node.js dependencies:
    ```bash
    npm install
    ```
3.  Start the React development server:
    ```bash
    npm run dev
    ```
    (App will open in browser on `http://localhost:5173/`)

---

**File Location:** Is `README.md` file ko `HireMind` project ki **root directory** mein banao (jahan `backend` aur `frontend` folders hain).