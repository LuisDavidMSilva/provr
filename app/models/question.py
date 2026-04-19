from typing import List
from datetime import datetime, timezone
from app import db
from sqlalchemy import String, Integer, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

class QuestionBank(db.Model):
    __tablename__ = 'question_banks'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    questions: Mapped[list["Question"]] = relationship(back_populates="bank", lazy=True, cascade='all, delete-orphan') 
    owner: Mapped["User"] = relationship(back_populates="banks")
    sessions: Mapped[list["QuizSession"]] = relationship(back_populates="bank")

    def __repr__(self):
        return f'<QuestionBank {self.name}>'


class Question(db.Model):
    __tablename__ = 'questions'

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    level: Mapped[str] = mapped_column(String(20))
    topic: Mapped[str] = mapped_column(String(100))
    alternatives: Mapped[dict] = mapped_column(JSON)
    correct_answer: Mapped[str] = mapped_column(String(10))
    bank_id: Mapped[int] = mapped_column(ForeignKey('question_banks.id'))

    bank: Mapped["QuestionBank"] = relationship(back_populates="questions")
    answers: Mapped[list["QuizAnswer"]] = relationship(back_populates="question", cascade="all, delete-orphan", passive_deletes=True)

    def __repr__(self):
        return f'<Question {self.text[:30]}...>'
