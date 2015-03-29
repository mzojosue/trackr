from xlrd import open_workbook, xldate_as_tuple
from xlwt import *
from xlutils.copy import copy
from datetime import datetime, date
from parse import parse
import environment
import objects

def import_po_log(create=False, poLog=environment.get_po_log):
	log = open_workbook(poLog, on_demand=True)
	_nsheet = log.nsheets
	for _sheetNum in range(1, _nsheet):  # Omit first template page
		_sheet = log.sheet_by_index(_sheetNum)
		if create:
			try:
				_job = objects.AwardedJob(*[i for i in parse("{} - {}", _sheet.name)], sheet_num=_sheetNum)
			except TypeError:
				pass    # Sheet name does not match regex
		for _row in range(2, _sheet.nrows):
			_row = _sheet.row_slice(_row)
			__po = _row[0].value
			if not __po:
				# skips empty row by assuming that a row without a PO# is a row without content
				continue
			__vend = _row[1].value
			__price = _row[2].value

			if _row[3].value:
				try:
					__date_issued = date(*xldate_as_tuple(_row[3].value, log.datemode)[:3])
				except ValueError:
					try:
						__date_issued = datetime.strptime(_row[3].value, '%m.%d.%Y').date()
					except ValueError:
						__date_issued = datetime.strptime(_row[3].value, '%m.%d.%y').date()
					except TypeError:
						__d = [int(i) for i in parse("{}.{}.{}", _row[3].value)]
						__date_issued = date(__d[2], __d[0], __d[1])
						del __d
			else:
				__date_issued = None

			# SKIP _row[4] -> "date expected"
			__mat_list_val = _row[5].value
			__quote_val = _row[6].value

			try:
				__comment = _row[7].value
			except IndexError:
				__comment = ""

			# Create MaterialList objects
			if create:
				if '\\' in __mat_list_val:
					__mat_list_val = str(__mat_list_val).replace('\\', '/')
					_mat_list = objects.MaterialList(job=_job, doc=objects.os.path.split(__mat_list_val), date_sent=__date_issued, task=False)
				else:
					_mat_list = objects.MaterialList(job=_job, items=__mat_list_val, date_sent=__date_issued, task=False)
				_mat_list.sent_out = True
				if _mat_list.age > 5:
					_mat_list.delivered = True

				# Create Quote objects
				if '\\' in __quote_val:
					_quote = objects.MaterialListQuote(mat_list=_mat_list, price=__price, vend=__vend, doc=objects.os.path.split(__quote_val))
				else:
					_quote = objects.MaterialListQuote(mat_list=_mat_list, price=__price, vend=__vend)

				# Create PO objects
				_pre = parse("{pre}-{:d}", __po)['pre']
				_num = parse("{}-{num:d}", __po)['num']
				if str(_pre) is not str(_job.po_pre):
					po_pre = _pre
				else: po_pre = None
				_po = objects.PO(_job, _mat_list, __date_issued, _quote, desc=__comment, po_num=_num, po_pre=po_pre, update=False)

				del _mat_list, _quote, _po

			else:
				print str(__mat_list_val).replace('\\', '/')
			# Delete all variables between each iteration
			del __po, __vend, __price, __date_issued, __mat_list_val, __quote_val, __comment


def parse_job_info(jobInfo):
	return NotImplemented


def parse_estimating_log(estimatingLog):
	return NotImplemented


def find_job_in_log(obj, poLog=environment.get_po_log):
	"""
	Finds and returns the given sheet number for the passed job object in the given po log
	:param obj: job object to find in log
	:param poLog: path to PO log to parse
	:return: integer which has the po log for given job
	"""
	return NotImplemented

def add_job_in_log(obj, poLog=environment.get_po_log):
	"""
	Adds a spreadsheet page to the passed log file to log POs for the given job
	:param obj: job object to add to log
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
	return NotImplemented

def add_po_in_log(obj, poLog=environment.get_po_log):
	try:
		log = open_workbook(poLog, on_demand=True)
	except IOError:
		print "'%s' is not a valid file path. Cannot update PO log." % poLog
		return False

	_sheet, _nrow = None, None
	if hasattr(obj, 'job'):
		_sheet = log.sheet_by_index(obj.job.sheet_num)
		# TODO: implement algorithm to apply styling and organization to PO log
		_nrow = _sheet.nrows
	log = copy(log)    # creates writable Workbook object

	# iterate through all rows and cache all POs on worksheet to validate obj against
	_pos = []
	for i in range(2, _nrow):
		_row = _sheet.row_slice(i)
		_po  = _row[0].value
		_pos.append(_po)

	if hasattr(obj.job, 'sheet_num') and (obj.num not in _pos):
		print obj
		_sheet = log.get_sheet(obj.job.sheet_num)   # creates writeable Worksheet object
		_date_issued = obj.date_issued.strftime("%m.%d.%y")
		_row = (obj.name, obj.vend, obj.price, _date_issued, None, obj.mat_list.doc, obj.quote.doc, None, None)
		_row = zip(range(len(_row)), _row)
		for col, val in _row:
			try:
				_sheet.write(_nrow, col, str(val))
			except Exception as e:
				raise Exception("Unexpected value given when writing %s to (%d,%d): %s" % (str(val), _nrow, col, e.args[0]))
		log.save(poLog)
	elif obj.po_num in _pos:
		# TODO: show an error to the user if po_num was user supplied. else, show an error in the log
		pass
	else:
		_sheet = log.sheet_by_name( '%d - %s' % (obj.number, obj.name) )

def update_po_in_log(poLog, obj, attr, value):
	"""
	:param poLog: poLog file object to write to
	:param obj: object to reflect changes on
	:param attr: object attribute that has been changed
	:param value: object attribute new value
	:return: True if operation successful
	"""
	_attr = ('number', 'vend', 'price', 'date_uploaded', 'date_sent', 'mat_list', 'quote')
	if attr in _attr:
		log = open_workbook(poLog)
		_sheet, _nrow = None

		if hasattr(obj, 'sheet_num'):
			_sheet = log.sheet_by_index(obj.sheet_num)
