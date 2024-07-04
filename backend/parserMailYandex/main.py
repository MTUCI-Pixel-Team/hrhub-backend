"""
    Основной файл для получения непрочитанных сообщений с почты HR-ов
    Получает список данных HR'ов, которые хотят отслеживать свою почту Yandex
    Проверяет почту на соответствие шаблону yandex.ru
    Для каждого HR-а вызывает функцию read_incoming_emails для получения непрочитанных сообщений
"""
import asyncio
import re

from app.api_utils import get_hr_list, read_incoming_emails
from app.exceptions import NotYandexMailException

# Паттерн для проверки почты на соответствие почте yandex.ru
PATTERN_YANDEX_EMAIL = r'^[a-zA-Z0-9._%+-]+@yandex\.ru$'

async def main():
    """
        Функция каждую итерацию получает список HR-ов и их почты, пароли приложений и id
        Это необходимо для обновления данных, если появится новый HR
        После этого функция вызывает функцию read_incoming_emails для каждого HR-а
        И сохранит в БД список непрочитанных сообщений, которые были отправлены HR-у
    """
    try:
        while True:
            hr_emails, hr_passwords, hr_ids = await get_hr_list()
            print(f'Emails: {hr_emails},\nPasswords: {hr_passwords}\n,IDS: {hr_ids}')
            for index, email in enumerate(hr_emails):
                try:
                    if re.match(PATTERN_YANDEX_EMAIL, email) is None:
                        raise NotYandexMailException('Неверный формат почты')
                except NotYandexMailException as e:
                    print(e, f'Название почты: {email}')
                    continue
                # HR_EMAILS[index] - тоже самое, что email, но для единой структуры пишу так
                await read_incoming_emails(hr_emails[index], hr_passwords[index], hr_ids[index])
            await asyncio.sleep(10)  # Пауза перед следующей итерацией
    # Обработка всех непредвиденных ошибок
    except KeyboardInterrupt:
        print('Программа завершена')
    except BaseException as e:
        print('Необработанная ошибка:', e)

if __name__ == "__main__":
    asyncio.run(main())
