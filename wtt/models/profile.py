from wtt.utils import date as date_utils
from wtt.utils import input as input_utils
from wtt.utils import uuid as uuid_utils


class Profile(object):
    def __init__(self, first_name, last_name, company, working_location, start_date, uuid=None, daily_office_hours=8,
                 required_lunch_time=1, auto_insert_lunch_time=0, max_allowed_extra_hours=2,
                 latest_working_hour='22:00:00',
                 min_hours_between_working_days=11, initial_extra_hours_balance=0, default_timezone='Etc/GMT-3',
                 created_at_utc=None, updated_at_utc=None):
        if uuid is None:
            uuid = uuid_utils.random_uuid()
        if type(start_date) is str:
            start_date = date_utils.iso_string_to_datetime(start_date)
        if type(latest_working_hour) is str:
            try:
                latest_working_hour = date_utils.string_to_datetime(latest_working_hour, date_format='%H:%M:%S')
            except ValueError:
                pass
            try:
                latest_working_hour = date_utils.string_to_datetime(latest_working_hour, date_format='%H:%M')
            except ValueError:
                pass
        if type(created_at_utc) is str:
            created_at_utc = date_utils.iso_string_to_datetime(created_at_utc)
        if type(updated_at_utc) is str:
            updated_at_utc = date_utils.iso_string_to_datetime(updated_at_utc)

        self.uuid = uuid
        self.first_name = first_name
        self.last_name = last_name
        self.company = company
        self.working_location = working_location
        self.start_date = start_date
        self.daily_office_hours = daily_office_hours
        self.required_lunch_time = required_lunch_time
        self.auto_insert_lunch_time = auto_insert_lunch_time
        self.max_allowed_extra_hours = max_allowed_extra_hours
        self.latest_working_hour = latest_working_hour
        self.min_hours_between_working_days = min_hours_between_working_days
        self.initial_extra_hours_balance = initial_extra_hours_balance
        self.default_timezone = default_timezone
        self.created_at_utc = created_at_utc
        self.updated_at_utc = updated_at_utc

    @staticmethod
    def FromDatabaseObj(database_obj):
        uuid = database_obj.get('uuid')
        first_name = database_obj.get('first_name')
        last_name = database_obj.get('last_name')
        company = database_obj.get('company')
        working_location = database_obj.get('working_location')
        start_date = database_obj.get('start_date')
        daily_office_hours = database_obj.get('daily_office_hours')
        required_lunch_time = database_obj.get('required_lunch_time')
        auto_insert_lunch_time = database_obj.get('auto_insert_lunch_time')
        max_allowed_extra_hours = database_obj.get('max_allowed_extra_hours')
        latest_working_hour = database_obj.get('latest_working_hour')
        min_hours_between_working_days = database_obj.get('min_hours_between_working_days')
        initial_extra_hours_balance = database_obj.get('initial_extra_hours_balance')
        default_timezone = database_obj.get('default_timezone')
        created_at_utc = database_obj.get('created_at_utc')
        updated_at_utc = database_obj.get('updated_at_utc')
        profile = Profile(uuid=uuid, first_name=first_name, last_name=last_name, company=company,
                          working_location=working_location, start_date=start_date,
                          daily_office_hours=daily_office_hours,
                          required_lunch_time=required_lunch_time, auto_insert_lunch_time=auto_insert_lunch_time,
                          max_allowed_extra_hours=max_allowed_extra_hours, latest_working_hour=latest_working_hour,
                          min_hours_between_working_days=min_hours_between_working_days,
                          initial_extra_hours_balance=initial_extra_hours_balance, default_timezone=default_timezone,
                          created_at_utc=created_at_utc, updated_at_utc=updated_at_utc)
        return profile

    @staticmethod
    def GetFields():
        fields = ("uuid", "first_name", "last_name", "company", "working_location", "start_date", "daily_office_hours",
                  "required_lunch_time", "auto_insert_lunch_time", "max_allowed_extra_hours", "latest_working_hour",
                  "min_hours_between_working_days",
                  "initial_extra_hours_balance", "default_timezone", "created_at_utc", "updated_at_utc")
        return fields

    @staticmethod
    def FromPrompt():
        print('Creating a new profile')
        uuid = None
        print('Enter the first name: ')
        first_name = input_utils.input_string()
        print('Enter the last name: ')
        last_name = input_utils.input_string()
        print('Enter the company name: ')
        company = input_utils.input_string()
        print('Enter the working location: ')
        working_location = input_utils.input_string()
        while True:
            try:
                print('Enter the job start date (dd/MM/yyyy): ')
                start_date = input_utils.input_string()
                date_utils.assert_datetime_string_format(start_date)
                start_date = date_utils.string_to_datetime(start_date)
                break
            except ValueError as e:
                print(e)
        print('Enter your daily shift (hours): ')
        daily_office_hours = input_utils.input_number(greater_or_eq=1, lower_or_eq=24)
        print('Enter your required lunch time (hours): ')
        required_lunch_time = input_utils.input_number(greater_or_eq=0, lower_or_eq=24)
        print('Enter the automatic lunch time insertion (hours): ')
        auto_insert_lunch_time = input_utils.input_number(greater_or_eq=0, lower_or_eq=24)
        print('Enter the max allowed daily extra hours: ')
        max_allowed_extra_hours = input_utils.input_number(greater_or_eq=0, lower_or_eq=24)
        while True:
            try:
                print('Enter the last working hour (hh:mm:ss): ')
                latest_working_hour = input_utils.input_string()
                date_utils.assert_datetime_string_format(latest_working_hour, date_format='%H:%M:%S')
                latest_working_hour = date_utils.string_to_datetime(latest_working_hour, date_format='%H:%M:%S')
                break
            except ValueError as e:
                print(e)
        print('Enter the minimum hours between working days: ')
        min_hours_between_working_days = input_utils.input_number(greater_or_eq=0, lower_or_eq=16)
        print('Enter the initial extra hours balance: ')
        initial_extra_hours_balance = input_utils.input_number(greater_or_eq=0)
        while True:
            try:
                print('Enter the default timezone (\'Etc/GMT-3\', \'America/Sao_Paulo\', ...): ')
                default_timezone = input_utils.input_string()
                date_utils.assert_valid_timezone(default_timezone)
                break
            except ValueError as e:
                print(e)
        created_at_utc = None
        updated_at_utc = None
        profile = Profile(uuid=uuid, first_name=first_name, last_name=last_name, company=company,
                          working_location=working_location, start_date=start_date,
                          daily_office_hours=daily_office_hours,
                          required_lunch_time=required_lunch_time, auto_insert_lunch_time=auto_insert_lunch_time,
                          max_allowed_extra_hours=max_allowed_extra_hours, latest_working_hour=latest_working_hour,
                          min_hours_between_working_days=min_hours_between_working_days,
                          initial_extra_hours_balance=initial_extra_hours_balance, default_timezone=default_timezone,
                          created_at_utc=created_at_utc, updated_at_utc=updated_at_utc)
        return profile

    def to_database_params(self):
        params = []
        params.append(self.uuid)
        params.append(self.first_name)
        params.append(self.last_name)
        params.append(self.company)
        params.append(self.working_location)
        params.append(self.start_date)
        params.append(self.daily_office_hours)
        params.append(self.required_lunch_time)
        params.append(self.auto_insert_lunch_time)
        params.append(self.max_allowed_extra_hours)
        params.append(self.latest_working_hour)
        params.append(self.max_allowed_extra_hours)
        params.append(self.min_hours_between_working_days)
        params.append(self.default_timezone)
        created_at_utc = self.created_at_utc
        if created_at_utc is None:
            created_at_utc = date_utils.get_utc_now()
        params.append(created_at_utc)
        self.updated_at_utc = date_utils.get_utc_now()
        params.append(self.updated_at_utc)
        params = tuple(params)
        return params
