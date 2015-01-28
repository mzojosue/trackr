from datetime import datetime

today = datetime.today
now = datetime.now

class Worker(object):
	workers = {}
	# pay rate constants
	A_RATE = 100.84
	A_RATE_journeyman = 97.38
	B_RATE = 51.76

	def __init__(self, name, phone=None, email=None, job=None, rate=None):
		self.name = name
		self.hash = abs(hash(str(self.name)))
		self.job = job
		self.prev_jobs = []
		self.phone = str(phone)
		self.email = str(email)
		if rate is 'a':
			self.rate = Worker.A_RATE
		elif rate is 'b':
			self.rate = Worker.B_RATE

		if hasattr(Worker, 'db'):
			Worker.db['workers'][self.hash] = self


	def __setattr__(self, name, value):
		if name is 'job':
			if self.job not in self.prev_jobs:
				self.prev_jobs.append(self.job)
		return super(Worker, self).__setattr__(name, value)

	@staticmethod
	def find(q_hash):
		if hasattr(Todo, 'db'):
			return Todo.db['workers'][q_hash]


class Job(object):
	number = 0
	jobs = {}

	def __init__(self, name, number=None, start_date=None, end_date=None, po_pre=None, address=None,
	             gc=None, gc_contact=None, scope=None, foreman=None, sub_path=None, desc=None,
	             rate='a', contract_amount=None, tax_exempt=False, certified_pay=False):
		##TODO:implement better document storage

		self.name = '-'.join([str(number), str(name)])
		if not number:
			if hasattr(Job, 'db'):
				Job.db['job_num'] += 1
				self.number = Job.db['job_num']
				# TODO:object does not save to shelve db when created.
				Job.db['jobs'][self.number] = self
		else:
			self.number = number
		self.alt_name = ""
		self.address = address
		self.start_date = start_date
		self.end_date = end_date
		self.gc = gc
		self.gc_contact = gc_contact
		self.scope = scope
		self.foreman = foreman
		self.workers = []
		self.materials = []
		self.po_pre = po_pre
		self.tax_exempt = tax_exempt
		self.certified_pay = certified_pay
		self._PO = 0  # stores most recent PO suffix number
		self.POs = {}  # stores PO strings as keys
		self.contract_amount = contract_amount
		self.tasks = {}
		self.desc = desc


		# Job.timesheets.key is datetime.datetime object
		# Job.timesheets.value is [ 'pathname/to/timesheet', hours ]
		self.timesheets = {}

		if rate is 'a':
			self.rate = Worker.A_RATE
		elif rate is 'b':
			self.rate = Worker.B_RATE
		self.start_date = None
		self.sub_path = sub_path

	@property
	def next_po(self):
		_po = self._PO
		self._PO += 1
		return _po

	@staticmethod
	def init_struct(self):
		""" Initializes project directory hierarchy. """
		##TODO:initialize documents w/ job information
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
		if hasattr(Todo, 'db'):
			return Todo.db['jobs'][num]


class MaterialList(object):
	lists = {}

	def __init__(self, job, items=None, foreman=None, date_sent=today(), date_due=None, comments="", doc=None):
		self.hash = abs(hash(str(now())))
		job.materials[self.hash] = (self)
		if hasattr(MaterialList, 'db'):
			MaterialList.db['materials'][self.hash] = self

		self.doc = doc
		self.job = job
		self.items = items
		self.foreman = foreman
		self.date_sent = date_sent
		self.date_due = date_due
		self.comments = comments
		self.quotes = []
		self.todo = True
		self.fulfilled = False

	def issue_po(self, quote, fulfills=False):
		return PO(self.job, quote=quote, fulfills=fulfills)


class Quotes(object):
	def __init__(self, mat_list, price=0.0, vend=None, doc=''):
		self.mat_list = mat_list
		self.mat_list.quotes.append(self)
		self.price = float(price)
		self.vend = str(vend)
		self.doc = str(doc)  # document target path/name


class PO(object):
	def __init__(self, job, date_issued=today(), fulfills=False,
	             mat_list=None, quote=None, desc=None, deliveries=None):
		num = job.nextPO()
		self.name = '-'.join([str(job.name), str(num)])
		self.job = job
		self.mat_list = mat_list
		if fulfills:
			self.mat_list.fulfilled = True
		self.quote = quote
		self.job.POs[self.name] = self
		self.date_issued = date_issued
		self.deliveries = deliveries  # stores initial delivery date
		self.backorders = None  # stores any backorder delivery dates
		self.desc = str(desc)


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
		self.hash = abs(hash(str(po.name)))
		if hasattr(Delivery, 'db'):
			Delivery.db['deliveries'][self.hash] = self
		self.delivered = False
		self.po = po
		if items is None:
			self.items = po.items
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

	# TODO:add __del__ descriptor to automatically remove instance from Todo.db

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