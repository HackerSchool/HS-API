from typing import Optional

from pydantic import BaseModel, Field

class FenixCallbackSchema(BaseModel):
    state: str = Field(pattern="^[0-9a-f]{32}$")
    code: Optional[str] = Field(default=None)
    error: Optional[str] = Field(default=None)