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
		"""
		Initializes employee representation object.
		:param name: employee's name. hash/key is created from this variable.
		:param job: current job that employee is at. if changed, the previous job will be added to self.prev_jobs
		:param phone: listed phone number for employee
		:param email: listed email address
		:param role: worker's role on the jobsite. ie: foreman, installer/mechanic, pipe fitter, etc
		:param rate: pay rate for employee. can be arbitrary value
		"""
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

		self.timesheets = []    # list that includes timesheet hashes that worker has been at


	def __setattr__(self, name, value):
		""" Alters attribute setting to listen to when self.job is changed,
			the previous job is stored in self.prev_jobs
		"""
		if name is 'job':
			value.add_worker(self)
			try:
				self.prev_jobs.append(self.job)
				del self.job.workers[self.name]
				self.job.update()
			except AttributeError:
				pass

		_return = super(Worker, self).__setattr__(name, value)
		self.update()
		return _return

	def __repr__(self):
		"""
		:return: describes object by self.name, self.role, and self.job.name
		"""
		# TODO:update output format
		# TODO:return date since working at job
		return "\"%s\". %s at %s" % (self.name, self.role, self.job.name)

	@staticmethod
	def find(q_hash):
		"""

		:param q_hash: hash to query database for
		:return: returns worker object that matches description
		"""
		if hasattr(Todo, 'db'):
			return Todo.db[q_hash]

	def update(self):
		"""
		Function re-initializes self.hash as the dictionary key pointed to self. Also adds itself to self.job.workers.
		:return: None
		"""
		if hasattr(Worker, 'db') and hasattr(self, 'hash'):
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
		"""
		:param job_num: desired job number
		:param name: primary job name
		:param start_date: planned job start date
		:param end_date: planned job completion date
		:param alt_name: secondary name/nickname for job
		:param po_pre: desired po prefix. defaults to job name
		:param address: listed address for jobsite
		:param gc: listed general contractor
		:param gc_contact: listed general contractor contact
		:param scope: scope of work. ie: full-airside, fabrication only, etc
		:param foreman: listed sheet metal foreman on job
		:param desc: short description of scope of work
		:param rate: default rate for workers on jobsite
		:param contract_amount: listed contract amount for job completion. job completion percentage is based off of this.
		:param tax_exempt: Boolean. True if job is tax exempt
		:param certified_pay: Boolean. True is job is a certified payroll job
		:param sub_path: The directory sub path for the job
		"""
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
				_folders = ('Addendums', 'Billing', 'Change Orders', 'Close Out', 'Contract Scope', 'Documents',
				            'Drawings', 'Materials', 'Quotes', 'RFIs', 'Specs', 'Submittals')
				for _folder in _folders:
					os.mkdir(os.path.join(self.sub_path, _folder))
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
		# Job.timesheets.key is datetime.datetime object for the week-ending
		# Job.timesheets.value is [ 'pathname/to/timesheet', { worker.hash: (worker, hours) } ]
		self.timesheets = {}

	def update(self):
		if hasattr(Job, 'db'):
			Job.db[self.number] = self

	def __setattr__(self, key, value):
		_return = super(Job, self).__setattr__(key, value)
		self.update()
		return _return

	def __repr__(self):
		return self.name

	@property
	def name(self):
		return '-'.join([str(self.number), str(self._name)])

	@property
	def next_po(self):
		"""
		Optimizes PO# usage by ensuring that all PO numbers are used, and none are skipped.
		:return: returns claimed PO number
		"""
		_keys = self.POs.keys()
		_k_len = len(_keys)

		if _k_len:
			# calculate ideal sum of continuous sequence of equal length
			_ideal_seq_sum = (_k_len/2) * (0 + (_k_len - 1))

			# calculate the real sum of existing po# sequence
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
		""" Shows formatted PO# that's available next.
		:return: returns the formatted value of the next available PO for considering it being given to a vendor
		"""
		_po = self._PO
		_po = '%03d' % _po        # add padding to PO #
		return '-'.join([self.name, _po])

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
		""" Calculates job cost total/progress taking into account materials purchased and labor paid.
		:returns: float for projected cost.
		"""
		amt = 0.0
		for i in self.timesheets.itervalues():
			amt += (float(i[1]) * float(self.rate))
		for i in self.POs.itervalues():
			amt += i.quote.price
		return amt

	@property
	def has_open_lists(self):
		"""
		Returns 0 if job has no open material lists
		:return: Integer of material lists that have not been purchased.
		"""
		open_lists = 0
		for mlist in self.materials.itervalues():
			if not mlist.fulfilled:
				open_lists += 1
		return open_lists

	@staticmethod
	def find(num):
		if hasattr(Job, 'db'):
			return Job.db[num]

	def add_task(self, task_obj):
		"""
		Blindly adds task object to self
		:param task_obj: task object to add to self.tasks
		:return: None
		"""
		self.tasks[task_obj.hash] = task_obj
		self.update()
		return None

	def add_mat_list(self, mlist_obj):
		"""
		Blindly adds material list object to self.
		:param mlist_obj: material list object to add to self
		:return: None
		"""
		self.materials[mlist_obj.hash] = mlist_obj
		self.update()
		return None

	def add_quote(self, quote_obj):
		"""
		Blindly adds quote object to self.
		:param quote_obj: quote object to add to self
		:return: None
		"""
		self.quotes[quote_obj.hash] = quote_obj
		self.materials[quote_obj.mat_list.hash].add_quote(quote_obj)
		self.update()
		return None

	def add_delivery(self, deliv_obj):
		"""
		Blindly adds delivery object to self.
		:param deliv_obj: delivery object to add to self
		:return: None
		"""
		self.deliveries[deliv_obj.hash] = deliv_obj
		self.update()
		return None

	def add_po(self, po_obj):
		"""
		Blindly adds PO object to self.
		:param po_obj: PO object to add to self.
		:return: None
		"""
		self.POs[po_obj.num] = po_obj
		self.update()
		return None

	def add_worker(self, wrkr_obj):
		"""
		Blindly adds worker object to self.
		:param wrkr_obj: Worker object to add to self
		:return: None
		"""
		self.workers[wrkr_obj.hash] = wrkr_obj
		self.update()

	def del_material_list(self, mlist_hash, delete=False):
		"""
		Deletes material list object from self.materials
		:param mlist_hash: hash to delete from self.materials
		:param delete: if True is passed, then the document is deleted from the filesystem
		:return: None
		"""
		del self.materials[mlist_hash]
		if delete:
			# TODO:delete document in filesystem
			pass
		self.update()
		return None

	def del_quote(self, quote_hash, delete=False):
		"""
		Deletes quote object from self.quotes
		:param quote_hash: hash to delete from self.quotes
		:param delete: if True is passed, then the document is deleted from the filesystem
		:return: None
		"""
		del self.quotes[quote_hash]
		if delete:
			# TODO:delete document in filesystem
			pass
		self.update()
		return None

	def del_task(self, task_hash):
		"""
		Delete task object from self.tasks
		:param task_hash: hash of task object to delete from internal db
		:return: None
		"""
		del self.tasks[task_hash]
		self.update()
		return None


class MaterialList(object):
	# Class/Instance variables under watch by MaterialList._listener
	listeners = ('sent_out', 'po', 'delivered')
	_steps = ('send_out', 'assess_quotes', 'send_po', 'receive_delivery', 'complete')

	def __init__(self, job, items=None, doc=None, foreman=None, date_sent=today(), date_due=None, comments="", label="", task=True):
		"""
		Initializes a representational object for a material list document.
		:param job: Job that material list is for
		:param items: A quantity/item tuple for items on the material list.
		:param doc: Document location in filesystem
		:param foreman: Foreman/worker who requested list
		:param date_sent: Date that material list was sent/uploaded
		:param date_due: Date that the material list was requested
		:param comments: Comments that foreman gave on material list
		:param label: Human readable label for material list
		:param task: Boolean. If True, SHOULD create a Todo object linked to self
		:return: None
		"""
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
		self.tasks = {}
		self.rentals = {}
		self.job.add_mat_list(self)
		self.fulfilled = False  # True once list has been purchased
		self.delivered = False  # True once order has been delivered
		self.delivery = None    # Stores Delivery object

		# TODO:set listener to delete todo object associated with sending self out to vendors
		self.sent_out = False   # Is set to true once list is given out for pricing
		self.po = None


	def __setattr__(self, key, value):
		_return = super(MaterialList, self).__setattr__(key, value)
		if key in MaterialList.listeners:
			self._listen(key, value)
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
		"""
		Used for highlighting unfulfilled material lists when displayed in a table.
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
		if type(self._doc) is not str:
			try:
				return (os.path.join( ENV_ROOT, self._doc[0] ), self._doc[1])
			except TypeError:
				pass
		elif self._doc:
			return (os.path.join(self.job.sub_path, 'Materials'), self._doc)
		else:
			return False

	def update(self):
		if hasattr(MaterialList, 'db'):
			MaterialList.db[self.hash] = self
			if hasattr(self, 'job'):
				self.job.add_mat_list(self)
		return None

	def add_quote(self, quote_obj):
		self.quotes[quote_obj.hash] = quote_obj
		self.sent_out = True
		self.update()
		return None

	def add_po(self, po_obj):
		self.po = po_obj
		self.fulfilled = True
		self.update()
		return None

	def add_task(self, task_obj=None):
		self.tasks[task_obj.hash] = task_obj
		self.update()
		return None

	def add_delivery(self, deliv_obj):
		self.delivery = deliv_obj
		self.update()
		return None

	def add_rental(self, obj):
		# return unique object id
		return NotImplemented

	def del_quote(self, quote_obj):
		del self.quotes[quote_obj.hash]
		self.update()
		return None

	def del_task(self, task_hash):
		del self.tasks[task_hash]
		self.update()
		return None

	def issue_po(self, quote_obj):
		quote_obj.awarded = True
		self.fulfilled = True
		self.sent_out = True
		_obj = PO(self.job, quote=quote_obj, mat_list=self)
		self.update()
		return _obj

	def return_rental(self, obj_id):
		#return self.rentals[obj_id]
		return NotImplemented

	def _listen(self, key, value):
		""" Listens for changes in variables. Performs actions when changes are made to certain variables.
		THIS FUNCTION IS NOT RESPONSIBLE FOR SETTING THE VALUE TO VARIABLES
		:param key: variable name to check
		:param value: variable value to work with
		:return: None
		"""
		if key is 'sent_out':
			try:
				# Call _Todo.complete() on object that matches metadata
				for t in self.tasks.itervalues():
					if t.metadata == 'listen::sent_out':
						t.complete(command=False)
			except RuntimeError:
				# Error should be raised since we are deleting an iterable
				pass
		return None

	@staticmethod
	def find(mlist_hash):
		if hasattr(MaterialList, 'db'):
			return MaterialList.db[int(mlist_hash)]


class Quotes(object):
	def __init__(self, mat_list, price=0.0, vend='unknown vendor', doc=None):
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
			self.num = job.next_po()
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
		self.job.lladd_po(self)
		# update material list object
		self.mat_list.add_po(self)
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
	def __init__(self, mat_list, expected=None, destination='shop'):

		# TODO:add object to job.deliveries

		self.hash = abs(hash(str(mat_list)))
		self.mat_list = mat_list
		self.delivered = False
		self.expected = expected
		self.destination = self.job.address

		self.job.add_delivery(self)
		self.mat_list.fulfilled = True
		self.mat_list.add_delivery(self)

	@staticmethod
	def find(q_hash):
		if hasattr(Delivery, 'db'):
			return Delivery.db[q_hash]

	def __setattr__(self, key, value):
		_return = super(Delivery, self).__setattr__(key, value)
		if hasattr(Delivery, 'db'):
			Delivery.db[self.hash] = self
		if hasattr(self, 'job'):
			self.po.job.deliveries[self.hash] = self
			self.job.update()
		return _return

	@property
	def job(self):
		return self.mat_list.job

	@property
	def po(self):
		return self.mat_list.po

	@property
	def vend(self):
		return self.po.quote.vend

	@property
	def countdown(self):
		return (self.expected - today()).days


class Todo(object):
	""" Represents tasks to-do
	:param
		name:   the name of the task
		task:   text description of the task. may include link
		due:    task due date
		notif:  date/time to follow-up
	"""

	def __init__(self, name, job=None, task="", due=None, notify=None, target=None, command=None, metadata=None):
		self.name = str(name)
		self.hash = abs(hash(self.name))  # ensure positive values

		if job:
			self.job = job
		if self.job:
			self.job.add_task(self)
		self.task = task
		self.due = due
		self.notify = notify
		if target:
			self.target = target
		if command:
			self.command = str(command)
		self.metadata = metadata

	def complete(self, command=True):
		if hasattr(Todo, 'db') and hasattr(Todo, 'completed_db'):
			Todo.completed_db[self.hash] = self
			try:
				del Todo.db[self.hash]
				print "deleted task from Todo.db"
			except KeyError:
				if Todo.completed_db[self.hash]:
					# assume partially deleted object
					print "object already in db"
					pass
				else:
					raise KeyError
		if hasattr(self, 'job'):
			try:
				self.job.del_task(self.hash)
				print "deleted task from job.tasks"
			except KeyError:
				# assume partially deleted object
				pass
		if hasattr(self, 'target') and hasattr(self.target, 'tasks'):
			try:
				self.target.del_task(self.hash)
				print "deleted task from target.tasks"
			except KeyError:
				# assume partially delted list
				pass
		if command and hasattr(self, 'command'):
			exec(compile(self.command, '', 'exec'))
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
		self.update()
		return _return

	def update(self):
		if hasattr(Todo, 'db') and hasattr(self, 'hash'):
			Todo.db[self.hash] = self
		if hasattr(self, 'job'):
			self.job.add_task(self)
		if hasattr(self, 'target'):
			self.target.add_task(self)


class InventoryItem(object):
	def __init__(self, item_id, item_label, stock=None):

		self.hash = abs(hash(str(item_id)))

		self.item_id = item_id
		self.item_label = item_label

		self.orders = {}  # keys: order datetime. value:order objects

		if hasattr(InventoryItem, 'db'):
			InventoryItem.db[self.hash] = self

	@property
	def stock(self):
		_qty = float()
		for i in self.orders.itervalues():
			_qty += i.quantity
		return str(_qty)

	def __setattr__(self, key, value):
		_return = super(InventoryItem, self).__setattr__(key, value)
		self.update()
		return _return

	def update(self):
		if hasattr(InventoryItem, 'db'):
			InventoryItem.db[self.hash] = self
		return None

	@staticmethod
	def find(query):
		try:
			if hasattr(InventoryItem, 'db'):
				return InventoryItem.db[int(query)]
		except KeyError:
			return False


class InventoryOrder(object):
	def __init__(self, item, price=0.0, vend=None, quantity=0, date_ordered=today(), po=None):

		self.hash = abs(hash(''.join([item.item_label, str(price), str(date_ordered)])))

		self.item = item
		self.price = price
		self.vend = vend
		self.quantity = float(quantity)
		self.date_ordered = date_ordered
		self.item.orders[self.hash] = self
		if po:
			self.po = po

		if hasattr(InventoryOrder, 'db'):
			InventoryOrder.db[self.hash] = self

	def __setattr__(self, key, value):
		_return = super(InventoryOrder, self).__setattr__(key, value)
		self.update()
		return _return

	def update(self):
		if hasattr(InventoryOrder, 'db'):
			InventoryOrder.db[self.hash] = self
		if hasattr(self, 'item'):
			self.item.orders[self.hash] = self
			self.item.update()
		return None

	@staticmethod
	def find(query):
		try:
			if hasattr(InventoryOrder, 'db'):
				return InventoryOrder.db[int(query)]
		except KeyError:
			return False


class Timesheet(object):
	def __init__(self, job, start_date=None, end_date=None, doc=None, timesheet=dict()):
		self.hash = abs(hash(''.join([str(job.number), str(start_date), str(end_date)])))
		self.job = job
		self.start_date = start_date
		self.end_date = end_date
		self.doc = doc

		# self.timesheet.key is worker.hash
		# self.timesheet.value is list of dates worked and hours
		self.timesheet = timesheet

	@property
	def hours(self):
		"""
		:return: total amount of hours as float
		"""
		_hrs = 0.0
		for _work in self.timesheet.itervalues():
			_hrs += float(_work[1])
		return _hrs

	def __setattr__(self, key, value):
		_return = super(Timesheet, self).__setattr__(key, value)
		self.update()
		return _return

	def __repr__(self):
		if not self.end_date:
			return "%d hours worked at %s. Dates unknown." % (self.hours, self.job)
		else:
			return "%d hours worked at %s for week ending %s" % (self.hours, self.job, self.end_date)

	def add_labor(self, worker, date_worked, hours):
		if hasattr(worker, 'hash'):
			if worker.hash in self.timesheet:
				self.timesheet[worker.hash].append([date_worked, float(hours)])
			else:
				self.timesheet[worker.hash] = [date_worked, float(hours)]
			if not self.hash in worker.timesheets:
				worker.timesheets.append(self.hash)
				worker.update()

	def update(self):
		if hasattr(Timesheet, 'db'):
			Timesheet.db[self.hash] = self
		if hasattr(self, 'job'):
			self.job.timesheets[self.hash] = self
			self.job.update()

	def bodies_on_field(self):
		return len(self.timesheet)


def get_job_num(*args):
	try:
		if hasattr(Job, 'db'):
			_keys = Job.db.keys()
			num = int(_keys[-1]) + 1
			return num
	except IndexError:
		print "Unknown Error:: Probably no jobs"
		return 1