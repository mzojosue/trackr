from objects import *

class Timesheet(object):
	def __init__(self, job, start_date=None, end_date=None, doc=None, timesheet=dict()):
		self.hash = abs(hash(''.join([str(job.number), str(start_date), str(end_date)])))
		self.job = job
		self.start_date = start_date
		self.end_date = end_date
		self.doc = doc

		# self.timesheet.key is worker.hash
		# self.timesheet.value is list of dates worked and hours
		self.timesheet = timesheet

	@property
	def hours(self):
		"""
		:return: total amount of hours as float
		"""
		_hrs = 0.0
		for _work in self.timesheet.itervalues():
			_hrs += float(_work[1])
		return _hrs

	def __setattr__(self, key, value):
		_return = super(Timesheet, self).__setattr__(key, value)
		self.update()
		return _return

	def __repr__(self):
		if not self.end_date:
			return "%d hours worked at %s. Dates unknown." % (self.hours, self.job)
		else:
			return "%d hours worked at %s for week ending %s" % (self.hours, self.job, self.end_date)

	def add_labor(self, worker, date_worked, hours):
		if hasattr(worker, 'hash'):
			if worker.hash in self.timesheet:
				self.timesheet[worker.hash].append([date_worked, float(hours)])
			else:
				self.timesheet[worker.hash] = [date_worked, float(hours)]
			if not self.hash in worker.timesheets:
				worker.timesheets.append(self.hash)
				worker.update()

	def update(self):
		if hasattr(Timesheet, 'db'):
			Timesheet.db[self.hash] = self
		if hasattr(self, 'jobs'):
			self.job.timesheets[self.hash] = self
			self.job.update()

	def bodies_on_field(self):
		return len(self.timesheet)