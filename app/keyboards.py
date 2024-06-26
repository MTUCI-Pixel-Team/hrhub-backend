from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, 
                           InlineKeyboardMarkup, InlineKeyboardButton)

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='📚 Каталог')], 
                                     [KeyboardButton(text='🛒 Корзина')], 
                                     [KeyboardButton(text='Контакты'), 
                                      KeyboardButton(text='О нас')]], resize_keyboard=True, input_field_placeholder='Выберите пункт меню...')

catalog = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📚 Книги', callback_data='books')], 
    [InlineKeyboardButton(text='Футболки', callback_data='t-shirt')],
    [InlineKeyboardButton(text='Кепки', callback_data='cap')]])

contact = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отправить телефон', request_contact=True)]], resize_keyboard=True)