from datetime import datetime, timezone
from app import db

class QuestionBank(db.Model):
    __tablename__ = 'questions_banks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    questions = db.relationship('Question', backref='bank', lazy=True) 
    owner = db.relationship('User', backref='banks')

    def __repr__(self):
        return f'<QuestionBank {self.name}>'

class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    level = db.Column(db.String(20), nullable=False)
    topic =  db.Column(db.String(100), nullable=False)
    alternatives = db.Column(db.JSON, nullable=False)
    correct_answer = db.Column(db.String(10), nullable=False)
    bank_id =  db.Column(db.Integer, db.ForeignKey('questions_banks.id'), nullable=False)


    def __repr__(self):
        return f'<Question {self.text[:30]}...>'
    

