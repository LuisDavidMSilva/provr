from typing import Optional, List, Any
from datetime import datetime, timezone
from sqlalchemy import String, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app import db

class QuizSession(db.Model):
    __tablename__ = 'quiz_sessions'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    bank_id: Mapped[Optional[int]] = mapped_column(ForeignKey('question_banks.id'))
    score: Mapped[Optional[int]] = mapped_column()
    total: Mapped[int] = mapped_column()
    time_limit: Mapped[Optional[int]] = mapped_column()
    started_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    finished_at: Mapped[Optional[datetime]] = mapped_column()
    
    current_index: Mapped[int] = mapped_column(default=0)
    question_ids: Mapped[list[int]] = mapped_column(JSON)

    user: Mapped["User"] = relationship(back_populates="sessions")
    bank: Mapped[Optional["QuestionBank"]] = relationship(back_populates="sessions")
    answers: Mapped[list["QuizAnswer"]] = relationship(back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f'<QuizSession User:{self.user_id} Bank:{self.bank_id} Score:{self.score}/{self.total}>'


class QuizAnswer(db.Model):
    __tablename__ = 'quiz_answers'

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey('quiz_sessions.id'))
    question_id: Mapped[Optional[int]] = mapped_column(ForeignKey('questions.id', ondelete='SET NULL'))
    selected_answer: Mapped[str] = mapped_column(String(10))
    is_correct: Mapped[bool] = mapped_column()

    session: Mapped["QuizSession"] = relationship(back_populates="answers")
    question: Mapped[Optional["Question"]] = relationship(back_populates="answers")

    def __repr__(self):
        return f'<QuizAnswer session:{self.session_id} question:{self.question_id} correct:{self.is_correct}>'