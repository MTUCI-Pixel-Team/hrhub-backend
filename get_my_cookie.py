"""
Открываем программу из main.py, комментриуем все, и расскомментируем get_my_cookie(cookie).
Дальше запускаем программу, в открывшемся окне авторизуемся, и ждем
Программа сама запишет куки в файл cookies.pkl, после чего возвращаем код в начальное положение и запускаем программу
"""

import pickle
from time import sleep


def get_my_cookie(cookie):
    """
    Сохраняет куки в файл cookies.pkl для дальнейшнего использования.
    """

    sleep(60)
    pickle.dump(cookie, open('cookies.pkl', 'wb'))