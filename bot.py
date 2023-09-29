# import aiogram.utils.markdown as md
from aiogram import  Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram import executor
from curs import *
from database import *
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import os
from dotenv import load_dotenv

storage = MemoryStorage()

load_dotenv()
api_token = os.getenv('API_TOKEN')

bot = Bot(token=api_token)
dp = Dispatcher(bot, storage=storage)

# Определяем кнопки меню
menu_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
item1 = types.KeyboardButton("Курс основных")
item2 = types.KeyboardButton("Курс валюты")
item3 = types.KeyboardButton("Курс между валютами")
item4 = types.KeyboardButton("Конвертор валют")
item5 = types.KeyboardButton("Коды валют")
item6 = types.KeyboardButton("График курса")
menu_keyboard.add(item1, item2, item3, item4, item5, item6)

# Создаем Inline Keyboard Markup (клавиатуру в сообщении)
period_keyboard = InlineKeyboardMarkup(row_width=2)
period_keyboard.add(
    InlineKeyboardButton("Месяц", callback_data="period_month"),
    InlineKeyboardButton("3 месяца", callback_data="period_3months"),
    InlineKeyboardButton("Полгода", callback_data="period_halfyear"),
    InlineKeyboardButton("Год", callback_data="period_year"),
    InlineKeyboardButton("3 года", callback_data="period_3years"),
    InlineKeyboardButton("5 лет", callback_data="period_5years"),
    InlineKeyboardButton("10 лет", callback_data="period_10years")
)

class BotState(StatesGroup):
    waiting_code_simple_course = State()
    waiting_1_valute_curse = State()
    waiting_2_valute_curse = State()
    waiting_quantity_converter = State()
    waiting_1_valute_converter = State()
    waiting_2_valute_converter = State()
    waiting_valute_graf = State()
    waiting_period_graph = State()


# Приветственное сообщение
@dp.message_handler(commands=['start'])
async def on_start(message: types.Message):
    user_id = str(message.from_user.id)
    username = message.from_user.username

    if not user_exists(user_id):
        # Пользователь не существует, выполняем регистрацию
        add_user(user_id, username)
        await message.answer("Добро пожаловать! Это ваш первый вход. Регистрация прошла успешно.")
    else:
        # Пользователь существует, приветствуем
        await message.answer("Привет! Давно не виделись. Регистрация не требуется")

# Обработчик команды "Курс основных"
@dp.message_handler(lambda message: message.text == "Курс основных")
async def get_main_curses(message: types.Message):
    curses = get_now_ruble_curses(['AUD', 'USD', 'EUR', 'CNY', 'SGD', 'GBP', 'CHF', 'JPY', 'TRY', 'AED'])
    aud_curse = curses['AUD']
    usd_curse = curses['USD']
    eur_curse = curses['EUR']
    cny_curse = curses['CNY']
    sgd_curse = curses['SGD']
    gbp_curse = curses['GBP']
    chf_curse = curses['CHF']
    jpy_curse = curses['JPY']
    try_curse = curses['TRY']
    aed_curse = curses['AED']
    response_text = f"""Текущий курс:
AUD: {aud_curse} RUB
USD: {usd_curse} RUB
EUR: {eur_curse} RUB
CNY: {cny_curse} RUB
SGD: {sgd_curse} RUB
GBP: {gbp_curse} RUB
CHF: {chf_curse} RUB
JPY: {jpy_curse} RUB
TRY: {try_curse} RUB
AED: {aed_curse} RUB"""
    await message.answer(response_text, reply_markup=menu_keyboard)

# Обработчик команды "Коды валют"
@dp.message_handler(lambda message: message.text == "Коды валют")
async def valute_codes(message: types.Message):
    response_text = f"""На данный момент доступны следующие коды валют:
AED, AMD, AUD, AZN, BGN, BRL, BYN, CAD, CHF, CNY, CZK, DKK, EGP, EUR, GBP, GEL, HKD, HUF, IDR, INR, JPY, KGS, KRW, KZT, MDL, NOK, NZD, PLN, QAR, RON, RSD, SEK, SGD, THB, TJS, TMT, TRY, UAH, USD, UZS, VND, XDR, ZAR"""
    await message.answer(response_text, reply_markup=menu_keyboard)

# Обработчик команды "Курс валюты"
@dp.message_handler(lambda message: message.text == "Курс валюты")
async def ruble_curse(message: types.Message):
    # Отправляем сообщение с запросом кода валюты
    await message.answer("Введите код валюты:")
    await BotState.waiting_code_simple_course.set()

# Обработчик ввода кода валюты
@dp.message_handler(lambda message: message.text, state=BotState.waiting_code_simple_course)
async def process_currency_code(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['currency_code'] = message.text.strip().upper()
        valute_code = message.text.strip().upper()  # Преобразуем введенный код в верхний регистр
        if valute_code == 'RUB':
            await message.answer("Курс рубля к рублю всегда 1.0.")
        else:
            if check_valute(valute_code)==(False,False):
                await message.answer("Валюта не найдена. Начните с начала с корректным кодом валюты (например, USD)")
            else:
                ruble_value = get_now_ruble_curse(valute_code)
                if ruble_value is False:
                    await message.answer("Неверный код валюты. Пожалуйста, введите корректный код.")
                else:
                    await message.answer(f"Текущий курс {valute_code}: {ruble_value} RUB")

    # Завершаем диалог и сбрасываем состояние
    await state.finish()

# Обработчик команды "Курс между валютами"
@dp.message_handler(lambda message: message.text == "Курс между валютами")
async def curse_between(message: types.Message):
    await message.answer("Какую валюту рассчитать?")
    await BotState.waiting_1_valute_curse.set()

# Обработчик ввода первой валюты
@dp.message_handler(lambda message: message.text, state=BotState.waiting_1_valute_curse)
async def process_first_currency(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['first_currency'] = message.text.strip().upper()
        valute_code1 = message.text.strip().upper()

        # Проверяем, существует ли введенная валюта
        if check_valute(valute_code1)==(False,False) and valute_code1!='RUB':
            await message.answer("Валюта не найдена. Начните с начала с корректным кодом валюты (например, USD)")
            await state.finish()
        else:
            await message.answer("Относительно какой валюты рассчитать?")
            await BotState.next()

# Обработчик ввода второй валюты
@dp.message_handler(lambda message: message.text, state=BotState.waiting_2_valute_curse)
async def process_second_currency(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['second_currency'] = message.text.strip().upper()
        valute_code2 = message.text.strip().upper()

    # Проверяем, существует ли введенная валюта
    if check_valute(valute_code2)==(False,False) and valute_code2!='RUB':
        await message.answer("Валюта не найдена. Начните с начала с корректным кодом валюты (например, USD)")
        await state.finish()
    else:
        result = None
        if data['first_currency'] == 'RUB' and data['second_currency'] == 'RUB':
            result = 1
        elif data['first_currency'] == 'RUB':
            result = 1/get_now_ruble_curse(data['second_currency'])
        elif data['second_currency'] == 'RUB':
            result = get_now_ruble_curse(data['first_currency'])
        else:
            # Выполняем функцию для получения курса между валютами
            result = get_now_other_curse(data['first_currency'], data['second_currency'])

        if result is not None:
            await message.answer(f"Курс {data['first_currency']} к {data['second_currency']}: {round(result, 4)}")
        else:
            await message.answer("Не удалось получить курс между валютами.")

    # Сбрасываем состояние
    await state.finish()

# Обработчик команды "Конвертор валют"
@dp.message_handler(lambda message: message.text == "Конвертор валют")
async def convertor(message: types.Message):
    await message.answer("Введите количество валюты для рассчета:")
    await BotState.waiting_quantity_converter.set()

# Обработчик ввода количества валюты
@dp.message_handler(lambda message: is_valid_number(message.text), state=BotState.waiting_quantity_converter)
async def process_quantity_convertor(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['quantity_convertor'] = message.text.strip()
        
    await message.answer("Какую валюту рассчитать?")
    await BotState.next()

# Обработчик ввода первой валюты
@dp.message_handler(lambda message: message.text, state=BotState.waiting_1_valute_converter)
async def process_first_currency_convertor(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['first_currency_convertor'] = message.text.strip().upper()
        valute_code1 = message.text.strip().upper()

    # Проверяем, существует ли введенная валюта
    if check_valute(valute_code1)==(False,False) and valute_code1 != 'RUB':
        await message.answer("Валюта не найдена. Начните с начала с корректным кодом валюты (например, USD)")
        await state.finish()
    else:
        await message.answer("В какую валюту сконвертировать?")
        await BotState.next()

# Обработчик ввода второй валюты
@dp.message_handler(lambda message: message.text, state=BotState.waiting_2_valute_converter)
async def process_second_currency_convertor(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['second_currency_convertor'] = message.text.strip().upper()
        valute_code2 = message.text.strip().upper()

    # Проверяем, существует ли введенная валюта
    if check_valute(valute_code2)==(False,False) and valute_code2 != 'RUB':
        await message.answer("Валюта не найдена. Начните с начала с корректным кодом валюты (например, USD)")
        await state.finish()
    else:   
        result = None 
        if data['first_currency_convertor'] == 'RUB' and data['second_currency_convertor'] == 'RUB':
            result = 1
        elif data['first_currency_convertor'] == 'RUB':
            result = 1/get_now_ruble_curse(data['second_currency_convertor'])
        elif data['second_currency_convertor'] == 'RUB':
            result = get_now_ruble_curse(data['first_currency_convertor'])
        else:
            # Выполняем функцию для получения курса между валютами
            result = get_now_other_curse(data['first_currency_convertor'], data['second_currency_convertor'])
        # Выполняем функцию для получения курса между валютами

        if result is not None:
            result = float(result)*float(data['quantity_convertor'])
            await message.answer(f"{data['quantity_convertor']} {data['first_currency_convertor']} равно {round(result, 4)} {data['second_currency_convertor']}")
        else:
            await message.answer("Не удалось получить курс между валютами.")

    # Сбрасываем состояние
    await state.finish()

# Обработчик команды "График курса"
@dp.message_handler(lambda message: message.text == "График курса")
async def grafik(message: types.Message):
    await message.answer("График курса какой валюты вы хотите отобразить?")
    await BotState.waiting_valute_graf.set()

# Обработчик ввода валюты для графика
@dp.message_handler(lambda message: message.text, state=BotState.waiting_valute_graf)
async def process_currency_graph(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['currency_code'] = message.text.strip().upper()

    if data['currency_code'] == 'RUB':
        await message.answer("Курс рубля к рублю всегда 1.0. Не имеет смысла строить график.")

    # Проверяем, существует ли введенная валюта
    if check_valute(data['currency_code'])==(False,False):
        await message.answer("Валюта не найдена. Начните с начала с корректным кодом валюты (например, USD)")

    await message.answer("За какой период отобразить график курса?", reply_markup=period_keyboard)
    await BotState.next()

@dp.callback_query_handler(lambda c: c.data == 'period_month', state=BotState.waiting_period_graph)
async def process_period_month(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['period_text'] = "Месяц"  # Устанавливаем текст периода в состояние
    await process_period_graph(callback_query, state)

@dp.callback_query_handler(lambda c: c.data == 'period_3months', state=BotState.waiting_period_graph)
async def process_period_3months(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['period_text'] = "3 месяца"  # Устанавливаем текст периода в состояние
    await process_period_graph(callback_query, state)

@dp.callback_query_handler(lambda c: c.data == 'period_halfyear', state=BotState.waiting_period_graph)
async def process_period_month(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['period_text'] = "Полгода"  # Устанавливаем текст периода в состояние
    await process_period_graph(callback_query, state)

@dp.callback_query_handler(lambda c: c.data == 'period_year', state=BotState.waiting_period_graph)
async def process_period_3months(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['period_text'] = "Год"  # Устанавливаем текст периода в состояние
    await process_period_graph(callback_query, state)

@dp.callback_query_handler(lambda c: c.data == 'period_3years', state=BotState.waiting_period_graph)
async def process_period_month(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['period_text'] = "3 года"  # Устанавливаем текст периода в состояние
    await process_period_graph(callback_query, state)

@dp.callback_query_handler(lambda c: c.data == 'period_5years', state=BotState.waiting_period_graph)
async def process_period_3months(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['period_text'] = "5 лет"  # Устанавливаем текст периода в состояние
    await process_period_graph(callback_query, state)

@dp.callback_query_handler(lambda c: c.data == 'period_10years', state=BotState.waiting_period_graph)
async def process_period_3months(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['period_text'] = "10 лет"  # Устанавливаем текст периода в состояние
    await process_period_graph(callback_query, state)

# Обработчик выбора периода
@dp.message_handler(lambda message: message.text in ["Месяц", "3 месяца", "Полгода", "Год", "3 года", "5 лет", "10 лет"], state=BotState.waiting_period_graph)
async def process_period_graph(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        period_mapping = {
        "Месяц": 31,
        "3 месяца": 92,
        "Полгода": 183,
        "Год": 365,
        "3 года": 1095,
        "5 лет": 1825,
        "10 лет": 3650
        }
        period_text = data.get('period_text', None)  # Получаем текст периода из состояния
        if period_text is not None:
            period = period_mapping.get(period_text)

            if period is not None:
                # Вызываем функцию для получения графика курса
                graph_image = get_graf(data['currency_code'], period)

                if graph_image:
                    # Отправляем изображение пользователю
                    await bot.send_photo(message.from_user.id, photo=graph_image)
                else:
                    await bot.send_message(message.from_user.id, "Не удалось получить график курса.")
            else:
                await bot.send_message(message.from_user.id, "Выберите период из предложенных вариантов.")
        else:
            await bot.send_message(message.from_user.id, "Период не выбран или устарел.")

    # Сбрасываем состояние
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

