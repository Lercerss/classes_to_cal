BASE_URL = "https://campus.concordia.ca/psp/pscsprd/EMPLOYEE/SA/"
HOME_URL = BASE_URL + "c/SA_LEARNER_SERVICES.SSS_STUDENT_CENTER.GBL"
DATA_URL = BASE_URL + "c/SA_LEARNER_SERVICES.SSR_SSENRL_SCHD_W.GBL"
LOGIN_ARGS = {"cmd": "login", "languageCd": "ENG"}
LOGOUT_ARGS = {"cmd": "logout"}
FRAME_ID = 'ptifrmtgtframe'
ID_REGEX = r'EMPLID:"(.{8})"'
