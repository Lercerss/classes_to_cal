import requests
import sys
import re
import icalendar
from datetime import datetime, timedelta
from bs4 import BeautifulSoup, Tag
from parse import table_to_2d_list
from login import authenticate
from const import DATA_URL, HOME_URL, FRAME_ID, ID_REGEX

session = requests.Session()
now_ = datetime.now()


class Event:
    weekdays_ = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']

    def __init__(self, cell_content, day_of_week):
        values = [elem for elem in cell_content if isinstance(elem, str)]
        self.title = ' '.join(values[0:2] + values[3:4]).replace('  ', ' ')
        self.time_start = datetime.strptime(values[2].split(' - ')[0], '%I:%M%p').time()
        self.time_end = datetime.strptime(values[2].split(' - ')[1], '%I:%M%p').time()
        self.day_of_week = day_of_week

    def __str__(self):
        return f'{self.title} {self.time_start} - {self.time_end} {self.day_of_week}'

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, Event) and hash(self) == hash(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def is_same_class(self, other):
        """Two events are considered to be the same class if they are the same except for the day_of_week"""
        return isinstance(other, Event) \
               and self.title == other.title \
               and self.time_start == other.time_start \
               and self.time_end == other.time_end

    def to_ical_event(self, start_date):
        event = icalendar.Event()
        event.add('uid', f'{now_.strftime("%Y%m%dT%H%M%S")}{str(hash(self))[:17]}@schedule.concordia.ca')
        event.add('dtstamp', now_)
        event.add('summary', self.title)
        event.add('description', self.title)
        day_offset = timedelta(
            days=min(day for day in self.day_of_week + [min(self.day_of_week) + 7] if day >= start_date.weekday()))
        monday = start_date - timedelta(days=start_date.weekday())
        event.add('dtstart', datetime.combine(monday, self.time_start) + day_offset)
        event.add('dtend', datetime.combine(monday, self.time_end) + day_offset)
        rrule = icalendar.vRecur()
        rrule['freq'] = 'WEEKLY'
        rrule['byday'] = [Event.weekdays_[d] for d in self.day_of_week]
        rrule['count'] = 13 * len(self.day_of_week)
        event.add('rrule', rrule)

        return event


def strip(string):
    return string.strip('\n').strip(' ')


def load_credentials(file_name):
    with open(file_name, 'r') as file:
        return [strip(l) for l in file.readlines()[:2]]


def gen_single_week_params(id_):
    return {"Page": "SSR_SS_WEEK", "Action": "A", "ExactKeys": "Y",
            "EMPLID": id_, "TargetFrameName": "None"}


def single_week_request(id_):
    params = gen_single_week_params(id_)
    soup = get_soup_for_url(DATA_URL, params=params)
    frame = soup.find('iframe', id=FRAME_ID)
    if frame:
        soup = get_soup_for_url(frame.get('src'))
        schedule_table = soup.find('table', id='WEEKLY_SCHED_HTMLAREA')
        result = table_to_2d_list(schedule_table)
        return [row[1:] for row in result]  # Remove time column


def parse_classes_from_schedule(schedule):
    event_set = set(Event(cell.contents, i) for row in schedule for i, cell in enumerate(row)
                    if isinstance(cell, Tag))
    result = []
    for event in event_set:
        if [e for e in result if event.is_same_class(e)]:
            continue
        event.day_of_week = [e.day_of_week for e in event_set if e.is_same_class(event)]
        result.append(event)
    return result


def get_soup_for_url(url, params=None):
    resp = session.get(url, params=params)
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


def convert_to_icalendar(classes, start_date):
    calendar = icalendar.Calendar()
    calendar['version'] = '2.0'
    calendar['prodid'] = '-//Lercerss//classes_to_cal//'
    for class_ in classes:
        calendar.add_component(class_.to_ical_event(start_date))
    return calendar


def main():
    file_name = sys.argv[1]
    start_date = datetime.strptime(strip(input("When does the semester start? (YYYY-MM-DD) ")), '%Y-%m-%d').date()

    with authenticate(session, *load_credentials(file_name)):
        student_id = parse_initial_frame()
        result = single_week_request(student_id)

    classes = parse_classes_from_schedule(result)
    calendar = convert_to_icalendar(classes, start_date)

    with open('class_schedule.ics', 'wb') as file:
        file.write(calendar.to_ical())


if __name__ == "__main__":
    main()
