from config import *
from datetime import datetime

@app.route('/estimating')
def estimating_home():
	return render_template('estimating.html')

@app.route('/estimating/create', methods=['GET', 'POST'])
def estimating_create_bid():
	if request.method == 'POST':
		_name = str(request.form['newBidName'])
		_addr = str(request.form['jobAddress'])
		_gc   = str(request.form['gc'])
		_gcContact = str(request.form['gcContact'])
		try:
			_bidDate = datetime(*request.form['bidDate'])
		except:
			_bidDate = None

		_scope = []
		__scope = ['materialsScope', 'equipmentScope', 'insulationScope', 'balancingScope']
		for i in __scope:
			try:
				if bool(request.form[i]):
					__s = str(i[0])
					__s = __s.upper()
					_scope.append(__s)
			except:
				continue

		bid = EstimatingJob(_name, address=_addr, gc=_gc, gc_contact=_gcContact, scope=_scope, date_end=_bidDate)
		return redirect(url_for('bid_overview', bid_num=bid.number))
	else:
		return render_template('estimating_create.html')

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
