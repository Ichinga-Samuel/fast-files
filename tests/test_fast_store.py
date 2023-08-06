"""
Test functions for the FastStore class.
All tests are run with pytest.

Functions:
    test_local_single: Test single file upload to local storage
    test_local_multiple: Test multiple files upload to local storage
    test_s3_single: Test single file upload to S3 storage
    test_s3_multiple: Test multiple files upload to S3 storage
    test_mem_single: Test single file upload to memory storage
    test_mem_multiple: Test multiple files upload to memory storage
"""
from . import client, test_file1, test_file2, test_file3, test_file4, test_file5, test_file6


def test_s3_single(test_file1):
    """
    Test single file upload to S3 storage.
    All arguments are fixtures from __init__.
    """
    response = client.post('/s3_single', files={'author': test_file1})
    assert response.status_code == 200
    res = response.json()
    assert res['status'] is True
    assert res['file']['filename'] == 'test_file1.txt'
    assert len(res['files']) == 1


def test_s3_multiple(test_file1, test_file2, test_file3, test_file6, test_file5):
    """
    Test multiple files upload to S3 storage.
    All arguments are fixtures from the __init__.py file
    """
    files = [('author', test_file1), ('author', test_file2),('author', test_file3), ('book', test_file3),
             ('book', test_file6)]
    response = client.post('/s3_multiple', files=files)
    res = response.json()
    assert response.status_code == 200
    assert res['status'] is True
    assert len(res['files']) == 4


def test_local_single(test_file1):
    """
    Test single file upload to local storage.
    All arguments are fixtures from the __init__.py file
    """
    response = client.post('/local_single', files={'book': test_file1})
    assert response.status_code == 200
    res = response.json()
    assert res['status'] is True
    assert res['file']['filename'] == 'test_file1.txt'
    assert len(res['files']) == 1


def test_local_multiple(test_file1, test_file2, test_file3, test_file6, test_file5):
    """
    Test multiple files upload to local storage.
    All arguments are fixtures from the __init__.py file
    """
    files = [('author', test_file1), ('author', test_file2), ('author', test_file3), ('book', test_file3),
             ('book', test_file6)]
    response = client.post('/local_multiple', files=files)
    res = response.json()
    assert response.status_code == 200
    assert res['status'] is True
    assert len(res['files']) == 3


def test_mem_single(test_file1):
    """
    Test single file upload to memory storage
    All arguments are fixtures from the __init__.py file
    """
    response = client.post('/mem_single', files={'cover': test_file1})
    assert response.status_code == 200
    res = response.json()
    assert res['status'] is True
    assert res['file']['filename'] == 'test_file1.txt'
    assert len(res['files']) == 1


def test_mem_multiple(test_file1, test_file2, test_file3, test_file6, test_file5):
    """
    Test multiple files upload to memory storage
    All arguments are fixtures from the __init__.py file
    """
    response = client.post('/mem_multiple', files=[('book', test_file3), ('book', test_file6)])
    res = response.json()
    assert response.status_code == 200
    assert res['status'] is True
    assert len(res['files']) == 2
