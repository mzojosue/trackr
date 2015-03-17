from objects import *
from operator import itemgetter

# Import parent classes for estimating objects
from job import Job
from material_cycle import Quote

class EstimatingJob(Job):
	def __init__(self, job_num, name, alt_name=None, date_received=today(), bid_date=None,
	             address=None, gc=None, gc_contact=None, scope=None, desc=None, rate='a',
	             tax_exempt=False, certified_pay=False, sub_path=None):
		# TODO: create function to grab next job number
		self.number = job_num

		super(EstimatingJob, self).__init__(name, date_received=date_received, date_end=bid_date, alt_name=alt_name,
		                                    address=address, scope=scope, desc=desc, rate=rate,
		                                    tax_exempt=tax_exempt, certified_pay=certified_pay)
		self.docs = {}
		self.quotes = {}
		self.bids = {}
		self.add_bid(date_received, gc, bid_date, gc_contact)

		for i in self.scope:
			# create sub-dictionaries for storing quotes by category/trade
			self.quotes[i] = {}

	@property
	def bid_date(self):
		return sorted(self.bids.values(), key=itemgetter('bid_date'))[0]['bid_date']

	@property
	def bidding_to(self):
		_gc = []
		for i in self.bids.itervalues():
			_gc.append(i['gc'])
		return _gc

	def update(self):
		return NotImplemented

	def add_bid(self, date_received, gc, bid_date='ASAP', gc_contact=None):
		_bid = {'gc': gc, 'gc_contact': gc_contact, 'bid_date': bid_date, 'date_received': date_received}
		_bid_hash = abs(hash(''.join([str(date_received), str(gc)])))
		self.bids[_bid_hash] = _bid
		return _bid

	def add_quote(self, quote_obj, category):
		if category in self.scope:
			self.bids[category][quote_obj.hash] = quote_obj
			self.update()

	def init_struct(self):
		# TODO:implement function to create filesystem hieracrchy to store documents, drawings, etc
		return NotImplemented


class EstimatingQuote(Quote):
	def __init__(self, job, vend, category, price=0.0, doc=None):
		super(EstimatingQuote, self).__init__(vend, price, doc)
		self.job = job
