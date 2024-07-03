"""
    Файл отвечает за чтение входящих писем с почты HR-a
"""
import re
from time import sleep

from read_incoming_emails import read_incoming_emails

PATTERN_YANDEX_EMAIL = r'^[a-zA-Z0-9._%+-]+@yandex\.ru$'

HR_EMAILS = ['jiopydryk011@yandex.ru', '1@yandex.ru']
# Пароль приложений. Создается в специальном разделе
HR_PASSWORDS = ['tdigxyrpiliyyyqq', '2']

assert len(HR_PASSWORDS) == len(HR_EMAILS), 'Количество паролей не совпадает с количеством почтовых ящиков'
while True:
    for i in range(min(len(HR_EMAILS), len(HR_PASSWORDS))):
        try:
            if re.match(PATTERN_YANDEX_EMAIL, HR_EMAILS[i]) is None:
                raise ValueError('Неверный формат почты')
        except ValueError as e:
            print(e, f'Название почты: {HR_EMAILS[i]}')
            continue
        print(read_incoming_emails(HR_EMAILS[i], HR_PASSWORDS[i]))
    sleep(10)