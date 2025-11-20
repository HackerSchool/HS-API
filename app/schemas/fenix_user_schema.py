from pydantic import BaseModel, Field

class FenixUserSchema(BaseModel):
    ist_id: str = Field(alias="username")
    name: str = Field(...)
    email: str = Field(...)