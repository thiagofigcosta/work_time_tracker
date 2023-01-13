from wtt.models.time_card import TimeCard
from wtt.repositories import execute_query
from wtt.utils import date as date_utils

SHORT_SEARCH_LIMIT_IN_DAYS = None  # None or number, such as 60


def get_all_time_cards():
    query = """
            SELECT * FROM time_cards
            ORDER BY event_timestamp_utc;
        """
    results = execute_query(query, fetch=True)
    results = [TimeCard.FromDatabaseObj(el) for el in results]
    return results


def filter_time_cards_before_localized(time_cards, last_date):
    last_date_only = date_utils.date_to_beginning_of_day(last_date)
    if len(time_cards) > 0:
        last_date_only = date_utils.set_timezone_on_datetime_from_datetime(last_date_only,
                                                                           time_cards[0].get_localized_timestamp())

    filtered_localized = []
    for tc in time_cards:
        localized_date_only = date_utils.date_to_beginning_of_day(tc.get_localized_timestamp())
        if localized_date_only <= last_date_only:
            filtered_localized.append(tc)
    return filtered_localized


def get_profile_time_cards(profile, start_date=None, end_date=None):
    if start_date is None:
        start_date = profile.start_date
    if end_date is None:
        end_date = date_utils.get_utc_now()
    end_date_plus_one = date_utils.add_days_to_datetime(end_date, 1)
    query = """
            SELECT * FROM time_cards
            WHERE profile_uuid = ? AND (event_timestamp_utc >= ? AND event_timestamp_utc <= ?)
            ORDER BY event_timestamp_utc;
        """
    params = (profile.uuid, start_date, end_date_plus_one)
    results = execute_query(query, params=params, fetch=True)
    results = [TimeCard.FromDatabaseObj(el) for el in results]
    results = filter_time_cards_before_localized(results, end_date)
    return results


def persist_time_card(time_card):
    params = time_card.to_database_params()
    fields = '(' + ', '.join([f'"{el}"' for el in TimeCard.GetFields()]) + ')'
    query_insert = f"""
        INSERT INTO time_cards 
            {fields}
        VALUES
            ({', '.join(['?'] * len(params))})
        ;
    """
    execute_query(query_insert, params=params)
    return time_card


def insert_time_card(profile, method, event_timestamp):
    time_card = TimeCard(profile.uuid, method, event_timestamp_utc=event_timestamp)
    return persist_time_card(time_card)


def insert_time_card_from_cli(profile):
    method = 'cli'
    time_card = TimeCard(profile.uuid, method)
    return persist_time_card(time_card)


def insert_time_card_manually(profile, event_timestamp):
    return insert_time_card(profile, 'manual', event_timestamp)


def get_today_time_cards(profile):
    start_date, end_date = date_utils.get_today_interval()
    start_date = date_utils.convert_datetime_timezone(start_date)
    end_date = date_utils.convert_datetime_timezone(end_date)
    return get_profile_time_cards(profile, start_date=start_date, end_date=end_date)


def get_profile_time_cards_grouped_by_day(profile, start_date=None, end_date=None):
    # """
    # SELECT
    #     strftime('%Y-%m-%d',event_timestamp_utc) as working_day,
    #     GROUP_CONCAT(event_timestamp_utc) as event_timestamps_utc
    # FROM time_cards
    # WHERE profile_uuid = ? AND (event_timestamp_utc >= ? AND event_timestamp_utc <= ?)
    # GROUP BY strftime('%Y-%m-%d',event_timestamp_utc)
    # ORDER BY strftime('%Y-%m-%d',event_timestamp_utc);
    # """
    time_cards = get_profile_time_cards(profile, start_date, end_date)
    results = {
        'glossary': set(),
        'results': []
    }
    aggregated = {}
    for time_card in time_cards:
        date_str = date_utils.datetime_to_string(time_card.get_localized_timestamp(), '%Y-%m-%d')
        working_day = date_utils.set_timezone_on_datetime(date_utils.iso_string_to_datetime(date_str), 'UTC')
        if working_day not in aggregated:
            aggregated[working_day] = []
        aggregated[working_day].append(time_card)
        results['glossary'].add(working_day)
    for date, cards in aggregated.items():
        parsed = {
            'date': date,
            'cards': sorted(cards, key=lambda x: x.event_timestamp_utc)
        }
        results['results'].append(parsed)
    return results


def delete_time_card(profile, card_uuid):
    query = """
            DELETE FROM time_cards
            WHERE profile_uuid = ? AND uuid = ?;
        """
    params = (profile.uuid, card_uuid)
    execute_query(query, params=params)
