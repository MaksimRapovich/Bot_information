import requests
import asyncio
import aiogram
import datetime
import aioschedule
import sqlite3
import config as cfg
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text
from googletrans import Translator
from bs4 import BeautifulSoup
from config import tg_bot_token, open_weather_token, currency_url


bot = Bot(token=tg_bot_token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

listlang = cfg.LANGUES
translator = Translator()

conn = sqlite3.connect('botinformation.db')
print('started')

@dp.message_handler(commands="start")
async def start(message: types.Message):
    start_buttons = ["👋 Поздороваться"]
    start_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_keyboard.add(*start_buttons)
    await message.answer("Приветствую! Я информационный бот", reply_markup=start_keyboard)
    cursor = conn.cursor()
    sql = "SELECT * FROM users WHERE id = ?"
    adr = (str(message.from_user.id),)
    cursor.execute(sql, adr)
    user_result = cursor.fetchall()
    print(user_result)
    if user_result is None or user_result == [] or user_result == ():
        cursor = conn.cursor()
        sql = "INSERT INTO users (id, lang) VALUES (?, ?)"
        user = (str(message.from_user.id), "ru")
        cursor.execute(sql, user)
        conn.commit()
        await message.answer("Ты зарегистрирован в моей базе банных")
    else:
        await message.answer("Ты уже есть в моей базе данных")


@dp.message_handler(Text(equals="👋 Поздороваться"))
async def select(message: types.Message):
    await message.answer(f"Привет, <b><u>{message.from_user.first_name} {message.from_user.last_name}</u></b>\n")
    select_buttons = ["Установить уведомление", "Узнать погоду", "Узнать курсы валют белорусского рубля",
                     "Узнать цены на бензин в Беларуси", "Переводчик", "Мелодия дня", "Вернуться в главное меню"]
    select_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    select_keyboard.add(*select_buttons)
    await message.answer("Что тебя интересует?", reply_markup=select_keyboard)

@dp.message_handler(Text(equals="Установить уведомление"))
async def select(message: types.Message):
    await message.answer("Привет. Напиши дату и время, когда тебя оповестить")

async def notify_message():
    await bot.send_message(chat_id=479054430, text='Привет! Ты попросил сообщить тебе, что...')

async def notify():
    aioschedule.every().day.at("19:56").do(notify_message)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def on_startup(_):
    asyncio.create_task(notify())

@dp.message_handler(Text(equals="Узнать погоду"))
async def weather(message: types.Message):
    weather_buttons = ["Вернуться в главное меню"]
    weather_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    weather_keyboard.add(*weather_buttons)
    await message.answer("Напиши мне название твоего города и я пришлю сводку погоды!", reply_markup=weather_keyboard)

    @dp.message_handler()
    async def get_weather(message: types.Message):
        code_to_smile = {
            "Clear": "Ясно \U00002600",
            "Clouds": "Облачно \U00002601",
            "Rain": "Дождь \U00002614",
            "Drizzle": "Дождь \U00002614",
            "Thunderstorm": "Гроза \U000026A1",
            "Snow": "Снег \U0001F328",
            "Mist": "Туман \U0001F32B"
        }

        try:
            reg = requests.get(
                f"http://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={open_weather_token}&units=metric"
            )
            data = reg.json()

            city = data["name"]
            cur_weather = data["main"]["temp"]

            weather_description = data["weather"][0]["main"]
            if weather_description in code_to_smile:
                wd = code_to_smile[weather_description]
            else:
                wd = "Не моу понять, какая погода за окном!"

            humidity = data["main"]["humidity"]
            pressure = data["main"]["pressure"]
            wind = data["wind"]["speed"]
            sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
            sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
            length_of_the_day = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) - datetime.datetime.fromtimestamp(
                data["sys"]["sunrise"])

            await message.reply(f"*** Данные о погоде на: <b>{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</b> ***\n"
                  f"Погода в городе: <b>{city}</b>\nТемпература: {cur_weather} C° {wd}\n"
                  f"Влажность: {humidity} %\nДавление: {pressure} мм.рт.ст\nВетер: {wind} м/с\n"
                  f"Восход солнца: {sunrise_timestamp}\nЗакат солнца: {sunset_timestamp}\nПродолжительность дня: {length_of_the_day}\n\n"
                  f"<b>--- Хорошего дня! 👋 ---</b>", reply_markup=weather_keyboard)

        except:
            await message.reply("Проверь, пожалуйста, название своего города", reply_markup=weather_keyboard)

        back_buttons = ["Вернуться в главное меню"]
        back_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        back_keyboard.add(*back_buttons)
        await message.answer("Что тебя ещё интересует?", reply_markup=back_keyboard)


@dp.message_handler(Text(equals="Узнать курсы валют белорусского рубля"))
async def currency(message: types.Message):
    currency_buttons = ["Доллары", "Евро", "Рос. рубль", "Вернуться в главное меню"]
    currency_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    currency_keyboard.add(*currency_buttons)
    await message.answer("Выбери валюту", reply_markup=currency_keyboard)


    @dp.message_handler(Text(equals="Доллары"))
    async def currency_dol(message: types.Message):
        await message.answer("Выполняю задачу. Подожди, пожалуйста, немного!")
        req_dol = requests.get(currency_url)
        response = req_dol.json()
        dol_buy = response[0]["USD_in"]
        dol_sale = response[0]["USD_out"]
        await message.answer(f"--- Информация сформирована на - <b>{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</b> ---\n"
                             f"Покупка $ банком - <b>{dol_buy} бел.руб</b>\nПродажа $ банком - <b>{dol_sale} бел.руб</b>",
                             reply_markup=currency_keyboard)

    @dp.message_handler(Text(equals="Евро"))
    async def currency_euro(message: types.Message):
        await message.answer("Выполняю задачу. Подожди, пожалуйста, немного!")
        req_euro = requests.get(currency_url)
        response = req_euro.json()
        euro_buy = response[0]["EUR_in"]
        euro_sale = response[0]["EUR_out"]
        await message.answer(f"--- Информация сформирована на - <b>{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</b> ---\n"
                             f"Покупка € банком - <b>{euro_buy} бел.руб</b>\nПродажа € банком - <b>{euro_sale} бел.руб</b>",
                             reply_markup=currency_keyboard)

    @dp.message_handler(Text(equals="Рос. рубль"))
    async def currency_rub(message: types.Message):
        await message.answer("Выполняю задачу. Подожди, пожалуйста, немного!")
        req_rub = requests.get(currency_url)
        response = req_rub.json()
        rub_buy = response[0]["RUB_in"]
        rub_sale = response[0]["RUB_out"]
        await message.answer(f"--- Информация сформирована на - <b>{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</b> ---\n"
                             f"Покупка ₽ банком - <b>{rub_buy} бел.руб</b>\nПродажа ₽ банком - <b>{rub_sale} бел.руб</b>",
                             reply_markup=currency_keyboard)

@dp.message_handler(Text(equals="Узнать цены на бензин в Беларуси"))
async def fuel(message: types.Message):
    fuel_buttons = ["Вернуться в главное меню"]
    fuel_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    fuel_keyboard.add(*fuel_buttons)
    await message.answer("Цены на бензин в Беларуси:", reply_markup=fuel_keyboard)

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/104.0.5112.102 Safari/537.36"
    }
    url = "https://azs.a-100.by/set-azs/fuel/"
    reg = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(reg.text, "lxml")
    articles_cards = soup.find_all("div", class_="grid__item col-lg-4 col-md-6 col-xs-12")
    article_date_time = soup.find("div", class_="note flc").text.strip()
    article_date_time = article_date_time[-16::]

    for article in articles_cards:
        article_title = article.find("div", class_="cert__title-main h2").text.strip()
        article_desc1 = article.find("strong").text.strip()
        article_desc2 = article.find("sup").text.strip()
        article_desc3 = article.find("small").text.strip()
        if "AdBlue" in article_title:
            continue

        await message.answer(f"{article_title} - {article_desc1}.{article_desc2} {article_desc3}",
                             reply_markup=fuel_keyboard)
    await message.answer(f"* Цены указаны по состоянию на <u>{article_date_time}</u>",
                         reply_markup=fuel_keyboard)

@dp.message_handler(Text(equals="Переводчик"))
async def translate(message: types.Message):
    keyb = InlineKeyboardMarkup()
    for i, j in cfg.LANGDICT.items():
        key = InlineKeyboardButton(j, callback_data=i)
        keyb.add(key)
    await message.answer("Выбери язык на который желаешь перевести", reply_markup=keyb)

    @dp.callback_query_handler(lambda c: c.data)
    async def process_callback(callback_query: aiogram.types.CallbackQuery):
        if callback_query.data in cfg.LANGUES:
            lang = callback_query.data
            cursor = conn.cursor()
            sql = "UPDATE users SET lang = ? WHERE id = ?"
            val = (lang, str(callback_query.from_user.id))
            cursor.execute(sql, val)

            await bot.send_message(callback_query.from_user.id, "Ты выбрал язык - " + cfg.LANGDICT[lang])

    @dp.message_handler()
    async def translat_message(message: types.Message):
        cursor = conn.cursor()
        sql = "SELECT * FROM users WHERE id = ?"
        adr = (message.from_user.id,)
        cursor.execute(sql, adr)
        user_result = cursor.fetchall()
        lang = user_result[0][1]
        word = translator.translate(message.text, dest=lang).text

        await bot.send_message(message.from_user.id, word)

        translate_back_buttons = ["Вернуться в главное меню"]
        translate_back_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        translate_back_keyboard.add(*translate_back_buttons)
        await message.answer("Что еще желаешь перевести? Или вернись в главное меню", reply_markup=translate_back_keyboard)

@dp.message_handler(Text(equals="Мелодия дня"))
async def melody(message: types.Message):
    buttons_melody = ["Вернуться в главное меню"]
    keyboard_melody = types.ReplyKeyboardMarkup(resize_keyboard=True)
    melody_keyboard = types.InlineKeyboardMarkup()
    keyboard_melody.add(*buttons_melody)
    melody_keyboard.add(types.InlineKeyboardButton("Перейти на сайт центр FM", url="https://centerfm.by/ru"))
    await message.answer("Мелодия дня", reply_markup=melody_keyboard)

@dp.message_handler(Text(equals="Вернуться в главное меню"))
async def back(message: types.Message):
    buttons_back = ["Установить уведомление", "Узнать погоду", "Узнать курсы валют белорусского рубля",
               "Узнать цены на бензин в Беларуси", "Переводчик", "Мелодия дня", "Вернуться в главное меню"]
    keyboard_back = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard_back.add(*buttons_back)
    await message.answer("Ты вернулся в главное меню! Что тебя интересует?", reply_markup=keyboard_back)

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)