from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text
from typing import Optional
from app import db

class ContentFilterConfig(db.Model):
    __tablename__ = 'content_filter_configs'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    value: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(String(256))
    is_active: Mapped[bool] = mapped_column(default=True)

    def __repr__(self):
        return f'<ContentFilterConfig {self.name}={self.value[:20]}>'

class ModerationLog(db.Model):
    __tablename__ = 'moderation_logs'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    username: Mapped[str] = mapped_column(String(80))
    action: Mapped[str] = mapped_column(String(80))  # 'blocked', 'flagged'
    content_type: Mapped[str] = mapped_column(String(80))  # 'profile_picture', 'question_bank_json', etc.
    reason: Mapped[str] = mapped_column(String(256))
    filename: Mapped[str] = mapped_column(String(100))
    timestamp: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    user = relationship("User")

    def __repr__(self):
        return f'<ModerationLog {self.username} - {self.action} - {self.content_type}>'