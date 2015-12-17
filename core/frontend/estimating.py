from werkzeug import secure_filename
import json

from job import *
from core.sorting import *


##############################
#** ROUTE/RENDER Functions **#

@app.route('/estimating')
def estimating_home():
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	return render_template('estimating/estimating.html', usr=auth)


@app.route('/estimating/bids/current', defaults={'sort_by': 'number'})
@app.route('/estimating/bids/current/sort/<sort_by>')
def current_bids(sort_by):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	if hasattr(EstimatingJob, 'db'):
		_estimates = EstimatingJob.db.values()
		_estimates = sort_bids(_estimates, sort_by)
		return render_template('estimating/current_bids.html', estimates=_estimates, usr=auth)


@app.route('/estimating/bids/past', defaults={'sort_by': 'number'})
@app.route('/estimating/bids/past/sort/<sort_by>')
def past_bids(sort_by):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login

	if hasattr(EstimatingJob, 'completed_db'):
		_estimates = EstimatingJob.completed_db.values()
		_estimates = sort_bids(_estimates, sort_by)
		return render_template('estimating/past_bids.html', estimates=_estimates, usr=auth)

@app.route('/estimating/analytics')
def estimating_analytics():
	return NotImplemented

@app.route('/estimating/bid/<int:bid_num>/overview')
def bid_overview(bid_num):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	if hasattr(EstimatingJob, 'db'):
		try:
			_bid = EstimatingJob.find(bid_num)
			return render_template('estimating/bid_overview.html', bid=_bid, usr=auth)
		except KeyError:
			return "Error: Bid does not exist."


@app.route('/estimating/bid/<int:bid_num>/calculate')
def bid_calculate(bid_num):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	if hasattr(EstimatingJob, 'db'):
		try:
			_bid = EstimatingJob.find(bid_num)
			return render_template('estimating/bid_calculate.html', bid=_bid, usr=auth)
		except KeyError:
			return "Error: Bid does not exist."


@app.route('/estimating/bid/<int:bid_num>/info', methods=['GET', 'POST'])
def bid_info(bid_num):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth
	if hasattr(EstimatingJob, 'db'):
		try:
			_bid = EstimatingJob.find(bid_num)
			return render_template('estimating/bid_info.html', bid=_bid, usr=auth)
		except KeyError:
			return "Error: Bid does not exist."


@app.route('/estimating/bid/<int:bid_num>/dir/<path:dir>')
def bid_folder(bid_num, dir):
	""" Renders given directory as page. Renders specific pages for 'Drawings', and 'Takeoffs'.
	:param bid_num: bid number to select
	:param dir: directory to iterate over and render
	:return:
	"""
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	if hasattr(EstimatingJob, 'db'):
		try:
			_bid = EstimatingJob.find(bid_num)
			if dir == 'Drawings':
				return render_template('estimating/bid_drawings.html', bid=_bid, usr=auth)
			else:
				_dir = os.path.join(_bid.path, dir)
				contents = _bid.dump_folder(_dir)
				return render_template('estimating/bid_folder.html', bid=_bid, usr=auth, dir=contents, current_page=dir)
		except KeyError:
			return "Error: Bid does not exist."


@app.route('/estimating/bid/<int:bid_num>/drawings')
def bid_drawings(bid_num):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	if hasattr(EstimatingJob, 'db'):
		try:
			_bid = EstimatingJob.find(bid_num)
			return render_template('estimating/bid_drawings.html', bid=_bid, usr=auth)
		except KeyError:
			return "Error: Bid does not exist."


@app.route('/estimating/bid/<int:bid_num>/takeoffs')
def bid_takeoffs(bid_num):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	if hasattr(EstimatingJob, 'db'):
		try:
			_bid = EstimatingJob.find(bid_num)
			return render_template('estimating/bid_takeoffs.html', bid=_bid, usr=auth)
		except KeyError:
			return "Error: Bid does not exist."


#######################
#** Estimating API **##


@app.route('/estimating/create', methods=['GET', 'POST'])
def create_bid():
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	if request.method == 'POST':
		data = json.loads(request.data)

		try:
			data['bid_date'] = datetime.strptime(data['bid_date'], '%Y-%m-%d')
		except KeyError:
			data['bid_date'] = None
		tmp = data['bid_date']
		del data['bid_date']
		data['date_end'] = tmp

		_scope = []
		for val, _bool in data['scope'].iteritems():		# decompress scope to List
			if _bool:
				_scope.append(val)
		data['scope'] = _scope

		print data

		bid = EstimatingJob(add_to_log=False, **data)
		return url_for('bid_overview', bid_num=bid.number)
	else:
		return render_template('estimating/estimating_create.html', usr=auth)


# Bid Completion Functions #

@app.route('/estimating/bid/<int:bid_num>/award/<int:bid_hash>')
def award_bid(bid_num, bid_hash):
	bid = EstimatingJob.find(bid_num)
	job = bid.award_bid(bid_hash)
	return redirect(url_for('job_overview', job_num=job.number))


@app.route('/estimating/bid/<int:bid_num>/cancel')
def cancel_bid(bid_num):
	""" Moves calls EstiamtingJob.complete_bid to separate submitted bids from unsubmitted ones.
	:param bid_num: Desired bid to complete
	:return:
	"""
	_bid = EstimatingJob.find(bid_num)
	_bid.cancel_bid()
	#TODO: somehow show feedback that bid was successfully moved
	return redirect(request.referrer)


@app.route('/estimating/bid/<int:bid_num>/complete')
def complete_bid(bid_num):
	""" Moves calls EstimatingJob.complete_bid to separate submitted bids from unsubmitted ones.
	:param bid_num: Desired bid to complete
	:return:
	"""
	_bid = EstimatingJob.find(bid_num)
	_bid.complete_bid()
	#TODO: somehow show feedback that bid was successfully moved
	return redirect(request.referrer)


@app.route('/estimating/bid/<int:bid_num>/delete')
def delete_bid(bid_num):
	""" Removes the existence of bid object via passed `bid_num`
	:param bid_num: Bid object to delete
	:return: Redirects page to `request.referrer`
	"""
	auth = check_login()  # verify that user has admin privileges
	if not hasattr(auth, 'passwd'):
		return auth
	_bid = EstimatingJob.find(bid_num)
	if _bid.delete_bid():
		return redirect(url_for('current_bids'))


# Sub Bid API #

@app.route('/estimating/bid/<int:bid_num>/sub/create', methods=['POST'])
def create_sub_bid(bid_num):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	_bid = EstimatingJob.find(bid_num)
	_gc = request.form['gcName']
	_gc_contact = request.form['gcContact']
	try:
		_bidDate = datetime.strptime(request.form['bidDate'], '%Y-%m-%d')
	except ValueError:
		_bidDate = None


	_scope = []
	__scope = ['materialsScope', 'equipmentScope', 'insulationScope', 'balancingScope']
	for i in __scope:
		try:
			if bool(request.form[i]):    # see if form with same id label returns bool
				__s = str(i[0]).upper()
				_scope.append(__s)       # append first letter to scope
		except:
			continue

	_sub_kwargs = {datetime.now(), _gc, _bidDate, _gc_contact, _scope}
	print _sub_kwargs
	_bid.add_sub(_sub_kwargs)
	return redirect(url_for('bid_overview', bid_num=_bid.number))


@app.route('/estimating/bid/<int:bid_num>/sub/<sub_hash>/delete')
def delete_sub_bid(bid_num, sub_hash):
	return NotImplemented



@app.route('/estimating/bid/<int:bid_num>/sub/<sub_hash>/cancel')
def cancel_sub_bid(bid_num, sub_hash):
	return NotImplemented


@app.route('/estimating/bid/<int:bid_num>/sub/<sub_hash>/award')
def award_sub_bid(bid_num, sub_hash):
		return NotImplemented


@app.route('/estimating/bid/<int:bid_num>/subs/update', methods=['POST'])
def update_sub_bid(bid_num):
	""" Updates sub bid attributes based on hardcoded attribute list ('gc', 'gc_contact', 'bid_date').
	Parses bid_date as datetime object.
	:param bid_num: Type int representing bid to update
	:param sub_hash: Sub bid to edit
	:return: Redirects to referring page
	"""
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	bid = EstimatingJob.find(bid_num)

	_json = json.loads(request.data)

	for _hash, data in _json.iteritems():
		tmp = {}
		for key, val in data.iteritems():				# load data to `tmp`
			tmp[key] = val

		tmp['date_received'] = datetime.strptime(tmp['date_received'], '%Y-%m-%d')
		tmp['bid_date'] = datetime.strptime(tmp['bid_date'], '%Y-%m-%d')

		_scope = []
		for val, _bool in tmp['scope'].iteritems():		# decompress scope to List
			if _bool:
				_scope.append(val)
		tmp['scope'] = _scope

		bid.bids[_hash] = tmp
		print tmp

	bid.update()
	return json.dumps(bid.bids)


# Bid Quote API #

@app.route('/estimating/<int:bid_num>/quote/<scope>/<int:q_hash>')
def bid_quote(bid_num, scope, q_hash):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	_bid = EstimatingJob.find(bid_num)
	_quote = _bid.quotes[scope][q_hash]
	return send_from_directory(*_quote.doc)


@app.route('/estimating/<int:bid_num>/quote/upload', methods=['POST'])
def upload_bid_quote(bid_num):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	_bid = EstimatingJob.find(bid_num)
	_scope = request.form['scope']
	_vend  = request.form['vendor']
	_price = request.form['quotePrice']

	_quote = request.files['quote']

	quote = EstimatingQuote(_bid, _vend, _scope, _price, _quote)

	if _quote and allowed_file(_quote.filename):
		filename = secure_filename(_quote.filename)
		quote._doc = filename
		quote.update()
		_path = os.path.join(*quote.doc)
		_quote.save(_path)
	return redirect(url_for('bid_overview', bid_num=_bid.number))


@app.route('/estimating/<int:bid_num>/quote/<int:q_hash>/update')
def update_bid_quote(bid_num, q_hash):
	""" Updates specified EstimatingQuote object. Meant to change price or add quote after quote has been added to EstimatingJob object.
	:param bid_num: bid number to search for quote in
	:param q_hash: quote to update
	:return: u
	"""
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	return NotImplemented


@app.route('/estimating/<int:bid_num>/quote/<int:q_hash>/del')
def delete_bid_quote(bid_num, q_hash):
	""" Deletes specified EstimatingQuote object from specified EstimatingJob object.
	:param bid_num:
	:param q_hash:
	:return:
	"""
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	return NotImplemented


# Bid Pricing API #

@app.route('/estimating/<int:bid_num>/pricing/section/create', methods=['POST'])
def create_section(bid_num):
	_data = json.loads(request.data.decode())
	print _data
	return "true"

@app.route('/estimating/bid/<int:bid_num>/pricing/available_items')
def get_available_items(bid_num):
	""" Returns all available items with AngularJS hooks in a JSON format
	:param bid_num:
	"""
	_return = {}
	bid = EstimatingJob.find(bid_num)
	for _scope in bid.scope:
		_return[_scope] = {}
		for key, obj in SectionItem.available_items[_scope].iteritems():

			_return[_scope][key] = {'id': key,
									'label': obj.label,
									'metric': obj.metric,
									'units': obj.units,
									'value': obj.value,
									'scope': obj.scope}
	return json.dumps(_return)


# Misc Bid API Routes #

@app.route('/estimating/bids/json')
def estimating_serialized_overview():
	""" Aggregates current bids based on due_dates via JSON. Used for Bootstrap Calender.
	:return: JSON containing Bid objects
	"""
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login

	# Grab 'from' and 'to' GET requests
	#TODO: implement 'from' and 'to' as search queries
	date_scope = [request.args.get('from'), request.args.get('to')]

	result = ['id', 'title', 'url', 'class', 'start', 'end']
	grab = ['hash', 'name', 'number', 'countdown', 'timestamp', 'timestamp']
	if hasattr(EstimatingJob, 'db'):
		_estimates = []
		for estimate in EstimatingJob.db.itervalues():
			_bid = {}
			for i, z in zip(result, grab):
				_bid[i] = estimate.__getattribute__(z)
			_bid['url'] = url_for('bid_overview', bid_num=_bid['url'])
			# TODO: format class value based on completion/countdown status
			_bid['class'] = 'event-success'
			# TODO: format start and end values
			_estimates.append(_bid)
		_return = {"success": 1,
				   "result": _estimates}
		return json.dumps(_return)

@app.route('/estimating/bid/<int:bid_num>/drawings/<dwg_name>')
def bid_drawing_doc(bid_num, dwg_name):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	_bid = EstimatingJob.find(bid_num)
	doc = _bid.drawings[dwg_name]  # extract returned dict
	if doc:
		dir = os.path.split(doc['path'])
		return send_from_directory(*dir)


@app.route('/estimating/bid/<int:bid_num>/get/<path:query>')
def bid_get_document(bid_num, query):

	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	_bid = EstimatingJob.find(bid_num)
	doc = os.path.join(_bid.path, query)
	print os.path.isfile(doc)
	if os.path.isfile(doc):
		return send_from_directory(*os.path.split(doc))


@app.route('/estimating/bid/<int:bid_num>/update', methods=['POST'])
def update_bid_info(bid_num):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	_bid = EstimatingJob.find(bid_num)
	_bid.desc = str(request.form['bidDesc'])
	return redirect(request.referrer)


@app.route('/estimating/json/valid_scope')
def serialized_valid_scope():
	_result = {}
	for scope in EstimatingJob.valid_scope:
		_result[scope] = False
	return json.dumps({"success": 1,
					   "result": _result})


@app.route('/estimating/bid/<int:bid_num>/bids/json')
def serialized_sub_bids(bid_num):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth
	_bid = EstimatingJob.find(bid_num)
	_result = copy(_bid.bids)
	for b in _result.itervalues():
		epoch = datetime(1969, 12, 31)  # why does this work???

		for _date in ('date_received', 'bid_date'):
			try:
				dt = b[_date]  		# format datetime object
				b[_date] = (dt - epoch).total_seconds() * 1000
			except TypeError:
				continue

		tmp = {}						# expand scope arguments to dict contained bool values
		for scope in EstimatingJob.valid_scope:
			if scope in b['scope']:
				tmp[scope] = True
			else:
				tmp[scope] = False
		b['scope'] = tmp

	return json.dumps({"success": 1,
	                   "result": _result})