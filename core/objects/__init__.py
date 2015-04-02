from objects import *
from estimating import *
from inventory import *
from job import *
from material_cycle import *
from timesheet import *
from todo import *


def get_job_num(*args):
	try:
		if hasattr(AwardedJob, 'db'):
			_keys = AwardedJob.db.keys()
			num = int(_keys[-1]) + 1
			return num
	except IndexError:
		print "Unknown Error:: Probably no jobs"
		return 1