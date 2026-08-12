from functools import wraps
from datetime import datetime, timezone
from collections import defaultdict
from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.question import QuestionBank, Question
from app.models.quiz import QuizSession, QuizAnswer
from app.models.moderation import ContentFilterConfig, ModerationLog
from flask_babel import gettext as _
from . import admin_bp

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_users = db.session.query(User).count()
    total_banks = db.session.query(QuestionBank).count()
    total_sessions = db.session.query(QuizSession).count()
    blocked_attempts = db.session.query(ModerationLog).filter_by(action='blocked').count()

    recent_users = db.session.scalars(
        db.select(User).order_by(User.created_at.desc()).limit(5)
    ).all()
    
    recent_logs = db.session.scalars(
        db.select(ModerationLog).order_by(ModerationLog.timestamp.desc()).limit(5)
    ).all()

    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        total_banks=total_banks,
        total_sessions=total_sessions,
        blocked_attempts=blocked_attempts,
        recent_users=recent_users,
        recent_logs=recent_logs
    )

@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    # NOTE: Scale limitation - this loads all users and sessions in-memory.
    # For MVP this is acceptable, but in production, this should use SQL aggregations.
    # 1. User Growth (Cumulative over time)
    users = db.session.scalars(db.select(User).order_by(User.created_at)).all()
    growth_data = []
    cumulative = 0
    for u in users:
        cumulative += 1
        date_str = u.created_at.strftime('%Y-%m-%d')
        if growth_data and growth_data[-1]['date'] == date_str:
            growth_data[-1]['count'] = cumulative
        else:
            growth_data.append({'date': date_str, 'count': cumulative})

    # 2. New registrations (by date)
    new_users_by_date = {}
    for u in users:
        date_str = u.created_at.strftime('%Y-%m-%d')
        new_users_by_date[date_str] = new_users_by_date.get(date_str, 0) + 1
    new_users_data = [{'date': d, 'count': c} for d, c in sorted(new_users_by_date.items())]

    # 3. Banks per User
    banks_per_user = []
    for u in db.session.scalars(db.select(User)).all():
        banks_per_user.append({
            'username': u.username,
            'count': len(u.banks)
        })

    # 4. Weekly Quizzes per user
    sessions = db.session.scalars(db.select(QuizSession).order_by(QuizSession.started_at)).all()
    weekly_data = defaultdict(lambda: defaultdict(int))
    all_weeks = set()
    all_usernames = set()
    
    for s in sessions:
        year, week, _ = s.started_at.isocalendar()
        week_key = f"{year}-W{week:02d}"
        username = s.user.username
        weekly_data[week_key][username] += 1
        all_weeks.add(week_key)
        all_usernames.add(username)
        
    sorted_weeks = sorted(list(all_weeks))
    quiz_datasets = []
    for uname in all_usernames:
        counts = []
        for wk in sorted_weeks:
            counts.append(weekly_data[wk][uname])
        quiz_datasets.append({
            'label': uname,
            'data': counts
        })

    return render_template(
        'admin/analytics.html',
        growth_data=growth_data,
        new_users_data=new_users_data,
        banks_per_user=banks_per_user,
        quiz_datasets=quiz_datasets,
        sorted_weeks=sorted_weeks
    )

@admin_bp.route('/performance')
@login_required
@admin_required
def performance():
    users = db.session.scalars(db.select(User)).all()
    user_stats = []
    
    for u in users:
        user_sessions = [s for s in u.sessions if s.finished_at is not None]
        total_quizzes = len(user_sessions)
        total_questions = sum(s.total for s in user_sessions)
        total_correct = sum(s.score or 0 for s in user_sessions)
        avg_score = (total_correct / total_questions * 100) if total_questions > 0 else 0
        
        # Progression: score percentage over time
        progression = []
        sorted_sessions = sorted(user_sessions, key=lambda x: x.started_at)
        for idx, s in enumerate(sorted_sessions):
            pct = (s.score / s.total * 100) if s.total > 0 else 0
            progression.append({
                'index': idx + 1,
                'date': s.started_at.strftime('%Y-%m-%d %H:%M'),
                'score_pct': round(pct, 1)
            })
            
        user_stats.append({
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'is_admin': u.is_admin,
            'total_quizzes': total_quizzes,
            'total_questions': total_questions,
            'total_correct': total_correct,
            'avg_score': round(avg_score, 1),
            'progression': progression
        })
        
    return render_template('admin/performance.html', user_stats=user_stats)

@admin_bp.route('/moderation', methods=['GET', 'POST'])
@login_required
@admin_required
def moderation():
    configs = db.session.scalars(db.select(ContentFilterConfig)).all()
    config_dict = {c.name: c for c in configs}

    # Fallback to seed defaults if missing
    if not config_dict:
        default_configs = [
            ('max_file_size', '3.0', 'Maximum allowed file size in MB for uploads'),
            ('blocked_keywords', 'hack,exploit,malware,script,dropper,trojan,eval,exec,system,killall,rm -rf', 'Comma separated list of blocked words in uploaded question banks'),
            ('blocked_extensions', 'exe,sh,bat,bin,js,php,py,pl,rb,cmd,com', 'Comma separated list of blocked file extensions')
        ]
        for name, value, desc in default_configs:
            cfg = ContentFilterConfig(name=name, value=value, description=desc)
            db.session.add(cfg)
        db.session.commit()
        configs = db.session.scalars(db.select(ContentFilterConfig)).all()
        config_dict = {c.name: c for c in configs}

    if request.method == 'POST':
        # Update settings
        for name, cfg in config_dict.items():
            val = request.form.get(name)
            active_key = f"{name}_active"
            is_active = request.form.get(active_key) == 'on'
            
            if val is not None:
                cfg.value = val.strip()
            cfg.is_active = is_active
            
        db.session.commit()
        flash(_('Content Moderation settings updated successfully!'), 'success')
        return redirect(url_for('admin.moderation'))

    logs = db.session.scalars(
        db.select(ModerationLog).order_by(ModerationLog.timestamp.desc())
    ).all()

    return render_template('admin/moderation.html', configs=configs, logs=logs)

@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = db.get_or_404(User, user_id)
    if user.id == current_user.id:
        flash(_('You cannot remove admin rights from yourself.'), 'danger')
        return redirect(url_for('admin.performance'))

    # If the user is currently an admin, make sure they are not the ONLY admin in the system.
    if user.is_admin:
        admin_count = db.session.scalar(db.select(db.func.count(User.id)).filter_by(is_admin=True))
        if admin_count <= 1:
            flash(_('Cannot demote the only remaining administrator in the system.'), 'danger')
            return redirect(url_for('admin.performance'))

    user.is_admin = not user.is_admin
    db.session.commit()
    status = _("promoted to Admin") if user.is_admin else _("demoted from Admin")
    flash(_('User %(username)s successfully %(status)s!') % {'username': user.username, 'status': status}, 'success')
    return redirect(url_for('admin.performance'))