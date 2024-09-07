from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
import aiohttp


async def get_specialists_keyboard():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://193.233.114.35:7000/api/service/list_tg/') as response:
            if response.status == 200:
                specialists = await response.json()
                keyboard = [[KeyboardButton(text=f"{specialist['service_username']} (ID: {specialist['id']})")] for
                            specialist in specialists]
                return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
            else:
                return None


def apply_job_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(
                text='Откликнуться (отправить номер телефона)', request_contact=True)],
            [KeyboardButton(
                text='Откликнуться (не отправлять номер телефона)')]
        ],
        resize_keyboard=True
    )
