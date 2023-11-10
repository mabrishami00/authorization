from pydantic import BaseModel, EmailStr, field_validator
import re


class BaseUser(BaseModel):
    username: str
    email: EmailStr


class UserCreate(BaseUser):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        if not re.match(pattern, value):
            raise ValueError(
                "password must have at least 8 characters and at least one uppercase, one lowercase and one punctuation."
            )
        return value


class UserLogin(BaseModel):
    username: str
    password: str

class UserLoginOTP(BaseModel):
    username: str

class UserCheckOTP(UserLoginOTP):
    email: EmailStr
    otp: int

class User(BaseUser):
    id: int


class RefreshToken(BaseModel):
    refresh_token: str
