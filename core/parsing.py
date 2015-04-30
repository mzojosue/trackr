from parse import parse
from xlrd import xldate_as_tuple
import openpyxl

from datetime import datetime, timedelta
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


def import_po_log(create=False, po_log=environment.get_po_log):
	# TODO: add logger debugging hooks
	log = openpyxl.load_workbook(po_log, read_only=True)
	_nsheet = len(log.get_sheet_names()) - 2
	for _sheetNum in range(1, _nsheet):
		_sheet = log.get_sheet_by_name(log.get_sheet_names()[_sheetNum])
		logger.debug('Working on worksheet "%s"' % _sheet.title)
		if create:
			try:
				_job = objects.AwardedJob(*[i for i in parse("{} - {}", _sheet.title)])
			except TypeError:
				continue                # skip sheet sheet does not match regex
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
			if type(_row[3].value) is datetime:
				__date_issued = _row[3].value
			else:
				try:
					__date_issued = datetime(*xldate_as_tuple(_row[3].value, 0))
				except ValueError:
					_date_formats = ['%m.%d.%y', '%m.%d.%Y', '%m/%d/%y', '%m/%d/%Y']
					for _format in _date_formats:
						try:
							__date_issued = datetime.strptime(_row[3].value, _format)
							break
						except ValueError:
							continue
						except TypeError:
							break
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


def find_job_in_log(obj, po_log=environment.get_po_log):
	"""
	Finds and returns the sheet title for the passed job object in the given po log
	:param obj: jobs object to find in log
	:param po_log: path to PO log to parse
	:return: integer which has the po log for given jobs
	"""
	if hasattr(po_log, 'get_sheet_by_name'):
		# checks to see if Book object was passed
		log = po_log
	else:
		log = openpyxl.load_workbook(po_log, read_only=True)

	if type(obj) is int:
		obj = objects.AwardedJob.find(obj)

	_sheet_name = '%d - %s' % (obj.number, obj._name)
	try:
		_sheet = log.get_sheet_by_name(_sheet_name)
		return _sheet, log
	except KeyError:
		return False


@ensure_write
def add_job_in_log(obj, po_log=environment.get_po_log, save=True):
	"""
	Adds a spreadsheet page to the passed log file to log POs for the given jobs
	:param obj: job object or int to add to log. Function assumes that the AwardedJob is new to the company
	:param po_log: path to PO log to to add spreadsheet page to
	:return: returns output of find_job_in_log to confirm output
	"""
	if hasattr(po_log, 'get_sheet_by_name'):
		# checks to see if Book object was passed
		log = po_log
	else:
		log = openpyxl.load_workbook(po_log)
	if type(obj) is int:
		obj = objects.AwardedJob.find(obj)
	_sheet_name = obj.sheet_name

	try:
		# returns False if sheet already exists
		log.get_sheet_by_name(_sheet_name)
		return False
	except KeyError:
		_sheet = log.create_sheet(-2, _sheet_name)
		# TODO: add header rows to _sheet
		if save:
			log.save(po_log)
		return find_job_in_log(obj, log)


def dump_pos_from_log(job, po_log=environment.get_po_log):
	if type(job) is int:
		# TODO: implement dumping POs from CompletedJob object instead of just AwardedJob
		# convert string object to job object
		job = objects.AwardedJob.find(job)

	_sheet, log = find_job_in_log(job, po_log=po_log)

	# calculate dimensions to iterate over
	_min_col = 'A'
	_min_row = 3     # do not iterate over header rows
	_max_col = 'I'
	_max_row = _sheet.max_row + 1
	_iter_dim = '%s%s:%s%s' % (_min_col, _min_row, _max_col, _max_row)

	_rows = []
	for _row in _sheet.iter_rows(_iter_dim):
		_rows.append(_row)
	_row_count = len(_rows)
	for _num, _row in zip(range(1, _row_count + 1), _rows):
		_num += 2    # offset for header rows
		yield (_num), _row


def find_po_in_log(obj, po_log=environment.get_po_log):
	"""
	Finds and returns spreadsheet page, and row number which corresponds to the given PO object passed
	:param obj: PO object to find in spreadsheet
	:param po_log: path to PO log to parse
	:return: returns tuple containing spreadsheet page integer and row number integer
	"""
	if hasattr(obj, 'job'):
		_job = obj.job

		_sheet, po_log = find_job_in_log(_job, po_log)
		_po_dump = dump_pos_from_log(_job, po_log)
		for _num, _row in _po_dump:
			if str(_row[0].value) == str(obj.name):
				_po_row = _num
				return _sheet.title, _po_row


@ensure_write
def add_po_in_log(obj, po_log=environment.get_po_log, save=True):
	if hasattr(po_log, 'get_sheet_by_name'):
		log = po_log
	else:
		try:
			_po_log = os.path.split(po_log)
			_po_log = os.path.join(_po_log[0], '_%s' % _po_log[1])
			os.rename(po_log, _po_log)
			log = openpyxl.load_workbook(_po_log, guess_types=True)
		except IOError:
			print "'%s' is not a valid file path. Cannot update PO log." % po_log
			return False

	_sheet_name = obj.job.sheet_name
	_sheet = log.get_sheet_by_name(_sheet_name)
	# TODO: implement algorithm to apply styling and organization to PO log
	_nrow = len(_sheet.rows) + 1
	if _nrow < 3:
		_nrow = 3

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
		if save:
			log.save(po_log)
			logger.info("Successfully saved %s to PO log" % obj)
			print "Successfully saved %s to PO log" % obj
	return find_po_in_log(obj, po_log)


@ensure_write
def update_po_in_log(obj=None, attr=None, value=None, po_log=environment.get_po_log, save=True):
	"""
	:param po_log: po_log file object to write to
	:param obj: object to reflect changes on
	:param attr: object attribute that has been changed
	:param value: object attribute new value
	:return: True if operation successful
	"""
	_attr = ('number', 'vend', 'price', 'date_sent', 'date_expected', 'mat_list', 'quote', 'ordered_by', 'quote_id')
	if attr in _attr:
		if hasattr(po_log, 'get_sheet_by_name'):
			log = po_log
		else:
			try:
				_po_log = os.path.split(po_log)
				_po_log = os.path.join(_po_log[0], '_%s' % _po_log[1])
				os.rename(po_log, _po_log)
				log = openpyxl.load_workbook(_po_log, guess_types=True)
			except IOError:
				print "'%s' is not a valid file path. Cannot update PO log." % po_log
				return False

		# pass opened PO Log object to function
		_sheet_name, _row = find_po_in_log(obj, log)
		_sheet = log.get_sheet_by_name(_sheet_name)

		# column to edit
		_col = _attr.index(attr) + 1

		# update information
		_sheet.cell(row=_row, column=_col).value = value

		# TODO: confirm update

		if save:
			log.save(po_log)

		return True

def get_po_attr(obj, attr, po_log=environment.get_po_log):
	# TODO: optimize this bs initialization
	_attr = {'number': 'A', 'vend': 'B', 'price': 'C', 'date_sent': 'D', 'date_expected': 'E',
	         'mat_list': 'F', 'quote': 'J', 'ordered_by': 'K', 'quote_id': 'L'}
	if attr in _attr:
		if hasattr(po_log, 'get_sheet_by_name'):
			log = po_log
		else:
			log = openpyxl.load_workbook(po_log, guess_types=True)

		_sheet, _row = find_po_in_log(obj, po_log)
		_sheet = log.get_sheet_by_name(_sheet)

		cell = '%s%d' % (_attr[attr], _row)
		val = _sheet[cell].value

		return val