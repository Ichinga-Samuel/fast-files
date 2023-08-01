"""
This module sets up the test environment.
All fixtures are defined here and can be used in any test file.
"""

import random
from string import ascii_letters, digits, whitespace

from fastapi.testclient import TestClient
from pytest import fixture

from .app import app

client = TestClient(app)


@fixture
def test_file1():
    """
    Create a test file with random content.

    Yields:
        file: A file reader object
    """
    file = 'tests/test_data/test_file1.txt'
    with open(file, 'w') as fh:
        lines = [''.join(random.choices(ascii_letters + digits + whitespace, k=1000)) for _ in range(1000)]
        fh.writelines(lines)
    yield open(file, 'rb')


@fixture
def test_file2():
    """
    Create a test file with random content.

    Yields:
        file: A file reader object
    """
    file = 'tests/test_data/test_file2.txt'
    with open(file, 'w') as fh:
        lines = [''.join(random.choices(ascii_letters + digits + whitespace, k=1000)) for _ in range(1000)]
        fh.writelines(lines)
    yield open(file, 'rb')


@fixture
def test_file3():
    """
    Create a test file with random content.

    Yields:
        file: A file reader object
    """
    file = 'tests/test_data/test_file3.txt'
    with open(file, 'w') as fh:
        lines = [''.join(random.choices(ascii_letters + digits + whitespace, k=1000)) for _ in range(1000)]
        fh.writelines(lines)
    yield open(file, 'rb')


@fixture
def test_file4():
    """
    Create a test file with random content.

    Yields:
        file: A file reader object
    """
    file = 'tests/test_data/test_file4.txt'
    with open(file, 'w') as fh:
        lines = [''.join(random.choices(ascii_letters + digits + whitespace, k=1000)) for _ in range(1000)]
        fh.writelines(lines)
    yield open(file, 'rb')


@fixture
def test_file5():
    """
    Create a test file with random content.

    Yields:
        file: A file reader object
    """
    file = 'tests/test_data/test_file5.env'
    with open(file, 'w') as fh:
        lines = [''.join(random.choices(ascii_letters + digits + whitespace, k=1000)) for _ in range(1000)]
        fh.writelines(lines)
    yield open(file, 'rb')


@fixture
def test_file6():
    """
    Create a test file with random content.

    Yields:
        file: A file reader object
    """
    file = 'tests/test_data/test_file6.env'
    with open(file, 'w') as fh:
        lines = [''.join(random.choices(ascii_letters + digits + whitespace, k=1000)) for _ in range(1000)]
        fh.writelines(lines)
    yield open(file, 'rb')
