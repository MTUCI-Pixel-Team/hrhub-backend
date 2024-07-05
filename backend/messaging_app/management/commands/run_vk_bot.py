# для запуска бота выполните команду "Python manage.py run_vk_bot" в командной строке, находясь в корневой папке проекта
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from django.core.management.base import BaseCommand
from django.conf import settings
from user_app.models import User
from messaging_app.models import Message
from services_app.models import ServiceAccount
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import math

class Command(BaseCommand):
    help = 'Запуск бота ВКонтакте'

    def __init__(self):
        self.current_hr = None

    def update_hr(self, new_hr):
        self.current_hr = new_hr
        
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
                    self.send_start_message(vk, user_id)
                elif message == "помощь":
                    self.send_help_message(vk, user_id)
                elif message == "выбрать hr":
                    self.send_hr_list(vk, user_id)
                elif message == "Вперед":
                    self.send_hr_list(vk, user_id, page=self.hr_pages[user_id] + 1)
                elif message == "Назад":
                    self.send_hr_list(vk, user_id, page=self.hr_pages[user_id] - 1)
                elif message.isdigit():
                    self.process_hr_selection(vk, user_id, int(message))
                else:
                    self.save_message(vk, user_id, message)

    def send_start_message(self, vk, user_id):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button("Выбрать HR", VkKeyboardColor.PRIMARY)
        keyboard.add_button("Помощь", VkKeyboardColor.PRIMARY)
        vk.messages.send(
            user_id=user_id,
            message="Привет! Для начала работы нажмите кнопку 'Выбрать HR'. Если вам нужна помощь, нажмите 'Помощь'.",
            keyboard=keyboard.get_keyboard(),
            random_id=get_random_id()
        )
        
    def send_help_message(self, vk, user_id):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button("Выбрать HR", VkKeyboardColor.PRIMARY)
        vk.messages.send(
            user_id=user_id,
            message=("Этот бот предназначен для общения с HR,  зарегистрировавшимся на сайте HRhub. Для отправки сообщения HR нажмите кнопку 'Выбрать HR'\n"
                "и выберите нужного HR из списка. Выбор нужно производить набором цифр. После этого напишите ваше сообщение. Сообщение не должно состоять\n"
                "только из цифр, а также не должно быть одной из команд бота"),
            keyboard=keyboard.get_keyboard(),
            random_id=get_random_id()
        )

    def send_hr_list(self, vk, user_id, page=1, items_per_page=10):
        vk_accounts = ServiceAccount.objects.filter(service_name="vk")
        hr_ids = [account.user_id_id for account in vk_accounts]
        hr_list = User.objects.filter(id__in=hr_ids).order_by("created_at")
        
        total_pages = math.ceil(len(hr_list) / items_per_page)
    
        start_index = (page - 1) * items_per_page
        end_index = start_index + items_per_page
        current_hr_list = hr_list[start_index:end_index]

        response = "Выберите HR, которому вы хотите написать:\n"
        for hr in current_hr_list:
            response += f"{hr.id}. {hr.username}\n"
        response += f"Страница {page} из {total_pages}"
           
        if total_pages == 1:
            vk.messages.send(
                user_id=user_id, 
                message=response,
                random_id=get_random_id()
                )   
        else:    
            keyboard = VkKeyboard(one_time=True)
            if page > 1:
                keyboard.add_button("Назад", VkKeyboardColor.PRIMARY)
            if page < total_pages:
                keyboard.add_button("Вперед", VkKeyboardColor.PRIMARY)
    
            vk.messages.send(
                user_id=user_id, 
                message=response,
                keyboard=keyboard.get_keyboard(),
                random_id=get_random_id()
                )

    def process_hr_selection(self, vk, user_id, hr_id):
        try:
            hr = User.objects.get(id=hr_id)
            self.update_hr(hr)
            vk.messages.send(
                user_id=user_id,
                message=f"Вы выбрали {self.current_hr.username}. Напишите ваше сообщение.",
                random_id=get_random_id()
            )

        except User.DoesNotExist:
            vk.messages.send(
                user_id=user_id,
                message="HR не найден. Попробуйте еще раз.",
                random_id=get_random_id()
            )

    def save_message(self, vk, user_id, text):
        service_account = ServiceAccount.objects.get(user_id=self.current_hr)
        from_username = vk.users.get(user_ids=user_id)[0]["first_name"]
        personal_chat_link = f"https://vk.com/id{user_id}"
        # Получаем сохраненный выбор HR для пользователя
        if self.current_hr is not None:
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button("Выбрать HR", VkKeyboardColor.PRIMARY)
            # Используем сохраненный hr_id для получения объекта HR
            Message.objects.create(
                account=service_account,
                from_username=from_username,
                text=text,
                personal_chat_link=personal_chat_link,)
            vk.messages.send(
                user_id=user_id,
                message="Сообщение отправлено и сохранено. HR свяжется с вами в ближайшее время. Для того, чтобы изменить HR, нажмите 'Выбрать HR'. Также вы можете отправить еще одно сообщение.",
                keyboard=keyboard.get_keyboard(),
                random_id=get_random_id()
            )
        else:
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button("Выбрать HR", VkKeyboardColor.PRIMARY)
            # Обработка случая, когда HR не был выбран
            vk.messages.send(
                user_id=user_id,
                message="HR не был выбран. Пожалуйста, выберите HR.",
                keyboard=keyboard.get_keyboard(),
                random_id=get_random_id()
            )
