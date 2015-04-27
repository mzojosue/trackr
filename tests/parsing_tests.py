import unittest

import core


class TestPOLogParsing(unittest.TestCase):
	def setUp(self):
		core.disconnect_db()
		self.log = core.openpyxl.Workbook()

		# Add 2 sheets to emulate 'stock' and 'small projects' pages (workbook already has active page)
		self.log.create_sheet()
		self.log.create_sheet()

		self.job = core.AwardedJob(core.get_job_num(), 'test_job')

	def testAddJob(self):

		core.add_job_in_log(self.job, po_log=self.log, save=False)

		# TODO: test that job was created

		return None

	def testFindJob(self):

		_sheet = core.find_job_in_log(self.job, po_log=self.log)[0]
		_sheet_name = _sheet.title.replace(' ', '')
		self.assertEqual(_sheet_name, self.job.name, '')
		return None

	def testAddPO(self):
		return None

	def testFindPO(self):
		return None

	def testUpdatePO(self):
		return None

	def testImportPOLog(self):
		return None

# TODO: class TestJobInfoParsing

# TODO: class TestEstimatingLogParsing

suite = unittest.TestLoader().loadTestsFromTestCase(TestPOLogParsing)
unittest.TextTestRunner(verbosity=2).run(suite)