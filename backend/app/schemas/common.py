from typing import Generic, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T
    message: str = "Request completed successfully"


class ErrorResponse(BaseModel):
    success: bool = False
    data: None = None
    message: str