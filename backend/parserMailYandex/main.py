"""
    Файл отвечает за чтение входящих писем на почту HR-a
"""
import re
from time import sleep

from app.api_utils import get_hr_list, read_incoming_emails

# Паттерн для проверки почты на соответствие почте yandex.ru
PATTERN_YANDEX_EMAIL = r'^[a-zA-Z0-9._%+-]+@yandex\.ru$'

while True:
    HR_EMAILS, HR_PASSWORDS, HR_IDS = get_hr_list()
    print(f'Emails: {HR_EMAILS},\nPasswords: {HR_PASSWORDS}\n,IDS: {HR_IDS}')
    for index, email in enumerate(HR_EMAILS):
        try:
            if re.match(PATTERN_YANDEX_EMAIL, email) is None:
                raise ValueError('Неверный формат почты')
        except ValueError as e:
            print(e, f'Название почты: {email}')
            continue
        # HR_EMAILS[index] - тоже самое, что email, но для единой структуры пишу так
        read_incoming_emails(HR_EMAILS[index], HR_PASSWORDS[index], HR_IDS[index])
    sleep(10)
