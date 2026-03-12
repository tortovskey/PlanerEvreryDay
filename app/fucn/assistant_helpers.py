import re
from datetime import date, datetime, timedelta

WEEKDAYS = {
    'понедельник': 0,
    'вторник': 1,
    'среда': 2,
    'четверг': 3,
    'пятница': 4,
    'суббота': 5,
    'воскресенье': 6,
}


def normalize_text(text: str) -> str:
    return ' '.join((text or '').strip().lower().split())


def detect_priority(text: str) -> str:
    text = normalize_text(text)
    if any(word in text for word in ['срочно', 'важно', 'high', 'критично']):
        return 'high'
    if any(word in text for word in ['низкий', 'несрочно', 'low', 'когда-нибудь']):
        return 'low'
    return 'medium'


def extract_time(text: str):
    match = re.search(r'([01]?\d|2[0-3]):([0-5]\d)', text)
    if not match:
        return None
    return f"{int(match.group(1)):02d}:{match.group(2)}"


def extract_date(text: str):
    text_norm = normalize_text(text)
    today = date.today()
    if 'послезавтра' in text_norm:
        return (today + timedelta(days=2)).isoformat()
    if 'завтра' in text_norm:
        return (today + timedelta(days=1)).isoformat()
    if 'сегодня' in text_norm:
        return today.isoformat()

    explicit = re.search(r'(\d{4}-\d{2}-\d{2})', text_norm)
    if explicit:
        return explicit.group(1)

    ru_date = re.search(r'(\d{1,2})[./](\d{1,2})(?:[./](\d{2,4}))?', text_norm)
    if ru_date:
        day = int(ru_date.group(1))
        month = int(ru_date.group(2))
        year = int(ru_date.group(3)) if ru_date.group(3) else today.year
        if year < 100:
            year += 2000
        try:
            return date(year, month, day).isoformat()
        except ValueError:
            return None

    for name, weekday in WEEKDAYS.items():
        if name in text_norm:
            delta = (weekday - today.weekday()) % 7
            delta = 7 if delta == 0 else delta
            return (today + timedelta(days=delta)).isoformat()

    return today.isoformat()


def extract_title_for_new_task(text: str) -> str:
    source = text.strip()
    source = re.sub(r'(добавь|создай|запланируй|поставь|нужно|надо|задачу|мне|пожалуйста)', ' ', source, flags=re.IGNORECASE)
    source = re.sub(r'(сегодня|завтра|послезавтра|в\s+\d{1,2}:\d{2}|на\s+\d{1,2}[./]\d{1,2}(?:[./]\d{2,4})?|на\s+\d{4}-\d{2}-\d{2})', ' ', source, flags=re.IGNORECASE)
    source = re.sub(r'(срочно|важно|низкий|несрочно|high|medium|low|критично)', ' ', source, flags=re.IGNORECASE)
    source = re.sub(r'\s+', ' ', source).strip(' ,.-')
    return source[:255]


def is_create_intent(text: str) -> bool:
    text = normalize_text(text)
    return any(word in text for word in ['добавь', 'создай', 'запланируй', 'поставь задачу'])


def is_stats_intent(text: str) -> bool:
    text = normalize_text(text)
    return any(word in text for word in ['статист', 'сводк', 'сколько задач', 'прогресс'])


def is_today_intent(text: str) -> bool:
    text = normalize_text(text)
    return any(word in text for word in ['сегодня', 'на сегодня'])


def is_tomorrow_intent(text: str) -> bool:
    text = normalize_text(text)
    return 'завтра' in text and 'послезавтра' not in text
