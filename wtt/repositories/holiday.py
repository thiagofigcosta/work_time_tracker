from wtt.models.holiday import Holiday
from wtt.repositories import execute_query
from wtt.utils import date as date_utils


def get_all_holidays():
    query = """
            SELECT * FROM holidays ORDER BY "date";
        """
    results = execute_query(query, fetch=True)
    results = [Holiday.FromDatabaseObj(el) for el in results]
    return results


def get_profile_holidays(profile):
    query = """
            SELECT * FROM holidays
            WHERE "location" = ?
            ORDER BY "date";
        """
    results = execute_query(query, params=(profile.working_location,), fetch=True)
    results = [Holiday.FromDatabaseObj(el) for el in results]
    return results


def has_holiday_on_date(profile, date):
    query = """
            SELECT * FROM holidays
            WHERE "location" = ? AND 
                ((repeats_every_year AND strftime('%d', "date") = ? AND strftime('%m', "date") = ?) OR 
                    (NOT repeats_every_year AND "date" = ?))
        """
    params = (profile.working_location, date.day, date.month, date)
    results = execute_query(query, params=params, fetch=True)
    result = len(results) > 0
    return result


def get_date_holiday(profile, date):
    query = """
            SELECT * FROM holidays
            WHERE "location" = ? AND 
                ((repeats_every_year AND strftime('%d', "date") = ? AND strftime('%m', "date") = ?) OR 
                    (NOT repeats_every_year AND strftime('%d/%m/%Y',"date") = ?))
            ORDER BY "working_hours";
        """
    params = (profile.working_location, f"{date.day:02d}", f"{date.month:02d}", date_utils.datetime_to_string(date, '%d/%m/%Y'))
    results = execute_query(query, params=params, fetch=True)
    if len(results) > 0:
        return Holiday.FromDatabaseObj(results[0])
    return None


def create_holiday(holiday):
    params = holiday.to_database_params()
    fields = '(' + ', '.join([f'"{el}"' for el in Holiday.GetFields()]) + ')'
    query_insert = f"""
        INSERT INTO holidays 
            {fields}
        VALUES
            ({', '.join(['?'] * len(params))})
        ;
    """
    execute_query(query_insert, params=params)
