import os
from datetime import datetime

today = datetime.today
now = datetime.now


class Worker(object):
	workers = {}

	# pay rate constants
	A_RATE = 100.84
	A_RATE_journeyman = 97.38
	B_RATE = 51.76

	def __init__(self, name, job, phone=None, email=None, role='Installer', rate=None):
		self.name = name
		self.hash = abs(hash(str(self.name)))
		self.job = job
		self.prev_jobs = []
		self.phone = str(phone)
		self.email = str(email)
		self.role = role
		if rate is 'a':
			self.rate = Worker.A_RATE
		elif rate is 'b':
			self.rate = Worker.B_RATE

		if hasattr(Worker, 'db'):
			Worker.db['workers'][self.hash] = self

	def __setattr__(self, name, value):
		""" Alters attribute setting to listen to when self.job is changed,
			the previous job is stored in self.prev_jobs
		"""
		if name is 'job':
			value.workers[self.hash] = self
			try:
				self.prev_jobs.append(self.job)
				del self.job.workers[self.hash]
			except AttributeError:
				pass

		return super(Worker, self).__setattr__(name, value)

	def __repr__(self):
		# TODO:update output format
		# TODO:return date since working at job
		return "\"%s\". %s at %s" % (self.name, self.role, self.job.name)

	@staticmethod
	def find(q_hash):
		if hasattr(Todo, 'db'):
			return Todo.db['workers'][q_hash]


class Job(object):
	number = 0
	jobs = {}

	default_sub_dir = "//SERVER/Documents/Esposito/Jobs"

	def __init__(self, job_num, name, start_date=None, end_date=None, alt_name=None, po_pre=None, address=None,
	             gc=None, gc_contact=None, scope=None, foreman=None, desc=None, rate='a',
	             contract_amount=None, tax_exempt=False, certified_pay=False, sub_path=None):
		# TODO:implement better document storage

		if hasattr(Job, 'db'):
			self.number = int(job_num)
			Job.db['job_num'] = job_num + 1
			Job.db['jobs'][self.number] = self
		self.name = '-'.join([str(self.number), str(name)])
		self.start_date = start_date
		self.end_date = end_date
		self.alt_name = alt_name
		self.po_pre = po_pre
		self.address = address

		self.gc = gc
		self.gc_contact = gc_contact
		self.scope = scope
		self.foreman = foreman
		self.desc = desc
		if rate is 'a':
			self.rate = Worker.A_RATE
		elif rate is 'b':
			self.rate = Worker.B_RATE

		self.contract_amount = contract_amount
		self.tax_exempt = tax_exempt
		self.certified_pay = certified_pay
		try:
			if sub_path:
				self.sub_path = sub_path
			elif not os.path.exists(os.path.join(Job.default_sub_dir, self.name)):
				os.mkdir(os.path.join(Job.default_sub_dir, self.name))
				self.sub_path = os.path.join(Job.default_sub_dir, self.name)
			else:
				self.sub_path = os.path.join(Job.default_sub_dir, self.name)
		except OSError:
			print "ERROR: cannot connect to server. File functions disabled.\n"

		self._PO = 0    # stores most recent PO suffix number
		self.POs = {}   # stores PO strings as keys
		self.workers = {}
		self.materials = {}
		self.deliveries = {}
		self.tasks = {}
		# Job.timesheets.key is datetime.datetime object
		# Job.timesheets.value is [ 'pathname/to/timesheet', hours ]
		self.timesheets = {}

	@property
	def next_po(self):
		""" Used for manually reserving a PO for use later
		:return: returns the value of the current available PO for considering it being given to a vendor
		"""
		_po = self._PO  # + 1
		_po = '%03d' % _po        # add padding to PO #
		return '-'.join([self.name, _po])

	@property
	def claim_po(self):
		""" Used for storing a PO number with a quote and sending it a vendor
		:return: returns unformatted PO number
		"""
		_po = self._PO
		self._PO += 1
		return _po

	@staticmethod
	def init_struct(self):
		""" Initializes project directory hierarchy. """
		# TODO:initialize documents w/ job information
		if self.sub_path:
			return NotImplemented

	@property
	def path(self):
		""" Return absolute sub path using global project path and Job.sub_path """
		return NotImplemented

	@property
	def labor(self):
		""" Calculates labor totals """
		hrs = 0.0
		for i in self.timesheets.itervalues():
			hrs += float(i[1])  # grab second item in list
		return hrs

	@property
	def cost(self):
		""" Calculates job cost totals """
		amt = 0.0
		for i in self.timesheets.itervalues():
			amt += (float(i[1]) * float(self.rate))
		for i in self.POs.itervalues():
			amt += i.quote.price
		return amt

	@staticmethod
	def find(num):
		if hasattr(Job, 'db'):
			return Job.db['jobs'][num]


class MaterialList(object):
	lists = {}

	def __init__(self, job, items=None, doc=None, foreman=None, date_sent=today(), date_due=None, comments=""):
		self.hash = abs(hash(str(now())))
		job.materials[self.hash] = self
		if hasattr(MaterialList, 'db'):
			MaterialList.db['materials'][self.hash] = self

		self.job = job
		self.items = items
		self.doc = doc
		self.foreman = foreman
		self.date_sent = date_sent
		self.date_due = date_due
		self.comments = comments

		self.quotes = []
		self.todo = True
		self.fulfilled = False

	def issue_po(self, quote, fulfills=False):
		return PO(self.job, quote=quote, fulfills=fulfills)

	@property
	def age(self):
		""" Used for highlighting unfulfilled material lists when displayed in a table.
		:return: days since material list was received. If fulfilled, returns False.
		"""
		# TODO:implement function
		return NotImplemented


class Quotes(object):
	def __init__(self, mat_list, price=0.0, vend=None, doc=None):
		self.mat_list = mat_list
		self.mat_list.quotes.append(self)
		self.price = float(price)
		self.vend = str(vend)
		self.doc = str(doc)  # document target path/name


class PO(object):
	def __init__(self, job, mat_list=None, date_issued=today(), fulfills=False,
	             quote=None, desc=None, deliveries=None):
		num = job.claim_po()
		self.name = '-'.join([str(job.name), str(num)])
		self.job = job
		self.mat_list = mat_list
		self.date_issued = date_issued
		if fulfills:
			self.mat_list.fulfilled = True
		self.quote = quote
		self.deliveries = deliveries  # stores initial delivery date
		self.desc = str(desc)

		self.job.POs[self.name] = self
		self.backorders = None  # stores any backorder delivery dates


class Vendor(object):
	def __init__(self):
		pass


class Delivery(object):
	""" Represents a future delivery.
	:param
		po:     pointer to PO object
	"""
	deliveries = {}

	def __init__(self, po, items=None, expected=None, destination='shop'):

		# TODO:add object to job.deliveries

		self.po = po
		del po
		self.hash = abs(hash(str(self.po.name)))
		if hasattr(Delivery, 'db'):
			Delivery.db['deliveries'][self.hash] = self
		self.delivered = False
		self.po.job.deliveries[self.hash] = self
		if items is None:
			self.items = self.po.mat_list
		else:
			self.items = items
		self.expected = expected
		self.destination = destination

	@staticmethod
	def find(q_hash):
		if hasattr(Todo, 'db'):
			return Todo.db['deliveries'][q_hash]


class Todo(object):
	""" Represents tasks to-do
	:param
		name:   the name of the task
		task:   text description of the task. may include link
		due:    task due date
		notif:  date/time to follow-up
	"""
	todos = {}
	completed = {}

	def __init__(self, name, task="", due=None, notify=None):
		self.name = str(name)
		self.hash = hash(self.name)
		self.hash = abs(self.hash)  # ensure positive values
		self.task = task
		self.due = due
		self.notify = notify
		if hasattr(Todo, 'db'):
			Todo.db['todos'][self.hash] = self

	def complete(self):
		if hasattr(Todo, 'db'):
			Todo.db['completed'][self.hash] = self
			del Todo.db['todos'][self.hash]
		return True

	@staticmethod
	def find(q_hash):
		if hasattr(Todo, 'db'):
			return Todo.db['todos'][q_hash]
		else:
			# TODO:create exception class
			raise BaseException