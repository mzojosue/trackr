from objects import *

import traceback
from datetime import timedelta


class Timesheet(object):
	def __init__(self, job, end_date=None, doc=None):
		self.hash = abs(hash(''.join([str(job.number), str(end_date)])))
		self.job = job
		self.start_date = end_date - timedelta(7)   # starting date should be a week before ending date
		self.end_date = end_date
		self.doc = doc

		# self.timesheet.key is worker.hash
		# self.timesheet.value is list of tuples containing dates worked as datetime and hours as float
		self.timesheet = {}

	@property
	def hours(self):
		"""
		:return: total amount of hours as float
		"""
		# TODO: calculate Saturday hours and overtime
		_hrs = 0.0
		for _work in self.timesheet.itervalues():
			_hrs += float(_work[1])
		return _hrs

	def __setattr__(self, key, value):
		_return = super(Timesheet, self).__setattr__(key, value)
		_caller = traceback.extract_stack(None, 2)[0][2]
		if _caller is not '__init__':
			self.update()
		return _return

	def __repr__(self):
		if not self.end_date:
			return "%d hours worked at %s. Dates unknown." % (self.hours, self.job)
		else:
			return "%d hours worked at %s for week ending %s" % (self.hours, self.job, self.end_date.date())

	def add_labor(self, worker, date_worked, hours):
		if hasattr(worker, 'hash'):
			if not hasattr(date_worked, 'date'):
				date_worked = datetime(*date_worked)

			if worker.hash in self.timesheet:
				self.timesheet[worker.hash].append((date_worked, float(hours)))
			else:
				self.timesheet[worker.hash] = [(date_worked, float(hours))]

			if self.hash not in worker.timesheets:
				worker.timesheets.append(self.hash)
				worker.update()
			self.update()

	def update(self):
		if hasattr(Timesheet, 'db'):
			Timesheet.db[self.hash] = self
		self.job.timesheets[self.hash] = self
		self.job.update()

	def bodies_on_field(self):
		return len(self.timesheet)