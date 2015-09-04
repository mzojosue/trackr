import unittest

import core


class TestEstimatingJob(unittest.TestCase):
	def setUp(self):
		return None

	def testInit(self):
		""" Tests all attributes creating during initialization
		:return:
		"""
		return NotImplemented

	def testBidDate(self):
		""" Tests the EstimatingJob.bid_date property
		:return:
		"""
		return NotImplemented

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