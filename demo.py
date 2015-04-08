from trackr import *
from random import sample
from datetime import datetime

now = datetime.now

amt = 5

def dummy_env(update=False):
	# create 10 dummy estimate jobs and create one rebid
	for i in xrange(amt):
		print 'creating mock bid #%d' % i
		bid = core.EstimatingJob('test_bid_job_%d' % i, scope=['M', 'E', 'I'] )
		for z in bid.scope:
			core.EstimatingQuote(bid, 'test vendor', z, i, 'test.file')
		bid.add_bid(now(), 'test gc', 'ASAP', scope=['M', 'E'])

	# create 10 dummy jobs
	for i in xrange(amt):
		print "creating mock AwardedJob %d" % i
		_job = core.AwardedJob(i, 'test_job')

	# create 10 dummy material lists for each job
		for z in xrange(amt):
			print "creating mock material list (%d) for %s" % (z, _job)
			_list = core.MaterialList(_job, items={'1', 'test item'})

			for y in xrange(amt):
				print "creating mock quote (%d) for %s" % (y, _list)
				core.MaterialListQuote(_list, 'vend')

	# issue POs to a random quote for each material list for each job
	for i in core.AwardedJob.db.itervalues():
		for z in i.materials.itervalues():
			quote = sample(z.quotes.values(), 1)[0]
			mat_list = quote.mat_list
			core.PO(i, mat_list=mat_list, quote=quote, update=update)

def test_po_log():
	# TODO: implement page creation test
	core.reset_db()
	job = core.AwardedJob.db[5]
	mat = core.MaterialList(job)
	mat._doc = ('path/to', 'file')
	q = core.MaterialListQuote(mat, 'test vendor')
	q._doc = ('path/to', 'file')
	p = core.PO(job, mat, quote=q)
	core.reset_db()


if __name__ == "__main__":
	dummy_env()
	core.app.run(host='0.0.0.0', port=8080, debug=True)