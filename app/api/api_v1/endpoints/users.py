from fastapi import APIRouter, Request, Body, status, Depends, Header
from fastapi.responses import JSONResponse

from schemas.users import (
    UserCreate,
    UserLogin,
    UserLoginOTP,
    UserCheckOTP,
    RefreshToken,
)
from db.redis import get_redis, get_redis_email
from core.config import settings

from my_simple_jwt_auth.my_simple_jwt_auth import jwt_authentication
import jwt
import httpx
import json

router = APIRouter(prefix="/authorization")


@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def user_register(user_data: UserCreate):
    user_data_dict = user_data.model_dump()
    async with httpx.AsyncClient() as client:
        url = settings.REGISTER_URL
        response = await client.post(url, json=user_data_dict)
        response_dict = json.loads(response.text)
        if response.status_code == 201:
            data = {
                "email": user_data_dict.get("email"),
                "message": "You have been registered successfully.",
            }
            url_email = settings.EMAIL_URL 
            response = await client.post(url_email, json=data)
            return JSONResponse(response_dict)
        elif response.status_code == 400:
            return JSONResponse(response_dict, status_code=status.HTTP_400_BAD_REQUEST)
        else:
            return JSONResponse(
                {"detail": "invalid request."}, status_code=status.HTTP_400_BAD_REQUEST
            )


@router.post("/login/", status_code=status.HTTP_200_OK)
async def user_login(user_data: UserLogin):
    user_data_dict = user_data.model_dump()
    async with httpx.AsyncClient() as client:
        url = settings.LOGIN_URL
        response = await client.post(url, json=user_data_dict)
        response_dict = json.loads(response.text)
        if response.status_code == 200:
            return JSONResponse(response_dict)
        elif response.status_code == 400:
            return JSONResponse(response_dict, status_code=status.HTTP_400_BAD_REQUEST)
        else:
            return JSONResponse(
                {"message": "invalid request."}, status_code=status.HTTP_400_BAD_REQUEST
            )


