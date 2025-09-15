from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import JSON, Column, DateTime
from sqlmodel import Field, SQLModel

from utils.datetime_utils import get_current_utc_datetime
from utils.asset_directory_utils import convert_absolute_path_to_web_path


class ImageAsset(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), nullable=False, default=get_current_utc_datetime
        ),
    )
    is_uploaded: bool = Field(default=False)
    path: str
    extras: Optional[dict] = Field(sa_column=Column(JSON), default=None)
    
    @property
    def web_path(self) -> str:
        """Get the web-accessible path for this image"""
        return convert_absolute_path_to_web_path(self.path)
