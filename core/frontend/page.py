from config import *


@app.route('/upload/<filename>')
def uploaded_file(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/')
def root():
	return redirect(url_for('home'))


################
## Home pages ##


## _Todo functions ##
@app.route('/home')
def home():
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
	if hasattr(InventoryItem, 'db'):
		_inventory = InventoryItem.db.itervalues()
		return render_template('inventory.html', inventory=_inventory)

@app.route('/inventory/item', methods=['POST'])
def new_inventory_item():
	_item_id = request.form['itemID']
	_item_label = request.form['itemLabel']
	InventoryItem(_item_id, _item_label)
	return redirect(request.referrer)

@app.route('/inventory/order', methods=['POST'])
def inventory_item_order():
	_item = InventoryItem.find(request.form['itemOrderID'])
	_vend_name = request.form['vendorName']
	_order_price = request.form['orderPrice']
	_order_amount = request.form['orderAmount']
	InventoryOrder(_item, _order_price, _vend_name, _order_amount)
	return redirect(request.referrer)

@app.route('/inventory/<int:item_hash>/del')
def del_inventory_item(item_hash):
	_item = InventoryItem.find(item_hash)
	if _item.orders and hasattr(InventoryOrder, 'db'):
		for i in _item.orders:
			del InventoryOrder.db[i]
	if hasattr(InventoryItem, 'db'):
		del InventoryItem.db[item_hash]
	return redirect(request.referrer)


@app.route('/timesheets')
def timesheets():
	if hasattr(Timesheet, 'db'):
		_jobs = AwardedJob.db.itervalues()
		_timesheets = Timesheet.db.itervalues()
		return render_template('timesheets.html', timesheets=_timesheets, jobs=_jobs)

@app.route('/timesheets/upload')
def upload_timesheet():
	return NotImplemented

@app.route('/analytics')
def analytics():
	return NotImplemented

@app.route('/rentals')
def rental_log():
	return NotImplemented

@app.route('/settings')
def user_settings():
	return NotImplemented

@app.route('/help')
def help():
	return NotImplemented