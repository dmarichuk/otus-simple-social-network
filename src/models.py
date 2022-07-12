from pydantic import BaseModel, Field, validator


class PollBase(BaseModel):
    first_name: str = Field(title="Person's first name", max_length=100)
    last_name: str = Field(title="Person's last name", max_length=100)
    age: int = Field(gt=0, title="Person's age")
    city: str = Field(title="Person's city", max_length=100)
    interests: str | None = Field(
        default=None, title="Person's interests", max_length=256
    )


class PollRegister(PollBase):
    login: str = Field(title="Person's login", max_length=20)
    password: str = Field(title="Person's password", max_length=48)

    @validator("login", "password")
    def ascii(cls, v: str):
        assert v.isascii(), "Must be a string of ASCII"
        return v

    class Config:
        validate_assignment = True


class PollRead(PollBase):
    id: int
