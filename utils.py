from datetime import datetime, timedelta


def get_first_slot_date():
    # получает первый слот (11.00) следующего дня
    current_date = datetime.now()
    next_day_date = current_date + timedelta(1)
    next_day_date_midnight = datetime(next_day_date.year, next_day_date.month, next_day_date.day)
    return next_day_date_midnight + timedelta(hours=11)


def get_all_slots_during_day(first_slot_date):
    slots = [first_slot_date]
    for i in range(1, 10):  # каждый час до 20.00
        slots.append(first_slot_date + timedelta(hours=i))
    return slots


def get_all_slots():
    # получить все возможные слоты на ближайшие 3 дня
    first_slot_date = get_first_slot_date()
    all_slots = get_all_slots_during_day(first_slot_date) \
                + get_all_slots_during_day(first_slot_date + timedelta(days=1)) \
                + get_all_slots_during_day(first_slot_date + timedelta(days=2))
    return all_slots


def chosen_slot_to_date(slot_str):
    splitted_slot = slot_str.split('(')  # ["Monday, 13 March", 13.03.2023)]
    date_str = splitted_slot[1][:-1]  # 13.03.2023
    return datetime.strptime(date_str, '%d.%m.%Y')
