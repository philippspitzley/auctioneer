from enum import Enum
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class Role(str, Enum):
    admin = "admin"
    user = "user"
    guest = "guest"


class User(SQLModel, table=True):
    # id: None is only for pydantic, because in code we use id = None. The id is generated py postgres when saving it to the db. Might change it to uuid in the future.
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(index=True, unique=True)
    password_hash: str = Field()
    role: Role = Field(default=Role.guest)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime | None = Field(default=None)

