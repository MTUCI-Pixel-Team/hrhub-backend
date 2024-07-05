# для запуска бота выполните команду "Python manage.py run_vk_bot" в командной строке, находясь в корневой папке проекта
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from django.core.management.base import BaseCommand
from django.conf import settings
from user_app.models import User
from messaging_app.models import Message
from services_app.models import ServiceAccount


class Command(BaseCommand):
    help = 'Запуск бота ВКонтакте'

    def __init__(self):
        self.hr_selections = {}

    def handle(self, *args, **options):
        vk_session = vk_api.VkApi(token=settings.VK_TOKEN)
        vk = vk_session.get_api()
        longpoll = VkLongPoll(vk_session)

        print("Бот запущен")

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                user_id = event.user_id
                message = event.text.lower()

                if message == "старт":
                    self.send_hr_list(vk, user_id)
                elif message.isdigit():
                    self.process_hr_selection(vk, user_id, int(message))
                else:
                    self.save_message(vk, user_id, message)

    def send_hr_list(self, vk, user_id):
        vk_accounts = ServiceAccount.objects.filter(service_name="vk")
        hr_ids = [account.user_id_id for account in vk_accounts]
        hr_list = User.objects.filter(id__in=hr_ids).order_by("created_at")
        response = "Выберите HR, которому вы хотите написать:\n"
        for hr in hr_list:
            response += f"{hr.id}. {hr.username}\n"
        vk.messages.send(user_id=user_id, message=response,
                         random_id=get_random_id())

    def process_hr_selection(self, vk, user_id, hr_id):
        try:
            hr = User.objects.get(id=hr_id)
            self.hr_selections[user_id] = hr_id
            vk.messages.send(
                user_id=user_id,
                message=f"Вы выбрали {hr.username}. Напишите ваше сообщение.",
                random_id=get_random_id()
            )

        except User.DoesNotExist:
            vk.messages.send(
                user_id=user_id,
                message="HR не найден. Попробуйте еще раз.",
                random_id=get_random_id()
            )

    def save_message(self, vk, user_id, text):
        hr_id = self.hr_selections.get(user_id)
        service_account = ServiceAccount.objects.get(user_id=hr_id)
        from_username = vk.users.get(user_ids=user_id)[0]["first_name"]
        personal_chat_link = f"https://vk.com/id{user_id}"
        # Получаем сохраненный выбор HR для пользователя
        receiver = self.hr_selections.get(user_id)
        if receiver is not None:
            # Используем сохраненный hr_id для получения объекта HR
            receiver = User.objects.get(id=receiver)
            Message.objects.create(
                account=service_account,
                from_username=from_username,
                text=text,
                personal_chat_link=personal_chat_link,)
            vk.messages.send(
                user_id=user_id,
                message="Сообщение отправлено и сохранено. HR свяжется с вами в ближайшее время.",
                random_id=get_random_id()
            )
        else:
            # Обработка случая, когда HR не был выбран
            vk.messages.send(
                user_id=user_id,
                message="HR не был выбран. Пожалуйста, выберите HR.",
                random_id=get_random_id()
            )
