from contextlib import contextmanager
from datetime import datetime
from const import BASE_URL, LOGOUT_ARGS, LOGIN_ARGS


def _gen_login_payload(username, password):
    now = datetime.now()
    utcnow = datetime.utcnow()
    timezoneOffSet = int((utcnow - now).total_seconds() / 60)
    return {"cufld": password, "userid": username,
            "pwd": password, "timezoneOffset": timezoneOffSet}


def _login(session, username, password):
    payload = _gen_login_payload(username, password)
    response = session.post(BASE_URL, params=LOGIN_ARGS, data=payload)
    response.raise_for_status()


def _logout(session):
    response = session.get(BASE_URL, params=LOGOUT_ARGS)
    response.raise_for_status()


@contextmanager
def authenticate(session, username, password):
    _login(session, username, password)
    yield
    _logout(session)
