import unittest
import os
from SI507project5_code import *


class TestKeys(unittest.TestCase):

    def test_apps(self):
        self.assertTrue(APP_ID)
        self.assertTrue(APP_SECRET)

    def test_URLs(self):
        self.assertTrue(AUTHORIZATION_BASE_URL)
        self.assertTrue(TOKEN_URL)
        self.assertTrue(REDIRECT_URI)


class TestOutput(unittest.TestCase):

    def setUp(self):
        self.data = prepare_data(
            "test.json", "/events/search/", {"location.address": "chicago", "page": 1})

    def test_data_type(self):
        self.assertIsInstance(self.data, dict)
        self.assertIsInstance(self.data["events"], list)

    def test_data_match_cache(self):
        self.file = open("test.json")
        testDict = json.loads(self.file.read())
        self.assertEqual(testDict, self.data)
        self.file.close()

    def test_cache_time(self):
        timeBefore = os.path.getmtime("test.json")
        prepare_data("test.json", "/events/search/",
                     {"location.address": "chicago", "page": 1})
        self.assertEqual(timeBefore, os.path.getmtime("test.json"))

    def tearDown(self):
        os.remove("test.json")


if __name__ == "__main__":
    unittest.main(verbosity=2)
