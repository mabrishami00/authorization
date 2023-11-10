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


@router.post("/login_otp/", status_code=status.HTTP_200_OK)
async def user_login_otp(user_data: UserLoginOTP):
    user_data = user_data.model_dump()
    print(user_data)
    async with httpx.AsyncClient() as client:
        url = settings.LOGIN_OTP_URL
        print(url)
        response = await client.post(url=url, json=user_data)
        response_text = json.loads(response.text)
        if response.status_code == 200:
            return JSONResponse(response_text)
        elif response.status_code == 401:
            return JSONResponse(response_text)
        else:
            return JSONResponse({"detail": "Invalid request."})


@router.post("/check_otp/", status_code=status.HTTP_200_OK)
async def user_check_otp(
    user_data: UserCheckOTP,
    redis=Depends(get_redis),
    redis_email=Depends(get_redis_email),
):
    username = user_data.username
    email = user_data.email
    otp = user_data.otp
    print(otp)
    result = await redis_email.get(email)
    result = int(result.decode("utf8"))
    print(result)
    if result == otp:
        (
            access_key,
            refresh_key,
            jti,
        ) = jwt_authentication.generate_access_and_refresh_token(
            username,
            settings.ACCESS_KEY_EXPIRE_TIME,
            settings.REFRESH_KEY_EXPIRE_TIME,
            settings.SECRET_KEY,
        )
        await redis.set(jti, username)
        return JSONResponse({"access_key": access_key, "refresh_key": refresh_key})
    else:
        return JSONResponse({"detail": "OTP is not correct."})


@router.post("/logout/", status_code=status.HTTP_200_OK)
async def user_logout(
    authorization: str = Header(default=None), redis=Depends(get_redis)
):
    try:
        username, jti = jwt_authentication.authenticate(
            authorization, settings.SECRET_KEY
        )
    except Exception as e:
        username = None
        jti = None

    result = await redis.get(jti)
    if username and result:
        await redis.delete(jti)
        return JSONResponse({"detail": "You have been logged out successfully."})
    else:
        return JSONResponse({"detail": "You are not logged in."})


@router.post("/logout_all/", status_code=status.HTTP_200_OK)
async def user_logout_all(
    authorization: str = Header(default=None), redis=Depends(get_redis)
):
    try:
        username, jti = jwt_authentication.authenticate(
            authorization, settings.SECRET_KEY
        )
    except Exception as e:
        username = None
        jti = None

    jtis = await redis.keys()
    for jti in jtis:
        username_redis = await redis.get(jti)
        if username_redis.decode("utf8") == username:
            await redis.delete(jti)
    return JSONResponse({"detail": "All accounts have been logged out."})


@router.post("/get_new_refresh_token/")
async def user_get_new_refresh_token(
    refresh_token: RefreshToken = Body(default=None), redis=Depends(get_redis)
):
    refresh_token = refresh_token.refresh_token
    print(refresh_token)
    try:
        jti, username = jwt_authentication.decode_refresh_token(
            refresh_token, settings.SECRET_KEY
        )
    except Exception as e:
        username = None
        jti = None
    print(username, jti)
    result = await redis.get(jti)
    if result:
        await redis.delete(jti)
        (
            access_token,
            refresh_token,
            jti,
        ) = jwt_authentication.generate_access_and_refresh_token(
            username,
            settings.ACCESS_KEY_EXPIRE_TIME,
            settings.REFRESH_KEY_EXPIRE_TIME,
            settings.SECRET_KEY,
        )
        await redis.set(jti, username)
        return JSONResponse(
            {"access_token": access_token, "refresh_token": refresh_token}
        )
    else:
        return JSONResponse(
            {"detail": "invalid request."}, status_code=status.HTTP_400_BAD_REQUEST
        )
