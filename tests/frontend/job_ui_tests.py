from flask.ext.testing import TestCase

from core.environment import disconnect_db
from core.frontend import *
from core.objects import AwardedJob, MaterialList, User


class TestJobUI(TestCase):
	def setUp(self):
		disconnect_db()  # ensure database objects aren't interfered with
		Job._dump_lock = True  # prevent object storage
		num = 1  # hardcoded int assignment is used in place `get_job_num()`
		self.job = AwardedJob(num, 'test job', init_struct=False)

		# Fake a user session
		User._dump_lock = True  # prevent local object storage
		self.user = User('test user', 'user', 'user@email.com', 1234)
		with self.client as c:
			with c.session_transaction() as sess:
				sess['hash_id'] = self.user.hash
				sess['logged_in'] = True

		# Enter the Sandbox
		if os.path.isdir('tests'):
			_dir = 'tests/.job_sandbox'
			try:
				os.mkdir(_dir)  # create sandbox
			except OSError:
				pass  			# assume that directory already exists for some reason
			self.job._path = os.getcwd()
			os.chdir(_dir)  	# move stack to sandbox

	def tearDown(self):
		# Exit the Sandbox
		if os.path.isdir('../../tests'):
			_escape = '../..'
			_delete = 'tests/.job_sandbox'
			os.chdir(_escape)
			shutil.rmtree(_delete)

	def create_app(self):
		"""
		Create app returns the Flask instance defined in core.frontend.config.
		The 'TESTING' config flag is activated to disable error catching, for better error reports.
		"""
		app.config['TESTING'] = True
		return app


	# Begin View Method Tests #

	def test_all_jobs(self):
		response = self.client.get('/j/')

		self.assert_200(response)
		self.assert_template_used('jobs/all_jobs.html')

	def test_job_overview(self):
		_get = '/j/%d' % self.job.number
		response = self.client.get(_get)

		self.assert_200(response)
		self.assert_template_used('jobs/job_overview.html')

		# TODO: test template variables

		# test invalid AwardedJob number
		_get = '/j/999'
		response = self.client.get(_get)

		_error = 'Error: AwardedJob does not exist'		# expected reply
		self.assertEqual(response.data, _error)

	def test_job_info(self):
		_get = '/j/%d/info' % self.job.number
		response = self.client.get(_get)

		self.assert_200(response)
		self.assert_template_used('jobs/job_info.html')

		# test with invalid AwardedJob number
		_get = '/j/999/info'
		response = self.client.get(_get)

		_error = 'Error: AwardedJob does not exist'		# expected reply
		self.assertEqual(response.data, _error)

	def test_job_analytics(self):
		return self.fail()

	def test_job_material_doc(self):
		# create document
		# add MaterialList object w/ document
		mlist_hash = 0
		_get = '/j/%d/materials/%d' % (self.job.number, mlist_hash)
		# response = self.client.get(_get)

		return self.fail()

	def test_delete_material_doc(self):
		mlist = MaterialList(self.job)
		self.assertIn(mlist, self.job.materials.values())

		_get = '/j/%d/materials/%d/del' % (self.job.number, mlist.hash)
		response = self.client.get(_get)

		self.assert_redirects(response, '/None')
		self.assertNotIn(mlist, self.job.materials)

	def test_update_job_quote(self):
		return self.fail()

	def test_delete_job_quote(self):
		return self.fail()

	def test_job_quote_award_po(self):
		return self.fail()

	def test_job_deliveries(self):
		return self.fail()

	def test_job_pos(self):
		return self.fail()

	def test_job_rentals(self):
		return self.fail()

	def test_create_job(self):
		return self.fail()

	def test_update_job_info(self):
		return self.fail()