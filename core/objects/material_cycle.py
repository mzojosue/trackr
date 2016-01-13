import os
import traceback
from datetime import datetime

from core.log import logger
from core.parsing.po_log import add_po_to_log
from core.scheduler import scheduler

today = datetime.today
now = datetime.now


class MaterialList(object):
	# Class/Instance variables under watch by MaterialList._listener
	listeners = ('sent_out', 'po', 'delivered')
	_steps = ('send_out', 'assess_quotes', 'send_po', 'receive_delivery', 'complete')

	def __init__(self, job, items=None, doc=None, foreman=None, date_sent=today(), date_due=None, comments="", label="",
				 task=True, user=None):
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
		if doc:
			self.hash = abs(hash(str(doc)))  # hash attribute is derived from document title
		else:  # create _hash attribute if it doesn't exist
			self.hash = abs(hash(''.join([str(now()), os.urandom(4)])))

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
		self.fulfilled = False  # True once list has been purchased
		self.delivered = False  # True once order has been delivered
		self.delivery = None  # Stores Delivery object
		self.backorders = {}

		# TODO: set listener to delete todo object associated with sending self out to vendors
		self.sent_out = False  # Is set to true once list is given out for pricing
		self.po = None  # Stores PO object

		self.update()

	def __setattr__(self, key, value):
		# do not update yaml file or call self.update() if self is still initializing
		_caller = traceback.extract_stack(None, 2)[0][2]
		if _caller is not '__init__':
			self.update()
		_return = super(MaterialList, self).__setattr__(key, value)
		# TODO: automate Task completion via variable listeners
		# if key in MaterialList.listeners:
		#	self._listen(key, value)
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

	def __len__(self):
		try:
			return len(self.items)
		except TypeError:
			return 0

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
		if hasattr(self, '_doc') and self._doc:
			_path = os.path.join(self.job.path, 'Materials')
			return _path, self._doc
		else:
			return False

	@doc.setter
	def doc(self, val):
		if val:
			_path = os.path.join(self.job.path, 'Materials')
			_path = os.path.join(_path, val)
			if os.path.isfile(_path):
				self._doc = val
			else:
				print "Document doesn't exist"

	def update(self):
		if hasattr(self, 'hash') and hasattr(self, 'job'):
			self.job.add_mat_list(self)
		return None

	def upgrade_quote(self, quote, **kwargs):
		""" Creates a MaterialListQuote belonging to self from `quote`
		:quote: Quote object to convert
		:**kwargs: Arguments to be passed to MaterialListQuote.__init__
		:return:
		"""
		if type(quote) == Quote:
			# TODO: verify that quote.doc document file still exists

			q_obj = MaterialListQuote(mat_list=self, doc=quote.doc, **kwargs)
			return q_obj
		else:
			raise TypeError

	def add_quote(self, quote_obj):
		self.quotes[quote_obj.hash] = quote_obj
		self.sent_out = True  # update is called
		return None

	def del_quote(self, quote_obj):
		if type(quote_obj) != int:
			_hash = quote_obj.hash
		else:
			_hash = quote_obj
		del self.quotes[_hash]
		self.update()
		return None

	def add_po(self, po_obj):
		self.po = po_obj
		self.job.add_po(po_obj)
		self.fulfilled = True
		self.update()
		return None

	def del_po(self, po_obj):
		return NotImplemented

	def add_task(self, task_obj=None):
		self.tasks[task_obj.hash] = task_obj
		self.update()
		return None

	def del_task(self, task_hash):
		del self.tasks[task_hash]
		self.update()
		return None

	def add_delivery(self, deliv_obj):
		self.delivery = deliv_obj
		self.update()
		return None

	def add_rental(self, obj):
		# return unique object id
		return NotImplemented

	def issue_po(self, quote_obj, user=None):
		_obj = PO(self.job, quote=quote_obj, mat_list=self, user=user)
		quote_obj.awarded = True
		self.fulfilled = True
		self.sent_out = True
		return _obj

	def return_rental(self, obj_id):
		# return self.rentals[obj_id]
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


class Quote(object):
	def __init__(self, vend, price=0.0, date_uploaded=None, doc=None):
		self.vend = vend
		try:
			self._price = float(price)
		except (TypeError, ValueError):
			logger.warning("Error parsing price for Quote %s. Defaulted to $0.0" % self.hash)
			self._price = 0.0
		self._doc = doc

		if not date_uploaded:
			self.date_uploaded = now()
		else:
			self.date_uploaded = date_uploaded
		self.awarded = False

	@property
	def hash(self):
		if hasattr(self, 'doc') and self.doc:
			return abs(hash(str(self.doc)))  # hash attribute is derived from document filename
		elif not hasattr(self, '_hash'):  # create _hash attribute if it doesn't exist
			self._hash = abs(hash(''.join([str(now()), os.urandom(4)])))
		return self._hash

	@property
	def doc(self):
		if self.path and self._doc:
			return self.path, self._doc
		elif self._doc:  # self has no path
			return self._doc
		else:
			return False

	def __repr__(self):
		return "Quote from %s" % self.vend

	@property
	def path(self):
		if hasattr(self, 'job') and hasattr(self.job, 'path'):
			_path = os.path.join(self.job.path, 'Quotes')
			return _path
		elif hasattr(self, '_path'):
			_path = os.path.join(self._path, 'Quotes')
			return _path

		else:
			return False

	@property
	def price(self):
		return self._price

	@price.setter
	def price(self, value):
		self._price = float(value)
		if hasattr(self, 'update'):
			self.update()


class MaterialListQuote(Quote):
	def __init__(self, mat_list, vend, price=0.0, date_uploaded=None, doc=None):
		super(MaterialListQuote, self).__init__(vend, price, date_uploaded, doc)
		self.mat_list = mat_list
		self.job.add_quote(self)

		self.update()

	@property
	def job(self):
		return self.mat_list.job

	def __setattr__(self, key, value):
		_return = super(MaterialListQuote, self).__setattr__(key, value)

		# do not update yaml file if self is still initializing
		_caller = traceback.extract_stack(None, 2)[0][2]
		if _caller is not '__init__':
			# scheduler.add_job(update_po_in_log, args=[self, key, value])
			self.update()
		return _return

	def update(self):
		if hasattr(MaterialListQuote, 'db'):
			MaterialListQuote.db[self.hash] = self
			if hasattr(self, 'mat_list'):
				self.mat_list.add_quote(self)
		return None


class PO(object):
	def __init__(self, job, mat_list=None, quote=None,
				 date_issued=today(), desc=None, delivery=None, po_num=None, po_pre=None, update=True, user=None):
		if not po_num:
			self.number = job.next_po
		else:
			self.number = int(po_num)
		self.job = job
		self.mat_list = mat_list
		self.date_issued = date_issued
		self.quote = quote
		self.delivery = delivery  # stores initial delivery date
		self.backorders = []  # stores any backorder delivery dates
		self.desc = str(desc)
		self.user = user
		if po_pre:
			self.po_pre = str(po_pre)

		# update jobs object
		self.job.add_po(self)
		# update material list object
		self.mat_list.add_po(self)
		# update quote object
		self.quote.awarded = True

		if update:
			try:
				scheduler.add_job(add_po_to_log, args=[self, self.job.get_po_log()])
			except TypeError:
				logger.warning('There was an error adding PO to the log.')
				print "There was an error adding PO to log. Possibly no spreadsheet for jobs??"

	@property
	def name(self):
		_num = '%03d' % self.number
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
		self.quote.update()

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

	def __repr__(self):
		if self.mat_list.label:
			return '%s delivery for %s expected %s' % (self.mat_list.label, self.job, self.expected)
		elif len(self.mat_list):
			return 'Delivery for %s containing %d item(s)' % (self.job, len(self.mat_list))
		else:
			return 'Delivery for %s ordered by %s' % (self.job, self.mat_list.po.user)

	def __setattr__(self, key, value):
		_return = super(Delivery, self).__setattr__(key, value)
		if hasattr(Delivery, 'db'):
			Delivery.db[self.hash] = self
		if hasattr(self, 'jobs'):
			self.po.job.deliveries[self.hash] = self
			self.job.update()
		return _return

	@property
	def label(self):
		return self.__repr__()

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

	@property
	def timestamp(self):
		epoch = datetime(1969, 12, 31)  # why does this work???
		return (self.expected - epoch).total_seconds() * 1000
