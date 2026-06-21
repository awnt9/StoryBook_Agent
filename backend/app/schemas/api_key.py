from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field as PydanticField
from sqlalchemy import Index, text
from sqlmodel import Field, SQLModel


class UserApiKey(SQLModel, table=True):
    __tablename__ = "user_api_keys"
    __table_args__ = (
        Index(
            "uq_user_api_keys_selected",
            "user_id",
            unique=True,
            postgresql_where=text("is_selected"),
        ),
    )

    id: int | None = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(
        foreign_key="users.id",
        ondelete="CASCADE",
        index=True,
        nullable=False,
    )
    label: str = Field(max_length=100, nullable=False)
    provider: str = Field(max_length=50, nullable=False)
    encrypted_key: str = Field(max_length=2048, nullable=False)
    last_four: str = Field(max_length=4, nullable=False)
    is_selected: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )


class ApiKeyCreate(BaseModel):
    label: str = PydanticField(min_length=1, max_length=100)
    provider: str = PydanticField(default="openai", min_length=1, max_length=50)
    api_key: str = PydanticField(min_length=8, max_length=2048)


class ApiKeyRead(BaseModel):
    id: int
    label: str
    provider: str
    masked_key: str
    is_selected: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApiKeyReveal(BaseModel):
    id: int
    api_key: str
