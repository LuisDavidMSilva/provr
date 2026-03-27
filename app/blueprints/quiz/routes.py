import json
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.question import QuestionBank, Question
from app.blueprints.quiz.forms import UploadBankForm
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
            content =  file.read().decode('utf-8')
            questions_data = json.loads(content)

            if not isinstance(questions_data, list):
                flash('Invalid format: file must contain JSON format!')
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
                    return redirect(url_for('quiz.upload'))

                question = Question(
                    text=item['text'],
                    level=item['level'],
                    topic=item['topic'],
                    alternatives=item['alternatives'],
                    correct_answer=item['correct_answer'],
                    bank_id=bank.id
                )
                db.session.add(question)

            db.session.commit()
            flash(f'Question bank "{bank.name}" uploaded successfully', 'success')
            return redirect(url_for('quiz.list_banks'))

        except json.JSONDecodeError:
            flash('Invalid JSON file. Please check the file format', 'danger')
            return redirect(url_for('quiz.upload'))

    return render_template('quiz/upload.html', form=form)


@quiz_bp.route('/banks')
@login_required
def list_banks():
    banks = QuestionBank.query.filter_by(owner_id=current_user.id).all()
    return render_template('quiz/list.html', banks=banks)