from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


# class TokenResponse(BaseModel):
#     token: str


class TokenData(BaseModel):
    username: str
    expiration: int
