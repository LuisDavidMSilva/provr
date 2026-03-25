from app import db
from datetime import datetime, timezone

class QuizSession(db.Model):
    __tablename__ = 'quiz_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bank_id = db.Column(db.Integer, db.ForeignKey('questions_banks.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    time_limit = db.Column(db.Integer, nullable=False)
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    finished_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', backref='sessions')
    bank = db.relationship('QuestionBank', backref='sessions')

    def __repr__(self):
        return f'<QuizSession User:{self.user_id} Bank:{self.bank_id} Score:{self.score}/{self.total}>'