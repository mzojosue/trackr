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
		if hasattr(self, 'jobs'):
			try:
				self.job.del_task(self.hash)
				print "deleted task from jobs.tasks"
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
		if hasattr(self, 'jobs'):
			self.job.add_task(self)
		if hasattr(self, 'target'):
			self.target.add_task(self)
