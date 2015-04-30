import hashlib
import uuid


class User(object):
	def __init__(self, username, email, passwd):
		self.username = username
		self.email = email
		self.hash = hash(str(username))
		self.passwd, self.salt = hash_secret(passwd)

		if hasattr(self, 'db'):
			self.db[self.hash] = self

	@staticmethod
	def find(query):
		if hasattr(User, 'db'):
			query = hash(query)
			try:
				return User.db[query]
			except KeyError:
				return False


def hash_secret(secret, salt=None):
	"""Hashes the passed secret using salt. A new salt is created if None.
    ::params:
        secret:     the secret (password or pin) to hash
        salt:       the salt stored in memory

    ::returns:
        hash:       salted/hashed secret
        salt:       random salt used with hashing """
	if salt is None:
		salt = uuid.uuid4().hex
	# Create salt and hash the variables in memory

	secret = hashlib.sha512(str(secret) + salt).hexdigest()
	return secret, salt


def pass_auth(obj, value):
	"""Authenticates passwd against obj.passwd
	::params:
	    obj:    should be type u, v or str. str is converted to u or v.
	::returns:
	    True:   when passwd == obj.passwd
	    False:  when passwd != obj.passwd
	    0:      when user doesn't exist"""
	#obj should be type u or v at this point
	passwd = hash_secret(value, obj.salt)[0]  # extract hashed result from returned list
	if passwd == obj.passwd:
		return True
	else:
		return False