"""
import public modules and classes from faststore
"""
from .main import FastStore, FileData, Store, FileField
from .memorystorage import MemoryStorage
from .localstorage import LocalStorage
try:
    from .s3 import S3Storage
except ImportError as err:
    print(err)
    pass
