import objects as obj

from datetime import datetime
from operator import attrgetter


def sort_pos(container, value='number', reverse=False):
	if value == 'date_issued':
		_container = []
		for i in container:
			if type(i.date_issued) is datetime:
				_container.append(i)
		container = _container
	return sorted(container, key=attrgetter(value), reverse=reverse)