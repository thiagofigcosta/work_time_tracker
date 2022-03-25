from wtt.models.profile import Profile
from wtt.repositories import profile as profile_repo


def get_current_profile():
    current_profile = profile_repo.get_current_profile()
    if current_profile is None:
        current_profile = prompt_and_insert_profile()
    return current_profile


def prompt_and_insert_profile():
    profile = Profile.FromPrompt()
    profile_repo.create_profile(profile)
    return profile
