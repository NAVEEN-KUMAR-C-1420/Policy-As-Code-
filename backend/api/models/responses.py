from pydantic import BaseModel


class BaseAPIResponse[T](BaseModel):
    success: bool
    message: str
    data: T | None = None
    errors: list[str] | None = None
