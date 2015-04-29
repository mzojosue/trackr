import unittest
import os.path as path

import core


class TestMaterialListMethods(unittest.TestCase):
	def setUp(self):
		num = core.get_job_num()
		job = core.AwardedJob(num, 'test_job')

		doc = core.os.path.join(job.sub_path, 'Materials')
		self._doc = (doc, 'doc.file')
		self.object = core.MaterialList(job, doc=self._doc)

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