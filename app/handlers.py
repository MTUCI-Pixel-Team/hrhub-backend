from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command, CommandStart
from aiogram import F, Router
import app.keyboards as kb
from aiogram.types import ContentType

router = Router()

# Функция возвращает словарь с информацией о пользователе
def get_info_about_user(message, contact=False):
    info_about_user = {
        'name': message.from_user.first_name,
        'lastName': message.from_user.last_name,
        'username': message.from_user.username,
        'id': message.from_user.id,
        'chatId': message.chat.id,
        'text': message.text,
        'date': message.date,
    }
    # Если пользователь согласился отправить номер телефона, то добавляем его в словарь
    if contact:
        info_about_user['phone'] = message.contact.phone_number
    return info_about_user

# Обработка /start, на этом этапе ещё не собираем информацию о пользователе
@router.message(CommandStart())
async def start(message: Message):
    await message.answer('Здравствуйте! Это чат с HR-специалистом. Если вы хотите откликнуться на вакансию, пожалуйста, нажмите кнопку ниже. После нажатия Вам предложат отправить в чат номер телефона - на Ваше усмотрение', reply_markup=kb.applyJob)

# Обработчик нажатия на кнопку "✅ Откликнуться (отправить номер телефона)"
@router.message(F.content_type == "contact")
async def contact_received(message: Message):
    info_about_user_with_phone = get_info_about_user(message, contact=True)
    print(info_about_user_with_phone)
    await message.answer(f"Спасибо, {info_about_user_with_phone['name']}, {info_about_user_with_phone['lastName']}! Мы получили ваш контакт. HR-специалист свяжется с вами в ближайшее время.", reply_markup=ReplyKeyboardRemove())

# обработчик всех сообщений, кроме тех, что уже обработаны выше
@router.message()
async def get_chat_id(message: Message):
    info_about_user = get_info_about_user(message)
    print(info_about_user)
    if info_about_user['text'] == '✅ Откликнуться (не отправлять номер телефона)':
        await message.answer(f"Спасибо, {info_about_user['name']}, {info_about_user['lastName']}. Информация HR-специалисту передана. Он свяжется с Вами в ближайшее время. Если хотите сообщить ещё какую-нибудь информацию о себе - можете написать в этот чат, HR её получит", reply_markup=ReplyKeyboardRemove())
    elif info_about_user['text'] == '✅ Откликнуться (отправить номер телефона)':
        await message.answer('Пожалуйста, отправьте Ваш номер телефона', reply_markup=kb.phone)