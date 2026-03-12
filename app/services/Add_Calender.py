from core.DB import fetch_all, fetch_one


def get_tasks_by_month(user_id, year, month):
    return fetch_all(
        '''
        SELECT * FROM calendar_tasks
        WHERE user_id = %s
          AND EXTRACT(YEAR FROM task_date) = %s
          AND EXTRACT(MONTH FROM task_date) = %s
        ORDER BY task_date ASC, task_time ASC NULLS LAST, id ASC
        ''',
        (user_id, year, month),
    )


def get_stats(user_id):
    row = fetch_one(
        '''
        SELECT
            COUNT(*) AS total_tasks,
            COUNT(*) FILTER (WHERE status = 'done') AS done_tasks,
            COUNT(*) FILTER (WHERE task_date = CURRENT_DATE) AS today_tasks,
            COUNT(*) FILTER (WHERE task_date >= CURRENT_DATE AND status <> 'done') AS upcoming_tasks,
            COUNT(*) FILTER (WHERE priority = 'high' AND status <> 'done') AS high_priority_open
        FROM calendar_tasks
        WHERE user_id = %s
        ''',
        (user_id,),
    )
    return dict(row or {})
