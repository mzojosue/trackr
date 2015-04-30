from estimating import *
from inventory import *
from job import *
from material_cycle import *
from timesheet import *
from todo import *
from user import *


def get_job_num(*args):
	try:
		if hasattr(AwardedJob, 'db'):
			_keys = AwardedJob.db.keys()
			_keys.sort()  # sort tuple of keys so that highest number is on right
			num = int(_keys[-1]) + 1
			return num
	except IndexError:
		# no bids in database. assume a jobs number of 1
		return 1