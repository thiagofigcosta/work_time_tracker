from wtt.utils import date as date_utils
from wtt.utils import input as input_utils
from wtt.utils import uuid as uuid_utils


class Absence(object):
    def __init__(self, profile_uuid, date, uuid=None, description=None, authorized=False):
        if uuid is None:
            uuid = uuid_utils.random_uuid()
        if type(date) is str:
            date = date_utils.iso_string_to_datetime(date)

        self.uuid = uuid
        self.profile_uuid = profile_uuid
        self.date = date
        self.description = description
        self.authorized = bool(authorized)

    @staticmethod
    def FromDatabaseObj(database_obj):
        uuid = database_obj.get('uuid')
        profile_uuid = database_obj.get('profile_uuid')
        date = database_obj.get('date')
        description = database_obj.get('description')
        authorized = database_obj.get('authorized')
        absence = Absence(uuid=uuid, profile_uuid=profile_uuid, date=date, description=description, authorized=authorized)
        return absence

    @staticmethod
    def FromPrompt(profile_uuid=None):
        print('Creating a new absence entry')
        uuid = None
        if profile_uuid is None:
            print('Enter the profile uuid: ')
            profile_uuid = input_utils.input_string()
        while True:
            try:
                print('Enter the absence date (dd/MM/yyyy): ')
                date = input_utils.input_string()
                date_utils.assert_datetime_string_format(date)
                date = date_utils.string_to_datetime(date)
                break
            except ValueError as e:
                print(e)
        print('Enter a description for your absence: ')
        description = input_utils.input_string()
        print('Is this absence authorized (don\'t have to "pay" the hours): ')
        authorized = input_utils.input_boolean()
        absence = Absence(uuid=uuid, profile_uuid=profile_uuid, date=date, description=description,authorized=authorized)
        return absence

    def to_database_params(self):
        params = []
        params.append(self.uuid)
        params.append(self.profile_uuid)
        params.append(self.date)
        params.append(self.description)
        params.append(self.authorized)
        params = tuple(params)
        return params

    @staticmethod
    def GetFields():
        fields = ("uuid", "profile_uuid", "date", "description", "authorized")
        return fields
