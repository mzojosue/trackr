import yaml, os, traceback

from datetime import timedelta
import core.log as log
from material_cycle import MaterialList, Quote
from timesheet import *


class Worker(object):
	# pay rate constants
	A_RATE = 100.84
	A_RATE_journeyman = 97.38
	B_RATE = 51.76

	yaml_tag = u'!Worker'
	_yaml_attr = ('date_created', '_job_num', 'prev_job', 'phone', 'email', 'role', 'rate', 'timesheets')
	_yaml_filename = 'workers.yaml'

	def __init__(self, name, job, phone=None, email=None, role='Installer', rate=None, date_created=today(),
				 timesheets=[]):
		"""
		Initializes employee representation object.
		:param name: employee's name. hash/key is created from this variable.
		:param job: current jobs that employee is at. if changed, the previous jobs will be added to self.prev_jobs
		:param phone: listed phone number for employee
		:param email: listed email address
		:param role: worker's role on the jobsite. ie: foreman, installer/mechanic, pipe fitter, etc
		:param rate: pay rate for employee. can be arbitrary value
		"""
		self.name = str(name)
		self.hash = abs(hash(str(self.name) + str(date_created)))
		self.date_created = date_created
		self.job = job
		self._job_num = self.job.number
		self.prev_jobs = []
		self.phone = str(phone)
		self.email = str(email)
		self.role = role
		if rate is 'a':
			self.rate = Worker.A_RATE
		elif rate is 'b':
			self.rate = Worker.B_RATE
		else:
			self.rate = rate

		self.job.add_worker(self)

		self.timesheets = timesheets  # list that includes timesheet hashes that worker has been at

		self.dump_info()

	@property
	def job_num(self):
		self._job_num = self.job.number
		return self.job.number

	def __setattr__(self, key, value):
		""" Alters attribute setting to listen to when self.jobs is changed,
			the previous jobs is stored in self.prev_jobs
		"""
		_caller = traceback.extract_stack(None, 2)[0][2]
		if _caller is not '__init__':
			if key is 'job':
				value.add_worker(self)
				self.prev_jobs.append(self.job.name)
				del self.job.workers[self.hash]
				self.job.update()
				self._job_num = self.job.number
			self.update()
		_return = super(Worker, self).__setattr__(key, value)
		return _return

	def __repr__(self):
		"""
		:return: describes object by self.name, self.role, and self.jobs.name
		"""
		# TODO:update output format
		# TODO:return date since working at jobs
		return "\"%s\". %s at %s" % (self.name, self.role, self.job.name)

	@staticmethod
	def find(q_hash):
		"""

		:param q_hash: hash to query database for
		:return: returns worker object that matches description
		"""
		if hasattr(Worker, 'db'):
			try:
				return Worker.db[q_hash]
			except KeyError:
				return False

	@staticmethod
	def get_set_or_create(name, job=None):
		_name = abs(hash(str(name)))
		worker = Worker.find(_name)
		if worker:
			if job:
				worker.job = job
			return worker
		else:
			return Worker(name, job)

	def add_labor(self, hours, date_worked=today(), week_end=None, job=None):
		if job:
			self.job = job

		if not week_end:
			# find correct week end (Wednesday)
			weekday = date_worked.isoweekday()
			_wed = 3  # Wednesday in iso format
			_diff = _wed - weekday
			_diff *= -1  # invert _diff
			_diff = timedelta(days=_diff)
			week_end = date_worked + _diff

		# calculate timesheet hash and call add_labor
		t_hash = abs(hash(''.join([str(self.job.number), str(week_end)])))
		work = (date_worked, hours)
		try:
			timesheet = self.job.timesheets[t_hash]
		except KeyError:
			timesheet = Timesheet(self.job, week_end)
		timesheet.add_labor(self, *work)

	@staticmethod
	def load_workers():
		""" Loads users from campano/workers.yaml in root environment"""
		fname = os.path.join(Worker.env_root, Worker._yaml_filename)
		try:
			with open(fname, 'r') as _file_dump:
				_file_dump = yaml.load(_file_dump)
				for _name, _attr in _file_dump.iteritems():
					_attr['job'] = AwardedJob.find(_attr['_job_num'])
					del _attr['job_num']
					Worker(**_attr)
			log.logger.info('Successfully imported users.yaml')
		except IOError:
			return False
		return True

	@classmethod
	def dump_info(cls):
		""" dump values from self to .yaml file """
		_filename = os.path.join(cls.env_root, cls._yaml_filename)

		_dump = {}
		if hasattr(Worker, 'db'):
			for _work in Worker.db.itervalues():
				_data = {}
				for i in cls._yaml_attr:
					try:
						_val = _work.__getattribute__(i)
						_data[i] = _val
					except AttributeError:
						continue
				_dump[_data['name']] = _data

		with open(_filename, 'w') as _data_file:
			# TODO: log file write
			yaml.dump(_dump, _data_file, default_flow_style=False)

	def update(self):
		"""
		Calls self.dump_all
		:return: None
		"""
		if hasattr(Worker, 'db') and hasattr(self, 'hash'):
			Worker.db[self.hash] = self
			if hasattr(self, 'job'):
				self.job.add_worker(self)
			self.dump_info()
		return None


class Job(yaml.YAMLObject):
	yaml_tag = u'!Job'
	yaml_filename = 'db_storage.yaml'
	valid_scope = ('M', 'E', 'B', 'I', 'P', 'sm')

	_yaml_attr = ['end_date', 'alt_name', 'address', 'gc_contact', 'scope', 'desc', 'po_pre' 'tax_exempt',
				  'certified_pay',
				  'rate', 'scope', 'bids', 'completed']  # TODO: somehow store POs in job YAML

	def __init__(self, name, date_received=None, date_end=None, alt_name=None, address=None, gc=None,
				 gc_contact=None, scope=None, desc=None, rate='a', tax_exempt=False, certified_pay=False,
				 completed=False):
		self._name = str(name)
		self._alt_name = alt_name
		self.date_received = date_received
		self.address = address
		self.gc = gc
		self.gc_contact = gc_contact
		self.scope = []
		if scope:
			for i in scope:  # validate scope items before appending to list
				if i in Job.valid_scope and len(i) == 1:
					self.scope.append(i)

		self.desc = desc
		if rate is 'a':
			self.rate = Worker.A_RATE
		elif rate is 'b':
			self.rate = Worker.B_RATE
		self.tax_exempt = tax_exempt
		self.certified_pay = certified_pay

		self._documents = {}

		self.completed = completed

	@property
	def name(self):
		if self._name[-1] == ' ':
			self._name = self._name[:-1]
		if hasattr(self, 'number'):
			return '-'.join([str(self.number), str(self._name)])
		else:
			return str(self._name)

	@property
	def alt_name(self):
		if hasattr(self, '_alt_name') and self._alt_name:
			return self._alt_name
		else:
			return self.name

	@alt_name.setter
	def alt_name(self, value):
		self._alt_name = str(value)

	@property
	def sub_path(self):
		"""
		:return: Relative directory path with respective documents and files
		"""
		if hasattr(self, 'default_sub_dir'):
			return os.path.join(self.default_sub_dir, self.name)
		else:
			return False

	@property
	def path(self):
		""" Return absolute sub path using program path and Class.sub_path """
		if hasattr(self, '_path') and self._path:
			return self._path
		elif self.sub_path:
			_path = os.path.join(self.env_root, self.sub_path)
			return _path
		else:
			return False

	def dump_folder(self, _dir):
		""" Iterates through contents of given _dir and returns file-names, paths, and last modified times
		:return:
		"""
		# TODO: update docstring
		if self.path:
			_dir = os.path.join(self.path, _dir)
			if os.path.isdir(_dir):
				_files = os.listdir(_dir)
				_return = {}
				for f in _files:
					_path = os.path.join(_dir, f)
					_mod_time = os.stat(_path)
					# TODO: process file type
					_sub_path = os.path.join(_dir, f)
					_return[f] = {'path': _path, 'sub_path': _sub_path, 'mod_time': _mod_time}
				return _return
			else:
				# TODO: log directory error
				pass
		# TODO: log attribute error
		return {}  # catchall

	@property
	def addendums(self):
		""" Iterates through contents of Addendums folder and returns file-names, paths, and last modified times
		:return: self.dump_folder
		"""
		return self.dump_folder('Addendums')

	@property
	def drawings(self):
		""" Iterates through contents of Drawings folder and returns file-names, paths, and last modified times
		:return: self.dump_folder
		"""
		_dump = self.dump_folder('Drawings')
		for fn, stats in _dump.iteritems():
			if os.path.isfile(stats['path']):
				print 'bam'
		return _dump

	@property
	def documents(self):
		""" Iterates through contents of Documents folder and returns file-names, paths, and last modified times
		:return: self.dump_folder
		"""
		return self.dump_folder('Documents')

	@property
	def has_drawings(self):
		""" Checks to see if self has any drawing documents
		:return: Returns boolean if self has files in Documents folder
		"""
		_dwgs = self.drawings
		return bool(len(_dwgs))

	@property
	def has_documents(self):
		""" Checks to see if self has any documents
		:return: Returns boolean if self has files in Documents folder
		"""
		_docs = self.documents
		return bool(len(_docs))

	@property
	def has_addendums(self):
		""" Checks to see if self has any Addendum documents
		:return: Returns boolean if self has files in Documents folder
		"""
		_adds = self.addendums
		return bool(len(_adds))

	def __setattr__(self, key, value):
		_return = super(Job, self).__setattr__(key, value)

		# do not update yaml file or call self.update() if self is still initializing
		_caller = traceback.extract_stack(None, 2)[0][2]
		if _caller is not '__init__' and _caller is not 'load_info':
			log.logger.info('In %s, updated "%s" attribute to %s')
			self.update()
		return _return

	def __repr__(self):
		return self.name

	def update(self):
		if hasattr(self, 'number'):
			if self.completed and hasattr(self, 'completed_db'):
				self.completed_db[self.number] = self
			elif hasattr(self, 'db'):
				self.db[self.number] = self
			else:  # no db attribute
				return 'DB_ERROR'  # returned for debugging
			if not hasattr(self, '_dump_lock'):  # ensures that file is not written multiple times during import
				self.dump_info()  # save to global yaml storage
		else:
			return False

	def dump_info(self):
		_filename = os.path.join(self.path, self.yaml_filename)
		stream = open(_filename, 'w')
		print 'Saving %s' % _filename
		yaml.dump(self, stream)
		print 'Local storage updated'

	@classmethod
	def storage(cls):
		if hasattr(cls, 'default_sub_dir') and hasattr(cls, 'env_root'):
			_filename = os.path.join(cls.env_root, cls.default_sub_dir, cls.yaml_filename)
			return _filename

	@classmethod
	def dump_all(cls):
		""" Iterates through class databases and saves all objects to YAML file
		:return: None
		"""
		if hasattr(cls, '_dump_lock') and cls._dump_lock:
			return None  # attribute to prevent object storage for testing purposes

		_jobs = {}  # aggregate both current and past jobs
		if hasattr(cls, 'completed_db'):
			for num, obj in cls.completed_db.iteritems():
				_jobs[num] = obj
		if hasattr(cls, 'db'):
			for num, obj in cls.db.iteritems():
				_jobs[num] = obj

		if hasattr(cls, 'default_sub_dir'):
			_filename = cls.storage()
			stream = file(_filename, 'w')
			print 'Saving %s' % _filename
			yaml.dump(_jobs, stream)


class AwardedJob(Job):
	yaml_tag = u'!AwardedJob'
	yaml_filename = 'job_storage.yaml'
	default_sub_dir = 'Jobs'

	def __init__(self, job_num, name, start_date=None, end_date=None, alt_name=None, po_pre=None, address=None,
				 gc=None, gc_contact=None, scope=None, foreman=None, desc=None, rate='a',
				 contract_amount=None, tax_exempt=False, certified_pay=False, sub_path=None, date_received=today(),
				 sheet_num=None, init_struct=True):
		"""
		:param job_num: desired jobs number
		:param name: primary jobs name
		:param start_date: planned jobs start date
		:param end_date: planned jobs completion date
		:param alt_name: secondary name/nickname for jobs
		:param po_pre: desired po prefix. defaults to jobs name
		:param address: listed address for jobsite
		:param gc: listed general contractor
		:param gc_contact: listed general contractor contact
		:param scope: scope of work. ie: full-airside, fabrication only, etc
		:param foreman: listed sheet metal foreman on jobs
		:param desc: short description of scope of work
		:param rate: default rate for workers on jobsite
		:param contract_amount: listed contract amount for jobs completion. jobs completion percentage is based off of this.
		:param tax_exempt: Boolean. True if jobs is tax exempt
		:param certified_pay: Boolean. True is jobs is a certified payroll jobs
		:param sub_path: The directory sub path for the jobs
		"""
		# TODO:implement better document storage
		self.number = int(job_num)
		super(AwardedJob, self).__init__(name=name, date_received=date_received, alt_name=alt_name,
										 address=address, gc=gc, gc_contact=gc_contact, scope=scope, desc=desc,
										 rate=rate, tax_exempt=tax_exempt, certified_pay=certified_pay)
		self.start_date = start_date
		self.end_date = end_date
		if po_pre:
			self.po_pre = po_pre
		else:
			self.po_pre = self.name
		self.foreman = foreman
		self.contract_amount = contract_amount
		self.sheet_num = sheet_num

		self._PO = 0  # stores most recent PO suffix number
		self.POs = {}  # stores PO strings as keys
		self.workers = {}  # stores all current Worker objects
		self._materials = {}  # stores all MaterialList objects
		self._quotes = {}  # stores unlinked Quote objects
		self.deliveries = {}  # TODO: iterate over _materials
		self.tasks = {}
		# AwardedJob.timesheets.key is datetime.datetime object for the week-ending
		# AwardedJob.timesheets.value is [ 'pathname/to/timesheet', { worker.hash: (worker, hours) } ]
		self.timesheets = {}

		if init_struct:
			self.init_struct()

		log.logger.info('Created \'%s\' AwardedJob object' % self.name)

		self.update()

	def init_struct(self):
		""" Initializes project directory hierarchy. """
		# TODO:initialize documents w/ jobs information
		try:
			os.makedirs(self.path)
			log.logger.debug('Created project directory for "%s"' % self.name)
		except OSError:
			log.logger.warning("...project folder already exists")

		log.logger.debug("Creating project sub directories for %s..." % self.name)
		_folders = ('Addendums', 'Billing', 'Change Orders', 'Close Out', 'Contract Scope', 'Documents',
					'Drawings', 'Materials', 'Quotes', 'RFIs', 'Specs', 'Submittals')
		for _folder in _folders:
			try:
				os.mkdir(os.path.join(self.path, _folder))
				log.logger.debug('Created sub directory, \'%s\', for \'%s\'' % (_folder, self.name))
			except OSError:
				log.logger.warning('Sub directory, "%s", for %s already exists!' % (_folder, self.name))

	# Material List Functions #

	@property
	def materials(self):
		""" Iterates through contents of 'Materials' folder and returns file names.
		Creates MaterialList objects for all files that aren't owned by an object.
		:return:
		"""
		if self.path:
			_dir = os.path.join(self.path, 'Materials')
			if os.path.isdir(_dir):
				_mats = os.listdir(_dir)
				for mat in _mats:
					_hash = abs(hash(str(mat)))
					if _hash not in self._materials:
						MaterialList(self, doc=mat)
			else:
				# TODO: log directory error
				pass
		return self._materials

	@property
	def has_open_lists(self):
		"""
		Returns 0 if jobs has no open material lists
		:return: Integer of material lists that have not been purchased.
		"""
		open_lists = []
		for mlist in self.materials.itervalues():
			if not mlist.fulfilled:
				open_lists.append(mlist)
		return open_lists

	def add_mat_list(self, mlist_obj):
		"""
		Blindly adds material list object to self.
		:param mlist_obj: material list object to add to self
		:return: None
		"""
		if not mlist_obj.hash in self._materials:
			log.logger.info('Added material list %s (%s) to %s' % (mlist_obj.hash, mlist_obj.items, self.name))

		self._materials[mlist_obj.hash] = mlist_obj
		self.update()

	def del_mat_list(self, mlist_hash, delete=False):
		"""
		Deletes material list object from self._materials
		:param mlist_hash: hash to delete from self._materials
		:param delete: if True is passed, then the document is deleted from the filesystem
		:return: None
		"""
		for i in self.POs.values():
			if i.mat_list.hash == mlist_hash:
				del self.POs[i.number]
		for i in self._quotes.values():
			if hasattr(i, 'mat_list') and i.mat_list.hash == mlist_hash:
				del self._quotes[i.hash]
		del self._materials[mlist_hash]

		if delete:
			# TODO:delete document in filesystem
			pass
		self.update()

		if not delete:
			log.logger.info('Deleted %s material list from %s' % (mlist_hash, self.name))

	# Quote Functions #

	@property
	def quotes(self):
		""" Aggregates unlinked Quote objects and material list quotes via self._quotes and self.materials[].quotes.
		Function calls unlinked_quotes to ensure that self._quotes is updated.
		:return: self._quotes and material list quotes
		"""
		try:
			_dir = os.path.join(self.path, 'Quotes')
			q_doc_len = len(os.listdir(_dir))
			if not hasattr(self, 'q_doc_len') or self.q_doc_len != q_doc_len:
				self.q_doc_len = q_doc_len
				self.unlinked_quotes()  # updates self._quotes
		except OSError:  # object directory does not exist
			pass

		_return = {}
		for _mlist in self.materials.itervalues():
			_return.update(_mlist.quotes)
		_return.update(self._quotes)  # Assume that _quotes is up to date
		return _return

	def unlinked_quotes(self):
		""" Grabs and returns unlinked quotes which have been added to the Quotes directory
		:return: self._quotes
		"""
		if self.path:
			_dir = os.path.join(self.path, 'Quotes')
			if os.path.isdir(_dir):
				_quotes = os.listdir(_dir)
				for q_doc in _quotes:
					_hash = abs(hash(str(q_doc)))
					if _hash not in self.quotes.keys() and _hash not in self._quotes.keys():
						_obj = Quote(vend=None, doc=q_doc)
						_obj._path = self.path
						self._quotes[_hash] = _obj
			else:
				# log directory error
				pass
		return self._quotes

	def add_quote(self, quote_obj):
		"""
		Blindly adds quote object to self.
		:param quote_obj: quote object to add to self
		:return: None
		"""
		_mat_list = quote_obj.mat_list.hash  # grab material list hash from object
		self._materials[_mat_list].add_quote(quote_obj)
		self.update()

		log.logger.info(
			'Added quote object from "%s" to "%s" material list for %s' % (quote_obj.vend, _mat_list, self.name))

	def del_quote(self, quote_hash, delete=False):
		"""
		Deletes quote object from self._quotes
		:param quote_hash: hash to delete from self._quotes
		:param delete: if True is passed, then the document is deleted from the filesystem
		:return: None
		"""
		for i in self._materials.values():
			if quote_hash in i.quotes.keys():
				del i.quotes[quote_hash]
		for i in self.POs.values():
			if i.quote.hash == quote_hash:
				del self.POs[i.number]

		if delete:
			# TODO:delete document in filesystem
			pass
		self.update()

		if not delete:
			log.logger.info('Deleted %s material list from %s' % (quote_hash, self.name))

	# PO Functions #

	def add_po(self, po_obj):
		"""
		Blindly adds PO object to self.
		:param po_obj: PO object to add to self.
		:return: None
		"""
		if po_obj.number not in self.POs:
			log.logger.info('Awarded %s to %s for %s' % (po_obj.name, po_obj.vend, self.name))
		self.POs[po_obj.number] = po_obj
		_mat_list = po_obj.mat_list.hash
		self._materials[_mat_list].po = po_obj
		self._materials[_mat_list].fulfilled = True
		self.update()

	@property
	def next_po(self):
		"""
		Optimizes PO# usage by ensuring that all PO numbers are used, and none are skipped.
		:return: returns claimed PO number
		"""
		_keys = self.POs.keys()
		_k_len = len(_keys)

		_return = 0
		if _k_len:
			# calculate ideal sum of continuous sequence of equal length
			_ideal_seq_sum = (_k_len / 2) * (0 + (_k_len - 1))

			# calculate the real sum of existing po# sequence
			_seq_sum = (_k_len / 2) * (_keys[0] - _keys[-1])

			# check to see if current sequence is continuous
			if not (int(_seq_sum) == int(_ideal_seq_sum)):
				# find the smallest integer to begin to complete the sequence.
				_new_PO = 0  # start search @ 0
				while True:
					if _new_PO not in _keys:
						_return = _new_PO
						break
					else:
						_new_PO += 1
			else:
				_return = _keys[-1] + 1
		return _return

	@property
	def show_po(self):
		""" Shows formatted PO# that's available next.
		:return: returns the formatted value of the next available PO for considering it being given to a vendor
		"""
		_po = self.next_po
		_po = '%03d' % _po  # add padding to PO number
		return '-'.join([self.name, _po])

	# Delivery Functions #

	def add_delivery(self, deliv_obj):
		"""
		Blindly adds delivery object to self.
		:param deliv_obj: delivery object to add to self
		:return: None
		"""
		self.deliveries[deliv_obj.hash] = deliv_obj
		self.update()

		log.logger.info('Scheduled delivery on %s for %s' % (deliv_obj.expected, self.name))

	# Worker/Labor/Cost Functions #

	def add_worker(self, wrkr_obj):
		"""
		Blindly adds worker object to self.
		:param wrkr_obj: Worker object to add to self
		:return: None
		"""
		self.workers[wrkr_obj.hash] = wrkr_obj
		self.update()

		log.logger.info('"%s" has been added to %s project' % (wrkr_obj.name, self.name))

	@property
	def labor(self):
		""" Calculates labor totals """
		hrs = 0.0
		for sheet in self.timesheets.itervalues():
			for worker in sheet.timesheet.itervalues():
				for hours in worker.itervalues():
					hrs += float(hours)  # grab second item in list
		return hrs

	@property
	def cost(self):
		""" Calculates jobs cost total/progress taking into account materials purchased and labor paid.
		:returns: float for projected cost.
		"""
		amt = 0.0
		for i in self.timesheets.itervalues():
			amt += (float(i[1]) * float(self.rate))
		for i in self.POs.itervalues():
			amt += i.quote.price
		return amt

	# Task Functions #

	def add_task(self, task_obj):
		"""
		Blindly adds task object to self
		:param task_obj: task object to add to self.tasks
		:return: None
		"""
		self.tasks[task_obj.hash] = task_obj
		self.update()

		log.logger.info('Added task object "%s" to %s' % (task_obj.name, self.name))

	def del_task(self, task_hash):
		"""
		Delete task object from self.tasks
		:param task_hash: hash of task object to delete from internal db
		:return: None
		"""
		del self.tasks[task_hash]
		self.update()

		log.logger.info('Deleted %s task from %s' % (task_hash, self.name))

	# Misc Functions #

	@property
	def sheet_name(self):
		if hasattr(self, 'number'):
			return ' - '.join([str(self.number), str(self._name)])

	@staticmethod
	def find(num):
		if hasattr(AwardedJob, 'db'):
			return AwardedJob.db[num]


def get_job_num(*args):
	try:
		if hasattr(AwardedJob, 'db'):
			_keys = AwardedJob.db.keys()
			_keys.sort()  # sort tuple of keys so that highest number is on right
			num = int(_keys[-1]) + 1
			return num
	except IndexError:
		# no bids in database. assume a jobs number of 1
		return 1
