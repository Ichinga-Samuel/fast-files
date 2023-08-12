"""
Utility functions for creating test cases.
"""
from pathlib import Path

from fastapi import Request, UploadFile
from starlette.datastructures import FormData

from filestore import LocalStorage, MemoryStorage, S3Storage, Store


def local_destination(req: Request, form: FormData, field: str, file: UploadFile) -> Path:
    """
    Local storage destination function.
    Pass this function to the LocalStorage config parameter 'destination' to create a destination for the file.
    Creates a directory named after the field inside the test_data/uploads folder if it doesn't exist.

    Returns:
        Path: Path to the stored file.
    """
    path = Path.cwd() / f'test_data/uploads/{field}'
    path.mkdir(parents=True, exist_ok=True) if not path.exists() else ...
    return path / f'{file.filename}'


def local_filter(req: Request, form: FormData, field: str, file: UploadFile) -> bool:
    """
    Local storage filter function.
    Returns:
        bool: True if the file is a text file, False otherwise.
    """
    return file.filename and file.filename.endswith('.txt')


def local_filename(req: Request, form: FormData, field: str, file: UploadFile) -> UploadFile:
    """
    Local storage filename function. Appends 'local_' to the filename.

    Returns:
        UploadFile: The file with the new filename.
    """
    file.filename = f'local_{file.filename}'
    return file


def s3_destination(req: Request, form: FormData, field: str, file: UploadFile) -> str:
    """
    S3 storage destination function. Returns the destination path for the file.
    With the field name as the folder name in title case and the filename as the file name.

    Returns:
        str: The destination path for the file.
    """
    return f'{field.title()}/{file.filename}'


# FastStore instances to be used in the app as dependencies.
multiple_s3 = S3Storage(fields=[{'name': 'author', 'max_count': 2}, {'name': 'book', 'max_count': 2}],
                        config={'destination': s3_destination})
single_s3 = S3Storage(name='author', required=True)
single_mem = MemoryStorage(name='cover')
multiple_mem = MemoryStorage(fields=[{'name': 'author', 'max_count': 5}, {'name': 'book', 'max_count': 2}])
single_local = LocalStorage(name='book', config={'dest': 'test_data/uploads/single'})
multiple_local = LocalStorage(fields=[{'name': 'author', 'max_count': 2},
                                      {'name': 'book', 'max_count': 1}],
                              config={'filter': local_filter, 'filename': local_filename,
                                      'destination': local_destination})
