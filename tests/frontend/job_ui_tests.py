from flask.ext.testing import TestCase

from core.db import disconnect_db
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
				pass  # assume that directory already exists for some reason
			self.job._path = os.getcwd()
			os.chdir(_dir)  # move stack to sandbox

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

	def test_all_jobs(self):
		return self.fail()

	def test_job_overview(self):
		return self.fail()

	def test_job_info(self):
		return self.fail()

	def test_job_material_doc(self):
		return self.fail()

	def test_delete_material_doc(self):
		return self.fail()

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