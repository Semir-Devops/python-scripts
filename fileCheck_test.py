'''
This is a testing file (work in progress) for fileCheck.py
This test is created using Pytest testing Framework
'''

import os
import datetime
import argparse
from pathlib import Path
from unittest.mock import patch
import pytest
import fileCheck
from fileCheck import parse_arguments, configure_logging, read_exclude_list, check_existing_files, log_created_file

@pytest.fixture
def mock_arguments(tmp_path, monkeypatch):
    directory_to_watch = tmp_path / "watched_directory"
    log_file_path = tmp_path / "test.log"

    # Set up a mocked argument namespace
    monkeypatch.setattr('sys.argv', ['fileCheck.py', '--directory', str(directory_to_watch), '--log-file', str(log_file_path)])

    return directory_to_watch, log_file_path

def test_parse_arguments(mock_arguments):
    directory_to_watch, log_file_path = mock_arguments
    args = fileCheck.parse_arguments()

    assert args.dirToW == str(directory_to_watch)
    assert args.lf == str(log_file_path)
    assert args.intl == 60  # Default interval
    assert args.excl_file is None  # No exclude file specified

def test_configure_logging(tmp_path, caplog, mock_arguments):
    directory_to_watch, log_file_path = mock_arguments

    # Ensure log file and directory exist
    assert not log_file_path.exists()
    assert not directory_to_watch.exists()

    # Create log file manually
    log_file_path.touch()

    # Configure logging and check log file
    fileCheck.configure_logging(log_file_path)

    assert log_file_path.exists()

def test_read_exclude_list(tmp_path, mock_arguments):
    directory_to_watch, _ = mock_arguments

    exclude_file_path = tmp_path / "exclude_test.txt"
    exclude_file_path.write_text("excluded_file.txt\nanother_excluded_file.txt\n")

    # Read exclude list
    exclude_list = fileCheck.read_exclude_list(str(exclude_file_path))

    # Verify exclusion list
    assert Path(directory_to_watch / "excluded_file.txt") in exclude_list
    assert directory_to_watch / "another_excluded_file.txt" in exclude_list

def test_check_existing_files(tmp_path, caplog, mock_arguments):
    directory_to_watch, log_file_path = mock_arguments

    # Create the parent directory
    directory_to_watch.mkdir(parents=True, exist_ok=True)

    # Create a test file
    test_file_path = directory_to_watch / "test_file.txt"
    test_file_path.touch()

    checked_files = set()

    with patch('fileCheck.datetime') as mock_datetime, \
        patch('fileCheck.time.sleep') as mock_sleep:
        mock_datetime.now.return_value = datetime.datetime(2023, 1, 1)  # Ensure it's a datetime object
        mock_sleep.side_effect = KeyboardInterrupt()
        exclusion_list = set()  # Provide a valid exclusion_list
        checked_files = fileCheck.check_existing_files(checked_files, directory_to_watch, log_file_path, exclusion_list)

    print("Checked Files in test:", checked_files)

    # Check if the log message is present in the captured logs
    assert f"File '{test_file_path.resolve()}' has been in the directory for more than ten seconds." in caplog.text

    assert len(checked_files) == 1



def test_log_created_file(tmp_path, caplog, mock_arguments):
    _, log_file_path = mock_arguments

    # Create a test file
    test_file_path = tmp_path / "test_file.txt"
    test_file_path.touch()

    # Log the created file
    fileCheck.log_created_file(str(test_file_path), str(log_file_path))

    # Verify log message for the created file
    assert f"File {test_file_path.resolve()} added at" in caplog.text


def test_main_function():
    with patch('fileCheck.configure_logging') as mock_configure_logging, \
            patch('fileCheck.read_exclude_list') as mock_read_exclude_list, \
            patch('fileCheck.check_existing_files') as mock_check_existing_files, \
            patch('fileCheck.log_created_file') as mock_log_created_file, \
            patch('time.sleep', side_effect=KeyboardInterrupt):

        # Mock the arguments
        mock_args = argparse.Namespace(dirToW='test_directory', lf='test_log.txt', intl=60, excl_file='test_exclude.txt')

        # Patch the argparse.ArgumentParser to return the mock_args
        with patch('argparse.ArgumentParser.parse_args', return_value=mock_args):
            fileCheck.main()

        # Add assertions based on the expected behavior of your script
        mock_configure_logging.assert_called_once_with('test_log.txt')
        mock_read_exclude_list.assert_called_once_with('test_exclude.txt')
        mock_check_existing_files.assert_called_once_with(set(), 'test_directory', 'test_log.txt', mock_read_exclude_list.return_value)
        # Add more assertions as needed

if __name__ == "__main__":
    pytest.main()
