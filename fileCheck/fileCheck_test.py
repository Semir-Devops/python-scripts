'''
This is a testing file (work in progress) for fileCheck.py
This test is created using Unittest testing Framework
'''

import unittest
import os
import logging
import tempfile
from unittest.mock import patch
from fileCheck import configure_logging, read_exclude_list, check_existing_files, log_created_file, delete_files

class TestScript(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create a single temporary directory for all tests
        cls.test_dir = tempfile.mkdtemp(dir='/home/semir-testing/floor/test-env/')

    def setUp(self):
        # Create mock directory within the single temporary directory
        self.mock_dir = os.path.join(self.test_dir, "mock_Dir")
        if not os.path.exists(self.mock_dir):
            os.makedirs(self.mock_dir)

        self.another_dir = os.path.join(self.mock_dir, "anotherDir")
        if not os.path.exists(self.another_dir):
            os.makedirs(self.another_dir)

        # Create the expired folder
        self.expired_folder = os.path.join(self.test_dir, "expired")
        if not os.path.exists(self.expired_folder):
            os.makedirs(self.expired_folder)

        # Write mock files
        with open(os.path.join(self.mock_dir, "file1"), "w") as f:
            f.write("content1\n")
        with open(os.path.join(self.mock_dir, "file2"), "w") as f:
            f.write("content2\n")
        with open(os.path.join(self.another_dir, "file3.txt"), "w") as f:
            f.write("content3\n")

        # Create the exclude file
        self.exclude_file = os.path.join(self.test_dir, "exclude.txt")
        with open(self.exclude_file, "w") as f:
            f.write(os.path.join(self.mock_dir, "file1\n"))

        # Create the metadata file
        self.metadata_file = os.path.join(self.test_dir, "metadata.txt")

        # Create the log file
        self.log_file = os.path.join(self.test_dir, "test.log")
        logging.basicConfig(filename=self.log_file, level=logging.DEBUG,
                            format='%(asctime)s - %(message)s', filemode='a+')

        # Configure logging for the tests
        configure_logging(self.log_file)

    def test_configure_logging_with_correct_settings(self):
        # Verify that logging is correctly configured
        logger = logging.getLogger()

        self.assertEqual(len(logger.handlers), 1)  # Check for one handler: file handler
        file_handler = logger.handlers[0]
        self.assertEqual(file_handler.baseFilename, self.log_file)
        self.assertEqual(file_handler.level, logging.DEBUG)
        self.assertEqual(file_handler.formatter._fmt, '%(asctime)s - %(message)s')

    def test_read_exclude_list(self):
        exclude_list = read_exclude_list(self.exclude_file)
        self.assertIn(str(os.path.join(self.mock_dir, "file1")), {str(path) for path in exclude_list})

    @patch('fileCheck.logging.info')
    def test_check_existing_files(self, mock_logging):
        # Create a test file in the directory
        test_file_path = os.path.join(self.mock_dir, "test_file.txt")
        with open(test_file_path, "w") as test_file:
            test_file.write("test\n")

        # Call check_existing_files and assert that it logs the file
        check_existing_files(set(), self.mock_dir, "test.log", set(), self.expired_folder, self.metadata_file)
        mock_logging.assert_called_once()

    @patch('pathlib.Path.write_text')
    def test_log_created_file(self, mock_write_text):
        log_created_file("test_file.txt", "test.log", self.expired_folder, self.metadata_file)
        mock_write_text.assert_called_once()

    @patch('os.remove')
    @patch('fileCheck.logging.info')
    def test_delete_files(self, mock_logging, mock_remove):
        # Create a file in the expired folder
        expired_file_path = os.path.join(self.expired_folder, "expired_file.txt")
        with open(expired_file_path, "w") as expired_file:
            expired_file.write("expired")

        # Call delete_files and assert that it deletes the file
        delete_files(self.mock_dir, self.expired_folder, self.metadata_file)
        mock_logging.assert_called_once()
        mock_remove.assert_called_once_with(expired_file_path)

if __name__ == '__main__':
    unittest.main()
