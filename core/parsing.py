from xlrd import open_workbook, xldate_as_tuple
from xlwt import *
from xlutils.copy import copy
from parse import parse
import openpyxl

from datetime import datetime, date, timedelta
import unicodedata
import os

import objects
import environment
from log import logger
from core.scheduler import scheduler


def ensure_write(f, *args, **kwargs):
	def schedule_job():
		# five_min = 60 * 5
		five_min = 30
		td = timedelta(0, five_min)
		sched = datetime.now() + td
		scheduler.add_job(f, 'date', run_date=sched, args=args, kwargs=kwargs)
		print "Scheduling '%s' for %s" % (f.__name__, sched)
		logger.warning('Operation (\'%s\') failed. Scheduling for %s' % (f.__name__, sched))
		return False
	def try_write(*args, **kwargs):
		try:
			return f(*args, **kwargs)
		except OSError:
			return schedule_job()
	return try_write


def import_po_log(create=False, poLog=environment.get_po_log):
	# TODO: add logger debugging hooks
	log = openpyxl.load_workbook(poLog, read_only=True, guess_types=True)
	_nsheet = len(log.get_sheet_names()) - 2
	for _sheetNum in range(1, _nsheet):
		_sheet = log.get_sheet_by_name(log.get_sheet_names()[_sheetNum])
		logger.debug('Working on worksheet "%s"' % _sheet.title)
		if create:
			try:
				_job = objects.AwardedJob(*[i for i in parse("{} - {}", _sheet.title)])
			except TypeError:
				pass                # sheet does not match regex
		for _row in _sheet.rows:
			__po = _row[0].value
			logger.debug('Processing row "%s"' % __po)
			try:
				__po = [i for i in parse("{:d}-{}-{:d}", __po)]
			except TypeError:
				logger.debug('...skipped row')
				continue
			if len(__po) is not 3:
				logger.debug('...skipped row')
				# skips empty row by assuming that a row
				continue
			# TODO: parse vendor cell and create vendor object
			__vend = _row[1].value
			__price = _row[2].value
			if _row[3].value:
				if type(_row[3].value) is unicode:
					_date_formats = ['%m.%d.%y', '%m.%d.%Y', '%m/%d/%y', '%m/%d/%Y']
					for _format in _date_formats:
						try:
							__date_issued = datetime.strptime(_row[3].value, _format)
							break
						except ValueError:
							continue
				else:
					__date_issued = _row[3].value
			try:
				__date_issued
			except NameError:
				__date_issued = None

			# SKIP _row[4] -> "date expected"
			try:
				__mat_list_val  = unicodedata.normalize('NFKD', _row[5].value).encode('ascii','ignore')
			except TypeError:
				__mat_list_val = ''
			try:
				__quote_val     = unicodedata.normalize('NFKD', _row[6].value).encode('ascii','ignore')
			except TypeError:
				__quote_val = ''

			try:
				__comment = _row[7].value
			except IndexError:
				__comment = ""

			if create:
				# Create MaterialList objects
				if '\\' in __mat_list_val:
					__mat_list_val = str(__mat_list_val).replace('\\', '/')
					_mat_list = objects.MaterialList(job=_job, doc=objects.os.path.split(__mat_list_val), date_sent=__date_issued, task=False)

				else:
					_mat_list = objects.MaterialList(job=_job, items=__mat_list_val, date_sent=__date_issued, task=False)
				_mat_list.sent_out = True
				if _mat_list.age > 5:
					_mat_list.delivered = True

				# Create MaterialListQuote objects
				if '\\' in __quote_val:
					_quote = objects.MaterialListQuote(mat_list=_mat_list, price=__price, vend=__vend, date_uploaded=__date_issued, doc=objects.os.path.split(__quote_val))
				else:
					_quote = objects.MaterialListQuote(mat_list=_mat_list, price=__price, vend=__vend, date_uploaded=__date_issued)

				# Create PO objects
				_po_pre  = '-'.join([str(i) for i in __po[:2]])
				_po_num  = __po[2]
				if str(_po_pre) is not str(_job.po_pre):
					_pre = _po_pre
				else:
					_pre = None
				_po = objects.PO(_job, _mat_list, __date_issued, _quote, desc=__comment, po_num=_po_num, po_pre=_pre, update=False)
			del __po, __vend, __price, __date_issued, __mat_list_val, __quote_val, __comment


def parse_job_info(jobInfo):
	return NotImplemented


def parse_estimating_log(estimatingLog):
	return NotImplemented


def find_job_in_log(obj, poLog=environment.get_po_log):
	"""
	Finds and returns the given sheet number for the passed jobs object in the given po log
	:param obj: jobs object to find in log
	:param poLog: path to PO log to parse
	:return: integer which has the po log for given jobs
	"""
	return NotImplemented


def add_job_in_log(obj, poLog=environment.get_po_log):
	"""
	Adds a spreadsheet page to the passed log file to log POs for the given jobs
	:param obj: jobs object to add to log
	:param poLog: path to PO log to to add spreadsheet page to
	:return: returns output of find_job_in_log to confirm output
	"""
	return NotImplemented


def find_po_in_log(obj, poLog=environment.get_po_log):
	"""
	Finds and returns spreadsheet page, and row number which corresponds to the given PO object passed
	:param obj: PO object to find in spreadsheet
	:param poLog: path to PO log to parse
	:return: returns tuple containing spreadsheet page integer and row number integer
	"""
	# values to be returned
	_po_row = None

	if hasattr(poLog, 'sheet_by_name'):
		# checks to see if Book object was passed
		log = poLog
	else:
		log = open_workbook(poLog, on_demand=True)


	if hasattr(obj, 'job'):
		_sheet_name = '%d - %s' % (obj.job.number, obj.job._name)
		_sheet = log.sheet_by_name(_sheet_name)
		_nrows = _sheet.nrows

		for i in range(2, _nrows):
			_row = _sheet.row_slice(i)
			try:
				if str(_row[0].value) == str(obj.name):
					_po_row = i
			except AttributeError:
				# this is run if a quote object is passed
				if str(_row[0].value) == str(obj.mat_list.po):
					_po_row = i
		return (_sheet, _po_row)


@ensure_write
def add_po_in_log(obj, poLog=environment.get_po_log):
	try:
		_poLog = os.path.split(poLog)
		_poLog = os.path.join(_poLog[0], '_%s' % _poLog[1])
		os.rename(poLog, _poLog)
		log = openpyxl.load_workbook(_poLog, guess_types=True)
	except IOError:
		print "'%s' is not a valid file path. Cannot update PO log." % poLog
		return False

	_sheet_name = '%d - %s' % (obj.job.number, obj.job._name)
	_sheet = log.get_sheet_by_name(_sheet_name)
	# TODO: implement algorithm to apply styling and organization to PO log
	_nrow = len(_sheet.rows) + 1

	# iterate through all rows and cache all POs on worksheet to validate obj against
	_pos = []
	for _row in _sheet.rows:
		_po = _row[0].value
		_pos.append(_po)

	if obj.__repr__() not in _pos:
		_date_issued = obj.date_issued.strftime("%m.%d.%y")
		try:
			_mdoc = objects.os.path.join(*obj.mat_list.doc)
		except TypeError:
			_mdoc = ''
		try:
			_qdoc = objects.os.path.join(*obj.quote.doc)
		except TypeError:
			_qdoc = ''
		_row = (obj.name, obj.vend, obj.price, _date_issued, None, _mdoc, _qdoc, None, None)
		_row = zip(range(1, len(_row) + 1), _row)
		for col, val in _row:
			try:
				_sheet.cell(row=_nrow, column=col, value=str(val))
			except Exception as e:
				raise Exception("Unexpected value given when writing %s to (%d,%d): %s" % (str(val), _nrow, col, e.args[0]))
		log.save(poLog)
	elif obj.po_num in _pos:
		# TODO: show an error to the user if po_num was user supplied. else, show an error in the log
		pass
	print "Successfully added %s to PO log" % obj


@ensure_write
def update_po_in_log(obj=None, attr=None, value=None, poLog=environment.get_po_log):
	"""
	:param poLog: poLog file object to write to
	:param obj: object to reflect changes on
	:param attr: object attribute that has been changed
	:param value: object attribute new value
	:return: True if operation successful
	"""
	_attr = ('number', 'vend', 'price', 'date_sent', 'date_expected', 'mat_list', 'quote', 'ordered_by', 'quote_id')
	if attr in _attr:
		try:
			_poLog = os.path.split(poLog)
			_poLog = os.path.join(_poLog[0], '_%s' % _poLog[1])
			os.rename(poLog, _poLog)
			log = open_workbook(_poLog, on_demand=True, formatting_info=True)
		except OSError:
			print "'%s' is not a valid file path. Cannot update PO log." % poLog
			raise OSError

		# pass opened PO Log object to function
		_sheet, _row = find_po_in_log(obj, log)

		# column to edit
		_col = _attr.index(attr)

		# create writable Workbook/Worksheet objects
		log = copy(log)
		_sheet = log.get_sheet(_sheet.number)

		# update information
		_sheet.write(_row, _col, value)

		log.save(poLog)

		return True

