pdf_url = "https://frisange.lu/wp-content/uploads/2022/05/Sidor_calendrier-ecologique_juillet-decembre-2022.pdf"

import re
import pytz
import uuid
import argparse
import logging
import urllib.request
from tika import parser
from icalendar import Calendar, Event
from datetime import datetime, timedelta

FORMAT = '%(levelname)s | %(message)s'
logging.basicConfig(format=FORMAT)

logger = logging.getLogger('tika.tika')
logger.setLevel(logging.ERROR)

def get_args():
	parser = argparse.ArgumentParser(description='Create collection calendar for the commune of Frisange. By default the events are created for the day before collection. Use --same-day option to override this behaviour.')
	parser.add_argument('--out', dest='output_filename', default='garbage_collection.ics', help='Output filename.')
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('--pdf', dest='pdf_calendar', default=None, help='Path to calendar in PDF.')
	group.add_argument('--url', dest='url_calendar', default=None, help='URL to calendar in PDF.')
	parser.add_argument('--event-start-hour', type=int, choices=range(0,24), help='Start hour for events.', metavar="[0-23]", default=20)
	parser.add_argument('--event-start-minute', type=int, choices=range(0,60), help='Start minute for events.', metavar="[0-59]", default=0)
	parser.add_argument('--event-duration', type=int, choices=range(10,61), help='Event duration.', metavar="[10-60]", default=15)
	parser.add_argument('--same-day', dest='same_day', action='store_true', help='By default the events are created for the day before collection. If this option is used, the events will be created for collection day.', default=False)
	parser.add_argument('-d','--debug', action='store_true', help='Debug True/False', default=False)

	args = parser.parse_args()
	if args.debug:
		logging.getLogger().setLevel(logging.DEBUG)
	else:
		logging.getLogger().setLevel(logging.INFO)

	if not args.same_day:
		logging.info(f'Events have been created for the day before collection. Use --same-day option to override this behaviour.')
	else:
		logging.info(f'Events have been created for collection day.')

	return args

class CalendarCreator:
	months = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
			  'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
	TZ = pytz.timezone('Europe/Luxembourg')

	def __init__(self, args):
		self.args = args
		self.content = None
		self.year = None
		self.month_positions = None
		self.available_months = None
		self.events = None
		self.extract_events()
		self.create_calendar()

	def _extract_content_from_pdf(self):
		if self.args.pdf_calendar is None:
			response = urllib.request.urlopen(self.args.url_calendar)
			raw = parser.from_buffer(response.read())
		else:
			raw = parser.from_file(args.pdf_calendar)
		self.content = raw['content']

	def _extract_year_from_header(self):
		self.year = int(re.search(r'CALENDRIER ÉCOLOGIQUE (\d{4})', self.content).group(1))

	def _extract_available_month_positions(self):
		self.month_positions = {}
		#get positions of available months
		for month in self.months:
			pos = self.content.find(month + '/')
			if pos > 0:
				self.month_positions[month] = pos

		self.available_months = list(self.month_positions.keys())

	def extract_events(self):
		self._extract_content_from_pdf()
		self._extract_year_from_header()
		self._extract_available_month_positions()
		self.events = {}
		for idx, month in enumerate(self.available_months):
			m_0 = self.available_months[idx]
			start = self.month_positions[m_0]
			if idx < (len(self.available_months)-1) :
				m_1 = self.available_months[idx+1]
				end = self.month_positions[m_1]
			else:
				end = -1
			lines = self.content[start:end].split('\n')
			
			month_number = self.months.index(month) + 1
			for line in lines:
				res = re.search(r'^(\d{1,2})\s\w{3}/\w{2}\s(.*$)', line)
				if res is not None:
					day, details = res.group(1), res.group(2)
					date = (int(day), month_number, self.year)
					self.events[date] = details
					logging.debug(f'Extracted event: {int(day):02d}/{month_number:02d}/{self.year} | {details}')
		logging.info(f'{len(self.events.values())} events found.')

	def export_calendar(self):
		if not self.args.output_filename.lower().endswith('.ics'):
			logging.info('Added .ics extension to output filename.')
			f = open(self.args.output_filename + '.ics', 'wb')
		else:
			f = open(self.args.output_filename, 'wb')
		f.write(self.cal.to_ical())
		f.close()
		logging.info(f'ICS File saved in: {self.args.output_filename}')

	def _create_event(self, date, details):
		e = Event()
		day, month, year = date
		start_date = datetime(year, month, day, self.args.event_start_hour, self.args.event_start_minute, 0, tzinfo=self.TZ)
		if not self.args.same_day:
			start_date = start_date - timedelta(days=1)
		end_date = start_date + timedelta(minutes=self.args.event_duration)
		e.add('summary', f'🚮 {details}')
		e.add('dtstart', start_date)
		e.add('dtend', end_date)
		e.add('description', f'Collecte des déchets ({details}): Matin {int(day):02d}/{month:02d}/{year}')
		e['location'] = 'Frisange (Luxembourg)'
		e['uid'] = str(uuid.uuid4())
		return e

	def create_calendar(self):
		# init the calendar
		self.cal = Calendar()
		# Properties to comply with RFC
		self.cal.add('prodid', '-//Calendrier Écologique Frisange//')
		self.cal.add('version', '1.0')

		for date, details in self.events.items():
			e = self._create_event(date, details)
			self.cal.add_component(e) # Add the event to the calendar

if __name__ == '__main__':
	args = get_args()
	cc = CalendarCreator(args)
	cc.export_calendar()
	