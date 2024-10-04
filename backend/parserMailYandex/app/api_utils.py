"""
    Файл содержит 3 функции
    get_hr_list возвращает список почт HR-ов, их пароли приложений и id
    read_incoming_emails отправляет каждое сообщение в виде словаря в БД для сохранения и передачи на front
    info_to_db отправляет информацию о сообщении на сервер
"""


import email
import imaplib
import json
from datetime import datetime, timezone
from email.header import decode_header

import aiohttp
from app.exceptions import MailTextException


async def get_hr_list():
    """
        Функция возвращает список почт HR-ов, их пароли приложений и id
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://147.45.40.23:7000/api/service/list_yandex_mail/') as response:
                if response.status == 200:
                    hrs_data = await response.json()
                    return [[hr['email'] for hr in hrs_data],
                            [hr['app_password'] for hr in hrs_data],
                            [hr['id'] for hr in hrs_data]]
                return None
    except BaseException as e:
        print('Ошибка при получении данных:', e)


async def read_incoming_emails(email_user, email_password, hr_id):
    """
        Функция отправляет каждое сообщение в виде словаря в БД для сохранения и передачи на front

        В словаре 5 полей: 'hr_id', 'subject', 'username', 'email', 'text'
        subject - тема письма, text - текст письма, username - имя отправителя,
        email - email отправителя, hr_id - id HR-а, которому написали сообщения

        Функция вызывается раз в 10 секунд (дольше, если hr'ов будет очень много)
    """
    try:
        mail = imaplib.IMAP4_SSL('imap.yandex.ru')
        try:
            mail.login(email_user, email_password)
        except imaplib.IMAP4.error:
            return 'Ошибка авторизации'
        # Папка "Входящие"
        mail.select('INBOX')

        response_data = []
        # Непрочитанные сообщения
        messages = mail.search(None, 'UNSEEN')[1]
        for num in messages[0].split():

            message_info = {}
            # Получение данных о письме
            data = mail.fetch(num, '(RFC822)')[1]
            email_msg = data[0][1]
            msg = email.message_from_bytes(email_msg)

            # Получение темы сообщения
            subject = decode_header(msg["Subject"])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()
            # Получение отправителя сообщения
            from_ = msg.get("From").split('<')

            username = from_[0].strip()
            if 'UTF-8' in username:
                byte_username = decode_header(from_[0].strip())
                username = ''.join(part[0].decode(part[1] or 'ascii') for part in byte_username)

            message_info['hr_id'] = hr_id
            message_info['subject'] = decode_mime_header(subject)
            message_info['username'] = decode_mime_header(username)
            message_info['email'] = from_[1].replace('>', '').strip('\r\n')
            
            if msg.is_multipart():
                for part in msg.walk():
                    # Проверяем, что это часть с нужным контентом (HTML или plain text)
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    if "attachment" not in content_disposition:
                        # Получаем только части с текстом (HTML или Plain text)
                        if content_type == "text/plain" or content_type == "text/html":
                            # Декодируем и возвращаем содержимое
                            payload = part.get_payload(decode=True)
                            body = payload.decode(part.get_content_charset() or 'utf-8')
                            message_info['text'] = body
            else:
                # Если письмо не multipart
                payload = msg.get_payload(decode=True)
                body = payload.decode(msg.get_content_charset() or 'utf-8')
                message_info['text'] = body.replace("</div>", " ", -1).replace("<div>", " ", -1)
            # Добавляем текст в данные, которые будем передавать
            try:
                if 'text' not in message_info:
                    raise MailTextException('Ошибка при получении текста сообщения')
                else:
                    response_data.append(message_info)
                    await info_to_db(message_info)
            except MailTextException as e:
                print(e)
                # Переходим к следующей итерации цикла т,к в этой не получится отдать данные в нормальном виде
                continue
        mail.logout()
        if response_data:
            return response_data
        else:
            return 'Новых писем нет'
    except BaseException as e:
        print('Ошибка при получении данных:', e)


# Функция для декодирования заголовков
def decode_mime_header(header_value):
    decoded_parts = decode_header(header_value)
    decoded_header = ''
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            decoded_header += part.decode(encoding or 'utf-8')
        else:
            decoded_header += part
    return decoded_header


async def info_to_db(info_about_message):
    """
        Функция отправляет информацию о сообщении на сервер
    """
    data = {
        "account_id": info_about_message['hr_id'],
        "from_username": info_about_message['username'],
        "text": info_about_message['text'],
        "personal_chat_link": f'https://mail.yandex.ru/compose?to={info_about_message["email"]}',
        "received_at": datetime.now(timezone.utc).isoformat(),
        "is_read": False,
    }

    async with aiohttp.ClientSession() as session:
        url = 'http://147.45.40.23:7000/api/message/create/'
        headers = {'Content-Type': 'application/json'}
        async with session.post(url, data=json.dumps(data), headers=headers) as response:
            response_text = await response.text()
            if response.status == 201:
                print("Сообщение успешно отправлено в базу данных")
                print(response_text)
            else:
                print(f"Ошибка при отправке сообщения в базу данных. Статус: {response.status}, Ответ: {response_text}")
