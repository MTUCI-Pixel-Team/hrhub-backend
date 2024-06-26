from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton)

applyJob = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='✅ Откликнуться (отправить номер телефона)', 
            request_contact=True)], [KeyboardButton(text='✅ Откликнуться (не отправлять номер телефона)')
            ]], resize_keyboard=True)
