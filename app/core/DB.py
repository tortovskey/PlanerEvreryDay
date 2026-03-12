import os
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'planer_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres123'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def _table_exists(cur, table_name):
    cur.execute("SELECT to_regclass(%s)", (f'public.{table_name}',))
    return cur.fetchone()[0] is not None


def _column_info(cur, table_name, column_name):
    cur.execute(
        '''
        SELECT data_type, udt_name, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s AND column_name = %s
        ''',
        (table_name, column_name),
    )
    row = cur.fetchone()
    if not row:
        return None
    return {'data_type': row[0], 'udt_name': row[1], 'is_nullable': row[2]}


def _constraint_exists(cur, table_name, constraint_name):
    cur.execute(
        '''
        SELECT 1
        FROM information_schema.table_constraints
        WHERE table_schema = 'public' AND table_name = %s AND constraint_name = %s
        ''',
        (table_name, constraint_name),
    )
    return cur.fetchone() is not None


def _ensure_users_table(cur):
    cur.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash TEXT,
            username VARCHAR(120),
            display_name VARCHAR(120),
            avatar_url TEXT DEFAULT '',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            last_login_at TIMESTAMP
        );
        '''
    )

    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(120);")
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS display_name VARCHAR(120);")
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url TEXT DEFAULT '';")
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;")
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;")
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP;")

    cur.execute(
        '''
        UPDATE users
        SET username = COALESCE(NULLIF(username, ''), split_part(email, '@', 1), 'user')
        WHERE username IS NULL OR btrim(username) = ''
        '''
    )
    cur.execute(
        '''
        UPDATE users
        SET display_name = COALESCE(NULLIF(display_name, ''), NULLIF(username, ''), split_part(email, '@', 1), 'User')
        WHERE display_name IS NULL OR btrim(display_name) = ''
        '''
    )
    cur.execute("UPDATE users SET avatar_url = '' WHERE avatar_url IS NULL;")
    cur.execute("UPDATE users SET is_active = TRUE WHERE is_active IS NULL;")
    cur.execute("UPDATE users SET last_login_at = COALESCE(last_login_at, last_login) WHERE last_login_at IS NULL;")

    # tighten only after backfilling legacy rows
    cur.execute("ALTER TABLE users ALTER COLUMN username SET NOT NULL;")
    cur.execute("ALTER TABLE users ALTER COLUMN display_name SET NOT NULL;")

    info = _column_info(cur, 'users', 'id')
    return 'UUID' if info and info['udt_name'] == 'uuid' else 'INTEGER'


def _ensure_user_id_column(cur, table_name, sql_type, *, unique=False, add_fk=True):
    info = _column_info(cur, table_name, 'user_id')
    expected_udt = 'uuid' if sql_type.upper() == 'UUID' else 'int4'

    if info and info['udt_name'] != expected_udt:
        if _constraint_exists(cur, table_name, f'{table_name}_user_id_fkey'):
            cur.execute(f'ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {table_name}_user_id_fkey;')
        if unique:
            cur.execute(f'ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {table_name}_user_id_key;')
        cur.execute(f'ALTER TABLE {table_name} RENAME COLUMN user_id TO legacy_user_id;')
        info = None

    if not info:
        cur.execute(f'ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS user_id {sql_type};')

    if unique and not _constraint_exists(cur, table_name, f'{table_name}_user_id_key'):
        try:
            cur.execute('SAVEPOINT add_user_id_unique')
            cur.execute(f'ALTER TABLE {table_name} ADD CONSTRAINT {table_name}_user_id_key UNIQUE (user_id);')
            cur.execute('RELEASE SAVEPOINT add_user_id_unique')
        except Exception:
            cur.execute('ROLLBACK TO SAVEPOINT add_user_id_unique')
            cur.execute('RELEASE SAVEPOINT add_user_id_unique')

    if add_fk and not _constraint_exists(cur, table_name, f'{table_name}_user_id_fkey'):
        try:
            cur.execute('SAVEPOINT add_user_id_fk')
            cur.execute(
                f'ALTER TABLE {table_name} ADD CONSTRAINT {table_name}_user_id_fkey '
                f'FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;'
            )
            cur.execute('RELEASE SAVEPOINT add_user_id_fk')
        except Exception:
            cur.execute('ROLLBACK TO SAVEPOINT add_user_id_fk')
            cur.execute('RELEASE SAVEPOINT add_user_id_fk')


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    user_id_type = _ensure_users_table(cur)

    cur.execute(
        f'''
        CREATE TABLE IF NOT EXISTS oauth_accounts (
            id SERIAL PRIMARY KEY,
            user_id {user_id_type},
            provider VARCHAR(40) NOT NULL,
            provider_user_id VARCHAR(255) NOT NULL,
            provider_email VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(provider, provider_user_id)
        );
        '''
    )
    _ensure_user_id_column(cur, 'oauth_accounts', user_id_type, unique=False, add_fk=True)

    cur.execute(
        f'''
        CREATE TABLE IF NOT EXISTS user_settings (
            id SERIAL PRIMARY KEY,
            user_id {user_id_type},
            theme VARCHAR(40) DEFAULT 'nebula',
            timezone VARCHAR(80) DEFAULT 'Europe/Paris',
            start_hour INTEGER DEFAULT 9,
            end_hour INTEGER DEFAULT 18,
            focus_minutes INTEGER DEFAULT 50,
            break_minutes INTEGER DEFAULT 10,
            email_notifications BOOLEAN DEFAULT FALSE,
            weekly_digest BOOLEAN DEFAULT TRUE,
            ai_mode VARCHAR(40) DEFAULT 'planner',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        '''
    )
    _ensure_user_id_column(cur, 'user_settings', user_id_type, unique=True, add_fk=True)

    cur.execute(
        f'''
        CREATE TABLE IF NOT EXISTS calendar_tasks (
            id SERIAL PRIMARY KEY,
            user_id {user_id_type},
            title VARCHAR(255) NOT NULL,
            description TEXT DEFAULT '',
            task_date DATE NOT NULL,
            task_time TIME NULL,
            duration_minutes INTEGER DEFAULT 60,
            priority VARCHAR(20) DEFAULT 'medium',
            status VARCHAR(20) DEFAULT 'pending',
            source VARCHAR(40) DEFAULT 'manual',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        '''
    )
    _ensure_user_id_column(cur, 'calendar_tasks', user_id_type, unique=False, add_fk=True)

    cur.execute("ALTER TABLE calendar_tasks ADD COLUMN IF NOT EXISTS description TEXT DEFAULT '';")
    cur.execute("ALTER TABLE calendar_tasks ADD COLUMN IF NOT EXISTS duration_minutes INTEGER DEFAULT 60;")
    cur.execute("ALTER TABLE calendar_tasks ADD COLUMN IF NOT EXISTS priority VARCHAR(20) DEFAULT 'medium';")
    cur.execute("ALTER TABLE calendar_tasks ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'pending';")
    cur.execute("ALTER TABLE calendar_tasks ADD COLUMN IF NOT EXISTS source VARCHAR(40) DEFAULT 'manual';")
    cur.execute("ALTER TABLE calendar_tasks ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
    cur.execute("ALTER TABLE calendar_tasks ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
    cur.execute("UPDATE calendar_tasks SET description = '' WHERE description IS NULL;")
    cur.execute("UPDATE calendar_tasks SET duration_minutes = 60 WHERE duration_minutes IS NULL;")
    cur.execute("UPDATE calendar_tasks SET priority = 'medium' WHERE priority IS NULL;")
    cur.execute("UPDATE calendar_tasks SET status = 'pending' WHERE status IS NULL;")
    cur.execute("UPDATE calendar_tasks SET source = 'manual' WHERE source IS NULL;")

    conn.commit()
    cur.close()
    conn.close()


def fetch_all(query, params=None):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(query, params or ())
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def fetch_one(query, params=None):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(query, params or ())
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return row


def execute(query, params=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params or ())
    affected = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    return affected
