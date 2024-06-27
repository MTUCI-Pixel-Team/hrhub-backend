from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton)

# Клавиатура, которая появляется после старта и откликнуться с отправкой номера телефона или без
applyJob = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='✅ Откликнуться (отправить номер телефона)', 
            request_contact=True)], [KeyboardButton(text='✅ Откликнуться (не отправлять номер телефона)')
            ]], resize_keyboard=True)
