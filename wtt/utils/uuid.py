import uuid


def random_uuid(without_dashes=False):
    if without_dashes:
        return uuid.uuid4().hex
    else:
        return str(uuid.uuid4())
