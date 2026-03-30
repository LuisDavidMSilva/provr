from app import db
from datetime import datetime, timezone

class QuizSession(db.Model):
    __tablename__ = 'quiz_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bank_id = db.Column(db.Integer, db.ForeignKey('question_banks.id'), nullable=False)
    score = db.Column(db.Integer, nullable=True)
    total = db.Column(db.Integer, nullable=False)
    time_limit = db.Column(db.Integer, nullable=False)
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    finished_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', backref='sessions')
    bank = db.relationship('QuestionBank', backref='sessions')

    def __repr__(self):
        return f'<QuizSession User:{self.user_id} Bank:{self.bank_id} Score:{self.score}/{self.total}>'

class QuizAnswer(db.Model):
    __tablename__ = 'quiz_answers'

    id              = db.Column(db.Integer, primary_key=True)
    session_id      = db.Column(db.Integer, db.ForeignKey('quiz_sessions.id'), nullable=False)
    question_id     = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    selected_answer = db.Column(db.String(10), nullable=False)
    is_correct      = db.Column(db.Boolean, nullable=False)

    session  = db.relationship('QuizSession', backref='answers')
    question = db.relationship('Question', backref='answers')

    def __repr__(self):
        return f'<QuizAnswer session:{self.session_id} question:{self.question_id} correct:{self.is_correct}>'