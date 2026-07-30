from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar('T')

class BaseAPIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T | None = None
    errors: list[str] | None = None
