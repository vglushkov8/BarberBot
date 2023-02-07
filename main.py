import telebot
from telebot.types import (
    ReplyKeyboardRemove, Message, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
)
import datetime
import time
import calendar
import sqlite3
from settings import BARBER_USERNAME, DB_NAME, BOT_API_KEY
from sql import CREATE_TABLE, SELECT_ALL_SLOTS, CREATE_SLOT
from utils import get_first_slot_date, get_all_slots_during_day, chosen_day_to_date, get_all_available_slots


bot = telebot.TeleBot(BOT_API_KEY)
db_connection = None
busy_slots = []
user_process_data = {}


@bot.message_handler(commands=['start'])
def handle_start(message: Message):
    user_name = message.from_user.username
    if user_name != BARBER_USERNAME:
        # regular user
        available_slots = []
        user_process_data[user_name] = {"available_slots": []}
        all_slots = get_all_available_slots()
        for slot in all_slots:
            if slot not in busy_slots:
                available_slots.append(slot)
        user_process_data[user_name]['available_slots'] = sorted(available_slots)

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        already_added_days = []
        for available_slot in sorted(available_slots):
            if available_slot.day not in already_added_days:
                keyboard.add(KeyboardButton(
                    text=f'{available_slot.strftime("%A")}, {available_slot.day} {available_slot.strftime("%B")} ({available_slot.strftime("%d.%m.%Y")})'))
                already_added_days.append(available_slot.day)

        bot.send_message(message.chat.id, 'Здравствуйте!', reply_markup=ReplyKeyboardRemove())
        if not user_process_data[user_name]['available_slots']:
            bot.send_message(message.chat.id, 'Нет свободных слотов, попробуйте позже')
        else:
            bot.send_message(message.chat.id, 'Выберите день для записи', reply_markup=keyboard)
            bot.register_next_step_handler(message, day_choose)
    else:
        # barber
        while True:
            bot.send_message(message.chat.id, 'Вы барбер')
            time.sleep(1)


def day_choose(message):
    user_name = message.from_user.username
    chosen_day = chosen_day_to_date(message.text)
    user_process_data[user_name]['chosen_date'] = chosen_day
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for available_slot in user_process_data[user_name]['available_slots']:
        if (
                available_slot.day == chosen_day.day and
                available_slot.month == chosen_day.month and
                available_slot.year == chosen_day.year
        ):
            keyboard.add(KeyboardButton(text=f'{available_slot.hour}:{available_slot.minute}0'))

    bot.send_message(message.chat.id, 'Выберите время', reply_markup=keyboard)
    bot.register_next_step_handler(message, time_choose)


def time_choose(message):
    user_name = message.from_user.username
    splitted_hour = message.text.split(':')
    chosen_date = user_process_data[user_name]['chosen_date']
    chosen_slot = datetime.datetime(
        chosen_date.year, chosen_date.month, chosen_date.day, int(splitted_hour[0]), int(splitted_hour[1])
    )
    if chosen_slot in busy_slots:
        bot.send_message(
            message.chat.id,
            'Упс, похоже это время уже заняли, пожалуйста начните сначала через команду /start'
        )
    else:
        busy_slots.append(chosen_slot)
        try:
            db_connection.execute(CREATE_SLOT.format(time=chosen_slot.strftime("%d.%m.%Y,%H:%M"), username=user_name))
            db_connection.commit()
        except Exception:
            bot.send_message(
                message.chat.id, 'Ошибка при создании записи, попробуйте снова', reply_markup=ReplyKeyboardRemove()
            )
        else:
            bot.send_message(message.chat.id, 'Вы успешно записаны, спасибо', reply_markup=ReplyKeyboardRemove())

    user_process_data.pop(user_name)


if __name__ == '__main__':
    db_connection = sqlite3.connect(DB_NAME, check_same_thread=False)
    try:
        db_connection.execute(CREATE_TABLE)
    except Exception:
        pass
    for row in db_connection.execute(SELECT_ALL_SLOTS):
        busy_slots.append(row)

    print("Starting bot...")
    bot.polling()
    print('Shutdown...')
    db_connection.close()
