from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart
import app.keyboards as kb
import re
from aiogram import Router
from aiogram import F

router = Router()
user_states = {}


def get_info_about_user(message, contact=False, service_account_id=None, text=None):
    user_id = message.from_user.id
    service_account_id = service_account_id if service_account_id else user_states.get(user_id, {}).get(
        'service_account_id')
    info_about_user = {
        'name': message.from_user.first_name,
        'lastName': message.from_user.last_name,
        'username': message.from_user.username,
        'id': user_id,
        'chatId': message.chat.id,
        'text': text if text is not None else message.text,
        'date': message.date,
        'service_account_id': service_account_id
    }
    if contact:
        info_about_user['phone'] = message.contact.phone_number
    return info_about_user


@router.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    user_states[user_id] = {"state": None, "service_account_id": None}
    keyboard = await kb.get_specialists_keyboard()
    await message.answer(
        'Здравствуйте! Это чат с HR-специалистом. Если вы хотите откликнуться, выберите HR-специалиста из списка',
        reply_markup=keyboard)


@router.message(F.content_type == "contact")
async def contact_received(message: Message):
    custom_text = "Потенциальный сотрудник откликнулся на ваше объявление и предоставил свой номер телефона"
    info_about_user_with_phone = get_info_about_user(message, contact=True, text=custom_text)
    print(info_about_user_with_phone)
    await message.answer(f"Спасибо, {info_about_user_with_phone['name']}! Мы получили ваш контакт. HR-специалист "
                         f"свяжется с вами в ближайшее время. Можете отправить дополнительную информацию о себе, "
                         f"мы так же отправим её специалисту", reply_markup=ReplyKeyboardRemove())
    user_states[message.from_user.id]["state"] = "awaiting_additional_info"


@router.message()
async def process_message(message: Message):
    user_id = message.from_user.id
    if "(ID: " in message.text:
        service_account_id_text = re.search(r"\(ID: (\d+)\)", message.text)
        if service_account_id_text:
            service_account_id = int(service_account_id_text.group(1))
            info_about_user = get_info_about_user(message, service_account_id=service_account_id)
            print(info_about_user)
            apply_keyboard = kb.apply_job_keyboard()
            await message.answer(
                f"Вы выбрали специалиста с ID: {service_account_id}. Если вы хотите откликнуться на вакансию, "
                f"пожалуйста, выберите, будете ли вы предоставлять свой телефон",
                reply_markup=apply_keyboard)
            user_states[message.from_user.id] = {"state": "awaiting_phone_number_decision",
                                                 "service_account_id": service_account_id}
    elif user_id in user_states:
        current_state = user_states[user_id].get("state")
        if current_state == "awaiting_phone_number_decision":
            if message.text == 'Откликнуться (не отправлять номер телефона)':
                custom_text = "Потенциальный сотрудник откликнулся на ваше объявление"
                info_about_user = get_info_about_user(message, text=custom_text)
                print(info_about_user)
                await message.answer(
                    "Спасибо за отклик. Ваша заявка на вакансию будет рассмотрена. Вы можете ввести дополнительную "
                    "информацию, рассказать о себе. Данные будут так же переданы специалисту.",
                    reply_markup=ReplyKeyboardRemove())
                user_states[user_id]["state"] = "awaiting_additional_info"
        elif current_state == "awaiting_additional_info":
            if message.text not in ['/start']:
                user_info = get_info_about_user(message)
                print(user_info)
                await message.answer("Спасибо за предоставленную информацию!")
                user_states[user_id]["state"] = None
            else:
                pass
        else:
            await message.answer("Не удалось распознать ваш запрос. Возможно вы уже обратились к специалисту. Для "
                                 "повторного обращения наберите /start")
    else:
        await message.answer("Не удалось распознать ваш запрос. Возможно вы уже обратились к специалисту. Для "
                             "повторного обращение наберите /start")
