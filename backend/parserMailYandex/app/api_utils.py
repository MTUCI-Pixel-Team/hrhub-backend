import email
import imaplib
import json
from datetime import datetime, timezone
from email.header import decode_header

import aiohttp


async def get_hr_list():
    """
        Функция возвращает список почт HR-ов, их пароли приложений и id
    """
    async with aiohttp.ClientSession() as session:
        async with session.get('http://147.45.40.23:7000/api/service/list_yandex_mail/') as response:
            if response.status == 200:
                hrs_data = await response.json()
                return [[hr['email'] for hr in hrs_data], [hr['app_password'] for hr in hrs_data], [hr['id'] for hr in hrs_data]]
            else:
                return None


async def read_incoming_emails(email_user, email_password, hr_id):
    """
        Функция отправляет каждое сообщение в виде словаря в БД для сохранения и передачи на front

        В словаре 5 полей: 'hr_id', 'subject', 'username', 'email', 'text'
        subject - тема письма, text - текст письма, username - имя отправителя,
        email - email отправителя, hr_id - id HR-а, которому написали сообщения

        Функция вызывается раз в 10 секунд (дольше, если hr'ов будет очень много)
    """
    mail = imaplib.IMAP4_SSL('imap.yandex.ru')
    try:
        mail.login(email_user, email_password)
    except imaplib.IMAP4.error:
        return ('Ошибка авторизации')
    # Папка "Входящие"
    mail.select('inbox')

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

        message_info['hr_id'] = hr_id
        message_info['subject'] = subject
        message_info['username'] = from_[0].strip()
        message_info['email'] = from_[1].replace('>', '').strip('\r\n')

        # Если сообщение многочастное, получаем тело сообщения
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    try:
                        if 'text' not in message_info.keys():
                            message_info['text'] = body
                        else:
                            raise ValueError('Сообщение содержит несколько текстовых частей')
                    except ValueError as e:
                        print(e)
                        # Переходим к следующей итерации цикла т,к в этой не получится отдать данные в нормальном виде
                        continue
        else:
            print('Сообщение не удалось декодировать')
        # Добавляем текст в данные, которые будем передавать
        try:
            if 'text' not in message_info.keys():
                raise ValueError('Ошибка при получении текста сообщения')
            else:
                response_data.append(message_info)
                await info_to_db(message_info)
        except ValueError as e:
            print(e)
            # Переходим к следующей итерации цикла т,к в этой не получится отдать данные в нормальном виде
            continue
    mail.logout()
    if response_data:
        return response_data
    else:
        return ('Новых писем нет')


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
            else:
                print(f"Ошибка при отправке сообщения в базу данных. Статус: {response.status}, Ответ: {response_text}")
