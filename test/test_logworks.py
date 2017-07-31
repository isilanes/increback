# Standard libs:
import sys
import mock
import logging
import unittest

# Our libs:
sys.path.append(".")
from libib import logworks

# Classes:
class TestLogger(unittest.TestCase):
    """Test Logger() class."""

    # Setup and teardown:
    def setUp(self):
        pass

    def tearDown(self):
        pass


    # Test constructor:
    def test_constructor_no_args(self):
        # Run:
        logger = logworks.Logger()

        # Assert:
        self.assertEqual(logger.conf, {})
        self.assertEqual(logger.nocolor, False)
        self.assertIsInstance(logger.logger, logging.Logger)
    
    def test_constructor_no_color(self):
        # Run:
        logger = logworks.Logger(nocolor=True)

        # Assert:
        self.assertEqual(logger.conf, {})
        self.assertEqual(logger.nocolor, True)
        self.assertIsInstance(logger.logger, logging.Logger)
    

    # Test print shortcuts:
    def test_info(self):
        # Prepare:
        logger = logworks.Logger()
        logger.logger.info = mock.Mock()
        logger.with_info_color = mock.Mock()
        texts = [ "something", "yadda yadda", "", None]

        for text in texts:
            # Prepare:
            logger.logger.info.reset_mock()
            logger.with_info_color.reset_mock()

            # Run:
            logger.info(text)

            # Assert:
            logger.logger.info.assert_called_once()
            self.assertIn(text, logger.logger.info.call_args[0])
            logger.with_info_color.assert_called_once()

    def test_warning(self):
        # Prepare:
        logger = logworks.Logger()
        logger.logger.info = mock.Mock()
        logger.with_info_color = mock.Mock()
        texts = [ "something", "yadda yadda", "", None]

        for text in texts:
            # Prepare:
            logger.logger.warning.reset_mock()
            logger.with_info_color.reset_mock()

            # Run:
            logger.warning(text)

            # Assert:
            logger.logger.warning.assert_called_once()
            self.assertIn(text, logger.logger.warning.call_args[0])
            logger.with_info_color.assert_called_once()

