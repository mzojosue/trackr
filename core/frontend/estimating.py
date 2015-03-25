from config import *

@app.route('/estimating')
def estimating_home():
	return render_template('estimating.html')

@app.route('/estimating/analytics')
def estimating_analytics():
	return NotImplemented

@app.route('/estimating/bids/current')
def current_bids():
	if hasattr(EstimatingJob, 'db'):
		_estimates = EstimatingJob.db.itervalues()
		return render_template('current_bids.html', estimates=_estimates)

@app.route('/estimating/bids/past')
def past_bids():
	return NotImplemented

@app.route('/estimating/bid/<int:bid_num>/overview')
def bid_overview(bid_num):
	if hasattr(EstimatingJob, 'db'):
		try:
			_bid = EstimatingJob.find(bid_num)
			return render_template('estimating_bid.html', bid=_bid)
		except KeyError:
			return "Error: Bid does not exist."

@app.route('/estimating/bid/<int:bid_num>/documents')
def bid_documents(bid_num):
	if hasattr(EstimatingJob, 'db'):
		try:
			_bid = EstimatingJob.find(bid_num)
			return render_template('bid_documents.html', bid=_bid)
		except KeyError:
			return "Error: Bid does not exist."

@app.route('/estimating/bid/<int:bid_num>/drawings')
def bid_drawings(bid_num):
	if hasattr(EstimatingJob, 'db'):
		try:
			_bid = EstimatingJob.find(bid_num)
			return render_template('bid_drawings.html', bid=_bid)
		except KeyError:
			return "Error: Bid does not exist."
