from flask.ext.testing import TestCase

from core.db import disconnect_db
from core.frontend import *
from core.objects import EstimatingJob, EstimatingQuote, User


class TestJobUI(TestCase):
	def setUp(self):
		disconnect_db()  # ensure database objects aren't interfered with
		Job._dump_lock = True  # prevent object storage
		self.bid = EstimatingJob('test bid', init_struct=False, add_to_log=False)

		# Fake a user session
		User._dump_lock = True  # prevent local object storage
		self.user = User('test user', 'user', 'user@email.com', 1234)
		with self.client as c:
			with c.session_transaction() as sess:
				sess['hash_id'] = self.user.hash
				sess['logged_in'] = True

		# Enter the Sandbox
		if os.path.isdir('tests'):
			_dir = 'tests/.bid_sandbox'
			try:
				os.mkdir(_dir)  # create sandbox
			except OSError:
				pass  # assume that directory already exists for some reason
			self.bid._path = os.getcwd()
			os.chdir(_dir)  # move stack to sandbox

	def tearDown(self):
		# Exit the Sandbox
		if os.path.isdir('../../tests'):
			_escape = '../..'
			_delete = 'tests/.bid_sandbox'
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

	def test_estimating_home(self):
		return self.fail()

	def test_current_bids(self):
		return self.fail()

	def test_past_bids(self):
		return self.fail()

	def test_estimating_analytics(self):
		return self.fail()

	def test_bid_overview(self):
		return self.fail()

	def test_bid_calculate(self):
		return self.fail()

	def test_bid_folder(self):
		return self.fail()

	def test_bid_drawings(self):
		return self.fail()

	def test_bid_takeoffs(self):
		return self.fail()

	def test_create_bid(self):
		return self.fail()

	def test_award_bid(self):
		return self.fail()

	def test_cancel_bid(self):
		return self.fail()

	def test_create_sub_bid(self):
		return self.fail()

	def test_delete_sub_bid(self):
		return self.fail()

	def test_cancel_sub_bid(self):
		return self.fail()

	def test_update_sub_bid(self):
		return self.fail()

	def test_bid_quote(self):
		return self.fail()

	def test_upload_bid_quote(self):
		return self.fail()

	def test_update_bid_quote(self):
		return self.fail()

	def test_delete_bid_quote(self):
		return self.fail()

	def test_get_available_items(self):
		return self.fail()

	def test_estimating_serialized_overview(self):
		return self.fail()

	def test_bid_drawing_doc(self):
		return self.fail()

	def test_bid_get_document(self):
		return self.fail()