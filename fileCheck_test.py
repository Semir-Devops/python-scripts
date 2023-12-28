'''
This is a testing file (work in progress) for fileCheck.py
This test is created using Pytest testing Framework
'''

import os
import time
import datetime
import argparse
from pathlib import Path
from unittest.mock import patch
import pytest
import fileCheck

def test_parse_arguments():
    with pytest.raises(SystemExit):
        fileCheck.parse_arguments()

def test_configure_logging(tmp_path):
    log_file_path = tmp_path / "test.log"
    fileCheck.configure_logging(log_file_path)
    print("Log file path:", log_file_path)
    assert os.path.exists(log_file_path)

def test_read_exclude_list(tmp_path):
    exclude_file_path = tmp_path / "exclude_test.txt"
    exclude_file_path.write_text("excluded_file.txt\nanother_excluded_file.txt\n")

    with patch('fileCheck.parse_arguments') as mock_parse_arguments:
        mock_parse_arguments.return_value = argparse.Namespace(excl_file=str(exclude_file_path))
        args = fileCheck.parse_arguments()
    exclude_list = fileCheck.read_exclude_list(args.excl_file)
    assert str(exclude_file_path) in exclude_list
    assert "excluded_file.txt" in exclude_list
    assert "another_excluded_file.txt" in exclude_list

def test_check_existing_files(tmp_path):
    checked_files = set()
    log_file_path = tmp_path / "test.log"
    file_path = tmp_path / "test_file.txt"
    file_path.touch()

    with patch('fileCheck.datetime') as mock_datetime, \
         patch('fileCheck.time.sleep') as mock_sleep:
        mock_datetime.now.return_value = datetime.datetime(2023, 1, 1)
        mock_sleep.side_effect = KeyboardInterrupt()
        exclusion_list = set()  # Provide a valid exclusion_list
        checked_files = fileCheck.check_existing_files(checked_files, tmp_path, log_file_path, exclusion_list)

    assert len(checked_files) == 1

def test_log_created_file(tmp_path, caplog):
    log_file_path = tmp_path / "test.log"
    file_path = tmp_path / "test_file.txt"
    file_path.touch()

    with patch('fileCheck.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime.datetime(2023, 1, 1)
        fileCheck.log_created_file(file_path, log_file_path)

    assert f"File {file_path} added at 2023-01-01 00:00:00" in caplog.text.replace('\n', '')

def test_main_function(tmp_path):
    log_file_path = tmp_path / "test.log"
    with patch('fileCheck.parse_arguments') as mock_parse_arguments, \
         patch('fileCheck.datetime') as mock_datetime, \
         patch('fileCheck.time.sleep') as mock_sleep:
        mock_parse_arguments.return_value = argparse.Namespace(directory="/path/to/dir", log_file=str(log_file_path))
        mock_datetime.now.return_value = datetime.datetime(2023, 1, 1)
        mock_sleep.side_effect = KeyboardInterrupt()

        with pytest.raises(SystemExit):
            fileCheck.main()

    assert os.path.exists(log_file_path)
