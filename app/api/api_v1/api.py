from fastapi import APIRouter
from .endpoints.users import router as user_router


router = APIRouter()
router.include_router(user_router)
