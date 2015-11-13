import os
import shutil
import unittest

import core


class TestMaterialListMethods(unittest.TestCase):
	def setUp(self):
		core.disconnect_db()		# ensure database objects aren't interfered with
		core.Job._dump_lock = True	# prevent object storage

		num = core.get_job_num()
		self.job = core.AwardedJob(num, 'test_job', init_struct=False)

		doc = core.os.path.join(self.job.sub_path, 'Materials')
		self._doc = (doc, 'doc.file')
		self.object = core.MaterialList(self.job, doc=self._doc)

		# Enter the Sandbox
		if os.path.isdir('tests'):
			_dir = 'tests/.job_sandbox'
			try:
				os.mkdir(_dir)  # create sandbox directory
			except OSError:
				pass
			os.chdir(_dir)  # enter sandbox directory
		else:
			raise OSError('Not started from program root')

	def tearDown(self):
		if os.path.isdir('../../tests'):  # checks if in project directory in tests/.job_sandbox
			_escape = '../..'  # escape tests/.job_sandbox
			_delete = 'tests/.bid_sandbox'
		else:
			_escape = '..'
			_delete = '.bid_sandbox'
		os.chdir(_escape)
		shutil.rmtree(_delete, ignore_errors=True)

	def test__init__(self):
		_test = [
			('quotes')
		]
		return NotImplemented


	def test__setattr__(self):
		""" Tests that update_po_in_log is correctly implemented """
		return NotImplemented

	def testDoc(self):
		## manually create dummy file in self.job project folder
		## verify returned path exists
		return NotImplemented

	def testAddQuote(self):
		## manually create quote
		## verify that quote was added to self.object.quotes
		## verify that quote was added to self.object.job.quotes
		## verify that self.object.sent_out is True
		return NotImplemented

	def testAddPO(self):
		## manually create po
		## verify that PO was added to self.object.po
		## verify that Job object has PO
		## verify that self.object.fulfilled is True
		return NotImplemented

	def testAddTask(self):
		## manually create task
		## verify that task was added to self.object
		return NotImplemented

	def testAddDelivery(self):
		## manually create Delivery
		## verify that delivery was added to self.object
		return NotImplemented

	def testAddRental(self):
		return NotImplemented

	def testDelQuote(self):
		## manually create Quote
		## verify that quote was deleted
		return NotImplemented

	def testDelTask(self):
		## manually create Task
		## verify that task was deleted
		return NotImplemented


class TestMaterialListQuoteMethods(unittest.TestCase):
	def setUp(self):
		## create _job
		## create _mat_list
		## self.object = core.MaterialListQuote
		return None

	def testSetAttr(self):
		# create faux po log
		# populate log
		# verify that __setattr__ updates po log
		return NotImplemented

	def testPath(self):
		## manually create dummy file in self.job project folder
		## verify returned path exists
		return NotImplemented


class TestPOMethods(unittest.TestCase):
	def setUp(self):
		## create _job
		## create _mat_list
		## create _quote
		## self.po = core.MaterialListQuote(update=False)
		return None


class TestDeliveryMethods(unittest.TestCase):
	def setUp(self):
		## create _job
		## create _mat_list
		## create _quote
		## create _po
		## self.delivery = core.Delivery
		return NotImplemented


suite = unittest.TestLoader().loadTestsFromTestCase(TestMaterialListMethods)
unittest.TextTestRunner(verbosity=2).run(suite)
suite = unittest.TestLoader().loadTestsFromTestCase(TestMaterialListQuoteMethods)
unittest.TextTestRunner(verbosity=2).run(suite)
suite = unittest.TestLoader().loadTestsFromTestCase(TestPOMethods)
unittest.TextTestRunner(verbosity=2).run(suite)
suite = unittest.TestLoader().loadTestsFromTestCase(TestDeliveryMethods)
unittest.TextTestRunner(verbosity=2).run(suite)
