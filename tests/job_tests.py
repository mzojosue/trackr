import unittest
import os
import shutil

import core


class TestWorker(unittest.TestCase):
	def setUp(self):
		core.disconnect_db()  # ensure database objects aren't interfered with
		self.name = 'test worker'
		self.job = core.AwardedJob(1, 'test_job')
		self.object = core.Worker(self.name, self.job)

		self.job._dump_lock = True  # prevent object storage

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

	def test_job_number(self):
		""" Tests job_num property and ensures _job_num attribute is updated as well.
		"""
		return NotImplemented

	def test___setattr__(self):
		""" Tests __setattr__ method and ensures that prev_job attribute is populated.
		"""
		return NotImplemented

	def test___repr__(self):
		""" Tests __repr__ function against hardcoded values.
		"""
		return NotImplemented

	def test_find(self):
		""" Creates arbitrary Worker objects then tests Worker.find
		"""
		return NotImplemented

	def test_get_set_or_create(self):
		""" Tests get set or create method by attempting to get, set, and create objects.
		"""
		return NotImplemented

	def add_labor(self):
		""" Calls add_labor with hardcoded values. Tests date_worked, week_end, and job.
		"""
		return NotImplemented

	def test_load_workers(self):
		""" Clears object storage then calls load_workers. Tests with and without path existing.
		"""
		return NotImplemented

	def test_dump_info(self):
		""" Creates arbitrary Worker objects then verifies contents written to disk by dump_info.
		Tests with/w/o db attribute.
		"""
		return NotImplemented

	def test_update(self):
		""" Tests update function with/w/o db and hash.
		"""
		return NotImplemented


class TestJob(unittest.TestCase):
	def setUp(self):
		core.disconnect_db()  # ensure database objects aren't interfered with
		self.name = 'test_job'
		self.job = core.Job(self.name)
		self.job._dump_lock = True  # prevent object storage

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

	def testInit(self):
		""" Tests all attributes creating during initialization as well as class attributes
		:return:
		"""
		return NotImplemented

	def test_name(self):
		""" Tests name property with and without number attribute
		"""
		# without number attribute
		self.assertEqual(self.job.name, self.name)

		# with number attribute
		_num = 15
		self.job.number = _num
		self.assertEqual(self.job.name, '%s-%s' % (_num, self.name))

	def test_alt_name(self):
		""" Tests alt_name property
		"""
		# without alt_name attribute
		self.assertEqual(self.job.alt_name, self.name)

		# with alt_name attribute
		_alt = 'test'
		self.job.alt_name = _alt
		self.assertEqual(self.job.alt_name, _alt)

	def test_sub_path(self):
		""" Tests sub_path property with/w/o default_sub_dir attribute.
		"""
		return NotImplemented

	def test_path(self):
		""" Tests path property with/w/o _path and sub_path. Compares against hardcoded path using env_root.
		"""
		return NotImplemented

	def test_addendums(self):
		""" Tests drawings property by creating empty files
		"""
		self.assertEqual(self.job.addendums, {})  # test without directory

		self.job._path = os.getcwd()  # set path attribute to current directory
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

	def test_drawings(self):
		""" Tests drawings property by creating empty files
		"""
		self.assertEqual(self.job.drawings, {})  # test without directory

		self.job._path = os.getcwd()  # set path attribute to current directory
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

	def test_documents(self):
		""" Tests drawings property by creating empty files
		"""
		self.assertEqual(self.job.documents, {})  # test without directory

		self.job._path = os.getcwd()  # set path attribute to current directory
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

	def test_has_drawings(self):
		""" Tests has_drawings property by parsing shell output
		"""
		self.assertEqual(self.job.has_drawings, False)  # without directory

		self.job._path = os.getcwd()  # set path attribute to current directory
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

	def test_has_documents(self):
		""" Tests has_documents property by parsing shell output
		"""
		self.assertEqual(self.job.has_documents, False)  # without directory

		self.job._path = os.getcwd()  # set path attribute to current directory
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

	def test_has_addendums(self):
		""" Checks to see if self has any takeoff
		"""
		self.assertEqual(self.job.has_addendums, False)  # without directory

		self.job._path = os.getcwd()  # set path attribute to current directory
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

	def test_update(self):
		""" Tests update function with and without 'number' and 'db' atrributes.
		"""
		self.assertEqual(self.job.update(), False)  # without number attribute

		_num = 24
		self.job.number = _num
		self.assertEqual(self.job.update(), 'DB_ERROR')  # without db attributes

		self.job.db = {}
		self.assertEqual(self.job.db.keys()[0], _num)  # ensure that update was called on __setattr__ previous line

	def test_dump_all(self):
		""" Creates multiple job objects in virtual db.
		Tests dump_all function with/without _dump_lock, completed_db, db, and default_sub_dir.
		"""


class TestAwardedJob(unittest.TestCase):
	def setUp(self):
		core.disconnect_db()  # ensure database objects aren't interfered with
		num = core.get_job_num()
		self.name = 'test_job'
		self.object = core.AwardedJob(num, self.name, init_struct=False)
		self.object._dump_lock = True  # prevent object storage

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

	def test_init_struct(self):
		""" Execute init_struct in sandbox and analyze created directory
		"""
		return NotImplemented


	# Material List Tests #

	def test_materials(self):
		""" Manually adds MaterialLists and creates files in 'Materials' directory.
		Tests with/w/o path attribute. Tests with/w/o Materials directory.
		Ensures newly created files are added to _materials.
		"""
		return NotImplemented

	def test_has_open_lists(self):
		""" Manually adds both fulfilled and unfulfilled MaterialLists """
		return NotImplemented

	def test_add_mat_list(self):
		""" Creates a MaterialList linked to self.object. """
		_mat_list_obj = core.MaterialList(self.object)  # add_mat_list is called during MaterialList.update

		_obj_dict = self.object.materials.values()
		self.assertIn(_mat_list_obj, _obj_dict, 'Material List was not added to AwardedJob.materials')

	def test_del_mat_list(self):
		""" Creates a MaterialList linked to self.object then calls del_mat_list.
		"""
		_mat_list_obj = core.MaterialList(self.object)  # add_mat_list is called during MaterialList.update

		# TODO: test filesystem delete function
		self.object.del_mat_list(_mat_list_obj.hash)
		_obj_dict = self.object.materials.values()
		self.assertNotIn(_mat_list_obj, _obj_dict, 'Material List was not deleted from AwardedJob.materials')


	# Quote Tests #

	def test_quotes(self):
		""" Manually create adds MaterialLists/Quotes and creates files in 'Quotes' directory.
		Tests with/w/o 'Quote' directory.
		"""
		return NotImplemented

	def test_unlinked_quotes(self):
		""" Manually add MaterialLists/Quotes and creates files in 'Quotes' directory.
		Tests that separation is maintained between quotes and _quotes.
		Tests with/w/o 'Quote' directory."""
		return NotImplemented

	def test_add_quote(self):
		""" Creates a MaterialList and Quote linked to self.object.
		"""
		_mat_list_obj = core.MaterialList(self.object)  # add_mat_list is called during MaterialList.update
		_quote_obj = core.MaterialListQuote(_mat_list_obj, 'Test Vendor @ Test')

		_quote_list = self.object.quotes.values()
		self.assertIn(_quote_obj, _quote_list, 'Quote was not added to AwardedJob.quotes')

	def test_del_quote(self):
		""" Creates a MaterialList and Quote linked to self.object then calls del_quote.
		"""
		_mat_list_obj = core.MaterialList(self.object)  # add_mat_list is called during MaterialList.update
		_quote_obj = core.MaterialListQuote(_mat_list_obj, 'Test Vendor @ Test')

		# TODO: test filesystem delete function
		self.object.del_quote(_quote_obj.hash, delete=False)
		_quote_list = self.object.quotes.values()
		self.assertNotIn(_quote_obj, _quote_list, 'Quote was not deleted from AwardedJob.quotes')


	def test_add_po(self):
		""" Creates a MaterialList/Quote/PO linked to self.object.
		Ensures that MaterialList objects are changed appropriately.
		"""
		return NotImplemented

	def test_next_po(self):
		""" Ensures that next_po keeps PO numbers continuous.
		Fills self.object.POs with arbitrary PO numbers and objects then calls next_po.
		"""
		return NotImplemented

	def test_show_po(self):
		""" Fills self.object.POs with arbitrary PO numbers and objects,
		then ensures that show_po can be parsed as a PO value
		"""
		return NotImplemented

	def test_add_delivery(self):
		""" Creates an arbitrary Delivery object linked to self.object.
		"""
		return NotImplemented

	def test_add_worker(self):
		""" Creates an arbitrary Worker object linked to self.object.
		"""
		return NotImplemented

	def test_labor(self):
		""" Creates arbitrary Worker and Timesheet objects linked to self.object and validates output.
		"""
		return NotImplemented

	def test_cost(self):
		""" Creates arbitrary Worker and Timesheet objects linked to self and validates cost output
		"""
		return NotImplemented

	def test_add_task(self):
		""" Creates a Task object linked to self.object then calls add_task.
		"""
		_task_obj = core.Todo('Test todo', job=self.object)
		_task_list = self.object.tasks.values()

		self.assertIn(_task_obj, _task_list, 'Task object was not added to AwardedJob.tasks')

	def test_del_task(self):
		""" Creates a Task object linked to self.object then calls del_task.
		"""
		_task_obj = core.Todo('Test todo', job=self.object)
		self.object.del_task(_task_obj.hash)

		_task_list = self.object.tasks.values()
		self.assertNotIn(_task_obj, _task_list, 'Task object was not deleted from AwardedJob.tasks')

	def test_sheet_name(self):
		""" Tests property by parsing sheet_name output and comparing to name and number attributes.
		"""
		return NotImplemented

	def test_find(self):
		""" Tests the find static method by creating arbitrary AwardedJob objects and calling AwardedJob.find
		"""
		return NotImplemented


suite = unittest.TestLoader().loadTestsFromTestCase(TestJob)
unittest.TextTestRunner(verbosity=2).run(suite)
suite = unittest.TestLoader().loadTestsFromTestCase(TestAwardedJob)
unittest.TextTestRunner(verbosity=2).run(suite)
