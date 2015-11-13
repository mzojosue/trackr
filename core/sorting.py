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


def sort_jobs(container, value='number', reverse=False):
	return sorted(container, key=attrgetter(value), reverse=reverse)


def sort_bids(container, value='number', reverse=True):
	""" Sorts bid objects according to given value. Defaults to sort bids by value, with highest bid number first.
	Separates bids w/o bid date when sorting by bid_date to account for 'ASAP' values.
	:param container: Container containing bids to sort
	:param value: Value to get and compare
	:param reverse: Defaults to True; higher values are shown first.
	:return: Returns sorted container
	"""
	# TODO: enable option to sort by bid_date
	return sorted(container, key=attrgetter(value), reverse=reverse)
