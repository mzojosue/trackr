from config import *
import json

@app.route('/upload/<filename>')
def uploaded_file(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/')
def root():
	return redirect(url_for('login'))



################
## Home pages ##


## _Todo functions ##
@app.route('/home')
def home():
	auth = check_login()
	if auth is not True:
		return auth  # redirects to login
	if hasattr(Todo, 'db') and hasattr(MaterialList, 'db') and hasattr(AwardedJob, 'db'):
		_todos = Todo.db.itervalues()
		_completed = Todo.completed_db.itervalues()
		_jobs = AwardedJob.db.itervalues()
		_lists = MaterialList.db.itervalues()
		return render_template('dashboard.html', jobs=_jobs, lists=_lists, todos=_todos, completed=_completed)
	else:
		# TODO:display db error on page
		return render_template('dashboard.html')


@app.route('/overview/json')
def serialized_overview():
	""" Sums up all events occuring within given timestamps. Pulls upcoming deliveries, bid due dates, and other key dates. """
	auth = check_login()
	if auth is not True:
		return auth  # redirects to login

	# Grab 'from' and 'to' GET requests
	#TODO: implement 'from' and 'to' as search queries
	date_scope = [request.args.get('from'), request.args.get('to')]

	result = ['id', 'title', 'url', 'class', 'start', 'end']
	_results = []

	# Estimating Variables to grab
	grab = ['number', 'name', 'number', 'countdown', 'bid_timestamp', 'bid_timestamp']
	if hasattr(EstimatingJob, 'completed_db'):
		_estimates = []
		for estimate in EstimatingJob.completed_db.itervalues():
			_bid = {}
			for i, z in zip(result, grab):
				_bid[i] = estimate.__getattribute__(z)
			_bid['url'] = url_for('bid_overview', bid_num=_bid['url'])
			# TODO: format class value based on countdown
			_bid['class'] = 'event-special'
			# TODO: format start and end values
			_estimates.append(_bid)
		_results.extend(_estimates)

	# Delivery variables to grab
	grab = ['hash', 'label', 'hash', 'countdown', 'timestamp', 'timestamp']
	if hasattr(Delivery, 'db'):
		_deliveries = []
		for delivery in Delivery.db.itervalues():
			_deliv = {}
			for i, z in zip(result, grab):
				_deliv[i] = delivery.__getattribute__(z)

			_deliv['url'] = url_for('material_list', m_hash=delivery.mat_list.hash)
			_deliv['class'] = 'event-info'
			#TODO: format start and end values
			_deliveries.append(_deliv)
		_results.extend(_deliveries)

	_return = {"success": 1, "result": _results}
	return json.dumps(_return)


@app.route('/inventory')
def inventory():
	auth = check_login()
	if auth is not True:
		return auth  # redirects to login
	if hasattr(InventoryItem, 'db'):
		_inventory = InventoryItem.db.itervalues()
		return render_template('inventory.html', inventory=_inventory)

@app.route('/inventory/item', methods=['POST'])
def new_inventory_item():
	auth = check_login()
	if auth is not True:
		return auth  # redirects to login
	_item_id = request.form['itemID']
	_item_label = request.form['itemLabel']
	InventoryItem(_item_id, _item_label)
	return redirect(request.referrer)

@app.route('/inventory/order', methods=['POST'])
def inventory_item_order():
	auth = check_login()
	if auth is not True:
		return auth  # redirects to login
	_item = InventoryItem.find(request.form['itemOrderID'])
	_vend_name = request.form['vendorName']
	_order_price = request.form['orderPrice']
	_order_amount = request.form['orderAmount']
	InventoryOrder(_item, _order_price, _vend_name, _order_amount)
	return redirect(request.referrer)

@app.route('/inventory/<int:item_hash>/del')
def del_inventory_item(item_hash):
	auth = check_login()
	if auth is not True:
		return auth  # redirects to login
	_item = InventoryItem.find(item_hash)
	if _item.orders and hasattr(InventoryOrder, 'db'):
		for i in _item.orders:
			del InventoryOrder.db[i]
	if hasattr(InventoryItem, 'db'):
		del InventoryItem.db[item_hash]
	return redirect(request.referrer)


@app.route('/timesheets')
def timesheets():
	auth = check_login()
	if auth is not True:
		return auth  # redirects to login
	if hasattr(Timesheet, 'db'):
		_jobs = sort_jobs(AwardedJob.db.values())
		_timesheets = Timesheet.db.itervalues()
		return render_template('timesheets.html', timesheets=_timesheets, jobs=_jobs)

@app.route('/timesheets/upload', methods=('POST', 'GET'))
def upload_timesheet():
	job = int(request.form['jobSelect'])
	job = AwardedJob.db[job]

	week_ending = datetime.strptime(request.form['weekEnding'], '%Y-%m-%d')

	workerCount = int(request.form['workerCounter']) + 1
	workerLines = {}
	for i in range(1, workerCount):
		_name = 'workerName_%d' % i
		_name = request.form[_name]
		_worker = Worker.get_set_or_create(_name, job)

		_work_week = []
		_days = ('thurs', 'fri', 'sat', 'mon', 'tue', 'wed')
		for _day in _days:
			_hours = '%s_Hours_%d' % (_day, i)
			_hours = int(request.form[_hours])
			_work_week.append(_hours)
		_work_week.insert(3, 0)                 # blank variable to account for Sunday

		_date = week_ending - timedelta(6)   # offset date to previous Thursday (week beginning)
		for hours in _work_week:
			if _date.isoweekday() is not 7:
				_worker.add_labor(hours, _date, week_ending, job)
			_date += timedelta(1)            # increment to next day
	return redirect(request.referrer)

@app.route('/analytics')
def analytics():
	return abort(404)

@app.route('/rentals')
def rental_log():
	return abort(404)

@app.route('/settings')
def user_settings():
	return abort(404)

@app.route('/help')
def help():
	return abort(404)

@app.route('/flash/test')
def flash_test():
	flash('test message', category='success')
	return redirect(request.referrer)