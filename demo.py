from trackr import *

# create 10 dummy estimate jobs
for i in xrange(1, 11):
	print 'create dummy bid #%d' % i
	core.EstimatingJob(i, 'test_bid_job', scope=['E-M', 'E-E', 'E-I'] )

if __name__ == "__main__":
	core.app.run(host='0.0.0.0', port=8080, debug=True)