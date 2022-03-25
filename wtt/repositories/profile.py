from wtt.models.profile import Profile
from wtt.repositories import execute_query


def get_all_profiles():
    query = """
            SELECT * FROM profiles ORDER BY created_at_utc;
        """
    results = execute_query(query, fetch=True)
    results = [Profile.FromDatabaseObj(el) for el in results]
    return results


def create_profile(profile):
    params = profile.to_database_params()
    fields = '(' + ', '.join([f'"{el}"' for el in Profile.GetFields()]) + ')'
    query_insert = f"""
        INSERT INTO profiles 
            {fields}
        VALUES
            ({', '.join(['?'] * len(params))})
        ;
    """
    execute_query(query_insert, params=params)


def get_current_profile():
    profiles = get_all_profiles()
    if len(profiles) == 0:
        return None
    elif len(profiles) == 1:
        return profiles[0]
    else:
        # TODO select between profiles using some configuration
        raise NotImplementedError('Not implemented yet!')
