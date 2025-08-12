# Document Analysis & RAG System

This repository contains a Streamlit application for document analysis using RAG (Retrieval-Augmented Generation). The app allows users to upload files, query them via an LLM, summarize text, and perform simple clustering.

## Running Locally

Follow these steps to start the app on your machine:

1. (Optional) Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
3. Provide an OpenAI API key (see [Managing Secrets](#managing-secrets)).
4. Launch Streamlit:

   ```bash
   streamlit run app.py
   ```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

### Docker

If you prefer running with Docker, use:

```bash
docker-compose up --build
```

## Managing Secrets

The application expects an OpenAI API key. You can provide it in two ways:

1. **`.streamlit/secrets.toml`** – Create this file and define `OPENAI_API_KEY`:

   ```toml
   [general]
   OPENAI_API_KEY = "sk-..."
   ```

2. **Environment variable** – Set `OPENAI_API_KEY` in your environment.

Do **not** commit your actual `secrets.toml` file or any `.env` files. The provided `.gitignore` already excludes them to keep credentials private.

