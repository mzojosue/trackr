import unittest

import core


class TestJob(unittest.TestCase):
	def setUp(self):
		self.job = core.Job('test_job')

	def testName(self):
		""" Tests name property with and without number attribute
		:return:
		"""
		return NotImplemented

	def testAltName(self):
		""" Tests alt_name property
		:return:
		"""
		return NotImplemented

	def testDrawings(self):
		""" Tests drawings property by creating empty files and parsing shell output
		:return:
		"""
		return NotImplemented

	def testHasDrawings(self):
		""" Tests has_drawings property by parsing shell output
		:return:
		"""
		return NotImplemented

	def testHasDocuments(self):
		""" Tests has_documents property by parsing shell output
		:return:
		"""
		return NotImplemented

	def testHasAddendums(self):
		""" Checks to see if self has any takeoff
		:return:
		"""

	def testUpdate(self):
		""" Tests update function with and without 'number' and 'db' atrributes
		:return:
		"""
		return NotImplemented

	def testLoadInfo(self):
		""" Tests load_info method with/without 'path' and with/without the directory existing
		:return:
		"""
		return NotImplemented

	def testDumpInfo(self):
		""" Tests dump_info method with/without 'path' and with/without the directory existing
		:return:
		"""


class TestAwardedJob(unittest.TestCase):
	def setUp(self):
		num = core.get_job_num()
		job = core.AwardedJob(num, 'test_job', init_struct=False)
		self.object = job

	def testAddDelList(self):
		_mat_list_obj = core.MaterialList(self.object)

		_obj_dict = self.object.materials.values()
		self.assertIn(_mat_list_obj, _obj_dict, 'Material List was not added to AwardedJob.materials')

		# TODO: test filesystem delete function
		self.object.del_material_list(_mat_list_obj.hash)
		_obj_dict = self.object.materials.values()
		self.assertNotIn(_mat_list_obj, _obj_dict, 'Material List was not deleted from AwardedJob.materials')

	def testAddDelQuote(self):
		_mat_list_obj = core.MaterialList(self.object)
		_quote_obj = core.MaterialListQuote(_mat_list_obj, 'Test Vendor @ Test')

		_quote_list = self.object.quotes.values()
		self.assertIn(_quote_obj, _quote_list, 'Quote was not added to AwardedJob.quotes')

		# TODO: test filesystem delete function
		self.object.del_quote(_quote_obj.hash, delete=False)
		_quote_list = self.object.quotes.values()
		self.assertNotIn(_quote_obj, _quote_list, 'Quote was not deleted from AwardedJob.quotes')

	def testAddDelTask(self):
		_task_obj = core.Todo('Test todo', job=self.object)
		_task_list = self.object.tasks.values()

		self.assertIn(_task_obj, _task_list, 'Task object was not added to AwardedJob.tasks')

		self.object.del_task(_task_obj.hash)
		_task_list = self.object.tasks.values()
		self.assertNotIn(_task_obj, _task_list, 'Task object was not deleted from AwardedJob.tasks')

	def testFolderStructure(self):
		# self.object.init_struct()
		# Confirm that all folders were created
		# Confirm that all sub-folders were created
		return None

	def testHasOpenList(self):
		# add 5 lists to job
		# self.object.has_open_lists should equal 5
		return None


suite = unittest.TestLoader().loadTestsFromTestCase(TestAwardedJob)
unittest.TextTestRunner(verbosity=2).run(suite)