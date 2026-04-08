from pydantic import BaseModel, Field, ConfigDict


class AuthenticationBase(BaseModel):
    username: str
    password: str


class AuthenticationCreate(AuthenticationBase):
    pass


class AuthenticationResponse(AuthenticationBase):
    username: str
    password: str

    model_config = ConfigDict(from_attributes=True)
