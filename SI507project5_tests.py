import unittest
from os import path
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
        self.file = open("test.json")

    def test_data_type(self):
        self.assertIsInstance(self.data, dict)
        self.assertIsInstance(self.data["events"], list)

    def test_data_match_cache(self):
        testDict = json.loads(self.file.read())
        self.assertEqual(testDict, self.data)

    def tearDown(self):
        self.file.close()


class TestCacheTime(unittest.TestCase):

    def test_cache_time(self):
        timeBefore = path.getmtime("test.json")
        prepare_data("test.json", "/events/search/",
                     {"location.address": "chicago", "page": 1})
        self.assertEqual(timeBefore, path.getmtime("test.json"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
