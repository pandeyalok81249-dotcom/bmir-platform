from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None

    model_config = ConfigDict(from_attributes=True)


class APIErrorDetails(BaseModel):
    code: str
    message: str
    details: Optional[List[Any]] = None


class APIErrorResponse(BaseModel):
    success: bool = False
    error: APIErrorDetails

