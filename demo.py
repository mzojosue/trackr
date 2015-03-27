from trackr import *
from random import sample

amt = 10

# create 10 dummy estimate jobs
for i in xrange(amt):
	print 'creating mock bid #%d' % i
	core.EstimatingJob(i, 'test_bid_job', scope=['M', 'E', 'I'] )

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

for i in core.AwardedJob.db.itervalues():
	for z in i.materials.itervalues():
		quote = sample(z.quotes.values(), 1)[0]
		mat_list = quote.mat_list
		core.PO(i, mat_list=mat_list, quote=quote)


if __name__ == "__main__":
	core.app.run(host='0.0.0.0', port=8080, debug=True)