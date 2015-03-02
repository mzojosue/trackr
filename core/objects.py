import os
from datetime import datetime

today = datetime.today
now = datetime.now

ENV_ROOT = "//SERVER/Documents/Esposito"


class Worker(object):
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

		_return = super(Worker, self).__setattr__(name, value)
		self.update()
		return _return

	def __repr__(self):
		# TODO:update output format
		# TODO:return date since working at job
		return "\"%s\". %s at %s" % (self.name, self.role, self.job.name)

	@staticmethod
	def find(q_hash):
		if hasattr(Todo, 'db'):
			return Todo.db[q_hash]

	def update(self):
		if hasattr(Worker, 'db'):
			Worker.db[self.hash] = self
			if hasattr(self, 'job'):
				self.job.add_worker(self)
		return None


class Job(object):
	jobs = {}

	default_sub_dir = "//SERVER/Documents/Esposito/Jobs"

	def __init__(self, job_num, name, start_date=None, end_date=None, alt_name=None, po_pre=None, address=None,
	             gc=None, gc_contact=None, scope=None, foreman=None, desc=None, rate='a',
	             contract_amount=None, tax_exempt=False, certified_pay=False, sub_path=None):
		# TODO:implement better document storage

		self.number = int(job_num)
		self._name = str(name)
		self.start_date = start_date
		self.end_date = end_date
		self.alt_name = alt_name
		if po_pre:
			self.po_pre = po_pre
		else:
			self.po_pre = self.name
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
				os.mkdir(os.path.join(self.sub_path, 'materials'))
				os.mkdir(os.path.join(self.sub_path, 'quotes'))
				os.mkdir(os.path.join(self.sub_path, 'drawings'))
				os.mkdir(os.path.join(self.sub_path, 'specs'))
				os.mkdir(os.path.join(self.sub_path, 'addendums'))
				os.mkdir(os.path.join(self.sub_path, 'submittals'))
			else:
				self.sub_path = os.path.join(Job.default_sub_dir, self.name)
		except OSError:
			print "ERROR: cannot connect to server. File functions disabled.\n"

		self._PO = 0    # stores most recent PO suffix number
		self.POs = {}   # stores PO strings as keys
		self.workers = {}
		self.materials = {}
		self.quotes = {}
		self.deliveries = {}
		self.tasks = {}
		# Job.timesheets.key is datetime.datetime object
		# Job.timesheets.value is [ 'pathname/to/timesheet', hours ]
		self.timesheets = {}

	def update(self):
		if hasattr(Job, 'db'):
			Job.db[self.number] = self

	def __setattr__(self, key, value):
		_return = super(Job, self).__setattr__(key, value)
		self.update()
		return _return

	@property
	def name(self):
		return '-'.join([str(self.number), str(self._name)])

	@property
	def next_po(self):
		_keys = self.POs.keys()
		_k_len = len(_keys)

		if _k_len:
			# calculate ideal sum of continuous sequence of equal length
			_ideal_seq_sum = (_k_len/2) * (0 + (_k_len - 1))

			# calculate the sum of existing po# sequence
			_seq_sum = (_k_len/2) * (_keys[0] - _keys[-1])

			# check to see if current sequence is continuous
			if not (int(_seq_sum) == int(_ideal_seq_sum)):
				#find the smallest integer to begin to complete the sequence.
				_new_PO = 0  # start search @ 0
				while True:
					if _new_PO not in _keys:
						self._PO = _new_PO
						break
					else:
						_new_PO += 1
			else:
				self._PO = _keys[-1] + 1
		return self._PO

	@property
	def show_po(self):
		""" Used for showing what PO# is available next.
		:return: returns the formatted value of the next available PO for considering it being given to a vendor
		"""
		_po = self.next_po
		_po = '%03d' % _po        # add padding to PO #
		return '-'.join([self.name, _po])

	def claim_po(self):
		""" Used for storing a PO number with a quote and sending it a vendor
		:return: returns unformatted PO number
		"""

		return self.next_po

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
			return Job.db[num]

	def add_task(self, task_obj):
		self.tasks[task_obj.hash] = task_obj
		self.update()
		return None

	def add_mat_list(self, mlist_obj):
		self.materials[mlist_obj.hash] = mlist_obj
		self.update()
		return None

	def add_quote(self, quote_obj):
		self.materials[quote_obj.mat_list.hash].add_quote(quote_obj)
		self.quotes[quote_obj.hash] = quote_obj
		self.update()
		return None

	def add_po(self, po_obj):

		# TODO:optimize the use of PO numbers

		self.POs[po_obj.num] = po_obj
		if not (self._PO+1 < po_obj.num):
			self._PO = po_obj.num
		self.update()
		return None

	def add_worker(self, wrkr_obj):
		self.workers[wrkr_obj.hash] = wrkr_obj

	def del_material_list(self, mlist_hash):
		del self.materials[mlist_hash]
		# TODO:delete document in filesystem
		self.update()
		return None

	def del_quote(self, quote_hash):
		del self.quotes[quote_hash]
		self.update()
		return None


class MaterialList(object):
	def __init__(self, job, items=None, doc=None, foreman=None, date_sent=today(), date_due=None, comments="", label=""):
		self.hash = abs(hash(str(now())))


		self.job = job
		self.items = items
		self._doc = doc
		if not foreman:
			self.foreman = self.job.foreman
		else:
			self.foreman = foreman
		self.date_sent = date_sent
		self.date_due = date_due
		self.label = label
		self.comments = comments

		self.quotes = {}
		# TODO:append MaterialList to task list
		self.todo = True
		if self.age < 5:
			_msg = "Send out list for %s to vendors" % self.job.name
			self.task = Todo(_msg, self.job)
		self.job.add_mat_list(self)
		self.fulfilled = False  # True once list has been purchased
		self.delivered = False  # True once order has been delivered
		self.sent_out = False   # Is set to true once list is given out for pricing
		self.po = None


	def __setattr__(self, key, value):
		_return = super(MaterialList, self).__setattr__(key, value)
		self.update()
		return _return

	def __repr__(self):
		if hasattr(self.date_sent, 'date'):
			dt = self.date_sent.date()
		else:
			dt = self.date_sent
		if len(self.label):
			return '"%s" from %s' % (self.label, dt)
		else:
			return "List from %s @ %s, from %s" % (self.foreman, self.job.name, dt)

	@property
	def age(self):
		""" Used for highlighting unfulfilled material lists when displayed in a table.
		:return: days since material list was received. If fulfilled, returns False.
		"""
		try:
			if self.date_due:
				return (self.date_due - today()).days
			else:
				return (today().date() - self.date_sent).days
		except TypeError:
			# `self.date_sent` is assumed to be 0
			return 0

	@property
	def doc(self):
		if self._doc:
			return (os.path.join( ENV_ROOT, self._doc[0] ), self._doc[1])
		return False

	def update(self):
		if hasattr(MaterialList, 'db'):
			MaterialList.db[self.hash] = self
			if hasattr(self, 'job'):
				self.job.add_mat_list(self)
		return None

	def add_quote(self, quote_obj):
		self.quotes[quote_obj.hash] = quote_obj
		MaterialList.db[self.hash] = self
		return None

	def del_quote(self, quote_obj):
		del self.quotes[quote_obj.hash]
		self.update()
		return None

	def issue_po(self, quote_obj):
		quote_obj.awarded = True
		self.fulfilled = True
		_obj = PO(self.job, quote=quote_obj, mat_list=self)
		return _obj

	def add_po(self, po_obj):
		self.po = po_obj
		self.update()
		return None


class Quotes(object):
	def __init__(self, mat_list, price=0.0, vend=None, doc=None):
		self.hash = abs(hash(now()))
		self.mat_list = mat_list
		try:
			self.price = float(price)
		except ValueError:
			self.price = 0.0
		self.vend = vend
		self._doc = doc  # document target path/name
		self.date_recvd = today()
		self.awarded = False
		self.mat_list.job.add_quote(self)

	def __setattr__(self, key, value):
		_return = super(Quotes, self).__setattr__(key, value)
		if hasattr(self, 'mat_list'):
			self.mat_list.add_quote(self)
		return _return

	def __repr__(self):
		return "Quote from %s for %s" % (self.vend, self.mat_list)

	@property
	def doc(self):
		if self._doc:
			return (os.path.join( ENV_ROOT, self._doc[0] ), self._doc[1])
		return False

	def update(self):
		if hasattr(Quotes, 'db'):
			Quotes.db[self.hash] = self
			if hasattr(self, 'mat_list'):
				self.mat_list.add_quote(self)
		return None


class PO(object):
	def __init__(self, job, mat_list=None, date_issued=today(),
	             quote=None, desc=None, deliveries=None, po_num=None, po_pre=None):
		if not po_num:
			self.num = job.claim_po()
		else:
			self.num = int(po_num)
		self.job = job
		self.mat_list = mat_list
		self.date_issued = date_issued
		self.quote = quote
		self.deliveries = deliveries  # stores initial delivery date
		self.desc = str(desc)
		self.deliveries = []
		if po_pre:
			self.po_pre = str(po_pre)

		self.backorders = None  # stores any backorder delivery dates

		# update job object
		self.job.add_po(self)
		# update material list object
		self.mat_list.add_po(self)
		self.mat_list.fulfilled = True
		if hasattr(self.mat_list, 'task'):
			self.mat_list.task.complete()
		self.mat_list.update()
		# update quote object
		self.quote.awarded = True
		self.quote.update()

	@property
	def name(self):
		_num = '%03d' % self.num
		if hasattr(self, 'po_pre'):
			return '-'.join([str(self.po_pre), _num])
		else:
			return '-'.join([str(self.job.po_pre), _num])

	def __repr__(self):
		return self.name


class Vendor(object):
	def __init__(self):
		pass


class Delivery(object):
	""" Represents a future delivery.
	:param
		po:     pointer to PO object
	"""
	def __init__(self, po, items=None, expected=None, destination='shop'):

		# TODO:add object to job.deliveries

		self.po = po
		del po
		self.hash = abs(hash(str(self.po.name)))
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
		if hasattr(Delivery, 'db'):
			return Delivery.db[q_hash]

	def __setattr__(self, key, value):
		_return = super(Delivery, self).__setattr__(key, value)
		if hasattr(Delivery, 'db'):
			Delivery.db[self.hash] = self
		return _return


class Todo(object):
	""" Represents tasks to-do
	:param
		name:   the name of the task
		task:   text description of the task. may include link
		due:    task due date
		notif:  date/time to follow-up
	"""

	def __init__(self, name, job=None, task="", due=None, notify=None):
		self.name = str(name)
		self.hash = abs(hash(self.name))  # ensure positive values

		self.job = job
		if self.job:
			self.job.add_task(self)
		self.task = task
		self.due = due
		self.notify = notify

	def complete(self):
		if hasattr(Todo, 'db') and hasattr(Todo, 'completed_db'):
			Todo.completed_db[self.hash] = self
			try:
				del Todo.db[self.hash]
			except KeyError:
				# assume that the task has been partially deleted
				pass
		if hasattr(self, 'job'):
			try:
				del self.job.tasks[self.hash]
				self.job.update()
			except KeyError:
				# assume that the task has been partially deleted
				pass
		return True

	@staticmethod
	def find(q_hash):
		if hasattr(Todo, 'db') and hasattr(Todo, 'completed_db'):
			try:
				return Todo.db[q_hash]
			except KeyError:
				return Todo.completed_db[q_hash]
		else:
			# TODO:create exception class
			raise BaseException

	def __setattr__(self, key, value):
		_return = super(Todo, self).__setattr__(key, value)
		if hasattr(Todo, 'db') and hasattr(self, 'hash'):
			Todo.db[self.hash] = self
		if hasattr(self, 'job'):
			self.job.add_task(self)
		return _return


def get_job_num(*args):
	try:
		if hasattr(Job, 'db'):
			_keys = Job.db.keys()
			num = int(_keys[-1]) + 1
			return num
	except IndexError:
		print "Unknown Error:: Probably no jobs"
		return 1