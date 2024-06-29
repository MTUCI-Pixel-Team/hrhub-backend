import pickle
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# from get_my_cookie import get_my_cookie
# сохраняет куки в файл cookies.pkl
# get_my_cookie(driver.get_cookies())

# Пропускаем чат с техподдержкой
number_of_chat = 2

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
wait = WebDriverWait(driver, 10, poll_frequency=1)
driver.get('https://www.avito.ru/')

# Удаляем все куки
driver.delete_all_cookies()

# Загружаем куки из файла
with open('cookies.pkl', 'rb') as file:
    cookies = pickle.load(file)  # Десериализация byte строки в объект Python

# Добавляем куки в браузер
for cookie in cookies:
    driver.add_cookie(cookie)
    # print(cookie)

sleep(5)
# Обновляем страницу
driver.refresh()

sleep(5)

# Переходим на страницу мессенджера
driver.find_element('xpath', 
                    '//a[@href="/profile/messenger" and @data-marker="header/messenger"]'
                    ).click()
sleep(3)
# Сколько всего чатов (за вычетом чата с техподдержкой)
chats_len = len(driver.find_elements('xpath', 
                    '//a[@data-marker="channels/channelLink"]'
                    )[1:])
print(f'Всего чатов: {chats_len}')
for _ in range(chats_len):
    sleep(3)
    chat = driver.find_element('xpath', 
                    f'(//a[@data-marker="channels/channelLink"])[{number_of_chat}]'
                    )
    chat.click()

    sleep(3)

    # Получаем все ЕГО сообщения
    spans = driver.find_elements('xpath', '//*[contains(@class, "message-base-left-")]//span[@data-marker="messageText"]')
    print(f'Chat {number_of_chat}')
    for span in spans:
        print(span.text)
    number_of_chat += 1
    driver.back()
    sleep(3)