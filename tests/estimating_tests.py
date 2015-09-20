import unittest
import os
import shutil
from datetime import datetime

today = datetime.today

import core


class TestEstimatingJob(unittest.TestCase):
	def setUp(self):
		core.disconnect_db()  # ensure database objects aren't interfered with
		self.name = 'test_bid'
		self.bid = core.EstimatingJob(self.name, add_to_log=False, struct=False)
		core.EstimatingJob._dump_lock = True

		if os.path.isdir('tests'):
			_dir = 'tests/.bid_sandbox'
		else:
			_dir = '.bid_sandbox'
		try:
			os.mkdir(_dir)  # create sandbox directory
		except OSError:
			pass
		os.chdir(_dir)  # enter sandbox directory

	def tearDown(self):
		if os.path.isdir('../../tests'):  # checks if in tests/.job_sandbox
			_escape = '../..'  # escape tests/.job_sandbox
			_delete = 'tests/.bid_sandbox'
		else:
			_escape = '..'
			_delete = '.bid_sandbox'
		os.chdir(_escape)
		shutil.rmtree(_delete)

	def testInit(self):
		""" Tests all attributes creating during initialization as well as class attributes
		:return:
		"""
		return NotImplemented

	def testHasTakeoff(self):
		""" Tests has_takeoff property by parsing shell output
		:return:
		"""
		self.assertEqual(self.bid.has_takeoff, False)  # without directory

		self.bid._path = os.getcwd()
		if os.path.isdir('../.bid_sandbox'):  # checks for sandbox
			_dir = 'Takeoffs'
			os.mkdir(_dir)
			os.chdir(_dir)
			self.assertEqual(self.bid.has_takeoff, False)  # with directory, without files

			_reports = ['report1', 'report2', 'report3']
			for fname in _reports:
				_fobj = open(fname, 'w')
				_fobj.close()
			self.assertEqual(self.bid.has_takeoff, True)  # with files
			os.chdir('..')  # leave Takeoffs

	def testBidDate(self):
		""" Tests the EstimatingJob.bid_date property with and without a bid_date attribute
		:return:
		"""
		self.assertEqual(self.bid.bid_date, 'ASAP')  # bid_date is 'ASAP'

		_date = datetime(2025, 1, 1)
		self.bid.bids.values()[0]['bid_date'] = _date
		self.assertEqual(self.bid.bid_date.date(), _date.date())  # bid_date is _date

	def testCountdown(self):
		""" Tests the result of EstimatingJob.countdown
		:return:
		"""
		return NotImplemented

	def testTimestamp(self):
		""" Tests EstimatingJob.timestamp by parsing it as a Unix timestamp
		:return:
		"""
		return NotImplemented

	def testBidCount(self):
		""" Tests bid_count property by comparing the returned value and EstimatingJob.bids
		:return:
		"""
		return NotImplemented

	def testBiddingTo(self):
		""" Tests bidding_to by comparing EstimatingJob.bids and returned each returned value
		:return:
		"""
		return NotImplemented

	def testPath(self):
		""" Tests EstimatingJob.sub_path and EstimatingJob.path by checking that it exists or could be created
		:return:
		"""
		return NotImplemented

	def testInitStruct(self):
		""" Tests init_struct and validates /Quotes contents
		:return:
		"""
		return NotImplemented

	def testQuotes(self):
		""" Tests the quotes property by touching empty files
		:return:
		"""
		return NotImplemented

	def testQuoteCount(self):
		""" Tests quote_count property by manually iterating through Quotes directory
		:return:
		"""
		return NotImplemented

	def testQuoteStatus(self):
		""" Tests quote_status property by parsing output and comparing to quotes property
		:return:
		"""
		return NotImplemented

	def testAddDelQuote(self):
		""" Tests add_quote and del_quote methods
		:return:
		"""
		return NotImplemented

	def testAddDelSub(self):
		""" Tests add_sub and del_sub
		:return:
		"""
		return NotImplemented

	def testCompleteBid(self):
		""" Tests complete_bid method. Ensures that self was moved to EstimatingJob.completed_db
		:return:
		"""
		return NotImplemented

	def testCancelBid(self):
		""" Tests cancel_bid method.
		:return:
		"""
		return NotImplemented

	def testDeleteBid(self):
		""" Tests delete_bid method
		:return:
		"""
		return NotImplemented

	def testAwardBid(self):
		""" Tests award_bid function and ensures that an appropriate AwardedJob object was created
		:return:
		"""
		return NotImplemented

	def testFind(self):
		""" Tests EstimatingJob.find method by looking for self in EstimatingJob .db and .completed_db
		:return:
		"""
		return NotImplemented

	def testFindRebid(self):
		""" Tests find_rebid method by creating a similar bid
		:return:
		"""
		return NotImplemented

	def testGetBidNum(self):
		""" Tests EstimatingJob.get_bid_num by looking at database keys
		:return:
		"""
		return NotImplemented


suite = unittest.TestLoader().loadTestsFromTestCase(TestEstimatingJob)
unittest.TextTestRunner(verbosity=2).run(suite)