import requests
from django.conf import settings
from services_app.models import ServiceAccount
from django.shortcuts import get_object_or_404


def get_tokens(client_id, client_secret, authorization_code):
    token_url = 'https://api.avito.ru/token'

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    token_params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'authorization_code',
        'code': authorization_code,
    }

    response = requests.post(token_url, headers=headers, data=token_params)
    if response.status_code == 200:
        token_data = response.json()
        tokens = {
            'access_token': token_data['access_token'],
            'refresh_token': token_data['refresh_token']
        }
        return tokens
    else:
        return response.status_code


def refresh_tokens(client_id, client_secret, refresh_token):
    token_url = 'https://api.avito.ru/token'

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    token_params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }

    response = requests.post(token_url, headers=headers, data=token_params)

    if response.status_code == 200:
        token_data = response.json()
        tokens = {
            'access_token': token_data['access_token'],
            'refresh_token': token_data['refresh_token']
        }
        return tokens
    else:
        return response.status_code


def get_user(token, hr_id=None):
    user_info_url = 'https://api.avito.ru/core/v1/accounts/self'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(user_info_url, headers=headers)
    if response.status_code == 200:
        user_info = response.json()
        user = {
            'email': user_info['email'],
            'id': user_info['id'],
            'name': user_info['name'],
            "phone": user_info['phone'],
            "profile_url": user_info['profile_url']
        }
        return user

    elif response.status_code == 403:
        service = get_object_or_404(ServiceAccount, user_id=hr_id, service_name='Avito')
        tokens = refresh_tokens(settings.CLIENT_ID, settings.CLIENT_SECRET, service.refresh_token)
        if tokens == 403:
            return "Refresh token is invalid. Please, re-login."
        elif isinstance(tokens, int):
            return tokens
        service.objects.update(access_token=tokens['access_token'], refresh_token=tokens['refresh_token'])
        return get_user(tokens['access_token'])

    else:
        return response.status_code


def get_chats(hr_id):
    service_account = get_object_or_404(ServiceAccount, user_id=hr_id, service_name='Avito')
    chats_info_url = f'https://api.avito.ru/messenger/v2/accounts/{service_account.service_user_id}/chats/'

    params = {
        'unread_only': 'true'
    }
    headers = {
        'Authorization': f'Bearer {service_account.access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(chats_info_url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 403:
        tokens = refresh_tokens(settings.CLIENT_ID, settings.CLIENT_SECRET, service_account.refresh_token)
        if tokens == 403:
            return "Refresh token is invalid. Please, re-login."
        elif isinstance(tokens, int):
            return tokens
        service_account.objects.update(access_token=tokens['access_token'], refresh_token=tokens['refresh_token'])
        return get_chats(hr_id)
    else:
        return response.status_code


def get_messages(hr_id, chat_id):
    service_account = get_object_or_404(ServiceAccount, user_id=hr_id, service_name='Avito')
    messages_url = f'https://api.avito.ru/messenger/v3/accounts/{service_account.service_user_id}/chats/{chat_id}/messages/'

    headers = {
        'Authorization': f'Bearer {service_account.access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(messages_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    if response.status_code == 403:
        tokens = refresh_tokens(settings.CLIENT_ID, settings.CLIENT_SECRET, service_account.refresh_token)
        if tokens == 403:
            return "Refresh token is invalid. Please, re-login."
        elif isinstance(tokens, int):
            return tokens
        service_account.objects.update(access_token=tokens['access_token'], refresh_token=tokens['refresh_token'])
        return get_messages(hr_id, chat_id)
    else:
        return response.status_code


def read_message(hr_id, chat_id):
    service_account = get_object_or_404(ServiceAccount, user_id=hr_id, service_name='Avito')
    read_message_url = f'https://api.avito.ru/messenger/v1/accounts/{service_account.service_user_id}/chats/{chat_id}/read'

    headers = {
        'Authorization': f'Bearer {service_account.access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.post(read_message_url, headers=headers)
    if response.status_code == 403:
        tokens = refresh_tokens(settings.CLIENT_ID, settings.CLIENT_SECRET, service_account.refresh_token)
        if tokens == 403:
            return "Refresh token is invalid. Please, re-login."
        elif isinstance(tokens, int):
            return tokens
        service_account.objects.update(access_token=tokens['access_token'], refresh_token=tokens['refresh_token'])
        return read_message(hr_id, chat_id)
    return response.status_code


def set_webhook(token, webhook_url):
    url = "https://api.avito.ru/messenger/v3/webhook"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    data = {
        "url": webhook_url,
    }
    response = requests.post(url, headers=headers, json=data)
    return response
