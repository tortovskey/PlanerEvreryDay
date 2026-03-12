import os
from urllib.parse import urlencode
import requests
from core.DB import fetch_one
from services.auth_service import get_user_by_email, create_user, get_user_by_id

PROVIDERS = {
    'yandex': {
        'client_id': os.getenv('YANDEX_CLIENT_ID', ''),
        'client_secret': os.getenv('YANDEX_CLIENT_SECRET', ''),
        'auth_url': os.getenv('YANDEX_AUTH_URL', 'https://oauth.yandex.ru/authorize'),
        'token_url': os.getenv('YANDEX_TOKEN_URL', 'https://oauth.yandex.ru/token'),
        'userinfo_url': os.getenv('YANDEX_USERINFO_URL', 'https://login.yandex.ru/info?format=json'),
        'scopes': os.getenv('YANDEX_SCOPES', 'login:email login:info'),
    },
    'vk': {
        'client_id': os.getenv('VK_CLIENT_ID', ''),
        'client_secret': os.getenv('VK_CLIENT_SECRET', ''),
        'auth_url': os.getenv('VK_AUTH_URL', 'https://id.vk.com/authorize'),
        'token_url': os.getenv('VK_TOKEN_URL', 'https://id.vk.com/oauth2/auth'),
        'userinfo_url': os.getenv('VK_USERINFO_URL', 'https://id.vk.com/oauth2/public_info'),
        'scopes': os.getenv('VK_SCOPES', 'email'),
    },
}


def build_redirect_uri(request_root, provider):
    return f"{request_root.rstrip('/')}/auth/{provider}/callback"


def get_oauth_login_url(provider, request_root, state):
    cfg = PROVIDERS[provider]
    if not cfg['client_id']:
        raise RuntimeError(f'Для {provider} не настроен client_id')
    params = {
        'response_type': 'code',
        'client_id': cfg['client_id'],
        'redirect_uri': build_redirect_uri(request_root, provider),
        'state': state,
        'scope': cfg['scopes'],
    }
    return f"{cfg['auth_url']}?{urlencode(params)}"


def exchange_code(provider, request_root, code):
    cfg = PROVIDERS[provider]
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': cfg['client_id'],
        'client_secret': cfg['client_secret'],
        'redirect_uri': build_redirect_uri(request_root, provider),
    }
    response = requests.post(cfg['token_url'], data=payload, timeout=20)
    response.raise_for_status()
    return response.json()


def fetch_profile(provider, access_token):
    cfg = PROVIDERS[provider]
    if provider == 'yandex':
        response = requests.get(cfg['userinfo_url'], headers={'Authorization': f'OAuth {access_token}'}, timeout=20)
        response.raise_for_status()
        data = response.json()
        return {
            'provider_user_id': str(data.get('id') or data.get('default_email') or data.get('login')),
            'email': data.get('default_email') or data.get('emails', [None])[0],
            'display_name': data.get('real_name') or data.get('display_name') or data.get('login') or 'Yandex User',
        }
    response = requests.post(cfg['userinfo_url'], headers={'Authorization': f'Bearer {access_token}'}, timeout=20)
    response.raise_for_status()
    raw = response.json()
    user = raw.get('user', raw)
    email = raw.get('email') or user.get('email')
    display_name = user.get('first_name', '') + (' ' + user.get('last_name', '') if user.get('last_name') else '')
    display_name = display_name.strip() or user.get('screen_name') or 'VK User'
    return {
        'provider_user_id': str(user.get('user_id') or user.get('id')),
        'email': email,
        'display_name': display_name,
    }


def get_or_create_oauth_user(provider, profile):
    account = fetch_one(
        'SELECT user_id FROM oauth_accounts WHERE provider = %s AND provider_user_id = %s',
        (provider, profile['provider_user_id'])
    )
    if account:
        return get_user_by_id(account['user_id'])

    email = profile.get('email') or f"{provider}_{profile['provider_user_id']}@placeholder.local"
    user = get_user_by_email(email)
    if not user:
        user = create_user(email, os.urandom(12).hex(), profile['display_name'])
    fetch_one(
        '''
        INSERT INTO oauth_accounts (user_id, provider, provider_user_id, provider_email)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (provider, provider_user_id) DO UPDATE SET provider_email = EXCLUDED.provider_email
        RETURNING *
        ''',
        (user['id'], provider, profile['provider_user_id'], profile.get('email')),
    )
    return get_user_by_id(user['id'])
