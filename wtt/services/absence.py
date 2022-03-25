from wtt.models.absence import Absence
from wtt.repositories import absence as absence_repo
from wtt.utils import date as date_utils


def prompt_and_insert_absence(profile):
    absence = Absence.FromPrompt(profile.uuid)
    absence_repo.create_absence(absence)
    print(f'A new absence was registered on {date_utils.datetime_to_string(absence.date, "%d/%m/%Y")}')
    return absence
