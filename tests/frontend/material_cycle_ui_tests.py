from flask.ext.testing import TestCase

from core.environment import disconnect_db
from core.frontend import *
from core.objects import AwardedJob, MaterialList, User


class TestMaterialCycleUI(TestCase):
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
			_dir = 'tests/.test_sandbox'
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
			_delete = 'tests/.test_sandbox'
			os.chdir(_escape)
			shutil.rmtree(_delete)

	def create_app(self):
		"""
		Create app returns the Flask instance defined in core.frontend.config.
		The 'TESTING' config flag is activated to disable error catching, for better error reports.
		"""
		app.config['TESTING'] = True
		return app

	def test_job_materials(self):
		"""
		Tests `job_materials` view function by ensuring that the correct AwardedJob is selected,
		and that the correct Jinja template is rendered.

		A HTTP POST is then created to test MaterialList creation and route redirection
		"""
		_get = '/j/%d/materials' % self.job.number
		response = self.client.get(_get)

		self.assert_200(response)
		self.assert_template_used('jobs/job_materials.html')
		# test redirect when AwardedJob does not exist
		# test redirect when new MaterialList is created
		# TODO: test MaterialList creation via HTTP POST

	def test_material_list(self):
		"""
		Tests `material_list` view function by passing an arbitrarily selected MaterialList,
		and ensures that the 'material_list.html' template is rendered.
		"""
		mlist = MaterialList(self.job)
		_get = '/j/%d/material/%d' % (self.job.number, mlist.hash)
		response = self.client.get(_get)

		self.assert_200(response)
		self.assert_template_used('material_list.html')
		# TODO: test errors when MaterialList doesn't exist
		# TODO: test errors when AwardedJob doesn't exist
		# TODO: test creating MaterialList w/ HTTP POST file stream
		# TODO: test creating MaterialList w/ HTTP POST variable 'itemCounter'

	def test_update_material_list(self):
		"""
		Tests `update_material_list` view method by arbitrarily modifying a MaterialList.
		"""
		# TODO: create MaterialList object
		# TODO: create TestRequest object
		# TODO: confirm redirect
		self.fail()

	def test_deliveries(self):
		"""
		Tests `deliveries` view method by asserting the loaded template.
		"""
		response = self.client.get('/deliveries')

		self.assert_200(response)
		self.assert_template_used('deliveries.html')

	def test_serialized_deliveries(self):
		"""
		Tests `serialized_deliveries` method by analyzing the returned JSON output.
		"""
		# TODO: create dummy MaterialList objects
		# TODO: create dummy Delivery objects
		response = self.client.get('/deliveries/json')

		self.assert_200(response)

		# Verify JSON API formatting
		_keys = ('success', 'result')
		for k in _keys:
			self.assertIn(k, response.json.keys())
		self.assertEqual(1, response.json['success'])			# verify 'success' status
		self.assertEqual(type(response.json['result']), list) 	# verify 'result' value type
		# TODO: verify 'results' contains Delivery objects

	def test_schedule_delivery(self):
		"""
		Tests `schedule_delivery` by passing arbitrary values and ensuring Delivery object was created.
		"""
		mlist = MaterialList(self.job)
		post = {'jobs-number': self.job.number,
				'materialListHash': mlist.hash,
				'destination': 'shop',
				'deliveryDate': today().date()}

		urls = ('/delivery/schedule', '/j/%d/deliveries/new' % self.job.number)
		for u in urls:
			response = self.client.post(u, data=post)
			self.assertRedirects(response, '/None')		# confirm redirect to referring page, which should be None

	def test_accept_delivery(self):
		"""
		Tests `accept_delivery` by arbitrarily modifying `Delivery.delivered` via HTTP GET variables.
		"""
		mlist = MaterialList(self.job)
		deliv = Delivery(mlist)
		response = self.client.get('/j/%d/deliveries/%d/delivered' % (self.job.number, deliv.hash))

		self.assertRedirects(response, '/None')		# confirm redirect to referring page, which should be None

	def test_quote(self):
		"""
		Tests `quote` by creating a MaterialListQuote via HTTP POST variables.
		"""
		mlist = MaterialList(self.job)
		post = {'materialListHash': mlist.hash,
				'quotePrice': 0.0,
				'vendor': 'test vendor',
				'quote': None}

		# TODO: test with and without file stream

		urls = ('/j/%d/material/quote' % self.job.number,
				'/j/%d/material/%d/quote' % (self.job.number, mlist.hash))
		for u in urls:
			response = self.client.post(u, data=post)
			_location = '/j/%d/material/%d' % (self.job.number, mlist.hash)		# target url to verify

			self.assertRedirects(response, _location)

	def test_add_quote_doc(self):
		"""
		Tests `add_quote_doc` API function by passing a file stream via a HTTP POST then checking for file in directory.
		"""
		mlist = MaterialList(self.job)
		quote = MaterialListQuote(mlist, 'test vendor')

		url = '/j/%d/material/%d/quote/%d/update/doc' % (self.job.number, mlist.hash, quote.hash)
		response = self.client.post(url)
		_location = '/j/%d/material/%d' % (self.job.number, mlist.hash)		# target for redirect (MaterialList view)
		# TODO: pass abstract file stream via HTTP POST

		self.assertRedirects(response, _location)

	def test_update_po_attr(self):
		"""
		Tests `update_po_attr` API function by updating a PO attribute via
		"""
		mlist = MaterialList(self.job)
		quote = MaterialListQuote(mlist, 'test vendor')
		po = PO(self.job, mlist, quote, update=False)
		self.assertEqual(po.price, 0.0)		# check value before modification

		_attr = 'price'						# PO attribute to modify
		post  = {'updateValue': 5.0}
		url = '/j/%d/po/%d/update/%s' % (self.job.number, po.number, _attr)
		response = self.client.post(url, data=post)

		self.assertRedirects(response, '/None')
		self.assertEqual(po.price, 5.0)		# test attribute modification

	def test_material_quote_doc(self):
		self.fail()
