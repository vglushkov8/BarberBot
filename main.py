import telebot
from telebot.types import (
    Message,
    KeyboardButton,
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
)
from datetime import datetime
import sqlite3
from settings import BARBER_USERNAME, DB_NAME, BOT_API_KEY
from sql import (
    CREATE_SLOT,
    SELECT_ALL_SLOTS,
    SLOTS_CREATE_TABLE,
    BARBER_CREATE_TABLE,
    CREATE_BARBER_CHAT_ID,
    SELECT_BARBER_CHAT_ID,
)
from utils import chosen_slot_to_date, get_all_slots


bot = telebot.TeleBot(BOT_API_KEY)
db_connection = None
busy_slots = []

# словарь, ключом является имя пользователя, значением - данные для перехода с разных шагов записи
user_process_data = {}
barber_chat_id = None


@bot.message_handler(commands=['start'])
def handle_start(message: Message):
    global barber_chat_id
    user_name = message.from_user.username
    if user_name != BARBER_USERNAME:
        # в этом случае логика для пользователя, который хочет записаться
        if barber_chat_id is None:
            bot.send_message(
                message.chat.id,
                'В системе не зарегистрировано ни одного барбера, попробуйте позже',
                reply_markup=ReplyKeyboardRemove()
            )
            return

        available_slots = []
        user_process_data[user_name] = {"available_slots": []}
        all_slots = get_all_slots()
        for slot in all_slots:
            if slot not in busy_slots:
                available_slots.append(slot)
        user_process_data[user_name]['available_slots'] = sorted(available_slots)
        bot.send_message(message.chat.id, 'Здравствуйте!', reply_markup=ReplyKeyboardRemove())
        if not available_slots:
            bot.send_message(message.chat.id, 'Нет свободных слотов, попробуйте позже')
            return

        keyboard_with_full_date = ReplyKeyboardMarkup(resize_keyboard=True)
        already_added_days = []
        for available_slot in sorted(available_slots):
            if available_slot.day not in already_added_days:
                keyboard_button = KeyboardButton(
                    text='{}, {} {} ({})'.format(
                        available_slot.strftime("%A"),  # Понедельник
                        available_slot.day,  # 13
                        available_slot.strftime("%B"),  # Март
                        available_slot.strftime("%d.%m.%Y"),  # 13.03.2023
                    )
                )
                keyboard_with_full_date.add(keyboard_button)
                already_added_days.append(available_slot.day)

        bot.send_message(message.chat.id, 'Здравствуйте!', reply_markup=ReplyKeyboardRemove())
        bot.send_message(message.chat.id, 'Выберите день для записи', reply_markup=keyboard_with_full_date)
        bot.register_next_step_handler(message, day_choose)
    else:
        # в этом случае логика для барбера
        if barber_chat_id != message.chat.id:
            barber_chat_id = message.chat.id
            try:
                db_connection.execute(CREATE_BARBER_CHAT_ID.format(chat_id=barber_chat_id))
                db_connection.commit()
            except Exception as e:
                print("[ERROR] Ошибка при записи данных о барбере: {}".format(str(e)))

        bot.send_message(barber_chat_id, 'Добрый день, готов принимать записи')


def day_choose(message):
    user_name = message.from_user.username
    chosen_slot = chosen_slot_to_date(message.text)
    user_process_data[user_name]['chosen_slot'] = chosen_slot
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for available_slot in user_process_data[user_name]['available_slots']:
        if (
                available_slot.day == chosen_slot.day and
                available_slot.month == chosen_slot.month and
                available_slot.year == chosen_slot.year
        ):
            keyboard.add(KeyboardButton(text='{}:{}0'.format(available_slot.hour, available_slot.minute)))

    bot.send_message(message.chat.id, 'Выберите время', reply_markup=keyboard)
    bot.register_next_step_handler(message, time_choose)


def time_choose(message):
    global barber_chat_id
    user_name = message.from_user.username
    splitted_time = message.text.split(':')  # [11, 00]
    chosen_slot = user_process_data[user_name]['chosen_slot']
    chosen_slot = datetime(
        chosen_slot.year, chosen_slot.month, chosen_slot.day, int(splitted_time[0]), int(splitted_time[1])
    )
    if chosen_slot in busy_slots:
        bot.send_message(
            message.chat.id,
            'Похоже это время уже заняли, пожалуйста начните сначала через команду /start'
        )
    else:
        busy_slots.append(chosen_slot)
        try:
            chosen_slot_str = chosen_slot.strftime("%d.%m.%Y,%H:%M")
            db_connection.execute(CREATE_SLOT.format(time=chosen_slot_str, username=user_name))
            db_connection.commit()
        except Exception:
            bot.send_message(
                message.chat.id, 'Ошибка при создании записи, попробуйте снова', reply_markup=ReplyKeyboardRemove()
            )
        else:
            bot.send_message(message.chat.id, 'Вы успешно записаны, спасибо', reply_markup=ReplyKeyboardRemove())
            bot.send_message(
                barber_chat_id,
                'У вас новая запись. Пользователь: {}, дата и время: {}'.format(user_name, chosen_slot_str))

    user_process_data.pop(user_name)


if __name__ == '__main__':
    db_connection = sqlite3.connect(DB_NAME, check_same_thread=False)
    for db_to_create in (SLOTS_CREATE_TABLE, BARBER_CREATE_TABLE):
        try:
            db_connection.execute(db_to_create)
        except Exception as e:
            pass

    for row in db_connection.execute(SELECT_ALL_SLOTS):
        # в row лежит, например: (13.03.2023,15:00, ), поэтому нужно достать row[0]
        busy_slots.append(datetime.strptime(row[0], '%d.%m.%Y,%H:%M'))

    barber_chat_id_result = db_connection.execute(SELECT_BARBER_CHAT_ID).fetchone()
    if barber_chat_id_result:
        barber_chat_id = barber_chat_id_result[0]

    print("Starting bot...")
    bot.infinity_polling()
    print('Shutdown...')
    db_connection.close()
