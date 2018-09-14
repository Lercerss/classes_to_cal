import requests
import sys
import re
from parse import table_to_2d_list
from bs4 import BeautifulSoup, Tag
from login import authenticate
from const import DATA_URL, HOME_URL, FRAME_ID, ID_REGEX

session = requests.Session()


class Event:
    def __init__(self, cell_content, day_of_week):
        values = [elem for elem in cell_content if isinstance(elem, str)]
        self.title = ' '.join(values[0:2] + values[3:4])
        self.room = values[3]
        self.time_start = values[2].split(' - ')[0]
        self.time_end = values[2].split(' - ')[1]
        self.day_of_week = day_of_week

    def __str__(self):
        return f'{self.title} {self.time_start} - {self.time_end} {self.room} {self.day_of_week}'

    def __hash__(self):
        return hash(self.__str__())

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, self.__class__) and hash(self) == hash(other)

    def __ne__(self, other):
        return not self.__eq__(other)


def strip(string):
    return string.strip('\n').strip(' ')


def load_template(file_name):
    with open(file_name, 'r') as file:
        raw = file.readlines()
    lines = (line.split(':') for line in raw if not strip(line).startswith('//'))
    return {strip(item[0]): strip(item[1]) for item in lines}


def load_credentials(file_name):
    with open(file_name, 'r') as file:
        return [strip(l) for l in file.readlines()[:2]]


def gen_single_week_params(id_):
    return {"Page": "SSR_SS_WEEK", "Action": "A", "ExactKeys": "Y",
            "EMPLID": id_, "TargetFrameName": "None"}


def single_week_request(id_):
    params = gen_single_week_params(id_)
    response = session.get(DATA_URL, params=params)
    soup = BeautifulSoup(response.text, 'html.parser')
    frame = soup.find('iframe', id=FRAME_ID)
    if frame:
        resp = session.get(frame.get('src'))
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        schedule_table = soup.find('table', id='WEEKLY_SCHED_HTMLAREA')
        result = table_to_2d_list(schedule_table)
        return [row[1:] for row in result]  # Remove time column


def parse_classes_from_schedule(schedule):
    return set(Event(cell.contents, i) for row in schedule for i, cell in enumerate(row)
               if isinstance(cell, Tag))


def get_soup_for_url(url):
    resp = session.get(url)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, 'html.parser')


def parse_frame_url():
    soup = get_soup_for_url(HOME_URL)
    iframe = soup.find('iframe', id=FRAME_ID)
    return iframe.get('src') if iframe else ''


def parse_initial_frame():
    url = parse_frame_url()
    if not url:
        return -1

    resp = session.get(url)
    resp.raise_for_status()
    match = re.search(ID_REGEX, resp.text)
    return match.group(1) if match else -1


if __name__ == "__main__":
    file_name = sys.argv[1]
    with authenticate(session, *load_credentials(file_name)):
        student_id = parse_initial_frame()
        result = single_week_request(student_id)
        from pprint import pprint
        pprint(parse_classes_from_schedule(result))
