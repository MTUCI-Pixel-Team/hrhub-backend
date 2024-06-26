from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command, CommandStart
from aiogram import F, Router
import app.keyboards as kb
from aiogram.types import ContentType

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    await message.answer('Здравствуйте! Это чат с HR-специалистом. Если вы хотите откликнуться на вакансию, пожалуйста, нажмите кнопку ниже. После нажатия Вам предложат отправить в чат номер телефона - на Ваше усмотрение', reply_markup=kb.applyJob)

@router.message(F.text == '✅ Откликнуться (не отправлять номер телефона)')
async def help(message: Message):
    await message.answer('Информацию HR-специалисту передана. Он свяжется с Вами в ближайшее время в этом чате. Если хотите сообщить ещё какую-нибудь информацию о себе - пишите в этот чат, HR её получит', reply_markup=ReplyKeyboardRemove())

@router.message(F.content_type == "contact")
async def contact_received(message: Message):
    contact = message.contact
    await message.answer(f"Спасибо, {contact.first_name}, {contact.last_name}! Мы получили ваш контакт. HR-специалист свяжется с вами в ближайшее время.")

# обработчик всех сообщений
@router.message()
async def get_chat_id(message: Message):
    user_id = message.from_user.username
    print(user_id)
    await message.answer(f"Ссылка на Вас: @{user_id}")
# @router.message(F.text == True)
# async def catalog(message: Message):
#     await message.answer(F.text)