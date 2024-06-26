from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from app.states import Register
import app.keyboards as kb

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    await message.answer('Hello!', reply_markup=kb.main)

@router.message(Command('help'))
async def help(message: Message):
    await message.answer('Help!')

@router.message(F.text == '📚 Каталог')
async def catalog(message: Message):
    await message.answer('Выберите категорию:', reply_markup=kb.catalog)

@router.callback_query(F.data == 'books')
async def books(callback: CallbackQuery):
    await callback.answer('Вы выбрали категорию книг.') #) show_alert=True

@router.message(Command('register'))
async def register(message: Message, state: FSMContext):
    await state.set_state(Register.name)
    await message.answer('Введите Ваше имя')

@router.message(Register.name)
async def register_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Register.age)
    await message.answer('Введите Ваш возраст')

@router.message(Register.age)
async def register_name(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await state.set_state(Register.phone)
    await message.answer('Введите Ваш телефон', reply_markup=kb.contact)

@router.message(Register.phone, F.contact)
async def register_name(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact)
    data = await state.get_data()
    # print(data['phone'].phone_number)
    await message.answer(f'Ваше имя - {data["name"]} Ваш возраст - {data["age"]} Ваш телефон - {data["phone"].phone_number}, а ЕЩЁ {data["phone"].first_name, data["phone"].last_name, data["phone"].user_id}')
    await state.clear()