import os
import sys
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, url_for, g, redirect

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(CURRENT_DIR)
if APP_DIR not in sys.path:
    sys.path.append(APP_DIR)

from core.DB import init_db, fetch_one, execute
from fucn.date_helpers import today_iso, validate_date, validate_time
from services.auth_service import get_settings, upsert_settings, update_profile
from services.add_task import (
    add_task_to_db,
    get_tasks_by_date,
    get_upcoming_tasks,
    search_tasks,
    update_task_in_db,
    delete_task_from_db,
    set_task_status,
)
from services.Add_Calender import get_tasks_by_month, get_stats
from services.ai_assistant import handle_assistant_message

TEMPLATE_DIR = os.path.join(APP_DIR, 'templates')
STATIC_DIR = os.path.join(APP_DIR, 'static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR, static_url_path='/static')
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-change-me')
init_db()

GUEST_EMAIL = os.getenv('GUEST_EMAIL', 'local@planer.everyday')
GUEST_NAME = os.getenv('GUEST_NAME', 'Local User')


def ensure_guest_user():
    user = fetch_one('SELECT * FROM users WHERE lower(email) = lower(%s)', (GUEST_EMAIL,))
    if user:
        fetch_one(
            """
            INSERT INTO user_settings (user_id)
            VALUES (%s)
            ON CONFLICT (user_id) DO UPDATE SET updated_at = CURRENT_TIMESTAMP
            RETURNING *
            """,
            (user['id'],),
        )
        return user

    username = 'local_user'
    counter = 1
    while fetch_one('SELECT id FROM users WHERE lower(username) = lower(%s)', (username,)):
        counter += 1
        username = f'local_user_{counter}'

    user = fetch_one(
        """
        INSERT INTO users (email, username, password_hash, display_name, avatar_url, is_active)
        VALUES (%s, %s, %s, %s, %s, TRUE)
        RETURNING *
        """,
        (GUEST_EMAIL, username, None, GUEST_NAME, ''),
    )
    fetch_one(
        """
        INSERT INTO user_settings (user_id)
        VALUES (%s)
        ON CONFLICT (user_id) DO UPDATE SET updated_at = CURRENT_TIMESTAMP
        RETURNING *
        """,
        (user['id'],),
    )
    return user


def current_user_id():
    user_id = session.get('user_id')
    if user_id:
        return str(user_id)
    user = ensure_guest_user()
    session['user_id'] = str(user['id'])
    return str(user['id'])


def serialize_task(task):
    return {
        'id': task['id'],
        'title': task['title'],
        'description': task.get('description') or '',
        'task_date': str(task['task_date']),
        'task_time': str(task['task_time'])[:5] if task.get('task_time') else '',
        'priority': task.get('priority') or 'medium',
        'status': task.get('status') or 'pending',
        'created_at': str(task.get('created_at') or ''),
        'duration_minutes': int(task.get('duration_minutes') or 60),
        'source': task.get('source') or 'manual',
    }


def serialize_user(user):
    settings = get_settings(user['id']) or {}
    return {
        'id': str(user['id']),
        'email': user['email'],
        'display_name': user.get('display_name') or user.get('username') or user['email'].split('@')[0],
        'avatar_url': user.get('avatar_url') or '',
        'theme': settings.get('theme', 'nebula'),
    }


def web_login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        current_user_id()
        return view(*args, **kwargs)
    return wrapper


@app.before_request
def load_user():
    g.user = None
    user_id = current_user_id()
    if user_id:
        g.user = fetch_one('SELECT * FROM users WHERE id = %s', (user_id,))


@app.context_processor
def inject_globals():
    settings = get_settings(g.user['id']) if getattr(g, 'user', None) else {'theme': 'nebula'}
    return {'current_user': getattr(g, 'user', None), 'current_settings': settings or {'theme': 'nebula'}, 'auth_disabled': True}


@app.route('/login')
def login():
    return redirect(url_for('index'))


@app.route('/register')
def register():
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.clear()
    current_user_id()
    return redirect(url_for('index'))


@app.route('/')
@app.route('/index')
@web_login_required
def index():
    return render_template('index.html')


@app.route('/calendar')
@app.route('/calendar.html')
@web_login_required
def calendar():
    return render_template('calendar.html')


@app.route('/today')
@app.route('/today.html')
@web_login_required
def today():
    return render_template('today.html')


@app.route('/settings')
@web_login_required
def settings_page():
    return render_template('settings.html')


@app.route('/account')
@web_login_required
def account_page():
    return render_template('account.html')


@app.route('/api/auth/register', methods=['POST'])
def auth_register():
    return jsonify({'error': 'Авторизация отключена в этой версии проекта'}), 410


@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    return jsonify({'error': 'Авторизация отключена в этой версии проекта'}), 410


@app.route('/api/auth/refresh', methods=['POST'])
def auth_refresh():
    user = g.user or ensure_guest_user()
    return jsonify({'access_token': '', 'user': serialize_user(user), 'mode': 'local_no_auth'})


@app.route('/api/auth/me')
def auth_me():
    user = g.user or ensure_guest_user()
    return jsonify({'user': serialize_user(user), 'settings': get_settings(user['id']) or {}, 'mode': 'local_no_auth'})


@app.route('/auth/<provider>/login')
def oauth_login(provider):
    return redirect(url_for('index'))


@app.route('/auth/<provider>/callback')
def oauth_callback(provider):
    return redirect(url_for('index'))


@app.route('/api/stats')
def api_stats():
    return jsonify(get_stats(current_user_id()))


@app.route('/api/tasks/upcoming')
def api_tasks_upcoming():
    limit = int(request.args.get('limit', 10))
    tasks = get_upcoming_tasks(current_user_id(), max(1, min(limit, 50)))
    return jsonify([serialize_task(task) for task in tasks])


@app.route('/api/tasks/search')
def api_tasks_search():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    tasks = search_tasks(current_user_id(), query)
    return jsonify([serialize_task(task) for task in tasks])


@app.route('/api/tasks/month')
def api_tasks_month():
    year = int(request.args.get('year'))
    month = int(request.args.get('month'))
    tasks = get_tasks_by_month(current_user_id(), year, month)
    return jsonify([serialize_task(task) for task in tasks])


@app.route('/api/tasks')
def api_tasks_by_date():
    task_date = request.args.get('date', '').strip() or today_iso()
    validate_date(task_date)
    tasks = get_tasks_by_date(current_user_id(), task_date)
    return jsonify([serialize_task(task) for task in tasks])


@app.route('/api/tasks', methods=['POST'])
def api_add_task():
    data = request.get_json(force=True)
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    task_date = data.get('task_date', '').strip()
    task_time = data.get('task_time', '').strip()
    priority = data.get('priority', 'medium').strip()
    duration_minutes = int(data.get('duration_minutes', 60) or 60)
    if not title:
        return jsonify({'error': 'Название задачи обязательно'}), 400
    validate_date(task_date)
    if task_time:
        validate_time(task_time)
    else:
        task_time = None
    if priority not in ['low', 'medium', 'high']:
        priority = 'medium'
    task = add_task_to_db(current_user_id(), title, description, task_date, task_time, priority, duration_minutes)
    return jsonify({'message': 'Задача добавлена', 'task': serialize_task(task)}), 201


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def api_update_task(task_id):
    data = request.get_json(force=True)
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    task_date = data.get('task_date', '').strip()
    task_time = data.get('task_time', '').strip()
    priority = data.get('priority', 'medium').strip()
    duration_minutes = int(data.get('duration_minutes', 60) or 60)
    if not title:
        return jsonify({'error': 'Название задачи обязательно'}), 400
    validate_date(task_date)
    if task_time:
        validate_time(task_time)
    else:
        task_time = None
    task = update_task_in_db(current_user_id(), task_id, title, description, task_date, task_time, priority, duration_minutes)
    if not task:
        return jsonify({'error': 'Задача не найдена'}), 404
    return jsonify({'message': 'Задача обновлена', 'task': serialize_task(task)})


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def api_delete_task(task_id):
    deleted = delete_task_from_db(current_user_id(), task_id)
    if not deleted:
        return jsonify({'error': 'Задача не найдена'}), 404
    return jsonify({'message': 'Задача удалена'})


@app.route('/api/tasks/<int:task_id>/status', methods=['PATCH'])
def api_change_status(task_id):
    data = request.get_json(force=True)
    status = data.get('status', 'pending').strip()
    if status not in ['pending', 'done']:
        return jsonify({'error': 'Недопустимый статус'}), 400
    task = set_task_status(current_user_id(), task_id, status)
    if not task:
        return jsonify({'error': 'Задача не найдена'}), 404
    return jsonify({'message': 'Статус обновлён', 'task': serialize_task(task)})


@app.route('/api/settings', methods=['GET', 'PUT'])
def api_settings():
    user_id = current_user_id()
    if request.method == 'GET':
        return jsonify(get_settings(user_id) or {})
    payload = request.get_json(force=True)
    settings = upsert_settings(user_id, payload)
    return jsonify(settings)


@app.route('/api/profile', methods=['PUT'])
def api_profile():
    payload = request.get_json(force=True)
    display_name = payload.get('display_name', '').strip() or 'User'
    avatar_url = payload.get('avatar_url', '').strip()
    user = update_profile(current_user_id(), display_name, avatar_url)
    if not user:
        return jsonify({'error': 'Пользователь не найден'}), 404
    return jsonify({'user': serialize_user(user)})


@app.route('/api/assistant', methods=['POST'])
def api_assistant():
    data = request.get_json(force=True)
    message = data.get('message', '').strip()
    result = handle_assistant_message(current_user_id(), message)
    if result.get('created_task'):
        result['created_task'] = serialize_task(result['created_task'])
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
