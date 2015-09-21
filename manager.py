from core import User

User.load_users()

# TODO: implement session manager
# TODO: implement log tools
# TODO: implement user manager

def add_user():
    usr = {}
    usr['name'] = str(raw_input("Please input user full name: "))
    usr['username'] = str(raw_input("Input login name: "))
    usr['role'] = str(raw_input("Select User role:\n\t* Admin\n\t* Estimator\n: ")).lower()
    usr['email'] = str(raw_input("Input user email: "))
    usr['passwd'] = str(raw_input("Input password: "))
    User(**usr)

def change_passwd():
    """ Changes user password """
    return NotImplemented

def delete_users():
    print "Delete Users:"
    db = User.db.values()
    _users = zip(range(0, len(db)), db)

    for num, item in _users:
        print num, item.name

    num = int(raw_input("Please select user to delete (#): "))
    _hash = _users[num][1].hash
    del User.db[_hash]
    return User.db.values()
    
        
