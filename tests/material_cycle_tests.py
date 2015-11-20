import os
import shutil
import unittest
from parse import parse

import core


class TestMaterialListMethods(unittest.TestCase):
	def setUp(self):
		core.disconnect_db()		# ensure database objects aren't interfered with
		core.Job._dump_lock = True	# prevent object storage

		num = core.get_job_num()
		self.job = core.AwardedJob(num, 'test_job', init_struct=False)

		self.object = core.MaterialList(self.job)

		# Enter the Sandbox
		if os.path.isdir('tests'):
			_dir = 'tests/.job_sandbox'
			try:
				os.mkdir(_dir)  # create sandbox directory
			except OSError:
				pass
			os.chdir(_dir)  	# have execution stack enter sandbox directory
			self.job._path = os.getcwd()	# put object in sandbox
		else:
			raise OSError('Not started from program root')

	def tearDown(self):
		if os.path.isdir('../../tests'):  # checks if in project directory in tests/.job_sandbox
			_escape = '../..'  # escape tests/.job_sandbox
			_delete = 'tests/.job_sandbox'
		else:
			_escape = '..'
			_delete = '.job_sandbox'
		os.chdir(_escape)
		shutil.rmtree(_delete, ignore_errors=True)

	def test__init__(self):
		""" Tests that the appropriate attributes are added to the Material List `self.object`
		:return:
		"""
		_tests = ('job', 'items', '_doc', 'foreman', 'date_sent', 'date_due',
				  'label', 'comments', 'quotes', 'tasks', 'rentals', 'fulfilled',
				  'delivered', 'delivery', 'backorders', 'sent_out', 'po')
		for _test in _tests:
			self.assertEqual(hasattr(self.object, _test), True)
		return NotImplemented

	def test__setattr__(self):
		""" Tests that update_po_in_log is correctly implemented """
		# store `__init__` function
		# override `__init__` with arbitrary function that sets a value to any attribute
		# test that `update` was called
		# test that `super(##).__setattr__(##)` was called
		return NotImplemented

	def test__repr__(self):
		""" Tests that __repr__ function incorporates datetime object and `label` correctly
		:return:
		"""
		return NotImplemented

	def test__len__(self):
		""" Tests that `__len__` does not crash on error and that correct value is returned
		:return:
		"""
		# Test with no items
		self.object.items = None
		self.assertEqual(len(self.object), 0)

		# Test with 4 items
		self.object.items = (1, 2, 3, 4)
		self.assertEqual(len(self.object), 4)

	def testAge(self):
		""" Tests age property with and without date_due attribute.
		:return:
		"""
		return NotImplemented

	def testDoc(self):
		self.assertEqual(self.object._doc, None)  # `self.object._doc` attribute should be empty
		self.assertEqual(self.object.doc, False)  # empty doc should return False

		_doc = 'test.txt'
		_path = os.path.join(self.job.path, 'Materials', _doc)
		self.job.init_struct()	# initialize directory structure before creating file
		open(_path, 'a').close()

		self.object.doc = _doc  					# test setter function
		self.assertEqual(self.object.doc[1], _doc)  # test getter function
		## manually create dummy file in self.job project folder
		## verify returned path exists
		return NotImplemented

	def testUpdate(self):
		"""	Tests that `self.job.mat_lists` attribute is updated
		:return:
		"""
		return NotImplemented

	def testUpgradeQuote(self):
		""" Tests that functions successfully returns a MaterialListQuote object of `self`
		:return:
		"""
		return NotImplemented

	def testAddQuote(self):
		## manually create quote
		## verify that quote was added to self.object.quotes
		## verify that quote was added to self.object.job.quotes
		## verify that self.object.sent_out is True
		return NotImplemented

	def testDelQuote(self):
		## manually create Quote
		## verify that quote was deleted
		return NotImplemented

	def testAddPO(self):
		## manually create po
		## verify that PO was added to self.object.po
		## verify that Job object has PO
		## verify that self.object.fulfilled is True
		return NotImplemented

	def testDelPO(self):
		""" Tests that passed object or hash is successfully deleted.
		:return:
		"""
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
