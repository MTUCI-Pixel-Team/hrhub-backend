import pickle
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# from get_my_cookie import get_my_cookie
# сохраняет куки в файл cookies.pkl
# get_my_cookie(driver.get_cookies())


def get_unread_chat():
    """ 
    Находит первый непрочитанный чат на странице.

    Возвращает элемент WebElement, представляющий ссылку на непрочитанный чат,
    или None, если непрочитанные чаты не найдены.
    Сделал таким способом, а не через get_elements, потому что при
    перезагрузке меняются данные и к старым чатам не получится обратиться
    """
    spans = driver.find_elements('xpath', "//div[starts-with(@class, 'chat-message-message-')]//span")
    for span in spans:
        # Получаем значение CSS свойства color для каждого элемента span
        color = span.value_of_css_property('color')
        if color == 'rgba(0, 0, 0, 1)':
            # Пытаемся найти родительский элемент a для данного span
            unread_сhat = span.find_element('xpath', './/ancestor::a')
            break
    return unread_сhat


def get_count_unread_chats():
    """
    Возвращает количество непрочитанных чатов на странице.
    """
    cnt = 0
    spans = driver.find_elements('xpath', "//div[starts-with(@class, 'chat-message-message-')]//span")
    for span in spans:
        # Получаем значение CSS свойства color для каждого элемента span
        color = span.value_of_css_property('color')
        if color == 'rgba(0, 0, 0, 1)':
            # Пытаемся найти родительский элемент a для данного span
            cnt += 1
    return cnt


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

sleep(3)
# Обновляем страницу
driver.refresh()

sleep(3)

# Переходим на страницу мессенджера
driver.find_element('xpath',
                    '//a[@href="/profile/messenger" and @data-marker="header/messenger"]'
                    ).click()
sleep(3)

# Заглавные буквы т.к константа
COUNT_UNREAD_CHAT = get_count_unread_chats()

print(f'Количество непрочитанных чатов: {COUNT_UNREAD_CHAT}')
for _ in range(COUNT_UNREAD_CHAT):
    chat = get_unread_chat()
    sleep(3)
    chat.click()
    sleep(3)
    # получаем имя пользователя и ссылку на чат
    username = driver.find_element('xpath', '//a[starts-with(@class, "header-view-name-")]').text
    link_to_chat = driver.current_url
    print(f'Имя пользователя: {username}')
    print(f'Ссылка на чат: {link_to_chat}')
    # Получаем все непрочитанные сообщения
    unreadMessage = driver.find_elements('xpath', """//div[starts-with(@class,
    'new-messages-delimiter-root-')]/following-sibling::
    div[starts-with(@class, 'message-base-root-')]//span[@data-marker='messageText']""")
    print('Получили непрочитанные сообщения')
    for message in unreadMessage:
        print(message.text)
    driver.execute_script("""var element = document.evaluate('//div[starts-with(@class, \"scroll-scroll\")]', document,
                        null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue; 
                        element.scrollTop = element.scrollHeight;""")
    sleep(3)
    driver.back()
    sleep(3)