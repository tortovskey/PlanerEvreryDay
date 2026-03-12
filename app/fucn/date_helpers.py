from datetime import datetime, date, timedelta


def today_iso():
    return date.today().isoformat()


def tomorrow_iso():
    return (date.today() + timedelta(days=1)).isoformat()


def validate_date(value: str):
    datetime.strptime(value, '%Y-%m-%d')
    return True


def validate_time(value: str):
    datetime.strptime(value, '%H:%M')
    return True


def human_day_label(value: str):
    dt = datetime.strptime(value, '%Y-%m-%d').date()
    today = date.today()
    if dt == today:
        return 'Сегодня'
    if dt == today + timedelta(days=1):
        return 'Завтра'
    if dt == today - timedelta(days=1):
        return 'Вчера'
    return dt.strftime('%d.%m.%Y')
