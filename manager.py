from core import User

# TODO: implement session manager
# TODO: implement log tools
# TODO: implement user manager

def add_user():
    usr = {}
    usr['name'] = str(raw_input("Please input user name"))
    usr['username'] = str(raw_input("Please input login name"))
    usr['email'] = str(raw_input("Please input user email"))
    usr['passwd'] = str(raw_input("Please input password"))
    User(**_usr)

def change_passwd():
    """ Chages user password """
    return NotImplemented

def delete_users():
    print "Delete Users:"
    db = User.db.items()
    _users = zip(range(1, len(db)), db)

    for usr in _users.iteritems():
        

    
        
