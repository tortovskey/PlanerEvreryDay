from core.DB import fetch_one, execute
from fucn.auth_helpers import hash_password, verify_password


def get_user_by_email(email):
    return fetch_one('SELECT * FROM users WHERE lower(email) = lower(%s)', (email,))


def get_user_by_id(user_id):
    return fetch_one('SELECT * FROM users WHERE id = %s', (str(user_id),))


def _build_unique_username(email):
    base = (email.split('@')[0].strip().lower() or 'user')[:100]
    username = base
    counter = 1
    while fetch_one('SELECT id FROM users WHERE lower(username) = lower(%s)', (username,)):
        counter += 1
        suffix = f'_{counter}'
        username = f"{base[:120-len(suffix)]}{suffix}"
    return username


def create_user(email, password, display_name):
    password_hash = hash_password(password)
    username = _build_unique_username(email)
    user = fetch_one(
        """
        INSERT INTO users (email, username, password_hash, display_name, avatar_url, is_active)
        VALUES (%s, %s, %s, %s, %s, TRUE)
        RETURNING *
        """,
        (email, username, password_hash, display_name, ''),
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


def authenticate_user(email, password):
    user = get_user_by_email(email)
    if not user or not user.get('password_hash'):
        return None
    if not verify_password(password, user['password_hash']):
        return None
    execute('UPDATE users SET last_login_at = CURRENT_TIMESTAMP, last_login = CURRENT_TIMESTAMP WHERE id = %s', (user['id'],))
    return get_user_by_id(user['id'])


def get_settings(user_id):
    return fetch_one('SELECT * FROM user_settings WHERE user_id = %s', (user_id,))


def upsert_settings(user_id, payload):
    existing = get_settings(user_id)
    fields = {
        'theme': payload.get('theme', existing['theme'] if existing else 'nebula'),
        'timezone': payload.get('timezone', existing['timezone'] if existing else 'Europe/Paris'),
        'start_hour': int(payload.get('start_hour', existing['start_hour'] if existing else 9)),
        'end_hour': int(payload.get('end_hour', existing['end_hour'] if existing else 18)),
        'focus_minutes': int(payload.get('focus_minutes', existing['focus_minutes'] if existing else 50)),
        'break_minutes': int(payload.get('break_minutes', existing['break_minutes'] if existing else 10)),
        'email_notifications': bool(payload.get('email_notifications', existing['email_notifications'] if existing else False)),
        'weekly_digest': bool(payload.get('weekly_digest', existing['weekly_digest'] if existing else True)),
        'ai_mode': payload.get('ai_mode', existing['ai_mode'] if existing else 'planner'),
    }
    return fetch_one(
        """
        INSERT INTO user_settings (user_id, theme, timezone, start_hour, end_hour, focus_minutes, break_minutes, email_notifications, weekly_digest, ai_mode)
        VALUES (%(user_id)s, %(theme)s, %(timezone)s, %(start_hour)s, %(end_hour)s, %(focus_minutes)s, %(break_minutes)s, %(email_notifications)s, %(weekly_digest)s, %(ai_mode)s)
        ON CONFLICT (user_id) DO UPDATE SET
            theme = EXCLUDED.theme,
            timezone = EXCLUDED.timezone,
            start_hour = EXCLUDED.start_hour,
            end_hour = EXCLUDED.end_hour,
            focus_minutes = EXCLUDED.focus_minutes,
            break_minutes = EXCLUDED.break_minutes,
            email_notifications = EXCLUDED.email_notifications,
            weekly_digest = EXCLUDED.weekly_digest,
            ai_mode = EXCLUDED.ai_mode,
            updated_at = CURRENT_TIMESTAMP
        RETURNING *
        """,
        {'user_id': user_id, **fields},
    )


def update_profile(user_id, display_name, avatar_url=''):
    return fetch_one(
        """
        UPDATE users
        SET display_name = %s,
            avatar_url = %s
        WHERE id = %s
        RETURNING *
        """,
        (display_name, avatar_url, user_id),
    )
