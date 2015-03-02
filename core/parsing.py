from xlrd import open_workbook, xldate_as_tuple
from datetime import datetime, date
from parse import parse
import objects

def parse_PO_log(poLog, sheet=None, create=False):
	log = open_workbook(poLog)
	_nsheet = log.nsheets
	for _sheetNum in range(1, _nsheet):  # Omit first template page
		_sheet = log.sheet_by_index(_sheetNum)
		if create:
			try:
				_job = objects.Job(*[i for i in parse("{} - {}", _sheet.name)])
				print _job.name
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
					_mat_list = objects.MaterialList(job=_job, doc=objects.os.path.split(__mat_list_val), date_sent=__date_issued)
				else:
					_mat_list = objects.MaterialList(job=_job, items=__mat_list_val, date_sent=__date_issued)
				_mat_list.sent_out = True
				if _mat_list.age > 5:
					_mat_list.delivered = True
				print _mat_list

				# Create Quote objects
				if '\\' in __quote_val:
					_quote = objects.Quotes(mat_list=_mat_list, price=__price, vend=__vend, doc=objects.os.path.split(__quote_val))
				else:
					_quote = objects.Quotes(mat_list=_mat_list, price=__price, vend=__vend)

				# Create PO objects
				_pre = parse("{pre}-{:d}", __po)['pre']
				_num = parse("{}-{num:d}", __po)['num']
				if str(_pre) is not str(_job.po_pre):
					po_pre = _pre
				else: po_pre = None
				_po = objects.PO(_job, _mat_list, __date_issued, _quote, desc=__comment, po_num=_num, po_pre=po_pre)

				del _mat_list, _quote, _po

			else:
				print str(__mat_list_val).replace('\\', '/')
			# Delete all variables between each iteration
			del __po, __vend, __price, __date_issued, __mat_list_val, __quote_val, __comment


def parse_job_info(jobInfo):
	return NotImplemented


def parse_estimating_log(estimatingLog):
	return NotImplemented