import datetime
import time


def get_first_slot_date():
    current_date = datetime.datetime.now()
    next_day_date_dirty = current_date + datetime.timedelta(1)
    next_day_date_midnight = datetime.datetime(next_day_date_dirty.year, next_day_date_dirty.month, next_day_date_dirty.day)
    return next_day_date_midnight + datetime.timedelta(hours=11)


def get_all_slots_during_day(date):
    slots = [date]
    for i in range(1, 10):
        slots.append(date + datetime.timedelta(hours=i))
    return slots


def get_all_available_slots():
    start_date = get_first_slot_date()
    all_slots = get_all_slots_during_day(start_date) + get_all_slots_during_day(
        start_date + datetime.timedelta(days=1)) + get_all_slots_during_day(start_date + datetime.timedelta(days=2))
    return all_slots


def chosen_day_to_date(button_text: str):
    splitted_date = button_text.split('(')
    date_str = splitted_date[1][:-1]
    return datetime.datetime.strptime(date_str, '%d.%m.%Y')
