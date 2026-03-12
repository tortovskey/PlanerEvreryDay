import re
from datetime import datetime, timedelta
from fucn.date_helpers import today_iso, tomorrow_iso
from fucn.planner_helpers import build_day_plan, focus_advice
from services.add_task import add_task_to_db, get_tasks_by_date, get_tasks_between, get_upcoming_tasks
from services.auth_service import get_settings

TIME_PATTERN = re.compile(r'(?:в\s*)?(\d{1,2}:\d{2})')
DURATION_PATTERN = re.compile(r'(\d{1,3})\s*(?:мин|минут|minutes?)', re.I)


def _extract_date(message: str):
    lower = message.lower()
    if 'завтра' in lower:
        return tomorrow_iso()
    if 'сегодня' in lower:
        return today_iso()
    match = re.search(r'(\d{4}-\d{2}-\d{2})', message)
    if match:
        return match.group(1)
    return today_iso()


def _extract_time(message: str):
    match = TIME_PATTERN.search(message)
    return match.group(1) if match else ''


def _extract_duration(message: str):
    match = DURATION_PATTERN.search(message)
    return int(match.group(1)) if match else 60


def _extract_priority(message: str):
    lower = message.lower()
    if any(word in lower for word in ['срочно', 'важно', 'важная', 'high']):
        return 'high'
    if any(word in lower for word in ['спокойно', 'не срочно', 'низкий', 'low']):
        return 'low'
    return 'medium'


def _extract_title(message: str):
    cleaned = re.sub(r'^(добавь|создай|запланируй|поставь)\s*', '', message.strip(), flags=re.I)
    cleaned = re.sub(r'\b(сегодня|завтра)\b', '', cleaned, flags=re.I)
    cleaned = TIME_PATTERN.sub('', cleaned)
    cleaned = DURATION_PATTERN.sub('', cleaned)
    cleaned = cleaned.strip(' ,.-')
    return cleaned[:255] if cleaned else 'Новая задача'


def handle_assistant_message(user_id, message):
    lower = message.lower().strip()
    settings = get_settings(user_id) or {'start_hour': 9, 'focus_minutes': 50, 'break_minutes': 10}

    if any(phrase in lower for phrase in ['план на день', 'спланируй день', 'распланируй день']):
        date_value = _extract_date(message)
        tasks = get_tasks_by_date(user_id, date_value)
        return {
            'reply': build_day_plan(tasks, settings, date_value),
            'mode': 'day_plan',
        }

    if 'сводк' in lower or 'summary' in lower:
        today_tasks = get_tasks_by_date(user_id, today_iso())
        upcoming = get_upcoming_tasks(user_id, 5)
        reply = [
            f"Сегодня задач: {len(today_tasks)}",
            f"Ближайших открытых: {len(upcoming)}",
            focus_advice(today_tasks),
        ]
        return {'reply': '\n'.join(reply), 'mode': 'summary'}

    if 'сегодня' in lower and 'задач' in lower:
        tasks = get_tasks_by_date(user_id, today_iso())
        if not tasks:
            return {'reply': 'На сегодня задач нет. Пустой день — это либо роскошь, либо тревожный пробел в системе.', 'mode': 'list'}
        lines = [f"- {task['title']} ({task['task_time'] or 'без времени'})" for task in tasks]
        return {'reply': 'Задачи на сегодня:\n' + '\n'.join(lines), 'mode': 'list'}

    if 'завтра' in lower and 'задач' in lower:
        tasks = get_tasks_by_date(user_id, tomorrow_iso())
        if not tasks:
            return {'reply': 'На завтра задач пока нет.', 'mode': 'list'}
        lines = [f"- {task['title']} ({task['task_time'] or 'без времени'})" for task in tasks]
        return {'reply': 'Задачи на завтра:\n' + '\n'.join(lines), 'mode': 'list'}

    if any(phrase in lower for phrase in ['что делать дальше', 'что дальше', 'с чего начать', 'focus']):
        upcoming = get_upcoming_tasks(user_id, 6)
        return {'reply': focus_advice(upcoming), 'mode': 'focus'}

    if any(word in lower for word in ['добавь', 'создай', 'запланируй', 'поставь']):
        task = add_task_to_db(
            user_id=user_id,
            title=_extract_title(message),
            description='Создано AI-помощником',
            task_date=_extract_date(message),
            task_time=_extract_time(message) or None,
            priority=_extract_priority(message),
            duration_minutes=_extract_duration(message),
            source='assistant',
        )
        reply = f"Готово. Добавил задачу «{task['title']}» на {task['task_date']} {str(task['task_time'])[:5] if task['task_time'] else ''}."
        return {'reply': reply.strip(), 'mode': 'create', 'created_task': task}

    date_value = _extract_date(message)
    tasks = get_tasks_by_date(user_id, date_value)
    return {
        'reply': build_day_plan(tasks, settings, date_value),
        'mode': 'fallback_plan',
    }
