from wtt.models.absence import Absence
from wtt.repositories import execute_query
from wtt.utils import date as date_utils


def get_all_absences():
    query = """
            SELECT * FROM absences ORDER BY "date";
        """
    results = execute_query(query, fetch=True)
    results = [Absence.FromDatabaseObj(el) for el in results]
    return results


def get_profile_absences(profile):
    query = """
            SELECT * FROM absences
            WHERE profile_uuid = ?
            ORDER BY "date";
        """
    results = execute_query(query, params=(profile.uuid,), fetch=True)
    results = [Absence.FromDatabaseObj(el) for el in results]
    return results


def get_absence_on_date(profile, date):
    query = """
            SELECT * FROM absences
            WHERE profile_uuid = ? AND strftime('%d/%m/%Y',"date") = ?;
        """
    params = (profile.uuid, date_utils.datetime_to_string(date, '%d/%m/%Y'))
    results = execute_query(query, params=params, fetch=True)
    if len(results) > 0:
        abs = Absence.FromDatabaseObj(results[0])
    else:
        abs = None
    return abs


def has_absence_on_date(profile, date):
    query = """
            SELECT * FROM absences
            WHERE profile_uuid = ? AND strftime('%d/%m/%Y',"date") = ?;
        """
    params = (profile.uuid, date_utils.datetime_to_string(date, '%d/%m/%Y'))
    results = execute_query(query, params=params, fetch=True)
    result = len(results) > 0
    return result


def has_authorized_absence_on_date(profile, date):
    query = """
            SELECT * FROM absences
            WHERE profile_uuid = ? AND strftime('%d/%m/%Y',"date") = ? AND authorized = True;
        """
    params = (profile.uuid, date_utils.datetime_to_string(date, '%d/%m/%Y'))
    results = execute_query(query, params=params, fetch=True)
    result = len(results) > 0
    return result


def create_absence(absence):
    params = absence.to_database_params()
    fields = '(' + ', '.join([f'"{el}"' for el in Absence.GetFields()]) + ')'
    query_insert = f"""
        INSERT INTO absences 
            {fields}
        VALUES
            ({', '.join(['?'] * len(params))})
        ;
    """
    execute_query(query_insert, params=params)
