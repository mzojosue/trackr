import core as env
from objects import *
from operator import itemgetter
from datetime import datetime

today = datetime.today

# Import parent classes for estimating objects
from job import Job
from material_cycle import Quote


class EstimatingJob(Job):
	default_sub_dir = 'Preconstruction'

	def __init__(self, name, job_num=None, alt_name=None, date_received=today(), date_end=None,
	             address=None, gc=None, gc_contact=None, rebid=False, scope=None, desc=None, rate='a',
	             tax_exempt=False, certified_pay=False, sub_path=None, group=False, completed=False):
		"""
		:param name: The desired name for the bid
		:param job_num: desired jobs number. if specified and a bid already exists, passed number is ignored.
		:param alt_name: the desired alternative name
		:param date_received: date that bid was received
		:param date_end: bid due date
		:param address: supplied address for jobs
		:param gc: general contractor that jobs is bid to
		:param gc_contact: gc contact email or Contact object
		:param scope: iterable containing scope of jobs
		:param desc: given description for jobs
		:param rate: given pay-rate for jobs
		:param tax_exempt: boolean that represents tax exemption status
		:param certified_pay: boolean that represents certified payroll status
		:param sub_path: if specified, and exists, is stored as the directory path for object
		:param group: variable that is either point ed to a sister object, a tuple of objects, a group str label, or a tuple of labels.
		"""
		if not job_num:
			self.number = self.get_bid_num()
		else:
			self.number = job_num

		# hash is used to keep bid unique
		self.hash = abs(hash(''.join([str(now()), os.urandom(4)])))

		super(EstimatingJob, self).__init__(name, date_received=date_received, alt_name=alt_name,
		                                    address=address, scope=scope, desc=desc, rate=rate,
		                                    tax_exempt=tax_exempt, certified_pay=certified_pay, completed=completed)
		self.quotes = {}

		# TODO: implement document/drawing storage
		self.docs = {}
		self.takeoff = {}  # stores dict of takeoff document paths stored as PDF. dict key is the md5 hash of file

		self.sub_path = os.path.join(self.default_sub_dir, self.name)
		# TODO:prevent directory structure from being created twice
		self.init_struct()

		for i in self.scope:
			# create sub-dictionaries for storing quotes by category/trade
			self.quotes[i] = {}
		self.bids = {}  # Stores previous bids. Stores self as first bid
		self.add_bid(date_received, gc, date_end, gc_contact)

		# False if jobs is not rebid. Rebid is defined by a bid that is shares the same name but differs in due date
		# Variable is pointed to object that is being rebid
		_rebid = self.find_rebid()
		if not rebid and _rebid and hasattr(_rebid, 'hash') and (_rebid.hash != self.hash):
			self.rebid = _rebid
		else:
			self.rebid = rebid

		# TODO: implement grouping system
		self.group = group

		self.load_info()

	@property
	def name(self):
		if hasattr(self, 'number'):
			return 'E%d-%s' % (self.number, self._name)


	@property
	def bid_date(self):
		""" finds and returns most recently due bid date """
		return sorted(self.bids.values(), key=itemgetter('bid_date'))[0]['bid_date']


	@property
	def countdown(self):
		"""
		:return: formatted string of countdown in days until bid is due
		"""
		_bid_date = self.bid_date
		if type(_bid_date) is datetime:
			_days = (_bid_date - today()).days
			if _days > 0:
				return 'Due in %s days' % _days
			elif _days < 0:
				return 'Was due %s days ago' % _days
			else:
				return 'Bid is due today'
		else:
			return 'Bid Due ASAP'


	@property
	def bid_timestamp(self):
		""" Returns the bid due date as a millisecond timestamp ready to be displayed on calendar """
		try:
			epoch = datetime(1969, 12, 31)  # why does this work???
			return (self.bid_date - epoch).total_seconds() * 1000
		except TypeError:
			return 0


	@property
	def bidding_to(self):
		"""
		:return: tuple of GC names that object is being bid to
		"""
		_gc = []
		for i in self.bids.itervalues():
			_gc.append(i['gc'])
		return _gc


	@property
	def path(self):
		""" Return absolute sub path using global project path and AwardedJob.sub_path """
		_path = os.path.join(env.env_root, self.sub_path)
		return _path


	@property
	def bid_count(self):
		"""
		:return: current number of bids
		"""
		return len(self.bids)


	@property
	def quote_count(self):
		count = 0
		for i in self.quotes.values():
			count += len(i)
		return count

	@property
	def quote_status(self):
		_scope_len = len(self.scope)
		_scope_fulfilled = 0
		_quotes_needed = 0
		for i in self.scope:
			if self.quotes[i]:
				_scope_fulfilled += 1
			else:
				_quotes_needed += 1
		_status = (float(_scope_fulfilled) / float(_scope_len))
		if _quotes_needed:
			_need = 'Need quotes from %d vendors' % _quotes_needed
		else:
			_need = 'No quotes needed'
		return (_status, _need)


	def add_bid(self, date_received, gc, bid_date='ASAP', gc_contact=None, scope=[]):
		"""
		:param date_received: date that bid request was received/uploaded
		:param gc: string or object of GC
		:param gc_contact: string or object of GC contact
		:param bid_date: datetime object of when bid is due
		:param scope: scope of bid request
		"""
		if not bid_date: bid_date = 'ASAP'
		_bid = {'gc': gc, 'gc_contact': gc_contact, 'bid_date': bid_date, 'date_received': date_received,
		        'scope': scope}
		_bid_hash = abs(hash(str(gc).lower()))
		self.bids[_bid_hash] = _bid
		for i in scope:
			if i not in self.scope:
				self.scope.append(i)
				self.quotes[i] = {}
		self.update()

		# TODO:prevent directory structure from being created twice
		# rebuild directory structure to implement new scope and for good measure
		self.init_struct()

	def add_quote(self, quote_obj, category):
		if category in self.scope:
			self.quotes[category][quote_obj.hash] = quote_obj
			self.update()

	def del_bid(self, bid_hash=None):
		if bid_hash:
			del self.bids[bid_hash]
		elif hasattr(self, 'db'):
			del self.db[self.number]
		del self
		return True

	def del_quote(self, quote_hash, category):
		if category in self.scope:
			del self.quotes[category][quote_hash]
			self.update()


	def find_rebid(self):
		"""
		:return: bid jobs object if there is a bid that has the same name. Else function returns false.
		"""
		if hasattr(self, 'db'):
			for i in self.db.values():
				if i._name == self._name:
					return i
			return False


	def complete_bid(self):
		if hasattr(self, 'db') and hasattr(self, 'completed_db'):
			if self.number in self.db.keys():
				self.completed_db[self.number] = self
				del self.db[self.number]
				self.completed = today()
				#TODO: update sent_out data cell in Estimating Log and style row
				return True

	def cancel_bid(self):
		if hasattr(self, 'db') and hasattr(self, 'completed_db'):
			if self.number in self.db.keys():
				self.completed_db[self.number] = self
				del self.db[self.number]
				self.completed = "No bid"
				#TODO: update sent_out data cell in Estimating Log and style row
				return True

	def award_bid(self, gc):
		""" Function that creates an AwardedJob object based on EstimatingJob object and selected gc. This function is run through the webApp and is bound to a specific bid/gc
		:param gc: string object representing GC that bid was sent to"""
		if hasattr(gc, 'lower'):  # proves that passed object is a string or Unicode
			gc = abs(hash(gc.lower))
			with self.bids[gc] as bid:
				AwardedJob(name=self.name, date_received=today(), alt_name=self.alt_name, address=self.address, gc=bid.gc,
			           gc_contact=bid.gc_contact, scope=self.scope, desc=self.desc, rate=self.rate)


	def init_struct(self):
		# create initial bid directory
		try:
			print "Creating directory for bid path..."
			os.mkdir(os.path.join(env.env_root, self.sub_path))
			print "...operation successful"
		except OSError:
			print "...Bid directory already exists"

		# create bid sub folders
		try:
			print "Creating bid sub folders..."
			_folders = ('Addendums', 'Documents', 'Drawings', 'Quotes')
			for _folder in _folders:
				os.mkdir(os.path.join(env.env_root, self.sub_path, _folder))
			print "...operation successful"
		except OSError:
			print "...Bid sub directories already exist"

		# create folders for holding quotes
		print "Creating sub folders for quotes"
		for _scope in self.scope:
			try:
				os.mkdir(os.path.join(env.env_root, self.sub_path, 'Quotes', _scope))
			except OSError:
				print "...Directory for [%s] quotes already exist" % _scope
		print "...operation successful"

		print "Folder directory for %s created\n" % self.name
		return True


	@staticmethod
	def find(num):
		if hasattr(EstimatingJob, 'db') and hasattr(EstimatingJob, 'completed_db'):
			try:
				return EstimatingJob.db[num]
			except KeyError:
				return EstimatingJob.completed_db[num]


	@staticmethod
	def get_bid_num():
		try:
			# TODO: check completed_db as well
			num = 0
			if hasattr(EstimatingJob, 'db'):
				_keys = EstimatingJob.db.keys()
				num = int(_keys[-1])
			if hasattr(EstimatingJob, 'completed_db'):
				_keys = EstimatingJob.completed_db.keys()
				_num = int(_keys[-1])
				if _num > num:
					num = _num
			return num + 1
		except IndexError:
			# no bids in database. assume a bid number of 1
			# TODO: check completed_db
			return 1


class EstimatingQuote(Quote):
	def __init__(self, bid, vend, category, price=0.0, doc=None):
		super(EstimatingQuote, self).__init__(vend, price, doc)
		self.bid = bid
		self.category = category

		self.update()

	def update(self):
		self.bid.add_quote(self, self.category)
		return None

	@property
	def sub_path(self):
		"""
		:return: relative directory location for quote object
		"""
		_path = os.path.join(self.bid.sub_path, 'Quotes')
		_path = os.path.join(_path, self.category)
		return _path

	@property
	def path(self):
		"""
		:return: absolute directory location for quote object
		"""
		_path = os.path.join(self.bid.path, 'Quotes')
		_path = os.path.join(_path, self.category)
		return _path

