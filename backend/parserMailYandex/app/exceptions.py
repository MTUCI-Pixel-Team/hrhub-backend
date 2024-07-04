"""
    Файл с кастомными исключениями
    Более говорящие названия упрощают работу с ошибками
"""

class NotYandexMailException(Exception):
    """
        Ошибка вызывается, если почта не соответствует шаблону yandex.ru
    """
    def __init__(self, *args):
        super().__init__(*args)

class MailTextException(Exception):
    """
        Ошибка вызывается, если сообщение не удалось декодировать в нормальном виде
        Или если текст отсутствует
    """
    def __init__(self, *args):
        super().__init__(*args)
