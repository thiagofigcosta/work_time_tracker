from wtt.utils import date as date_utils
from wtt.utils import uuid as uuid_utils


class TimeCard(object):
    def __init__(self, profile_uuid, insertion_method, uuid=None, event_timestamp_utc=None, gen_uuid=True):
        if uuid is None and gen_uuid:
            uuid = uuid_utils.random_uuid()
        if type(event_timestamp_utc) is str:
            event_timestamp_utc = date_utils.iso_string_to_datetime(event_timestamp_utc)

        self.uuid = uuid
        self.profile_uuid = profile_uuid
        self.insertion_method = insertion_method
        self.event_timestamp_utc = event_timestamp_utc

    @staticmethod
    def GetFields():
        fields = ("uuid", "profile_uuid", "event_timestamp_utc", "insertion_method")
        return fields

    @staticmethod
    def FromDatabaseObj(database_obj):
        uuid = database_obj.get('uuid')
        profile_uuid = database_obj.get('profile_uuid')
        event_timestamp_utc = database_obj.get('event_timestamp_utc')
        insertion_method = database_obj.get('insertion_method')
        time_card = TimeCard(uuid=uuid, profile_uuid=profile_uuid, event_timestamp_utc=event_timestamp_utc,
                             insertion_method=insertion_method)
        return time_card

    def to_database_params(self):
        params = []
        params.append(self.uuid)
        params.append(self.profile_uuid)
        if self.event_timestamp_utc is None:
            self.event_timestamp_utc = date_utils.get_utc_now()
        params.append(self.event_timestamp_utc)
        params.append(self.insertion_method)
        params = tuple(params)
        return params

    def __str__(self):
        converted_date = date_utils.convert_datetime_timezone_to_local(self.event_timestamp_utc)
        converted_date = date_utils.datetime_to_string(converted_date)
        string = f'uuid: {self.uuid} | event_timestamp: {converted_date} | profile_uuid: {self.profile_uuid} | insertion_method: {self.insertion_method}'
        return string

    def __repr__(self):
        return self.__str__()
