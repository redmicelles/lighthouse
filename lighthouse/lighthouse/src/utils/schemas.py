from enum import Enum
from typing import Annotated
from uuid import uuid4

from pydantic import AliasPath
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import field_validator
from typing_extensions import Self


class StatusEnum(str, Enum):
    """
    Status Enum
    """
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"


class UpdateTaskSchema(BaseModel):
    """
    Pydantic validation model for Tasks
    PUT request body
    """
    model_config = ConfigDict(extra="forbid")

    title: Annotated[str, Field(min_length=3)]
    description: Annotated[str, Field(min_length=3)]
    status: Annotated[StatusEnum, Field(...)]

    @field_validator("status")
    @classmethod
    def format_status(cls, status: StatusEnum) -> Self:
        return status.value


class CreateTaskSchema(BaseModel):
    """
    Pydantic validation model for Tasks
    POST request body
    """
    model_config = ConfigDict(extra="forbid")

    taskId: Annotated[str, Field(default_factory=lambda: uuid4().hex)]
    title: Annotated[str, Field(min_length=3)]
    description: Annotated[str, Field(min_length=3)]
    status: Annotated[StatusEnum, Field(...)]

    @field_validator("status")
    @classmethod
    def format_status(cls, status: StatusEnum) -> Self:
        return status.value


class RetrieveTaskSchema(BaseModel):
    """
    Pydantic validation model for Tasks retrieve from
    DyanmoDB
    """
    taskId: Annotated[str, Field(validation_alias=AliasPath("Items", 0, "taskId", "S"))]
    title: Annotated[str, Field(validation_alias=AliasPath("Items", 0, "title", "S"))]
    description: Annotated[
        str, Field(validation_alias=AliasPath("Items", 0, "description", "S"))
    ]
    status: Annotated[str, Field(validation_alias=AliasPath("Items", 0, "status", "S"))]
