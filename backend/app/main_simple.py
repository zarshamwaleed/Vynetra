from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Vynetra", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"name": "Vynetra", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/v1/health")
async def api_health():
    return {"status": "healthy", "services": {"api": "ok"}}
