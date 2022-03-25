from wtt.models.holiday import Holiday
from wtt.repositories import holiday as holiday_repo
from wtt.utils import date as date_utils


def prompt_and_insert_holiday():
    holiday = Holiday.FromPrompt()
    holiday_repo.create_holiday(holiday)
    print(f'A new holiday was added on {date_utils.datetime_to_string(holiday.date, "%d/%m/%Y")}')
    return holiday
