from objects import *


class InventoryItem(object):
	def __init__(self, item_id, item_label, stock=None):

		self.hash = abs(hash(str(item_id)))

		self.item_id = item_id
		self.item_label = item_label

		self.orders = {}  # keys: order datetime. value:order objects

		if hasattr(InventoryItem, 'db'):
			InventoryItem.db[self.hash] = self

	@property
	def stock(self):
		_qty = float()
		for i in self.orders.itervalues():
			_qty += i.quantity
		return str(_qty)

	def __setattr__(self, key, value):
		_return = super(InventoryItem, self).__setattr__(key, value)
		self.update()
		return _return

	def update(self):
		if hasattr(InventoryItem, 'db'):
			InventoryItem.db[self.hash] = self
		return None

	@staticmethod
	def find(query):
		try:
			if hasattr(InventoryItem, 'db'):
				return InventoryItem.db[int(query)]
		except KeyError:
			return False


class InventoryOrder(object):
	def __init__(self, item, price=0.0, vend=None, quantity=0, date_ordered=today(), po=None):

		self.hash = abs(hash(''.join([item.item_label, str(price), str(date_ordered)])))

		self.item = item
		self.price = price
		self.vend = vend
		self.quantity = float(quantity)
		self.date_ordered = date_ordered
		self.item.orders[self.hash] = self
		if po:
			self.po = po

		if hasattr(InventoryOrder, 'db'):
			InventoryOrder.db[self.hash] = self

	def __setattr__(self, key, value):
		_return = super(InventoryOrder, self).__setattr__(key, value)
		self.update()
		return _return

	def update(self):
		if hasattr(InventoryOrder, 'db'):
			InventoryOrder.db[self.hash] = self
		if hasattr(self, 'item'):
			self.item.orders[self.hash] = self
			self.item.update()
		return None

	@staticmethod
	def find(query):
		try:
			if hasattr(InventoryOrder, 'db'):
				return InventoryOrder.db[int(query)]
		except KeyError:
			return False
