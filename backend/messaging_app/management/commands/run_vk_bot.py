# для запуска бота выполните команду "Python manage.py run_vk_bot" в командной строке, находясь в корневой папке проекта
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from django.core.management.base import BaseCommand
from django.conf import settings
from user_app.models import User
from services_app.models import ServiceAccount
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from django.shortcuts import get_object_or_404
from messaging_app.serializers import MessageSerializer
import requests
import math
import time
import re
import json


class Command(BaseCommand):
    help = "Запуск бота ВКонтакте"

    def __init__(self):
        self.current_hr = None
        self.phone_number = {}
        self.user_states = {}
        self.page = 1

    def update_hr(self, new_hr):
        self.current_hr = new_hr

    def is_valid_phone_number(self, phone_number):
        pattern = r"^\+\d+$"
        phone_number = str(phone_number)
        if phone_number.startswith("8"):
            phone_number = "+7" + phone_number[1:]
        if (
            bool(re.match(pattern, phone_number))
            and len(phone_number) > 7
            and len(phone_number) > 10
        ):
            return phone_number
        else:
            return 0

    def handle(self, *args, **options):
        while True:
            try:
                self.run_bot()
            except Exception as e:
                print(f"Произошла ошибка: {e}. Перезапуск бота через 10 секунд...")
                time.sleep(5)  # Подождать перед перезапуском

    def run_bot(self):
        print("Запуск бота ВКонтакте...")
        print(settings.VK_TOKEN)
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
                elif message == "выбрать hr" and self.user_states[user_id] == "start":
                    self.send_hr_list(vk, user_id)
                    self.user_states[user_id] = "choose_hr"
                elif (
                    self.user_states.get(user_id) == "choose_hr" and message == "вперед"
                ):
                    self.page += 1
                    self.send_hr_list(vk, user_id, self.page)
                elif (
                    self.user_states.get(user_id) == "choose_hr" and message == "назад"
                ):
                    self.page -= 1
                    self.send_hr_list(vk, user_id, self.page)
                elif self.user_states.get(user_id) == "choose_hr":
                    message = message.split(".")[0]
                    if message.isdigit():
                        self.process_hr_selection(vk, user_id, int(message))
                    else:
                        vk.messages.send(
                            user_id=user_id,
                            message="Введите корректный id",
                            random_id=get_random_id(),
                        )
                elif self.user_states.get(user_id) == "choose_phone or write_message":
                    if message == "оставить номер":
                        vk.messages.send(
                            user_id=user_id,
                            message="Введите контактный номер телефона",
                            random_id=get_random_id(),
                        )
                        self.user_states[user_id] = "choose_phone"
                    elif message == "пропустить":
                        vk.messages.send(
                            user_id=user_id,
                            message="Напишите ваше сообщение",
                            random_id=get_random_id(),
                        )
                        self.user_states[user_id] = "write_message"
                        self.phone_number[user_id] = None
                elif self.user_states.get(user_id) == "choose_phone":
                    self.save_phone_number(vk, user_id, message)
                elif self.user_states.get(user_id) == "write_message":
                    self.save_message(vk, user_id, message)
                else:
                    self.send_help_message(vk, user_id)
                    self.user_states[user_id] = None

    def send_start_message(self, vk, user_id):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button("Выбрать HR", VkKeyboardColor.PRIMARY)
        keyboard.add_button("Помощь", VkKeyboardColor.PRIMARY)
        vk.messages.send(
            user_id=user_id,
            message="Привет! Для начала работы нажмите кнопку 'Выбрать HR'. Если вам нужна помощь, нажмите 'Помощь'.",
            keyboard=keyboard.get_keyboard(),
            random_id=get_random_id(),
        )
        self.user_states[user_id] = "start"

    def send_help_message(self, vk, user_id):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button("Старт", VkKeyboardColor.PRIMARY)
        vk.messages.send(
            user_id=user_id,
            message=(
                "Этот бот предназначен для связи с HR,  зарегистрировавшимися на сайте HRhub. Для начала работы нажмите Старт, далее нажмите кнопку 'Выбрать HR'\n"
                "и выберите нужного HR из списка. После этого напишите ваше сообщение. После сообщения вы можете оставить свою контактную информацию"
            ),
            keyboard=keyboard.get_keyboard(),
            random_id=get_random_id(),
        )
        self.user_states[user_id] = "start"

    def send_hr_list(self, vk, user_id, page=1, items_per_page=12):
        if page < 1:
            page = 1
        vk_accounts = ServiceAccount.objects.filter(service_name="vk")
        hr_ids = [account.user_id_id for account in vk_accounts]
        hr_list = User.objects.filter(id__in=hr_ids).order_by("id")

        total_pages = math.ceil(len(hr_list) / items_per_page)
        if page > total_pages:
            page = total_pages

        start_index = (page - 1) * items_per_page
        end_index = start_index + items_per_page
        current_hr_list = hr_list[start_index:end_index]

        response = "Выберите HR, которому вы хотите написать:\n"
        keyboard = VkKeyboard(one_time=True)
        counter = 0
        for hr in current_hr_list:
            if counter == 3 and current_hr_list != 3:
                keyboard.add_line()
                counter = 0
            keyboard.add_button(f"{hr.id}. {hr.username}", VkKeyboardColor.PRIMARY)
            counter += 1

        response += f"Страница {page} из {total_pages}"

        if total_pages == 1:
            vk.messages.send(
                user_id=user_id,
                message=response,
                keyboard=keyboard.get_keyboard(),
                random_id=get_random_id(),
            )
        else:
            keyboard.add_line()
            if page > 1 and page < total_pages:
                keyboard.add_button("Назад", VkKeyboardColor.SECONDARY)
                keyboard.add_button("Вперед", VkKeyboardColor.SECONDARY)
            elif page > 1:
                keyboard.add_button("Назад", VkKeyboardColor.SECONDARY)
            elif page < total_pages:
                keyboard.add_button("Вперед", VkKeyboardColor.SECONDARY)

            vk.messages.send(
                user_id=user_id,
                message=response,
                keyboard=keyboard.get_keyboard(),
                random_id=get_random_id(),
            )

    def process_hr_selection(self, vk, user_id, hr_id):
        try:
            hr = User.objects.get(id=hr_id)
            ServiceAccount.objects.get(user_id=hr.id, service_name="vk")
            self.update_hr(hr)
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button("Оставить номер", VkKeyboardColor.PRIMARY)
            keyboard.add_button("Пропустить", VkKeyboardColor.PRIMARY)
            vk.messages.send(
                user_id=user_id,
                message=f"Вы выбрали {self.current_hr.username}.Можете оставить свой номер телефона для связи, перед тем как продолжить",
                keyboard=keyboard.get_keyboard(),
                random_id=get_random_id(),
            )
            self.user_states[user_id] = "choose_phone or write_message"
            service_account = get_object_or_404(
                ServiceAccount, user_id=self.current_hr, service_name="vk"
            )
            from_username = vk.users.get(user_ids=user_id)[0]["first_name"]
            personal_chat_link = f"https://vk.com/id{user_id}"
            if self.current_hr is not None:
                message_serializer = MessageSerializer(
                    data={
                        "account_id": service_account.id,
                        "from_username": from_username,
                        "text": "Потенциальный сотрудник откликнулся на ваше объявление",
                        "personal_chat_link": personal_chat_link,
                    }
                )
                if message_serializer.is_valid():
                    url = "http://193.233.114.35:7000/api/message/create/"
                    headers = {"Content-Type": "application/json"}
                    requests.post(
                        url, headers=headers, data=json.dumps(message_serializer.data)
                    )

        except User.DoesNotExist:
            vk.messages.send(
                user_id=user_id,
                message="HR не найден. Попробуйте еще раз.",
                random_id=get_random_id(),
            )
        except ServiceAccount.DoesNotExist or User.DoesNotExist:
            vk.messages.send(
                user_id=user_id,
                message="HR не найден. Попробуйте еще раз.",
                random_id=get_random_id(),
            )

    def save_phone_number(self, vk, user_id, phone_number):
        if self.is_valid_phone_number(phone_number):
            self.phone_number[user_id] = self.is_valid_phone_number(phone_number)
            vk.messages.send(
                user_id=user_id,
                message="Номер сохранен. Можете ввести дополнительную информацию",
                random_id=get_random_id(),
            )
            self.user_states[user_id] = "write_message"
        else:
            vk.messages.send(
                user_id=user_id,
                message="Неверный формат номера",
                random_id=get_random_id(),
            )
            self.user_states[user_id] = "choose_phone"

    def save_message(self, vk, user_id, text):
        service_account = get_object_or_404(
            ServiceAccount, user_id=self.current_hr, service_name="vk"
        )
        from_username = vk.users.get(user_ids=user_id)[0]["first_name"]
        personal_chat_link = f"https://vk.com/id{user_id}"
        if self.current_hr is not None:
            if self.phone_number[user_id]:
                message_serializer = MessageSerializer(
                    data={
                        "account_id": service_account.id,
                        "from_username": from_username,
                        "from_userphone": self.phone_number[user_id],
                        "text": text,
                        "personal_chat_link": personal_chat_link,
                    }
                )
            else:
                message_serializer = MessageSerializer(
                    data={
                        "account_id": service_account.id,
                        "from_username": from_username,
                        "text": text,
                        "personal_chat_link": personal_chat_link,
                    }
                )
            if message_serializer.is_valid():
                url = "http://193.233.114.35:7000/api/message/create/"
                headers = {"Content-Type": "application/json"}
                response = requests.post(
                    url, headers=headers, data=json.dumps(message_serializer.data)
                )
                if response.status_code == 201:
                    vk.messages.send(
                        user_id=user_id,
                        message="Сообщение отправлено и сохранено. HR свяжется с вами в ближайшее время.",
                        random_id=get_random_id(),
                    )
                    self.user_states[user_id] = None
                else:
                    vk.messages.send(
                        user_id=user_id,
                        message="Ошибка при сохранении сообщения. Попробуйте еще раз. Для перезапуска бота напишете 'Старт'",
                        random_id=get_random_id(),
                    )
            else:
                vk.messages.send(
                    user_id=user_id,
                    message="Ошибка при обработке данных. Попробуйте еще раз. Для перезапуска бота напишете 'Старт'",
                    random_id=get_random_id(),
                )
        else:
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button("Выбрать HR", VkKeyboardColor.PRIMARY)
            vk.messages.send(
                user_id=user_id,
                message="HR не был выбран. Пожалуйста, выберите HR.",
                keyboard=keyboard.get_keyboard(),
                random_id=get_random_id(),
            )
            self.user_states[user_id] = "start"
