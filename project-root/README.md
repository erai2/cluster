# Unified Saju Project

## Run with Docker
```bash
docker-compose up --build
```

## Run Backend (dev)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Run Frontend (dev)
```bash
cd frontend
npm install
npm run dev
```

## Run Streamlit
```bash
cd streamlit_app
pip install -r requirements.txt
streamlit run app.py --server.address=0.0.0.0 --server.port=8501
```
