import yaml
import traceback

from objects import *
import core.environment as env
import core.log as log


class Worker(object):
	# pay rate constants
	A_RATE = 100.84
	A_RATE_journeyman = 97.38
	B_RATE = 51.76

	def __init__(self, name, job, phone=None, email=None, role='Installer', rate=None):
		"""
		Initializes employee representation object.
		:param name: employee's name. hash/key is created from this variable.
		:param job: current jobs that employee is at. if changed, the previous jobs will be added to self.prev_jobs
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
		""" Alters attribute setting to listen to when self.jobs is changed,
			the previous jobs is stored in self.prev_jobs
		"""
		if name is 'jobs':
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
			return Worker.db[q_hash]

	def update(self):
		"""
		Function re-initializes self.hash as the dictionary key pointed to self. Also adds itself to self.jobs.workers.
		:return: None
		"""
		if hasattr(Worker, 'db') and hasattr(self, 'hash'):
			Worker.db[self.hash] = self
			if hasattr(self, 'jobs'):
				self.job.add_worker(self)
		return None


class Job(object):

	valid_scope = ('M', 'E', 'B', 'I', 'P', 'fabrication')

	_yaml_filename = '.job_info.yaml'
	_yaml_attr = ['end_date', 'alt_name', 'address', 'gc_contact', 'scope', 'desc', 'tax_exempt', 'certified_pay']

	def __init__(self, name, date_received=None, date_end=None, alt_name=None, address=None, gc=None,
	             gc_contact=None, scope=None, desc=None, rate='a', tax_exempt=False, certified_pay=False):
		self._update = False
		self._name = str(name)
		self.date_received = date_received
		self.alt_name = alt_name
		self.address = address
		self.gc = gc
		self.gc_contact = gc_contact
		# validate scope argument and then add to self
		try:
			self.scope = []
			for i in scope:
				if i in Job.valid_scope:
					self.scope.append(i)
		except TypeError:
			self.scope = scope

		self.desc = desc
		if rate is 'a':
			self.rate = Worker.A_RATE
		elif rate is 'b':
			self.rate = Worker.B_RATE
		self.tax_exempt = tax_exempt
		self.certified_pay = certified_pay

		self.documents = {}
		self.drawings = {}

		self._update = True

	@property
	def name(self):
		if hasattr(self, 'number'):
			return '-'.join([str(self.number), str(self._name)])

	def __setattr__(self, key, value):
		_return = super(Job, self).__setattr__(key, value)

		# do not update yaml file or call self.update() if self is still initializing
		_caller = traceback.extract_stack(None, 2)[0][2]
		if _caller is not '__init__':
			self.dump_info()
			self.update()
		return _return

	def __repr__(self):
		return self.name

	def update(self):
		if hasattr(self, 'db') and hasattr(self, 'number'):
			self.db[self.number] = self
		# self.dump_info()

	def load_info(self):
		_data_file = os.path.join(self.path, self._yaml_filename)
		try:
			_data = open(_data_file, 'r')
			_data = yaml.load(_data)
			for i in self._yaml_attr:
				_val = _data[i]
				# load values from .yaml file to self
				self.__setattr__(i, _val)
		except IOError:
			self.dump_info()

	def dump_info(self):
		# dump values from self to .yaml file
		_data = {}
		for i in self._yaml_attr:
			try:
				_val = self.__getattribute__(i)
				_data[i] = _val
			except AttributeError:
				continue

		if hasattr(self, 'path'):
			_filename = os.path.join(self.path, self._yaml_filename)
			_data_file = open(_filename, 'w')
			yaml.dump(_data, _data_file, default_flow_style=False)
			_data_file.close()


class AwardedJob(Job):

	Job._yaml_attr.append('po_pre')
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

		self._PO = 0    # stores most recent PO suffix number
		self.POs = {}   # stores PO strings as keys
		self.workers = {}
		self.materials = {}
		self.quotes = {}
		self.deliveries = {}
		self.tasks = {}
		# AwardedJob.timesheets.key is datetime.datetime object for the week-ending
		# AwardedJob.timesheets.value is [ 'pathname/to/timesheet', { worker.hash: (worker, hours) } ]
		self.timesheets = {}

		self.sub_path = os.path.join(self.default_sub_dir, self.name)
		if init_struct:
			self.init_struct()
		self.load_info()

		log.logger.info('Created \'%s\' AwardedJob object' % self.name)

	@property
	def sheet_name(self):
		if hasattr(self, 'number'):
			return ' - '.join([str(self.number), str(self._name)])

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

	def init_struct(self):
		""" Initializes project directory hierarchy. """
		# TODO:initialize documents w/ jobs information
		try:
			os.mkdir(os.path.join(env.env_root, self.sub_path))
			log.logger.debug('Created project directory for "%s"' % self.name)
		except OSError:
			log.logger.warning("...project folder already exists")

		log.logger.debug("Creating project sub directories for %s..." % self.name)
		_folders = ('Addendums', 'Billing', 'Change Orders', 'Close Out', 'Contract Scope', 'Documents',
					'Drawings', 'Materials', 'Quotes', 'RFIs', 'Specs', 'Submittals')
		for _folder in _folders:
			try:
				os.mkdir(os.path.join(env.env_root, self.sub_path, _folder))
				log.logger.debug('Created sub directory, \'%s\', for \'%s\'' % (_folder, self.name))
			except OSError:
				log.logger.warning('Sub directory, "%s", for %s already exists!' % (_folder, self.name))

	@property
	def path(self):
		""" Return absolute sub path using global project path and AwardedJob.sub_path """
		_path = os.path.join(env.env_root, self.sub_path)
		return _path

	@property
	def labor(self):
		""" Calculates labor totals """
		hrs = 0.0
		for i in self.timesheets.itervalues():
			hrs += float(i[1])  # grab second item in list
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

	@property
	def has_open_lists(self):
		"""
		Returns 0 if jobs has no open material lists
		:return: Integer of material lists that have not been purchased.
		"""
		open_lists = 0
		for mlist in self.materials.itervalues():
			if not mlist.fulfilled:
				open_lists += 1
		return open_lists

	def add_task(self, task_obj):
		"""
		Blindly adds task object to self
		:param task_obj: task object to add to self.tasks
		:return: None
		"""
		self.tasks[task_obj.hash] = task_obj
		self.update()

		log.logger.info('Added task object "%s" to %s' % (task_obj.name, self.name))

	def add_mat_list(self, mlist_obj):
		"""
		Blindly adds material list object to self.
		:param mlist_obj: material list object to add to self
		:return: None
		"""
		self.materials[mlist_obj.hash] = mlist_obj
		self.update()

		log.logger.info('Added material list %s (%s) to %s' % (mlist_obj.hash, mlist_obj.items, self.name))

	def add_quote(self, quote_obj):
		"""
		Blindly adds quote object to self.
		:param quote_obj: quote object to add to self
		:return: None
		"""
		_mat_list = quote_obj.mat_list.hash
		self.quotes[quote_obj.hash] = quote_obj
		self.materials[_mat_list].add_quote(quote_obj)
		self.update()

		log.logger.info('Added quote object from "%s" to "%s" material list for %s' % (quote_obj.vend, _mat_list, self.name))

	def add_delivery(self, deliv_obj):
		"""
		Blindly adds delivery object to self.
		:param deliv_obj: delivery object to add to self
		:return: None
		"""
		self.deliveries[deliv_obj.hash] = deliv_obj
		self.update()

		log.logger.info('Scheduled delivery on %s for %s' % (deliv_obj.expected, self.name))

	def add_po(self, po_obj):
		"""
		Blindly adds PO object to self.
		:param po_obj: PO object to add to self.
		:return: None
		"""
		self.POs[po_obj.number] = po_obj
		_mat_list = po_obj.mat_list.hash
		self.materials[_mat_list].po = po_obj
		self.materials[_mat_list].fulfilled = True
		self.update()

		log.logger.info('Awarded %s to %s for %s' % (po_obj.name, po_obj.vend, self.name))

	def add_worker(self, wrkr_obj):
		"""
		Blindly adds worker object to self.
		:param wrkr_obj: Worker object to add to self
		:return: None
		"""
		self.workers[wrkr_obj.hash] = wrkr_obj
		self.update()

		log.logger.info('"%s" has been added to %s project' % (wrkr_obj.name, self.name))

	def del_material_list(self, mlist_hash, delete=False):
		"""
		Deletes material list object from self.materials
		:param mlist_hash: hash to delete from self.materials
		:param delete: if True is passed, then the document is deleted from the filesystem
		:return: None
		"""
		for i in self.POs.values():
			if i.mat_list.hash == mlist_hash:
				del self.POs[i.number]
		for i in self.quotes.values():
			if i.mat_list.hash == mlist_hash:
				del self.quotes[i.hash]
		del self.materials[mlist_hash]

		if delete:
			# TODO:delete document in filesystem
			pass
		self.update()

		if not delete:
			log.logger.info('Deleted %s material list from %s' % (mlist_hash, self.name))

	def del_quote(self, quote_hash, delete=False):
		"""
		Deletes quote object from self.quotes
		:param quote_hash: hash to delete from self.quotes
		:param delete: if True is passed, then the document is deleted from the filesystem
		:return: None
		"""
		for i in self.materials.values():
			if quote_hash in i.quotes.keys():
				del i.quotes[quote_hash]
		for i in self.POs.values():
			if i.quote.hash == quote_hash:
				del self.POs[i.number]
		del self.quotes[quote_hash]

		if delete:
			# TODO:delete document in filesystem
			pass
		self.update()

		if not delete:
			log.logger.info('Deleted %s material list from %s' % (quote_hash, self.name))

	def del_task(self, task_hash):
		"""
		Delete task object from self.tasks
		:param task_hash: hash of task object to delete from internal db
		:return: None
		"""
		del self.tasks[task_hash]
		self.update()

		log.logger.info('Deleted %s task from %s' % (task_hash, self.name))

	@staticmethod
	def find(num):
		if hasattr(AwardedJob, 'db'):
			return AwardedJob.db[num]
