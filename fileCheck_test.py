'''
This is a testing file (work in progress) for fileCheck.py
This test is created using Unittest testing Framework
'''

import unittest
import os
import shutil
import tempfile
import logging
from unittest.mock import patch
from fileCheck import configure_logging, read_exclude_list, check_existing_files, log_created_file, delete_files

class TestScript(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.mock_dir = os.path.join(self.test_dir, "mock_Dir")
        self.another_dir = os.path.join(self.mock_dir, "anotherDir")
        os.makedirs(self.another_dir)

        # Create mock files
        with open(os.path.join(self.mock_dir, "file1"), "w") as f:
            f.write("content1")
        with open(os.path.join(self.mock_dir, "file2"), "w") as f:
            f.write("content2")
        with open(os.path.join(self.another_dir, "file3.txt"), "w") as f:
            f.write("content3")

        # Create the expired folder
        self.expired_folder = os.path.join(self.test_dir, "expired")
        os.makedirs(self.expired_folder)

        # Write file1's full path into the exclude file
        self.exclude_file = os.path.join(self.test_dir, "exclude.txt")
        with open(self.exclude_file, "w") as f:
            f.write(os.path.join(self.mock_dir, "file1"))

    def tearDown(self):
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    def test_configure_logging(self):
        with patch('fileCheck.logging.basicConfig') as mock_logging:
            configure_logging("test.log")
            mock_logging.assert_called_once_with(filename="test.log", level=logging.DEBUG,
                                                  format='%(asctime)s - %(message)s', filemode='a+')

    def test_read_exclude_list(self):
        exclude_list = read_exclude_list(self.exclude_file)
        self.assertIn(str(os.path.join(self.mock_dir, "file1")), {str(path) for path in exclude_list})

    @patch('fileCheck.logging.info')
    def test_check_existing_files(self, mock_logging):
        # Create a test file in the directory
        test_file_path = os.path.join(self.mock_dir, "test_file.txt")
        with open(test_file_path, "w") as test_file:
            test_file.write("test")

        # Call check_existing_files and assert that it logs the file
        check_existing_files(set(), self.mock_dir, "test.log", set(), self.expired_folder, "metadata.txt")
        mock_logging.assert_called_once()

    def test_log_created_file(self):
        # Mock the Path.write_text method to check if it's called
        with patch('pathlib.Path.write_text') as mock_write_text:
            log_created_file("test_file.txt", "test.log", self.expired_folder, "metadata.txt")
            mock_write_text.assert_called_once()

    def test_delete_files(self):
        # Create a file in the expired folder
        expired_file_path = os.path.join(self.expired_folder, "expired_file.txt")
        with open(expired_file_path, "w") as expired_file:
            expired_file.write("expired")

        # Call delete_files and assert that it deletes the file
        with patch('fileCheck.logging.info') as mock_logging:
            with patch('os.remove') as mock_remove:
                delete_files(self.mock_dir, self.expired_folder, "metadata.txt")
                mock_logging.assert_called_once()
                mock_remove.assert_called_once_with(expired_file_path)

if __name__ == '__main__':
    unittest.main()
