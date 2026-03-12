from core.DB import fetch_all, fetch_one, execute


def add_task_to_db(user_id, title, description, task_date, task_time, priority='medium', duration_minutes=60, source='manual'):
    return fetch_one(
        '''
        INSERT INTO calendar_tasks (user_id, title, description, task_date, task_time, priority, status, duration_minutes, source)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
        ''',
        (user_id, title, description, task_date, task_time, priority, 'pending', duration_minutes, source),
    )


def get_tasks_by_date(user_id, task_date):
    return fetch_all(
        '''
        SELECT * FROM calendar_tasks
        WHERE user_id = %s AND task_date = %s
        ORDER BY task_time ASC NULLS LAST, priority DESC, id ASC
        ''',
        (user_id, task_date),
    )


def get_upcoming_tasks(user_id, limit=8):
    return fetch_all(
        '''
        SELECT * FROM calendar_tasks
        WHERE user_id = %s AND task_date >= CURRENT_DATE AND status <> 'done'
        ORDER BY task_date ASC, task_time ASC NULLS LAST, id ASC
        LIMIT %s
        ''',
        (user_id, limit),
    )


def search_tasks(user_id, query):
    like = f'%{query}%'
    return fetch_all(
        '''
        SELECT * FROM calendar_tasks
        WHERE user_id = %s AND (title ILIKE %s OR description ILIKE %s)
        ORDER BY task_date ASC, task_time ASC NULLS LAST
        LIMIT 20
        ''',
        (user_id, like, like),
    )


def update_task_in_db(user_id, task_id, title, description, task_date, task_time, priority, duration_minutes=60):
    return fetch_one(
        '''
        UPDATE calendar_tasks
        SET title = %s,
            description = %s,
            task_date = %s,
            task_time = %s,
            priority = %s,
            duration_minutes = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND user_id = %s
        RETURNING *
        ''',
        (title, description, task_date, task_time, priority, duration_minutes, task_id, user_id),
    )


def delete_task_from_db(user_id, task_id):
    return execute('DELETE FROM calendar_tasks WHERE id = %s AND user_id = %s', (task_id, user_id)) > 0


def set_task_status(user_id, task_id, status):
    return fetch_one(
        '''
        UPDATE calendar_tasks
        SET status = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND user_id = %s
        RETURNING *
        ''',
        (status, task_id, user_id),
    )


def get_tasks_between(user_id, start_date, end_date):
    return fetch_all(
        '''
        SELECT * FROM calendar_tasks
        WHERE user_id = %s AND task_date BETWEEN %s AND %s
        ORDER BY task_date ASC, task_time ASC NULLS LAST
        ''',
        (user_id, start_date, end_date),
    )
