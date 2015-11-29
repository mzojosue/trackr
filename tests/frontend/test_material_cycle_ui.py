from flask.ext.testing import TestCase



class TestMaterialCycleUI(TestCase):
    def setUp(self):
        return NotImplemented

    def tearDown(self):
        return NotImplemented

    def create_app(self):
        return NotImplemented

    def test_job_materials(self):
        """
        Tests `job_materials` view function by ensuring that the correct AwardedJob is selected,
        and that the correct Jinja template is rendered.

        A HTTP POST is then created to test MaterialList creation and route redirection
        """
        # test redirect when AwardedJob does not exist
        self.fail()

    def test_material_list(self):
        """
        Tests `material_list` view function by passing an arbitrarily selected MaterialList,
        and ensures that the 'material_list.html' template is rendered.
        """
        self.fail()

    def test_update_material_list(self):
        """
        Tests `update_material_list` view method by arbitrarily modifying a MaterialList.
        """
        # confirm redirect
        self.fail()

    def test_deliveries(self):
        """
        Tests `deliveries` view method by asserting the loaded template.
        """
        self.fail()

    def test_serialized_deliveries(self):
        """
        Tests `serialized_deliveries` method by analyzing the returned JSON output.
        """
        self.fail()

    def test_schedule_delivery(self):
        """
        Tests `schedule_delivery` by passing arbitrary values and ensuring Delivery object was created.
        """
        self.fail()

    def test_accept_delivery(self):
        """
        Tests `accept_delivery` by arbitrarily modifying `Delivery.delivered` via HTTP GET variables.
        """
        self.fail()

    def test_quote(self):
        """
        Tests `quote` by creating a MaterialListQuote via HTTP POST variables.
        """
        self.fail()

    def test_add_quote_doc(self):
        """
        Tests `add_quote_doc` API function by passing a file stream via a HTTP POST then checking for file in directory.
        """
        self.fail()

    def test_update_po_attr(self):
        """
        Tests `update_po_attr` API function by updating a PO attribute via
        """
        self.fail()

    def test_material_quote_doc(self):
        self.fail()