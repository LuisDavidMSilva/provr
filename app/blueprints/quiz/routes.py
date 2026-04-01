import json
import random
from datetime import datetime, timezone
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
    banks = QuestionBank.query.filter_by(owner_id=current_user.id).all()
    form = DeleteBankForm()
    return render_template('quiz/list.html', banks=banks, form=form)


@quiz_bp.route('/banks/<int:bank_id>/delete', methods=['POST'])
@login_required
def delete_bank(bank_id):
    bank = QuestionBank.query.get_or_404(bank_id)
    if bank.owner_id != current_user.id:
        flash('You are not allowed to delete this bank.', 'danger')
        return redirect(url_for('quiz.list_banks'))
    db.session.delete(bank)
    db.session.commit()
    flash(f'Question bank "{bank.name}" deleted successfully.', 'success')
    return redirect(url_for('quiz.list_banks'))


@quiz_bp.route('/banks/<int:bank_id>/configure', methods=['GET', 'POST'])
@login_required
def configure(bank_id):
    bank = QuestionBank.query.get_or_404(bank_id)
    if bank.owner_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('quiz.list_banks'))

    form = QuizConfigForm()
    if form.validate_on_submit():
        level = form.level.data
        quantity = form.quantity.data
        time_limit = int(form.time_limit.data)

        query = Question.query.filter_by(bank_id=bank.id)
        if level != 'all':
            query = query.filter_by(level=level)

        questions = query.all()

        if len(questions) < quantity:
            flash(f'Not enough questions. This bank has {len(questions)} questions for the selected level.', 'danger')
            return redirect(url_for('quiz.configure', bank_id=bank.id))

        selected = random.sample(questions, quantity)

        quiz_session = QuizSession(
            user_id=current_user.id,
            bank_id=bank.id,
            total=quantity,
            time_limit=time_limit,
            started_at=datetime.now(timezone.utc)
        )
        db.session.add(quiz_session)
        db.session.flush()

        session['quiz_session_id'] = quiz_session.id
        session['question_ids'] = [q.id for q in selected]
        session['current_index'] = 0
        session['time_limit'] = time_limit

        db.session.commit()
        return redirect(url_for('quiz.take'))

    return render_template('quiz/configure.html', form=form, bank=bank)


@quiz_bp.route('/take', methods=['GET', 'POST'])
@login_required
def take():
    quiz_session_id = session.get('quiz_session_id')
    question_ids = session.get('question_ids')
    current_index = session.get('current_index', 0)
    time_limit = session.get('time_limit')

    if not quiz_session_id or not question_ids:
        flash('No active quiz session.', 'danger')
        return redirect(url_for('quiz.list_banks'))

    quiz_session = QuizSession.query.get(quiz_session_id)
    if not quiz_session:
        flash('Quiz session not found.', 'danger')
        return redirect(url_for('quiz.list_banks'))

    started_at_ts = int(quiz_session.started_at.replace(tzinfo=timezone.utc).timestamp())

    if current_index >= len(question_ids):
        return redirect(url_for('quiz.result'))

    question = Question.query.get_or_404(question_ids[current_index])
    form = AnswerForm()

    if form.validate_on_submit():
        if time_limit and time_limit > 0:
            now_ts = int(datetime.now(timezone.utc).timestamp())
            elapsed = now_ts - started_at_ts

            time_limit_seconds = time_limit * 60
            
            if elapsed > (time_limit_seconds + 5):
                flash('Time is up! Your quiz was automatically submitted.', 'warning')
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
        db.session.commit()

        session['current_index'] = current_index + 1
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

    quiz_session = QuizSession.query.get_or_404(quiz_session_id)
    answers = QuizAnswer.query.filter_by(session_id=quiz_session_id).all()
    score = sum(1 for a in answers if a.is_correct)

    quiz_session.score = score
    quiz_session.finished_at = datetime.now(timezone.utc)
    db.session.commit()

    session.pop('quiz_session_id', None)
    session.pop('question_ids', None)
    session.pop('current_index', None)

    return render_template('quiz/result.html',
                           quiz_session=quiz_session,
                           answers=answers,
                           score=score)


@quiz_bp.route('/history')
@login_required
def history():
    sessions = QuizSession.query.filter_by(user_id=current_user.id).order_by(QuizSession.started_at.desc()).all()
    return render_template('quiz/history.html', sessions=sessions)


@quiz_bp.route('/history/<int:session_id>')
@login_required
def session_detail(session_id):
    quiz_session = QuizSession.query.get_or_404(session_id)
    if quiz_session.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('quiz.history'))

    answers = QuizAnswer.query.filter_by(session_id=session_id).all()
    return render_template('quiz/result.html', quiz_session=quiz_session, answers=answers, score=quiz_session.score)