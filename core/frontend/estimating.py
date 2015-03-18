from config import *

@app.route('/estimating')
def estimating_home():
	return render_template('estimating.html')

@app.route('/estimating/analytics')
def estimating_analytics():
	return NotImplemented

@app.route('/estimating/bids/current')
def current_bids():
	return NotImplemented

@app.route('/estimating/bids/past')
def past_bids():
	return NotImplemented

@app.route('/estimating/bid/<int:bid_num>')
def show_bid(bid_num):
	if hasattr(EstimatingJob, 'db'):
		try:
			_bid = EstimatingJob.find(bid_num)
			return render_template('estimating_bid.html', bid=_bid)
		except KeyError:
			return "Error: Bid does not exist."