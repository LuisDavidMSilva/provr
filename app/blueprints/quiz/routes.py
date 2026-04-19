import json
import random
import os
from datetime import datetime, time, timezone
from flask import render_template, redirect, url_for, flash, session, request
from flask_login import login_required, current_user
from app import db
from app.models.question import QuestionBank, Question
from app.models.quiz import QuizSession, QuizAnswer
from app.blueprints.quiz.forms import UploadBankForm, DeleteBankForm, QuizConfigForm, AnswerForm
from . import quiz_bp


@quiz_bp.route('/')
@login_required
def index():
    return render_template('quiz/index.html')


@quiz_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadBankForm()
    if form.validate_on_submit():
        file = form.file.data
        
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        
        if size > 3 * 1024 * 1024:
            flash('JSON file is too large (max 3MB).', 'danger')
            return redirect(url_for('quiz.upload'))

        try:
            content = file.read().decode('utf-8')
            questions_data = json.loads(content)

            if not isinstance(questions_data, list):
                flash('Invalid format: file must contain a JSON array.', 'danger')
                return redirect(url_for('quiz.upload'))

            bank = QuestionBank(
                name=form.name.data,
                owner_id=current_user.id
            )
            db.session.add(bank)
            db.session.flush()

            for item in questions_data:
                if not all(k in item for k in ('text', 'level', 'alternatives', 'correct_answer')):
                    db.session.rollback()
                    flash('One or more questions have missing fields.', 'danger')
                    return redirect(url_for('quiz.upload'))

                question = Question(
                    text=item['text'],
                    level=item['level'],
                    topic=item.get('topic'),
                    alternatives=item['alternatives'],
                    correct_answer=item['correct_answer'],
                    bank_id=bank.id
                )
                db.session.add(question)

            db.session.commit()
            flash(f'Question bank "{bank.name}" uploaded successfully!', 'success')
            return redirect(url_for('quiz.list_banks'))

        except json.JSONDecodeError:
            flash('Invalid JSON file. Please check the file format.', 'danger')
            return redirect(url_for('quiz.upload'))

    return render_template('quiz/upload.html', form=form)


@quiz_bp.route('/banks')
@login_required
def list_banks():
    banks = db.session.scalars(db.select(QuestionBank).filter_by(owner_id=current_user.id)).all()
    form = DeleteBankForm()
    return render_template('quiz/list.html', banks=banks, form=form)


@quiz_bp.route('/banks/<int:bank_id>/delete', methods=['POST'])
@login_required
def delete_bank(bank_id):
    bank = db.get_or_404(QuestionBank, bank_id)
    if bank.owner_id != current_user.id:
        flash('You are not allowed to delete this bank.', 'danger')
        return redirect(url_for('quiz.list_banks'))
    db.session.delete(bank)
    db.session.commit()
    flash(f'Question bank "{bank.name}" deleted successfully.', 'success')
    return redirect(url_for('quiz.list_banks'))

LEVEL_ALIASES = {
        'easy':   ['easy', 'fácil', 'facil', 'Fácil', 'Facil'],
        'medium': ['medium', 'médio', 'medio', 'Médio', 'Medio'],
        'hard':   ['hard', 'difícil', 'dificil', 'Difícil', 'Dificil'],
}

@quiz_bp.route('/banks/<int:bank_id>/configure', methods=['GET', 'POST'])
@login_required
def configure(bank_id):
    bank = db.get_or_404(QuestionBank, bank_id)
    if bank.owner_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('quiz.list_banks'))

    form = QuizConfigForm()
    if form.validate_on_submit():
        level = form.level.data
        quantity = form.quantity.data
        time_limit = int(form.time_limit.data)

        query = db.select(Question).filter_by(bank_id=bank.id)
        if level != 'all':
            aliases = LEVEL_ALIASES.get(level, [level])
            query = query.filter(Question.level.in_(aliases))

        questions = list(db.session.scalars(query).all())

        if len(questions) < quantity:
            flash(f'Not enough questions. This bank has {len(questions)} questions for the selected level.', 'danger')
            return redirect(url_for('quiz.configure', bank_id=bank.id))

        selected = random.sample(questions, quantity)
        question_ids = [q.id for q in selected]

        quiz_session = QuizSession(
            user_id=current_user.id,
            bank_id=bank.id,
            total=quantity,
            time_limit=time_limit,
            started_at=datetime.now(timezone.utc),
            question_ids=[q.id for q in selected],
            current_index=0
        )
        db.session.add(quiz_session)
        db.session.commit()

        session['quiz_session_id'] = quiz_session.id
        session['time_limit'] = time_limit
        session['started_at_ts'] = int(datetime.now(timezone.utc).timestamp())

        return redirect(url_for('quiz.take'))

    return render_template('quiz/configure.html', form=form, bank=bank)


@quiz_bp.route('/take', methods=['GET', 'POST'])
@login_required
def take():
    quiz_session_id = session.get('quiz_session_id')
    time_limit = session.get('time_limit')
    started_at_ts = session.get('started_at_ts') 

    if not quiz_session_id or not started_at_ts:
        flash('No active quiz session.', 'danger')
        return redirect(url_for('quiz.list_banks'))

    quiz_session = db.session.get(QuizSession, quiz_session_id)
    if not quiz_session:
        flash('Quiz session not found.', 'danger')
        return redirect(url_for('quiz.list_banks'))

    question_ids = quiz_session.question_ids
    current_index = quiz_session.current_index

    if current_index >= len(question_ids):
        if quiz_session.finished_at is None:
            answers = db.session.scalars(db.select(QuizAnswer).filter_by(session_id=quiz_session_id)).all()
            quiz_session.score = sum(1 for a in answers if a.is_correct)
            quiz_session.finished_at = datetime.now(timezone.utc)
            db.session.commit()
        return redirect(url_for('quiz.result'))

    question = db.get_or_404(Question, question_ids[current_index])
    form = AnswerForm()

    if form.validate_on_submit():
        if time_limit and time_limit > 0:
            now_ts = int(datetime.now(timezone.utc).timestamp())
            elapsed = now_ts - started_at_ts
            
            if elapsed > (time_limit + 5):
                flash('Time is up! Your quiz was automatically submitted.', 'warning')
                if quiz_session.finished_at is None:
                    answers = db.session.scalars(db.select(QuizAnswer).filter_by(session_id=quiz_session_id)).all()
                    quiz_session.score = sum(1 for a in answers if a.is_correct)
                    quiz_session.finished_at = datetime.now(timezone.utc)
                    db.session.commit()
                return redirect(url_for('quiz.result'))

        selected = request.form.get('answer')
        if not selected:
            flash('Please select an answer.', 'danger')
            return redirect(url_for('quiz.take'))

        is_correct = selected == question.correct_answer

        answer = QuizAnswer(
            session_id=quiz_session_id,
            question_id=question.id,
            selected_answer=selected,
            is_correct=is_correct
        )
        db.session.add(answer)
        quiz_session.current_index += 1
        db.session.commit()

        return redirect(url_for('quiz.take'))

    return render_template('quiz/take.html',
                           form=form,
                           question=question,
                           time_limit=time_limit,
                           quiz_session=quiz_session,
                           current=current_index + 1,
                           total=len(question_ids),
                           quiz_session_id=quiz_session_id,
                           started_at_ts=started_at_ts)


@quiz_bp.route('/result')
@login_required
def result():
    quiz_session_id = session.get('quiz_session_id')
    if not quiz_session_id:
        return redirect(url_for('quiz.list_banks'))

    quiz_session = db.get_or_404(QuizSession, quiz_session_id)
    answers = db.session.scalars(db.select(QuizAnswer).filter_by(session_id=quiz_session_id)).all()
    score = quiz_session.score

    session.pop('quiz_session_id', None)
    session.pop('time_limit', None)
    session.pop('started_at_ts', None)

    return render_template('quiz/result.html',
                           quiz_session=quiz_session,
                           answers=answers,
                           score=score)


@quiz_bp.route('/history')
@login_required
def history():
    sessions = db.session.scalars(db.select(QuizSession).filter_by(user_id=current_user.id).order_by(QuizSession.started_at.desc())).all()
    return render_template('quiz/history.html', sessions=sessions)


@quiz_bp.route('/history/<int:session_id>')
@login_required
def session_detail(session_id):
    quiz_session = db.get_or_404(QuizSession, session_id)
    if quiz_session.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('quiz.history'))

    answers = db.session.scalars(db.select(QuizAnswer).filter_by(session_id=session_id)).all()
    return render_template('quiz/result.html', quiz_session=quiz_session, answers=answers, score=quiz_session.score)