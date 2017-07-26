# Standard libs:
import sys
import mock
import hashlib
import unittest
import argparse
from datetime import datetime

# Our libs:
sys.path.append(".")
from libib import core

# Classes:
class TestFunctions(unittest.TestCase):
    """Test functions."""

    # Setup and teardown:
    def setUp(self):
        pass

    def tearDown(self):
        pass


    # Test timestamp():
    def test_timestamp_default(self):
        ret = core.timestamp()

        self.assertRegex(ret, "^\d{4}\.\d{2}\.\d{2}$")

    def test_timestamp_feed_date(self):
        inputs = [
            [datetime(1977, 6, 11), "1977.06.11"],
            [datetime(2017, 1, 1), "2017.01.01"],
        ]
        for day, string in inputs:
            ret = core.timestamp(day=day)
            self.assertEqual(ret, string)

    def test_timestamp_feed_date_and_offset(self):
        inputs = [
            [datetime(1977, 6, 11), 0, "1977.06.11"],
            [datetime(1977, 6, 11), 1, "1977.06.12"],
            [datetime(1977, 6, 11), 75, "1977.08.25"],
            [datetime(2017, 1, 1), 0, "2017.01.01"],
            [datetime(2017, 1, 1), -1, "2016.12.31"],
            [datetime(2017, 1, 1), -100, "2016.09.23"],
        ]
        for day, offset, string in inputs:
            ret = core.timestamp(day=day, offset=offset)
            self.assertEqual(ret, string)


    # Test parse_args():
    def test_parse_args(self):
        ret = core.parse_args([])
        self.assertIsInstance(ret, argparse.Namespace)

    def test_parse_args_config(self):
        cases = [
            (["--config", "wtf.json"], "wtf.json"),
            ([], None),
        ]
        for args, value in cases:
            ret = core.parse_args(args)
            self.assertEqual(ret.config, value)

    def test_parse_args_dryrun(self):
        cases = [
            (["-y"], True),
            (["--dry-run"], True),
            ([], False),
        ]
        for args, value in cases:
            ret = core.parse_args(args)
            self.assertEqual(ret.dry_run, value)

class TestSync(unittest.TestCase):
    """Test Sync() class."""

    # Setup and teardown:
    def setUp(self):
        pass

    def tearDown(self):
        pass


    # Test timestamp():
    def test_constructor(self):
        # Assemble:
        cases = (
            ({}, "something"),
        )

        for data, item in cases:
            # Act:
            sync = core.Sync(data, item)

            # Assert:
            self.assertEqual(sync.item, item)
            self.assertEqual(sync.data, data)
    

    # Test run():
    def test_run(self):
        pass

# Main loop:
if __name__ == "__main__":
    unittest.main()
