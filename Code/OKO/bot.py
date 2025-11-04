import asyncio
import aiogram
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import filters
from config import *
import UserManager, AlertManager
from UserManager import is_key
import datetime
import pandas as pd
from UserManager import set_alert_configuration

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

async def set_commands(bot: Bot):
    commands = [
        types.BotCommand(command="/start", description="Начало работы"),
        types.BotCommand(command="/settings", description="Настройки"),
        types.BotCommand(command="/help", description="Инструкция"),
        types.BotCommand(command="/default", description="Сбросить настройки"),
        types.BotCommand(command="/long_set", description="LONG SET"),
        types.BotCommand(command="/short_set", description="SHORT SET"),
        types.BotCommand(command="/impulse_trade_set", description="IMPULSE TRADE SET"),
        types.BotCommand(command="/day_trading_set", description="DAY TRADING SET SET"),
        types.BotCommand(command="/basic_oko_set", description="BASIC OKO SET"),
    ]
    await bot.set_my_commands(commands)

@dp.message_handler(commands=['long_set'])
async def long_set_command(message: types.Message):
    user_id = message.from_user.id

    # Проверяем, зарегистрирован ли пользователь
    if not UserManager.has_user(user_id):
        await message.answer("Для начала работы нажмите /start")
        return

    # Устанавливаем новую конфигурацию алертов
    new_config = "111101001111"
    set_alert_configuration(user_id, new_config)

    # Уведомляем пользователя об успешном изменении
    await message.answer(f"Вы выставили пресет LONG SET")

@dp.message_handler(commands=['default'])
async def long_set_command(message: types.Message):
    user_id = message.from_user.id

    # Проверяем, зарегистрирован ли пользователь
    if not UserManager.has_user(user_id):
        await message.answer("Для начала работы нажмите /start")
        return

    # Устанавливаем новую конфигурацию алертов
    new_config = "111111111111"
    set_alert_configuration(user_id, new_config)

    # Уведомляем пользователя об успешном изменении
    await message.answer(f"Вы успешно сбросили настройки")

@dp.message_handler(commands=['short_set'])
async def long_set_command(message: types.Message):
    user_id = message.from_user.id

    # Проверяем, зарегистрирован ли пользователь
    if not UserManager.has_user(user_id):
        await message.answer("Для начала работы нажмите /start")
        return

    # Устанавливаем новую конфигурацию алертов
    new_config = "111011001111"
    set_alert_configuration(user_id, new_config)

    # Уведомляем пользователя об успешном изменении
    await message.answer(f"Вы выставили пресет SHORT SET")

@dp.message_handler(commands=['impulse_trade_set'])
async def long_set_command(message: types.Message):
    user_id = message.from_user.id

    # Проверяем, зарегистрирован ли пользователь
    if not UserManager.has_user(user_id):
        await message.answer("Для начала работы нажмите /start")
        return

    # Устанавливаем новую конфигурацию алертов
    new_config = "011111001111"
    set_alert_configuration(user_id, new_config)

    # Уведомляем пользователя об успешном изменении
    await message.answer(f"Вы выставили пресет IMPULSE TRADE SET")

@dp.message_handler(commands=['day_trading_set'])
async def long_set_command(message: types.Message):
    user_id = message.from_user.id

    # Проверяем, зарегистрирован ли пользователь
    if not UserManager.has_user(user_id):
        await message.answer("Для начала работы нажмите /start")
        return

    # Устанавливаем новую конфигурацию алертов
    new_config = "111110101111"
    set_alert_configuration(user_id, new_config)

    # Уведомляем пользователя об успешном изменении
    await message.answer(f"Вы выставили пресет DAY TRADING SET SET")

@dp.message_handler(commands=['basic_oko_set'])
async def long_set_command(message: types.Message):
    user_id = message.from_user.id

    # Проверяем, зарегистрирован ли пользователь
    if not UserManager.has_user(user_id):
        await message.answer("Для начала работы нажмите /start")
        return

    # Устанавливаем новую конфигурацию алертов
    new_config = "111111001110"
    set_alert_configuration(user_id, new_config)

    # Уведомляем пользователя об успешном изменении
    await message.answer(f"Вы выставили пресет BASIC OKO SET")

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(hello_message)

@dp.message_handler(commands=['settings'])
async def settings(message: types.Message):
    if not UserManager.has_user(message.from_user.id):
        await message.answer(error_registration_required_message)
        return
    await message.answer(alert_settings_message, reply_markup=get_alerts_kb(message.from_user.id))

@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    help_text = "Ознакомьтесь с инструкцией/FAQ по ссылкам ниже👇"
    help_link = "https://dzen.ru/a/Z6p9T4qMyifrl5dw"  # Укажите ссылку, которую должна открывать первая кнопка
    additional_link = "https://dzen.ru/a/Z6iNF_SQX0pvB06z"  # Укажите ссылку для второй кнопки

    help_kb = InlineKeyboardMarkup().row(
        InlineKeyboardButton("Открыть инструкцию", url=help_link),
        InlineKeyboardButton("Открыть FAQ", url=additional_link)
    )

    await message.answer(help_text, reply_markup=help_kb)

@dp.message_handler(chat_type=types.ChatType.PRIVATE)
async def on_message(message: types.Message):
    text = message.text
    long = is_key(text)
    if long:
        if UserManager.enroll(message.from_user.id, text, float(long)):
            await message.answer(successful_enrollment_message)
        else:
            await message.answer(error_key_already_used_message)
    else:
        await message.answer(error_key_not_exists_message)

@dp.message_handler(chat_id=WORKING_GROUPS)
async def on_message(message: types.Message):
    # Извлекаем текст или подпись из сообщения
    text = message.caption if message.caption else message.text

    # Проверяем и корректируем ключи пользователей
    await correct_keys()

    # Получаем пользователей с совпадающей конфигурацией
    members = AlertManager.get_members(text)
    print(f"Сообщение отправляется следующим пользователям: {members}")

    for member in members:
        try:
            await message.forward(member)
        except aiogram.utils.exceptions.BotBlocked:
            print(f"Бот заблокирован пользователем: {member}")

@dp.callback_query_handler(lambda c: c.data.startswith('alert'))
async def process_callback_kb1btn1(callback_query: types.CallbackQuery):
    try:
        code = int(callback_query.data[callback_query.data.find("_")+1:])
        state = UserManager.get_alerts(callback_query.from_user.id)
        UserManager.set_alert(callback_query.from_user.id, code-1, not state[code-1])
        await bot.edit_message_reply_markup(callback_query.from_user.id, callback_query.message.message_id, reply_markup=get_alerts_kb(callback_query.from_user.id))
    except:
        pass

async def scheduler():
    while True:
        now = datetime.datetime.now()
        if now.hour == 12 and now.minute == 25:
            await remember_endings()
        await asyncio.sleep(60)

async def remember_endings():
    ending_members = UserManager.get_ending_members(SUBSCRIPTION_END_ALERT)
    for member in ending_members:
        try:
            await bot.send_message(member, subscription_ending_alert)
        except Exception as e:
            print(e)

async def correct_keys():
    invalides = UserManager.get_users_with_invalid_keys()
    members = UserManager.get_all_members()
    for invalid in invalides:
        if invalid in members:
            UserManager.set_membership(invalid, 0)
            try:
                await bot.send_message(invalid, invalid_key_alert)
            except:
                print('Тут ошибка')

def get_alerts_kb(uid):
    state = UserManager.get_alerts(uid)
    alerts_kb = InlineKeyboardMarkup(row_width=1)
    names, sigs = AlertManager.get_alerts()
    for n, name in enumerate(names):
        alerts_kb.add(InlineKeyboardButton(pstate(state[n]) + name, callback_data='alert_' + str(n + 1)))
    return alerts_kb

def pstate(state):
    return "🟢" if state else "🔴"

async def main():
    while True:
        try:
            await set_commands(bot)
            task1 = asyncio.create_task(dp.start_polling())
            task2 = asyncio.create_task(scheduler())
            await asyncio.gather(task1, task2)
        except aiogram.utils.exceptions.NetworkError as e:
            print(f"NetworkError: {e}, waiting for 10 seconds.")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Unknown exception: {e}")

if __name__ == "__main__":
    UserManager.begin()
    asyncio.run(main())
