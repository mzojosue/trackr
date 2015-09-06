import unittest
import os
import shutil

import core


class TestJob(unittest.TestCase):
	def setUp(self):
		self.name = 'test_job'
		self.job = core.Job(self.name)

		if os.path.isdir('tests'):
			_dir = 'tests/.job_sandbox'
		else:
			_dir = '.job_sandbox'
		try:
			os.mkdir(_dir)  # create sandbox directory
		except OSError:
			pass
		os.chdir(_dir)  # enter sandbox directory

	def tearDown(self):
		if os.path.isdir('../../tests'):  # checks if in tests/.job_sandbox
			_escape = '../..'  # escape tests/.job_sandbox
			_delete = 'tests/.job_sandbox'
		else:
			_escape = '..'
			_delete = '.job_sandbox'
		os.chdir(_escape)
		shutil.rmtree(_delete)

	def testName(self):
		""" Tests name property with and without number attribute
		:return:
		"""
		# without number attribute
		self.assertEqual(self.job.name, self.name)

		# with number attribute
		_num = 15
		self.job.number = _num
		self.assertEqual(self.job.name, '%s-%s' % (_num, self.name))

	def testAltName(self):
		""" Tests alt_name property
		:return:
		"""
		# without alt_name attribute
		self.assertEqual(self.job.alt_name, self.name)

		# with alt_name attribute
		_alt = 'test'
		self.job.alt_name = _alt
		self.assertEqual(self.job.alt_name, _alt)

	def testAddendums(self):
		""" Tests drawings property by creating empty files
		:return:
		"""
		self.assertEqual(self.job.addendums, {})  # test without directory

		self.job.path = os.getcwd()  # set path attribute to current directory
		if os.path.isdir('../.job_sandbox'):  # checks for sandbox
			_dir = 'Addendums'
			os.mkdir(_dir)
			os.chdir(_dir)
			self.assertEqual(self.job.addendums, {})  # test with directory, without files

			_adds = ['add1', 'add2', 'add3']
			for fname in _adds:
				_fobj = open(fname, 'w')
				_fobj.close()
			self.assertEqual(self.job.addendums.keys().sort(), _adds.sort())  # check returned keys against created files
			os.chdir('..')

	def testDrawings(self):
		""" Tests drawings property by creating empty files
		:return:
		"""
		self.assertEqual(self.job.drawings, {})  # test without directory

		self.job.path = os.getcwd()  # set path attribute to current directory
		if os.path.isdir('../.job_sandbox'):  # checks for sandbox
			_dir = 'Drawings'
			os.mkdir(_dir)
			os.chdir(_dir)
			self.assertEqual(self.job.drawings, {})  # test with directory, without files

			_dwgs = ['dwg1', 'dwg2', 'dwg3']
			for fname in _dwgs:
				_fobj = open(fname, 'w')
				_fobj.close()
			self.assertEqual(self.job.drawings.keys().sort(), _dwgs.sort())  # check returned keys against created files
			os.chdir('..')

	def testDocuments(self):
		""" Tests drawings property by creating empty files
		:return:
		"""
		self.assertEqual(self.job.documents, {})  # test without directory

		self.job.path = os.getcwd()  # set path attribute to current directory
		if os.path.isdir('../.job_sandbox'):  # checks for sandbox
			_dir = 'Documents'
			os.mkdir(_dir)
			os.chdir(_dir)
			self.assertEqual(self.job.documents, {})  # test with directory, without files

			_docs = ['doc1', 'doc2', 'doc3']
			for fname in _docs:
				_fobj = open(fname, 'w')
				_fobj.close()
			self.assertEqual(self.job.documents.keys().sort(), _docs.sort())  # check returned keys against created files
			os.chdir('..')

	def testHasDrawings(self):
		""" Tests has_drawings property by parsing shell output
		:return:
		"""
		self.assertEqual(self.job.has_drawings, False)  # without directory

		self.job.path = os.getcwd()  # set path attribute to current directory
		if os.path.isdir('../.job_sandbox'):  # checks for sandbox
			_dir = 'Drawings'
			os.mkdir(_dir)
			os.chdir(_dir)
			self.assertEqual(self.job.has_drawings, False)  # with directory, without files

			_dwgs = ['dwg1', 'dwg2', 'dwg3']
			for fname in _dwgs:
				_fobj = open(fname, 'w')
				_fobj.close()
			self.assertEqual(self.job.has_drawings, True)  # with files
			os.chdir('..')

	def testHasDocuments(self):
		""" Tests has_documents property by parsing shell output
		:return:
		"""
		self.assertEqual(self.job.has_documents, False)  # without directory

		self.job.path = os.getcwd()  # set path attribute to current directory
		if os.path.isdir('../.job_sandbox'):  # checks for sandbox
			_dir = 'Documents'
			os.mkdir(_dir)
			os.chdir(_dir)
			self.assertEqual(self.job.has_documents, False)  # with directory, without files

			_docs = ['doc1', 'doc2', 'doc3']
			for fname in _docs:
				_fobj = open(fname, 'w')
				_fobj.close()
			self.assertEqual(self.job.has_documents, True)  # with files
			os.chdir('..')

	def testHasAddendums(self):
		""" Checks to see if self has any takeoff
		:return:
		"""
		self.assertEqual(self.job.has_addendums, False)  # without directory

		self.job.path = os.getcwd()  # set path attribute to current directory
		if os.path.isdir('../.job_sandbox'):  # checks for sandbox
			_dir = 'Addendums'
			os.mkdir(_dir)
			os.chdir(_dir)
			self.assertEqual(self.job.has_addendums, False)  # with directory, without files

			_adds = ['add1', 'add2', 'add3']
			for fname in _adds:
				_fobj = open(fname, 'w')
				_fobj.close()
			self.assertEqual(self.job.has_addendums, True)  # with files
			os.chdir('..')

	def testUpdate(self):
		""" Tests update function with and without 'number' and 'db' atrributes.
		:return:
		"""
		self.assertEqual(self.job.update(), False)  # without number attribute

		_num = 24
		self.job.number = _num
		self.assertEqual(self.job.update(), 'DB_ERROR')  # without db attributes

		self.job.db = {}
		self.assertEqual(self.job.db.keys()[0], _num)  # ensure that update was called on __setattr__ previous line

	def testLoadInfo(self):
		""" Tests load_info method with/without 'path' and with/without the directory existing
		:return:
		"""

		self.assertEqual(self.job.load_info(), False)  # without path attribute

		_dir = os.path.join(os.getcwd(), 'tmp')
		self.job.path = _dir
		self.assertEqual(self.job.load_info(), False)  # with path, directory doesn't exist

		os.mkdir(_dir)
		self.assertEqual(self.job.load_info(), True)   # dump_info is called
		#TODO: create new YAML file with arbitrary values

	def testDumpInfo(self):
		""" Tests dump_info method with/without 'path' and with/without the directory existing
		:return:
		"""
		self.assertEqual(self.job.dump_info(), False)  # without path attribute

		_dir = os.path.join(os.getcwd(), 'tmp')
		self.job.path = _dir
		self.assertEqual(self.job.dump_info(), False)  # with path, directory doesn't exist

		os.mkdir(_dir)
		self.assertEqual(self.job.dump_info(), True)

		# TODO: validate YAML file


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


suite = unittest.TestLoader().loadTestsFromTestCase(TestJob)
unittest.TextTestRunner(verbosity=2).run(suite)
suite = unittest.TestLoader().loadTestsFromTestCase(TestAwardedJob)
unittest.TextTestRunner(verbosity=2).run(suite)
