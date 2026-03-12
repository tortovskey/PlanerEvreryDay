import os
from functools import wraps
from typing import Optional

from flask import request, jsonify, session, g
from itsdangerous import URLSafeTimedSerializer, BadSignature, BadTimeSignature, SignatureExpired
from werkzeug.security import generate_password_hash, check_password_hash

JWT_SECRET = os.getenv('JWT_SECRET', 'dev-jwt-secret-change-me')
ACCESS_MINUTES = int(os.getenv('JWT_ACCESS_MINUTES', '60'))
REFRESH_DAYS = int(os.getenv('JWT_REFRESH_DAYS', '30'))

_serializer = URLSafeTimedSerializer(JWT_SECRET, salt='planer-auth')


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return check_password_hash(password_hash, password)


def _make_token(user_id, token_type: str) -> str:
    return _serializer.dumps({'sub': str(user_id), 'type': token_type})


def create_access_token(user_id) -> str:
    return _make_token(user_id, 'access')


def create_refresh_token(user_id) -> str:
    return _make_token(user_id, 'refresh')


def decode_token(token: str, expected_type: Optional[str] = None):
    max_age = REFRESH_DAYS * 24 * 60 * 60 if expected_type == 'refresh' else ACCESS_MINUTES * 60
    try:
        payload = _serializer.loads(token, max_age=max_age)
    except (SignatureExpired, BadTimeSignature, BadSignature) as exc:
        raise ValueError('Недействительный или просроченный токен') from exc
    if expected_type and payload.get('type') != expected_type:
        raise ValueError('Неверный тип токена')
    return payload


def get_request_user_id(req=None):
    req = req or request
    auth = req.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        token = auth.split(' ', 1)[1].strip()
        payload = decode_token(token, expected_type='access')
        return str(payload['sub'])
    if session.get('user_id'):
        return str(session['user_id'])
    return None


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        try:
            user_id = get_request_user_id()
        except Exception:
            user_id = None
        if not user_id:
            return jsonify({'error': 'Нужна авторизация'}), 401
        g.user_id = user_id
        return view(*args, **kwargs)
    return wrapper
