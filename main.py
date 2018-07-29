import requests
import sys
import time
from datetime import datetime

BASE_URL = "https://campus.concordia.ca/psp/pscsprd/EMPLOYEE/SA/"
LOGIN_ARGS = {"cmd" : "login", "languageCd" : "ENG"}
LOGOUT_ARGS = {"cmd" : "logout"}

session = requests.Session()

def gen_login_payload(username, password):
    now = datetime.now()
    utcnow = datetime.utcnow()
    timezoneOffSet = int((utcnow - now).total_seconds() / 60)
    return {"cufld" : password, "userid" : username,
            "pwd" : password, "timezoneOffset" : timezoneOffSet}


def login(username, password):
    payload = gen_login_payload(username, password)
    print(payload)
    response = session.post(BASE_URL, params=LOGIN_ARGS, data=payload)
    response.raise_for_status()


def logout():
    response = session.get(BASE_URL, params=LOGOUT_ARGS)
    response.raise_for_status()


if __name__ == "__main__":
    username = sys.argv[1]
    password = sys.argv[2]
    login(username, password)
    logout()

