import os

from wtt.models.time_card import TimeCard
from wtt.repositories import absence as absence_repo
from wtt.repositories import holiday as holiday_repo
from wtt.repositories import time_card as time_card_repo
from wtt.utils import date as date_utils
from wtt.utils import time as time_utils

COOLDOWN_IN_SECONDS = int(os.getenv('COOLDOWN_IN_SECONDS', '60'))


def clock_in_out(profile):
    time_cards = time_card_repo.get_today_time_cards(profile)
    if len(time_cards) == 0 or abs(
            time_cards[-1].event_timestamp_utc - date_utils.get_utc_now()).seconds >= COOLDOWN_IN_SECONDS:
        time_card = time_card_repo.insert_time_card_from_cli(profile)
        local_tc_event = date_utils.convert_datetime_timezone_to_local(time_card.event_timestamp_utc)
        print(
            f'Added time card for {profile.first_name} at {date_utils.datetime_to_string(local_tc_event)}')
    else:
        raise TimeoutError('Error while storing time card, the clock operation is still on cooldown')


def clock_in_out_manually(profile, event_timestamp):
    event_timestamp = date_utils.string_to_datetime(event_timestamp, '%d/%m/%Y %H:%M:%S')
    time_card = time_card_repo.insert_time_card_manually(profile, event_timestamp)
    local_tc_event = date_utils.convert_datetime_timezone_to_local(time_card.event_timestamp_utc)
    print(
        f'Added time card for {profile.first_name} at {date_utils.datetime_to_string(local_tc_event)}')


def convert_time_cards_to_minutes(time_cards):
    time_cards_in_min = [time_utils.datetime_to_minutes(el.event_timestamp_utc) for el in time_cards]
    return time_cards_in_min


def print_today_report(profile):
    office_hours = profile.daily_office_hours
    today = date_utils.get_now()
    is_work_day = date_utils.is_work_day(today)
    today_holiday = holiday_repo.get_date_holiday(profile, today)
    has_recorded_absence = absence_repo.has_absence_on_date(profile, today)
    time_cards = time_card_repo.get_today_time_cards(profile)

    if (not is_work_day and len(time_cards) == 0) or today_holiday is not None or has_recorded_absence:
        if today_holiday is not None:
            office_hours = today_holiday.working_hours
        if not is_work_day and len(time_cards) == 0:
            office_hours = 0
        if has_recorded_absence:
            office_hours = 0
        if office_hours == 0:
            has_holiday = today_holiday is not None
            report = get_report_for_non_working_day(is_work_day, has_holiday, has_recorded_absence)
            print(report)
            return

    worked_minutes = get_worked_time_from_any_cards(time_cards, profile.auto_insert_lunch_time)
    report = get_default_report(office_hours, profile.max_allowed_extra_hours, worked_minutes, len(time_cards))
    print(report)


def get_worked_time_from_any_cards(time_cards, auto_insert_lunch_time=0):
    if len(time_cards) == 0:
        worked_minutes = 0
    elif len(time_cards) in (1, 2):
        worked_minutes = get_worked_time_from_1_2_cards(time_cards, auto_insert_lunch_time)
    elif len(time_cards) == 3:
        worked_minutes = get_worked_time_from_3_cards(time_cards)
    elif len(time_cards) % 2 == 0:
        worked_minutes = get_worked_time_from_even_cards(time_cards)
    else:
        worked_minutes = get_worked_time_from_odd_cards(time_cards)
    return worked_minutes


def get_worked_time_from_1_2_cards(time_cards, automatic_lunch_insert=0):
    time_cards_in_mins = convert_time_cards_to_minutes(time_cards)
    t1 = time_cards_in_mins[0]
    if len(time_cards) == 2:
        t_last = time_cards_in_mins[1]
    else:
        t_last = time_utils.datetime_to_minutes(date_utils.get_utc_now())

    p1 = t_last - t1

    worked_minutes = max(p1 - automatic_lunch_insert, 0)  # Automatically includes launch time
    return worked_minutes


def get_worked_time_from_3_cards(time_cards):
    t1, t2, t3 = convert_time_cards_to_minutes(time_cards)
    now = time_utils.datetime_to_minutes(date_utils.get_utc_now())

    p1 = t2 - t1
    p2 = now - t3

    worked_minutes = p2 + p1
    return worked_minutes


def get_worked_time_from_even_cards(time_cards):
    time_cards_in_mins = convert_time_cards_to_minutes(time_cards)
    sum_of_worked_mins = sum_of_worked_timecards(time_cards_in_mins)

    return sum_of_worked_mins


def get_worked_time_from_odd_cards(time_cards):
    return get_worked_time_from_even_cards(
        time_cards + [TimeCard(time_cards[0].profile_uuid, event_timestamp_utc=date_utils.get_utc_now(),
                               insertion_method='mocked')])


def sum_of_worked_timecards(time_cards_in_mins):
    if len(time_cards_in_mins) % 2 != 0:
        raise Exception('Expecting an even amount of cards in minutes')

    sum_of_worked_mins = 0
    for i in range(0, len(time_cards_in_mins), 2):
        sum_of_worked_mins += time_cards_in_mins[i + 1] - time_cards_in_mins[i]
    return sum_of_worked_mins


def get_report_for_non_working_day(is_work_day, has_holiday, has_recorded_absence):
    local_time = date_utils.get_now()

    if has_recorded_absence:
        reason = 'You don\'t have to work today, since you already registered absence today'
    elif has_holiday:
        reason = 'You don\'t have to work today, since today is holiday'
    elif not is_work_day:
        reason = 'You don\'t have to work today, since today is not a workday'
    else:
        reason = 'ERROR'

    report = f"Now: {date_utils.datetime_to_string(local_time)}\n{reason}"
    return report


def get_default_report(daily_office_hours, max_extra_hours, worked_minutes, amount_cards):
    local_time = date_utils.get_now()

    missing_minutes_regular_shift = daily_office_hours * 60 - worked_minutes
    missing_minutes_extra_shift = (daily_office_hours + max_extra_hours) * 60 - worked_minutes

    clock_out_at_regular_shift = date_utils.add_minutes_to_datetime(local_time, missing_minutes_regular_shift)
    clock_out_at_extra_shift = date_utils.add_minutes_to_datetime(local_time, missing_minutes_extra_shift)

    worked_time_str = f'Worked: {time_utils.timestamp_to_human_readable_str(worked_minutes, minutes=True)} ({amount_cards} time cards)'
    if worked_minutes == 0:
        worked_time_str = 'You haven\'t started to work yet'

    report = f"""Now: {date_utils.datetime_to_string(local_time)}
    
    {worked_time_str}
    
    Regular shift ({daily_office_hours}h): 
        Clock out at: {date_utils.datetime_to_string(clock_out_at_regular_shift, date_format='%H:%M:%S')}
        Missing: {time_utils.timestamp_to_human_readable_str(missing_minutes_regular_shift, minutes=True)}
        
    Extra hours shift ({daily_office_hours + max_extra_hours}h): 
        Clock out at: {date_utils.datetime_to_string(clock_out_at_extra_shift, date_format='%H:%M:%S')}
        Missing: {time_utils.timestamp_to_human_readable_str(missing_minutes_extra_shift, minutes=True)}"""
    return report


def print_extra_hours_balance_in_minutes(profile):
    bal = get_extra_hours_balance_in_minutes(profile)
    report = get_report_from_extra_hours_balance_in_minutes(bal)
    print(report)


def get_extra_hours_balance_in_minutes(profile):
    grouped_time_cards = time_card_repo.get_profile_time_cards_grouped_by_day(profile)
    all_work_days = date_utils.get_all_dates_between(profile.start_date, date_utils.get_now())
    all_work_days = list(filter(date_utils.is_work_day, all_work_days))
    for work_day in all_work_days:
        if work_day not in grouped_time_cards['glossary']:
            grouped_time_cards['glossary'].add(work_day)
            grouped_time_cards['results'].append({
                'date': work_day,
                'cards': []
            })

    total_balance_in_min = 0
    for work_day in grouped_time_cards['results']:
        total_shift = profile.daily_office_hours
        holiday = holiday_repo.get_date_holiday(profile, work_day['date'])
        if holiday is not None:
            total_shift = holiday.working_hours
        if len(work_day['cards']) % 2 != 0:  # avoid dealing with incorrect time_cards
            work_day['cards'] = work_day['cards'][:-1]
        day_balance_in_min = get_worked_time_from_any_cards(work_day['cards']) - total_shift * 60
        total_balance_in_min += day_balance_in_min
    return total_balance_in_min


def get_report_from_extra_hours_balance_in_minutes(total_balance_in_min):
    total_balance = 'Extra hours balance: '
    if total_balance_in_min < 0:
        total_balance += '- '
    else:
        total_balance += '+ '
    total_balance += f'{int(abs(total_balance_in_min) // 60)} hours'
    remainder = int(abs(total_balance_in_min) % 60)
    if remainder > 0:
        total_balance += f' and {remainder} minutes'
    return total_balance


def display_time_cards_of_a_day(profile, date):
    start_date, end_date = date_utils.get_day_interval_from_date(date)
    cards = time_card_repo.get_profile_time_cards(profile, start_date, end_date)
    print(f'Cards for {date_utils.datetime_to_string(date, "%d/%m/%Y")}:')
    if len(cards) == 0:
        print('\tEmpty')
    for card in cards:
        print(f'\t{card}')
    print()


def delete_time_card(profile, card_uuid):
    time_card_repo.delete_time_card(profile, card_uuid)
    print(f'Deleted time card with uuid {card_uuid}')
