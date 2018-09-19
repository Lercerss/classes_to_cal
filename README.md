# Classes to Cal
Retrieves class schedule found on MyConcordia to export it to iCal format.

## Dependencies
This scraper requires Python 3.
To install requirements for this project: `pip3 install -r requirements.txt`

## Usage
Create file containing user credentials in the following format to authenticate the user:
```
username
password
```
Run using command: `python3 main.py <path-to-credentials-file>`

Your class schedule will be found at `./class_schedule.ics`

## Limitations
- Only supports scraping the current term's schedule
- Assumes all classes are weekly occurences, i.e. does not support classes that happen once every 2 weeks
- Requires the user to input the start date of the semester, assumes semester lasts 13 weeks
