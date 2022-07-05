from wtt.utils import date as date_utils
from wtt.utils import input as input_utils
from wtt.utils import uuid as uuid_utils


class Holiday(object):
    def __init__(self, date, location, uuid=None, description=None, working_hours=0, repeats_every_year=True):
        if uuid is None:
            uuid = uuid_utils.random_uuid()
        if type(date) is str:
            date = date_utils.iso_string_to_datetime(date)

        self.uuid = uuid
        self.description = description
        self.date = date
        self.location = location
        self.working_hours = working_hours
        self.repeats_every_year = bool(repeats_every_year)

    @staticmethod
    def FromDatabaseObj(database_obj):
        uuid = database_obj.get('uuid')
        description = database_obj.get('description')
        date = database_obj.get('date')
        location = database_obj.get('location')
        working_hours = database_obj.get('working_hours')
        repeats_every_year = database_obj.get('repeats_every_year')
        holiday = Holiday(uuid=uuid, description=description, date=date, location=location,
                          working_hours=working_hours, repeats_every_year=repeats_every_year)
        return holiday

    @staticmethod
    def FromPrompt():
        print('Creating a new holiday')
        uuid = None
        print('Enter the holiday description: ')
        description = input_utils.input_string()
        while True:
            try:
                print('Enter the holiday date (dd/MM/yyyy): ')
                date = input_utils.input_string()
                date_utils.assert_datetime_string_format(date)
                date = date_utils.string_to_datetime(date)
                date = date_utils.set_timezone_on_datetime(date, 'UTC')
                break
            except ValueError as e:
                print(e)
        print('Enter the holiday location (Brasil): ')
        location = input_utils.input_string()
        print('Enter how many hours you need to work on this holiday (0): ')
        working_hours = input_utils.input_number(greater_or_eq=0, lower_or_eq=24)
        print('Does this holiday occurs every year?: ')
        repeats_every_year = input_utils.input_boolean()
        holiday = Holiday(uuid=uuid, description=description, date=date, location=location,
                          working_hours=working_hours, repeats_every_year=repeats_every_year)
        return holiday

    def to_database_params(self):
        params = []
        params.append(self.uuid)
        params.append(self.description)
        params.append(self.date)
        params.append(self.location)
        params.append(self.working_hours)
        params.append(self.repeats_every_year)
        params = tuple(params)
        return params

    @staticmethod
    def GetFields():
        fields = ("uuid", "description", "date", "location", "working_hours", "repeats_every_year")
        return fields
