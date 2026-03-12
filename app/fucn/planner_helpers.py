from datetime import datetime, timedelta


def sort_tasks_for_focus(tasks):
    priority_weight = {'high': 0, 'medium': 1, 'low': 2}
    def key(task):
        date_part = str(task.get('task_date') or '')
        time_part = str(task.get('task_time') or '23:59')[:5]
        return (
            task.get('status') == 'done',
            priority_weight.get(task.get('priority'), 1),
            date_part,
            time_part,
            task.get('id', 0),
        )
    return sorted(tasks, key=key)


def build_day_plan(tasks, settings, date_label):
    start_hour = settings.get('start_hour', 9)
    focus = settings.get('focus_minutes', 50)
    pause = settings.get('break_minutes', 10)
    current = datetime.strptime(f'{date_label} {start_hour:02d}:00', '%Y-%m-%d %H:%M')
    lines = []
    sorted_tasks = sort_tasks_for_focus(tasks)
    for index, task in enumerate(sorted_tasks[:8], start=1):
        duration = int(task.get('duration_minutes') or 60)
        duration = max(20, min(duration, 240))
        start = current.strftime('%H:%M')
        current += timedelta(minutes=duration)
        end = current.strftime('%H:%M')
        marker = '⭐' if task.get('priority') == 'high' else '•'
        lines.append(f"{marker} {start}-{end} — {task.get('title')}")
        if index < len(sorted_tasks[:8]):
            current += timedelta(minutes=pause)
    if not lines:
        return 'На этот день задач нет. Лучший план — создать 1 важную задачу и 1 короткую, иначе день превращается в философию без действий.'
    return '\n'.join(lines)


def focus_advice(tasks):
    open_tasks = [t for t in tasks if t.get('status') != 'done']
    high = [t for t in open_tasks if t.get('priority') == 'high']
    if high:
        return f"Начни с важной задачи: {high[0]['title']}. Потом добей одну короткую. Так мозг получает и результат, и импульс."
    if open_tasks:
        return f"Сначала закрой самую раннюю открытую задачу: {open_tasks[0]['title']}. Не дроби внимание на пять фронтов сразу."
    return 'Все задачи закрыты. Это редкий момент цивилизации. Можно планировать завтра.'
