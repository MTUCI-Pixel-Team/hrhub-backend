"""
    Основной файл для парсинга личных непрочитанных сообщений из авито. 
    Тут происходят все основные действия. Подробнее расписано в комментариях
"""

import pickle
import sys
from time import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from paths import any_chat_path, icon_chats_path, spans_path, unread_chat_path, unread_messages_path, username_path

SCRIPT_TO_DOWN_PAGE = """var element = document.evaluate('//div[starts-with(@class, \"scroll-scroll\")]', document,
                                null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue; 
                                element.scrollTop = element.scrollHeight;"""


def timer_10_sec():
    """Таймер, на 10 секунд, который не дает программе идти дальше"""
    start_time = time()
    while time() - start_time < 10:
        pass
    return True

def get_unread_chat():
    """ 
    Находит первый непрочитанный чат на странице.

    Возвращает элемент WebElement, представляющий ссылку на непрочитанный чат,
    или None, если непрочитанные чаты не найдены.
    Сделал таким способом, а не через get_elements, потому что при
    перезагрузке меняются данные и к старым чатам не получится обратиться
    """
    spans = driver.find_elements(*spans_path)
    for span in spans:
        # Получаем значение CSS свойства color для каждого элемента span
        color = span.value_of_css_property('color')
        if color == 'rgba(0, 0, 0, 1)':
            # Пытаемся найти родительский элемент a для данного span
            unread_сhat = span.find_element(*unread_chat_path)
            break
    return unread_сhat


def get_count_unread_chats():
    """
    Возвращает количество непрочитанных чатов на странице.
    """
    cnt = 0
    spans = driver.find_elements(*spans_path)
    for span in spans:
        # Получаем значение CSS свойства color для каждого элемента span
        color = span.value_of_css_property('color')
        if color == 'rgba(0, 0, 0, 1)':
            # Пытаемся найти родительский элемент a для данного span
            cnt += 1
    return cnt


service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
wait = WebDriverWait(driver, 15, poll_frequency=1)
driver.get('https://www.avito.ru/')

# сохраняет куки в файл cookies.pkl
# from get_my_cookie import get_my_cookie

# sleep(50)
# get_my_cookie(driver.get_cookies())

# Удаляем все куки
driver.delete_all_cookies()

# Загружаем куки из файла
with open('cookies.pkl', 'rb') as file:
    cookies = pickle.load(file)  # Десериализация byte строки в объект Python

# Добавляем куки в браузер
for cookie in cookies:
    driver.add_cookie(cookie)
    # print(cookie)

# Обновляем страницу
driver.refresh()

# Ждем, пока появится кнопка чатов и нажимаем на неё
wait.until(EC.visibility_of_element_located(icon_chats_path)).click()
# Ждем, пока загрузятся чаты и приступаем к работе
wait.until(EC.visibility_of_element_located(any_chat_path))
# Для принудительной остановки программы с помощью Ctrl+C
try:
    while True:
        # Заглавные буквы т.к константа
        COUNT_UNREAD_CHAT = get_count_unread_chats()
        info_to_service = dict()
        unread_messages = []

        print(f'Количество непрочитанных чатов: {COUNT_UNREAD_CHAT}')
        for _ in range(COUNT_UNREAD_CHAT):
            chat = get_unread_chat()
            chat.click()
            wait.until(EC.visibility_of_element_located(unread_messages_path))
            # получаем имя пользователя и ссылку на чат
            username = driver.find_element(*username_path).text
            # url текущей страницы (страницы чата)
            link_to_chat = driver.current_url
            # Получаем все непрочитанные сообщения
            find_unread_messages = driver.find_elements(*unread_messages_path)
            print('Получили непрочитанные сообщения')
            for message in find_unread_messages:
                unread_messages.append(message.text)
            # Прокручиваем чат до конца, чтобы он стал прочитанным
            driver.execute_script(SCRIPT_TO_DOWN_PAGE)
            # Возвращаемся на страницу списка чатов
            driver.back()
            # Тут хранится информация
            info_to_service['username'] = username
            info_to_service['link_to_chat'] = link_to_chat
            info_to_service['messages'] = unread_messages
            """Тут должен быть код, который отправляет данные в сервис Илье"""
            print(info_to_service)
        timer_10_sec()
except KeyboardInterrupt:
    print('Программа завершена')
    sys.exit(0)