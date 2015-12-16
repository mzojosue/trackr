from datetime import datetime

today = datetime.today
now = datetime.now

class ObjectStore(object):
	def __init__(self, key_value='hash'):
		self.store = []
		self.last_updated = None

		self._key_value = key_value

	def __repr__(self):
		"""
		:return: A dict object containing objects from self.store w/ self._key_value as key object
		"""
		_return = {}
		for i in self.store:
			if hasattr(i, self._key_value) and getattr(i, self._key_value):
				_return[getattr(i, self._key_value)] = i

		return _return

	def __getitem__(self, item):
		for _obj in self.store:
			if getattr(_obj, self._key_value) == item:
				return _obj
		raise KeyError

	def __delitem__(self, key):
		for _obj in self.store:
			if getattr(_obj, self._key_value) == key:
				del _obj
				return None
		raise KeyError

	def __setitem__(self, key, value):
		if hasattr(value, self._key_value):
			if getattr(value, self._key_value) == key:
				self.store.append(value)

	def __iter__(self):
		for _obj in self.store:
			if hasattr(_obj, self._key_value):
				yield getattr(_obj, self._key_value), _obj

	def iteritems(self):
		return self.__iter__()

	def itervalues(self):
		for _obj in self.store:
			yield _obj

	def iterkeys(self):
		for _obj in self.store:
			if hasattr(_obj, self._key_value):
				yield getattr(_obj, self._key_value)

	def values(self):
		return self.store