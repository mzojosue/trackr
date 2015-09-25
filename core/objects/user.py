import hashlib
import uuid
import os
import traceback
from datetime import datetime

import yaml

from core.log import logger
import core.environment as env


today = datetime.today


class User(object):
	_yaml_filename = 'users.yaml'
	_yaml_attr = ('username', 'email', 'salt', 'passwd', 'date_created', 'role')

	_user_roles = ('admin', 'estimator')

	def __init__(self, name, username, email, passwd, role='admin', salt=None, date_created=today()):
		self.name = name
		self.username = username
		self.email = email
		self.hash = abs(hash(str(username) + str(date_created)))
		self.date_created = date_created
		if not salt:
			self.passwd, self.salt = hash_secret(passwd)
		else:
			self.passwd = passwd
			self.salt = salt

		if role in self._user_roles:
			self.role = role
		else:
			self.role = None

		if hasattr(self, 'db'):
			self.db[self.hash] = self

		self.dump_info()

	def __setattr__(self, key, value):
		_return = super(User, self).__setattr__(key, value)
		_caller = traceback.extract_stack(None, 2)[0][2]
		if _caller is not '__init__':
			self.update()
		return _return

	def __repr__(self):
		return "'%s', %s" % (self.username, self.role)

	@staticmethod
	def find(query):
		"""
		:param query: string representing username or hash value
		:return: first object matching query
		"""
		if hasattr(User, 'db'):
			for _key, obj in User.db.iteritems():
				# TODO: detect multiple objects matching query
				if _key == query:
					return obj
				elif obj.username == str(query):
					return obj
		return False

	@staticmethod
	def load_users():
		""" Loads users from campano/users.yaml in root environment"""
		fname = os.path.join(env.env_root, User._yaml_filename)
		try:
			with open(fname, 'r') as _file_dump:
				_file_dump = yaml.load(_file_dump)
				try:
					for _uname, _attr in _file_dump.iteritems():
						_attr['name'] = _uname
						User(**_attr)
				except AttributeError:
					return False
			logger.info('Successfully imported users.yaml')
		except IOError:
			pass
		return True

	def dump_info(self):
		_filename = os.path.join(env.env_root, self._yaml_filename)
		try:
			with open(_filename, 'r') as _data_file:
				_dump = yaml.load(_data_file)
				try:
					if self.name in _dump:
						# TODO: update object instead of quitting
						return True
				except TypeError:
					pass
		except IOError:
			pass
		_data = {}
		for i in self._yaml_attr:
			try:
				_val = self.__getattribute__(i)
				_data[i] = _val
			except AttributeError:
				continue
		_data = {self.name: _data}

		with open(_filename, 'a') as _data_file:
			yaml.dump(_data, _data_file, default_flow_style=False)

	def update(self):
		"""
		Function re-initializes self.hash as the dictionary key pointed to self
		:return: None
		"""
		if hasattr(User, 'db') and hasattr(self, 'hash'):
			User.db[self.hash] = self
		return None


def hash_secret(secret, salt=None):
	"""Hashes the passed secret using salt. A new salt is created if None.
    ::params:
        secret:     the secret (password or pin) to hash
        salt:       the salt stored in memory

    ::returns:
        hash:       salted/hashed secret
        salt:       random salt used with hashing """
	if salt is None:
		salt = uuid.uuid4().hex
	# Create salt and hash the variables in memory

	secret = hashlib.sha512(str(secret) + salt).hexdigest()
	return secret, salt


def pass_auth(obj, value):
	"""Authenticates passwd against obj.passwd
	::params:
	    obj:    should be type User or str. str is converted to User.
	::returns:
	    True:   when passwd == obj.passwd
	    False:  when passwd != obj.passwd
	    0:      when user doesn't exist"""
	passwd = hash_secret(value, obj.salt)[0]  # extract hashed result from returned list
	if passwd == obj.passwd:
		return True
	else:
		return False