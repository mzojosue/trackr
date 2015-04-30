from config import *


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
		_jobs = AwardedJob.db.itervalues()
		_timesheets = Timesheet.db.itervalues()
		return render_template('timesheets.html', timesheets=_timesheets, jobs=_jobs)

@app.route('/timesheets/upload')
def upload_timesheet():
	return abort(404)

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