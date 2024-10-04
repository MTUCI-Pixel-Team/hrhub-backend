import aiohttp
import json
import re
from datetime import datetime, timezone


def is_specialist_selection_message(text):
    return bool(re.search(r".* \(ID: \d+\)$", text))


async def send_message_to_db(info_about_user):
    if is_specialist_selection_message(info_about_user['text']):
        return

    personal_chat_link = f"https://web.telegram.org/k/#@{info_about_user['username']}"
    data = {
        "account_id": info_about_user['service_account_id'],
        "from_username": info_about_user['username'],
        "from_userphone": info_about_user.get('phone', ''),
        "text": info_about_user['text'],
        "personal_chat_link": personal_chat_link,
        "received_at": datetime.now(timezone.utc).isoformat(),
        "is_read": False,
    }

    async with aiohttp.ClientSession() as session:
        url = 'http://193.233.114.35:7000/api/message/create/'
        headers = {'Content-Type': 'application/json'}
        async with session.post(url, data=json.dumps(data), headers=headers) as response:
            response_text = await response.text()
            if response.status == 201:
                print("Сообщение успешно отправлено в базу данных")
            else:
                print(
                    f"Ошибка при отправке сообщения в базу данных. Статус: {response.status}, Ответ: {response_text}")
