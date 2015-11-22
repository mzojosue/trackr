from operator import itemgetter
import os
from datetime import datetime
from copy import copy
import re
import shutil

# Import parent classes and methods for estimating objects
import core.environment as env

from core.parsing.bid_log import *
from material_cycle import Quote
from job import AwardedJob, get_job_num, Job
from core.log import logger

today = datetime.today
now = datetime.now


class EstimatingJob(Job):
	yaml_tag = u'!EstimatingJob'
	yaml_filename = 'bid_storage.yaml'
	_dir_folders = ('Addendums', 'Documents', 'Drawings', 'Quotes', 'Specs', 'Takeoffs')
	default_sub_dir = 'Preconstruction'

	def __init__(self, name, job_num=None, alt_name=None, date_received=today(), date_end=None,
				 address=None, gc=None, gc_contact=None, rebid=False, scope=None, desc=None, rate='a',
				 tax_exempt=False, certified_pay=False, sub_path=None, group=False, completed=False,
				 struct=True, add_to_log=True):
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
		self._quotes = {}

		# TODO: implement document/drawing storage
		self.docs = {}
		self.takeoff = {}  # stores dict of takeoff document paths stored as PDF. dict key is the md5 hash of file

		for i in self.scope:
			# create sub-dictionaries for storing quotes by category/trade
			self._quotes[i] = {}
		self.bids = {}  # Stores previous bids. Stores self as first bid

		# False if jobs is not rebid. Rebid is defined by a bid that is shares the same name but differs in due date
		# Variable is pointed to object that is being rebid
		_rebid = self.find_rebid()
		if not rebid and _rebid and hasattr(_rebid, 'hash') and (_rebid.hash != self.hash):
			self.rebid = _rebid
		else:
			self.rebid = rebid

		# TODO: implement grouping system
		self.group = group

		self.add_sub(date_received=date_received, gc=gc, bid_date=date_end, gc_contact=gc_contact, scope=scope,
					 struct=struct, add_to_log=False)
		if add_to_log:
			add_bid_to_log(self)

	@property
	def name(self):
		if hasattr(self, 'number'):
			return '%d - %s' % (self.number, self._name)

	@property
	def takeoffs(self):
		""" Iterates through contents of Takeoffs folder and returns file-names, paths, and last modified times
		:return: dump_folder
		"""
		return self.dump_folder('Takeoffs')

	@property
	def has_takeoff(self):
		""" Checks to see if self has any takeoff documents
		:return: Returns boolean if self has files in Takeoff folder
		"""
		_takeoffs = self.takeoffs
		return bool(len(_takeoffs))

	@property
	def bid_date(self):
		""" finds and returns most recently due bid date """
		try:
			return sorted(self.bids.values(), key=itemgetter('bid_date'))[0]['bid_date']
		except TypeError:  # occurs when at least one date is 'ASAP'
			return today()

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
	def timestamp(self):
		""" Returns the bid due date as a millisecond timestamp ready to be displayed on calendar """
		try:
			epoch = datetime(1969, 12, 31)  # why does this work???
			return (self.bid_date - epoch).total_seconds() * 1000
		except TypeError:
			return 0

	@property
	def bid_count(self):
		"""
		:return: current number of bids
		"""
		return len(self.bids)

	@property
	def bidding_to(self):
		"""
		:return: tuple of GC names that object is being bid to
		"""
		_gc = []
		for i in self.bids.itervalues():
			_gc.append(str(i['gc']))
		return _gc

	def init_struct(self):
		""" Rebuilds directory structure based off self.path, EstimatingJob._dir_folders, and self.scope
		:return: False if global path error. Otherwise returns True
		"""
		# create initial bid directory
		try:
			os.makedirs(self.path)
		except OSError:
			if os.path.isdir(self.path):
				pass  # top level directory already exists
			else:
				return False  # global path error

		# create bid sub folders
		for _folder in self._dir_folders:
			try:
				os.mkdir(os.path.join(self.path, _folder))
			except OSError:
				pass  # assume project sub folders already exist

		# create folders for holding quotes
		for _scope in self.scope:
			if len(_scope) == 1:  # only create directories for (M, E, I, B, P) not 'Install' or 'Fab'
				try:
					os.mkdir(os.path.join(self.path, 'Quotes', _scope))
				except OSError:
					pass  # assume quote folders already exist

		# Import and rename template documents
		_name = self._name
		_name = _name.replace(' ', '_')  # normalize _name string as filename

		_srch = ' '.join(os.listdir(self.path))                 # enumerate top-level file and dir names in project folder
		_patterns = ('proposal\.docx', 'pricing\.xls')
		_temp_dir = os.path.join(env.env_root, 'Templates')     # Document template directory
		if os.path.isdir(_temp_dir):
			_templates = ' '.join(os.listdir(_temp_dir))            # Grab document template names
			for _doc in _patterns:
				if not re.search('\w+\.%s' % _doc, _srch):          # document not in project folder
					doc = _doc.replace("\\", "")                    # exclude '\' from file name
					doc = '%s.%s' % (_name, doc)                    # new document filename to save
					template = re.search('\w+\.%s' % _doc, _templates)
					if template:
						template = template.group()                 # convert SRE_Match obj to str
						template = os.path.join(env.env_root, 'Templates', template)
						_dest = os.path.join(self.path, doc)
						shutil.copyfile(template, _dest)
					else:  # template does not exist in Template directory
						print "WARNING: Template matching regex '%s' not found in '%s'" % (_doc, _temp_dir)
				else:
					print "NOTE: Template matching regex '%s' is already in project folder for %s" % (_doc, self.name)

			return True


	# Quote Functions

	@property
	def quotes(self):
		_dir = os.path.join(env.env_root, self.sub_path, 'Quotes')
		_return = {}
		if os.path.isdir(_dir):
			_scope_folders = os.listdir(_dir)
			for i in _scope_folders:
				_scope = os.path.join(_dir, i)
				if os.path.isdir(_scope):
					_return[i] = os.listdir(_scope)
		# TODO: join files in Quotes directory with self._quotes
		return _return

	@property
	def quote_count(self):
		""" Iterates self.quotes and counts the number of quotes in each scope
		:return: int reflecting the amount of quotes stored
		"""
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
		try:
			_status = (float(_scope_fulfilled) / float(_scope_len))
		except ZeroDivisionError:
			_status = 0.0
		if _quotes_needed:
			_need = 'Need quotes from %d vendors' % _quotes_needed
		else:
			_need = 'No quotes needed'
		return _status, _need

	def add_quote(self, quote_obj, category):
		if category in self.scope:
			self._quotes[category][quote_obj.hash] = quote_obj
			self.update()

	def del_quote(self, quote_hash, category):
		if category in self.scope:
			del self.quotes[category][quote_hash]
			self.update()


	# Sub Bid Methods #

	def add_sub(self, date_received, gc, bid_date='ASAP', gc_contact=None, scope=[], struct=True, add_to_log=True):
		"""
		:param date_received: date that bid request was received/uploaded
		:param gc: string or object of GC
		:param gc_contact: string or object of GC contact
		:param bid_date: datetime object of when bid is due
		:param scope: scope of bid request
		"""
		if not bid_date: bid_date = 'ASAP'
		_bid_hash = abs(hash(str(gc).lower()))
		_bid = {'bid_hash': _bid_hash, 'gc': gc, 'gc_contact': gc_contact,
				'bid_date': bid_date, 'date_received': date_received, 'scope': scope}
		self.bids[_bid_hash] = _bid
		if scope:
			for i in scope:
				if i not in self.scope and i in self.valid_scope:
					self.scope.append(i)
					self._quotes[i] = {}

		self.update()
		if struct:
			self.init_struct()  # rebuild directory structure to implement new scope and for good measure
		if add_to_log:
			return add_sub_bid_to_log(self, _bid_hash)
		return True

	def del_sub(self, bid_hash):
		"""
		Deletes the specified sub bid based on bid hash
		:param bid_hash: Bid hash to delete
		:return: Returns True if operation successful
		"""
		del self.bids[bid_hash]
		self.update()
		return True


	# Top-level Bid Functions #

	def complete_bid(self):
		if hasattr(self, 'db') and hasattr(self, 'completed_db'):
			if self.number in self.db.keys():
				self.completed_db[self.number] = self
				self.completed = today()
				del self.db[self.number]
				logger.info('EstimatingJob %s was updated as complete!' % self.name)

				#TODO: update sent_out data cell in Estimating Log and style row
				update_bid_in_log(self, 'complete', self.completed.date())
				return True

	def cancel_bid(self):
		if hasattr(self, 'db') and hasattr(self, 'completed_db'):
			if self.number in self.db.keys():
				self.completed_db[self.number] = self
				self.completed = "No bid"
				del EstimatingJob.db[self.number]
				logger.info('Canceled EstimatingJob %s' % self.name)

				#TODO: update sent_out data cell in Estimating Log and style row
				update_bid_in_log(self, 'complete', "No bid")
				return True

	def delete_bid(self, remove=False):
		try:
			if hasattr(self, 'db'):
				del self.db[self.number]
		except KeyError:
			if hasattr(self, 'completed_db'):
				del self.completed_db[self.number]
		_name = self.name
		del self
		EstimatingJob.dump_all()
		logger.info('Deleted EstimatingJob %s' % _name)

		if remove:
			# TODO: delete row(s) from Estimating Log
			pass
		return True

	def award_bid(self, bid_hash):
		""" Function that creates an AwardedJob object based on EstimatingJob object and selected gc.
		This function is run through the webApp and is bound to a specific bid/gc
		:param gc: string object representing GC that bid was sent to """
		bid = self.bids[bid_hash]
		if not self.completed:
			self.complete_bid()
		logger.info('Awarded EstimatingJob %s!' % self.name)

		return AwardedJob(job_num=get_job_num(), name=self._name, date_received=today(), alt_name=self.alt_name,
						  address=self.address, gc=bid['gc'], gc_contact=bid['gc_contact'], scope=self.scope,
						  desc=self.desc, rate=self.rate)

	@staticmethod
	def find(num):
		if hasattr(EstimatingJob, 'db') and hasattr(EstimatingJob, 'completed_db'):
			try:
				return EstimatingJob.db[num]
			except KeyError:
				return EstimatingJob.completed_db[num]

	def find_rebid(self):
		"""
		:return: bid jobs object if there is a bid that has the same name. Else function returns false.
		"""
		# TODO: implement a deep search (eg: address attribute, desc attribute, 'st'/'ave' in name, etc)
		if hasattr(self, 'db'):
			for i in self.db.values():
				if i._name == self._name:
					return i
			return False

	@staticmethod
	def get_bid_num():
		try:
			# TODO: check completed_db as well
			num = 0
			if hasattr(EstimatingJob, 'db'):
				_keys = EstimatingJob.db.keys()
				num = int(sorted(_keys)[-1])
			if hasattr(EstimatingJob, 'completed_db'):
				_keys = EstimatingJob.completed_db.keys()
				_num = int(sorted(_keys)[-1])
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


class BidSheet(object):
	""" BidSheet manages the cost and collection of takeoff metrics, quote values, and GC scopes. """

	valid_scope = Job.valid_scope

	def __init__(self, label=None, date_created=now(), bid=None, revision=None, scope=valid_scope):
		"""
		:param label: string identify object
		:param date_created: defaults to `now()`
		:param bid: bid number, bid object or tuple( parent bid number, sub bid hash value )
		:param revision: revision label or date
		:return:
		"""
		self.label = label
		self.date_created = date_created
		if not date_created:
			self.date_created = now()
		self.bid = bid
		self.scope = []
		for i in scope:
			if str(i) in self.valid_scope:
				self.scope.append(str(i))

		self.sections = {}  # container for storing bid sections with section label as key
		self.subcontractors = {}  # container for storing subcontractor bid sections with arbitrary key

	def add_section(self, section):
		if hasattr(section, 'label'):
			self.sections[section.label] = section
			return self.sections

	def del_sections(self, label):
		if hasattr(self.sections, 'label'):
			del self.sections[label]
			return True

	def calculate(self, output='hours', rate=None):
		_labor = 0  # dynamically create variables based on output type
		_purch = 0.0
		# sub_cost = 0.0  # subcontractor cost

		for section in self.sections.itervalues():
			_calc = section.calculate(output, rate)
			if hasattr(_calc, '__getitem__'):  # working with dollar and labor amounts
				_labor += _calc[0]
				_purch += _calc[1]
			else:
				_labor += _calc  # working with dollar amounts

		# Calculate labor cost
		# Return sum of all costs with profit markup
		if _purch:
			return (_labor, _purch)
		else:
			return _purch


class BidSection(object):
	""" BidSection manages the cost and collection of SectionItems. """
	value_outputs = ('cost', 'hours')

	def __init__(self, label, iterate=1):
		self.label = label
		self.iterate = int(iterate)
		self.section = {}

	def add_item(self, item):
		# TODO: check scope
		if hasattr(item, 'calculate') and hasattr(item, 'id'):  # assume that item passed is SectionItem object
			self.section[item.name] = copy(item)  # make item in section independent from global item
			return True
		elif str(item) in SectionItem.available_items:
			self.section[item] = copy(SectionItem.available_items[item])
			return True

	def del_item(self, item):
		"""
		:param item: could be item id str or object
		:return: False if operation not completed
		"""
		if item in self.section:  # treat item as id str
			del self.section[item]
		elif hasattr(item, 'id'):  # treat item as SectionItem object
			del self.section[item.name]
		else:
			return False

	def calculate(self, output='hours', rate=None):
		""" Sums the cost of each SectionItem in self.section.
		:param output: defines returned value. Can either be 'cost' or 'hours', defaults to 'hours'.
		:param rate: used in conjunction with output when calculating total cost from labor hours.
			The rate value should be passed down from the parent bid.
		:return:
		"""
		_return = 0
		_cost = 0

		for item in self.section.itervalues():
			_calc = item.calculate(output, rate)
			if hasattr(_calc, '__getitem__'):
				_return += _calc[0]
				_cost += _calc[1]
			else:
				_return += _calc
		_return *= self.iterate
		_cost *= self.iterate

		if _cost:
			return (_return, _cost)
		else:
			return _return


class SectionItem(object):
	""" Object that stores numeric values and methods of calculating cost based on given metric.
	Eg: 'labor cost per item plus cost', 'hours per foot', 'labor cost per pound'
	"""
	valid_scope = Job.valid_scope
	valid_outputs = ('cost', 'hours')
	valid_metrics = ('count', 'length', 'weight')
	default_metric = 'count'

	available_items = {}  # organizes items by scope
	for i in valid_scope:
		available_items[i] = {}

	def __init__(self, id, scope, label=None, amount=0, metric=default_metric, units=None, value=0.0, cost=0.0, correction_factor=1.0):
		self.id = id
		if scope in self.valid_scope:
			self.scope = scope
		elif scope[0].upper() in self.valid_scope:
			self.scope = scope[0].upper()
		else:
			self.scope = None
		if self.scope:  # add self to item storage
			SectionItem.available_items[self.scope][self.id] = self

		self.label = label
		self.amount = amount
		self.metric = metric
		self._units = units  # used for UI. Should be plural string
		self.value = value
		self.cost = cost
		self.correction_factor = correction_factor

	@property
	def units(self):
		if hasattr(self, '_units') and self._units:
			return self._units
		else:
			if self.metric is 'length':
				return 'feet, 0"'
			elif self.metric is 'weight':
				return 'lbs'
			else:  # assum self.metric == 'count'
				return 'pieces'


	def calculate(self, output='hours', rate=None):
		""" Process value based on metric and output type while implementing cost and correction factor.
		:param output: defines returned value. Can either be 'cost' or 'hours', defaults to 'hours'.
		:param rate: used in conjunction with output when calculating total cost from labor hours.
			The rate value should be passed down from the parent bid and BidSection.
		:return: total amount of labor hours by calculating product of self.amount, self.value, and self.correction_factor.
			If output=='cost' and a valid rate is given, labor cost is calculated by multiplying by rate passed, and adding the purchasing cost.
		"""
		_return = self.amount * self.value * self.correction_factor  # calculate labor hours

		if str(output) is 'cost' and rate:  # labor rate must be passed
			_return *= rate       # convert labor hours to labor cost
			_return += self.cost  # add item cost to output
			return _return
		else:
			return (_return, self.cost)

	def __repr__(self):
		_metric = self.metric
		_format = (float(self.amount), self.id, self.value)
		if _metric is 'item':
			return "%s %s(s) @ %s hours per item" % _format
		elif _metric is 'length':
			return "%s feet of %s @ %s hours per foot" % _format
		elif _metric is 'weight':
			return "%s pounds of %s @ %s hours per pound" % _format

# Create default section items
SectionItem('sm_shop', label="Sheet Metal Fabrication", metric='weight', value=30, scope='sm')
SectionItem('sm_field', label="Sheet Metal Installation",  metric='weight', value=25, scope='sm')
SectionItem('RGD', label="Air Device", units="pieces", value=0.25, scope='materials')
SectionItem('linear', label="Linear Air Device", metric='length', value=0.25, scope='materials')  # TODO: fix labor value
SectionItem('FSD', label="Fire/Smoke Damper", units="pieces", value=1, scope='materials')
SectionItem('vol_damper', label="Volume Damper", units="pieces", value=.3, scope='materials')
SectionItem('ceiling_fan', label="Ceiling Fan", units="fans", value=1.25, scope='equipment')
SectionItem('curbed_fan',  label="Curbed Fan", units="fans", value=2.25, scope='equipment')
SectionItem('louver', label="Louver", units="pieces", value=0.5, scope='louvers')
SectionItem('RTU', label="Packaged Rooftop Unit", units="units", value=4, scope='equipment')
SectionItem('VAV', label="Terminal/VAV Unit", units="units", value=2.25, scope='equipment')

