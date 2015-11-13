from core import User

User.load_users()


# TODO: implement session manager
# TODO: implement log tools
# TODO: implement user manager

def add_user():
	usr = {}
	usr['name'] = str(raw_input("Please input user full name: "))
	usr['username'] = str(raw_input("Please input login name: "))
	usr['email'] = str(raw_input("Please input user email: "))
	usr['passwd'] = str(raw_input("Please input password: "))
	return User(**usr)


def change_passwd():
    """ Chages user password """
    return NotImplemented


def update_role():
	name = str(raw_input("Please input username: "))
	usr = User.find(name)
	if usr:
		print "User is currently '%s'" % usr.role
		_str = "Enter new user role ('%s'): " % "\', \'".join(User._user_roles)
		role = str(raw_input(_str))
		if role in User._user_roles:
			usr.role = role
			return "Updated %s" % usr
		else:
			print "Error: Invalid role '%s'" % role
	else:
		print "User doesn't exist"

def list_users():
	db = User.db.values()
	_users = zip(range(0, len(db)), db)

	print "# |\tUser"
	for num, item in _users:
		print "%s |\t %s" % (num, item)
	return _users

def delete_user():
	print "Delete Users:"
	_users = list_users()

	num = int(raw_input("Please select user to delete (#): "))
	_hash = _users[num][1].hash
	del User.db[_hash]
	return User.db.values()
