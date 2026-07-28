from fastapi import APIRouter
router = APIRouter()

@router.get("")
async def health_check():
    return {"status": "healthy", "services": {"api": "ok"}}

@router.get("/ping")
async def ping():
    return {"ping": "pong"}
