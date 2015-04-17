from objects import *
from core.environment import *
from core.parsing import add_po_in_log, update_po_in_log


class MaterialList(object):
	# Class/Instance variables under watch by MaterialList._listener
	listeners = ('sent_out', 'po', 'delivered')
	_steps = ('send_out', 'assess_quotes', 'send_po', 'receive_delivery', 'complete')

	def __init__(self, job, items=None, doc=None, foreman=None, date_sent=today(), date_due=None, comments="", label="", task=True):
		"""
		Initializes a representational object for a material list document.
		:param job: AwardedJob that material list is for
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
		self.hash = abs(hash( ''.join([ str(now()), os.urandom(4)]) ))

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
		update_po_in_log(self, key, value)
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
		if type(self._doc) is tuple:
			_path = os.path.join(self.job.path, self._doc[0])
			return (_path, self._doc[1])
		elif type(self._doc) is str:
			_path = os.path.join(self.job.path, 'Materials')
			return (_path, self._doc)
		return False

	def update(self):
		if hasattr(MaterialList, 'db'):
			MaterialList.db[self.hash] = self
			if hasattr(self, 'jobs'):
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


class Quote(object):
	def __init__(self, vend, price=0.0, date_uploaded=None, doc=None):
		self.hash = abs(hash( ''.join([ str(now()), os.urandom(4)]) ))
		self.vend = vend
		try:
			self.price = float(price)
		except ValueError:
			print "Error parsing price, %s. Defaulted to 0.0" % price
			self.price = 0.0
		self._doc = doc

		if not date_uploaded:
			self.date_uploaded = now()
		else:
			self.date_uploaded = date_uploaded
		self.awarded = False

	@property
	def doc(self):
		if type(self._doc) is tuple:
			_path = os.path.join(self.job.path, self._doc[0])
			return (_path, self._doc[1])
		elif type(self._doc) is str:
			return (self.path, self._doc)
		return False

	def __repr__(self):
		return "Quote from %s" % self.vend

	def update(self):
		return NotImplemented

	@property
	def path(self):
		_path = os.path.join(self.job.path, 'Quotes')
		return _path


class MaterialListQuote(Quote):
	def __init__(self, mat_list, vend, price=0.0, date_uploaded=None, doc=None):
		super(MaterialListQuote, self).__init__(vend, price, date_uploaded, doc)
		self.mat_list = mat_list
		self.mat_list.job.add_quote(self)

	@property
	def job(self):
		return self.mat_list.job

	def __setattr__(self, key, value):
		_return = super(MaterialListQuote, self).__setattr__(key, value)
		if hasattr(self, 'mat_list'):
			self.mat_list.add_quote(self)
		update_po_in_log(self, key, value)
		return _return

	def update(self):
		if hasattr(MaterialListQuote, 'db'):
			MaterialListQuote.db[self.hash] = self
			if hasattr(self, 'mat_list'):
				self.mat_list.add_quote(self)
		return None


class PO(object):
	def __init__(self, job, mat_list=None, date_issued=today(),
	             quote=None, desc=None, deliveries=None, po_num=None, po_pre=None, update=True):
		if not po_num:
			self.num = job.next_po
		else:
			self.num = int(po_num)
		self.job = job
		self.mat_list = mat_list
		self.date_issued = date_issued
		self.quote = quote
		self.deliveries = deliveries  # stores initial delivery date
		self.backorders = []          # stores any backorder delivery dates
		self.desc = str(desc)
		if po_pre:
			self.po_pre = str(po_pre)

		# update jobs object
		self.job.add_po(self)
		# update material list object
		self.mat_list.add_po(self)
		# update quote object
		self.quote.awarded = True
		self.quote.update()

		if update:
			try:
				add_po_in_log(self)
			except TypeError:
				print "There was an error adding PO to log. Possibly no spreadsheet for jobs??"

	@property
	def name(self):
		_num = '%03d' % self.num
		if hasattr(self, 'po_pre'):
			return '-'.join([str(self.po_pre), _num])
		else:
			return '-'.join([str(self.job.po_pre), _num])

	@property
	def vend(self):
		return self.quote.vend

	@property
	def price(self):
		return self.quote.price

	@price.setter
	def price(self, value):
		self.quote.price = value


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

		# TODO:add object to jobs.deliveries

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
		if hasattr(self, 'jobs'):
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