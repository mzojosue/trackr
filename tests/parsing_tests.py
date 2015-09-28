import unittest

import core
from core.parsing.po_log import *


class TestPOLogParsing(unittest.TestCase):
	def setUp(self):
		core.disconnect_db()
		self.log = core.openpyxl.Workbook()

		# Add 2 sheets to emulate 'stock' and 'small projects' pages (workbook already has active page)
		self.log.create_sheet()
		self.log.create_sheet()

		core.Job._dump_lock = True  # prevent object storage
		self.job = core.AwardedJob(core.get_job_num(), 'test_job', init_struct=False)
		_mat_list = core.MaterialList(self.job)
		_quote = core.MaterialListQuote(_mat_list, 'test vendor', price=500)
		self.po = core.PO(self.job, mat_list=_mat_list, quote=_quote, update=False)
		return None

	def testAddJob(self):
		""" Tests core.add_job_to_log by using Workbook.get_sheet_names() """
		add_job_to_log(self.job, po_log=self.log, save=False)

		_sheets = self.log.get_sheet_names()
		self.assertIn(self.job.sheet_name, _sheets)

	def testFindJob(self):
		""" Tests core.find_job_in_log by comparing Worksheet.title and AwardedJob.sheet_name """
		add_job_to_log(self.job, po_log=self.log, save=False)

		_sheet = find_job_in_log(self.job, self.log)[0]
		_sheet_name = _sheet.title

		self.assertEqual(_sheet_name, self.job.sheet_name, 'Function did not return correct object.')

	def testAddPO(self):
		""" Tests core.add_po_to_log by manually verifying POs """
		add_job_to_log(self.job, po_log=self.log, save=False)

		_sheet, _row = add_po_to_log(obj=self.po, po_log=self.log, save=False)
		_sheet = self.log.get_sheet_by_name(_sheet)

		_po_cell = 'A%d' % _row
		_po_cell = str(_sheet.cell(_po_cell).value)
		self.assertEqual(self.po.name, _po_cell, "Function did not return correct object")

	def testFindPO(self):
		""" Tests core.find_po_in_log by manually verifying POs """
		add_job_to_log(self.job, po_log=self.log, save=False)

		_sheet, _row = add_po_to_log(obj=self.po, po_log=self.log, save=False)
		_sheet = self.log.get_sheet_by_name(_sheet)

		_po_cell = 'A%d' % _row
		_po_cell = str(_sheet.cell(_po_cell).value)
		self.assertEqual(self.po.name, _po_cell, "Function did not return correct object")

	def testUpdatePO(self):
		add_job_to_log(self.job, po_log=self.log, save=False)
		add_po_to_log(obj=self.po, po_log=self.log, save=False)

		update_po_in_log(self.po, 'price', 999, self.log, save=False)
		val = get_po_attr(self.po, 'price', self.log)
		val = float(val)
		self.assertEqual(999, val, 'Function did not update correct cell')

	def testImportPOLog(self):
		return None

# TODO: class TestJobInfoParsing

# TODO: class TestEstimatingLogParsing

suite = unittest.TestLoader().loadTestsFromTestCase(TestPOLogParsing)
unittest.TextTestRunner(verbosity=2).run(suite)