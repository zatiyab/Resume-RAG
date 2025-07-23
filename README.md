<<<<<<< HEAD

# Resume RAG Documentation

## Modules Used

- `zipfile`: For creating a ZIP file of retrieved documents to send to the frontend.
- `io.BytesIO`: In-memory byte buffer that holds the ZIP file.
- `qdrant_client`: Used to initialize and interact with Qdrant vector DB — for adding, deleting, and querying vectors.
- `os`: To read and iterate over files in the `resumes/` folder.
- `langchain_cohere.ChatCohere`: LLM wrapper for Cohere Command R+ — used for generating vector payloads and answering queries.
- `dotenv.load_dotenv`: Loads API keys from a `.env` file into the environment.
- `data_processing`: Contains functions like `add_vectors`, `delete_collection`, `basic_text_normalization`, and `all_dict`.
- `metadata_filter`: Includes `generate_filter()` to create metadata filters.
- `json`: Reads and writes to a `unique.json` file that tracks unique payload values per key.
- `langchain`: Used for prompt templating and creating the main RAG chain using `Runnable` components.
- `streamlit`: Builds the frontend UI for interacting with the RAG system.
- `sentence_transformers.SentenceTransformer`: Generates embeddings for both resumes and chat history.

---

## Why These Modules?

- **Cohere Command R+**: Offers a large context window, generous free tier, and performs very well for RAG tasks.
- **Google Gemini 2.0 Flash Lite**: Fast and accurate for filter generation.
- **Qdrant Vector DB**: Uses HNSW indexing (faster than brute-force methods like FAISS’s `IndexFlatV2` or ChromaDB). Also supports self-hosting and cloud deployment.

---

## Resume RAG Setup Guide

### 1. Add Resumes

Place all resume files into the `resumes/` folder.

```
project_root/
└── resumes/
    ├── resume1.pdf
    ├── resume2.docx
    └── ...
```

---

### 2. Create `qdrant_data` Folder

Run:

```
mkdir qdrant_data
```

This folder will store your Qdrant vector database files.

---

### 3. Install Docker & Run Qdrant

Make sure Docker is installed, then run:

```
docker run -d \
  -p 6333:6333 \
  -v $(pwd)/qdrant_data:/qdrant/storage \
  qdrant/qdrant
```

This will:
- Run Qdrant in the background
- Expose the dashboard at `localhost:6333`
- Persist data in `qdrant_data`

---

### 4. Install Python Dependencies

```
pip install -r requirements.txt
```

---

### 5. Access Qdrant Dashboard

Open in your browser:

```
http://localhost:6333/dashboard
```

---

### 6. Start the App

Run the main file using:

```
streamlit run main.py
```


<!-- Command to delete things from qdrant folder -->
sudo rm -rf /home/anubhav/svn_workspace/Resume_RAG/qdrant_data/*

<!-- Command to run project from scratch --!>
python -m venv venv
source ./venv/bin/activate => windows ./venv/scripts/activate
pip install -r requirements.txt
streamlit run frontend.py
=======
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
>>>>>>> origin/hiremind-ui-initial
