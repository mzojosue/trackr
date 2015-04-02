import unittest
import os.path as path

import core


class TestMaterialListMethods(unittest.TestCase):
	def setUp(self):
		num = core.get_job_num()
		job = core.AwardedJob(num, 'test_job')

		doc = core.os.path.join(job.sub_path, 'Materials')
		self._doc = (doc, 'doc.file')
		self.object = core.MaterialList(job, doc=self._doc)

	def runTest(self):
		root = core.env_root
		doc = path.join(*self._doc)
		doc = (root, doc)
		self.assertEqual(self.object.doc, doc, 'incorrect document path')


suite=unittest.TestLoader().loadTestsFromTestCase(TestMaterialListMethods)
unittest.TextTestRunner(verbosity=2).run(suite)