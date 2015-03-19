from trackr import *

# create 10 dummy estimate jobs
for i in xrange(1, 11):
	print 'creating mock bid #%d' % i
	core.EstimatingJob(i, 'test_bid_job', scope=['M', 'E', 'I'] )

# create 10 dummy jobs
for i in xrange(1, 11):
	print "creating mock AwardedJob %d" % i
	_job = core.AwardedJob(i, 'test_job')
# create 10 dummy material lists for each job
	for z in xrange(1, 11):
		print "creating mock material list (%d) for %s" % (z, _job.name)
		core.MaterialList(_job, items={'1', 'test item'})

if __name__ == "__main__":
	core.app.run(host='0.0.0.0', port=8080, debug=True)