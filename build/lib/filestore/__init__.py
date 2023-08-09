"""
import public modules and classes from faststore
"""
from .main import FastStore, FileData, Result
from .memorystorage import MemoryStorage
from .localstorage import LocalStorage
try:
    from .s3 import S3Storage
except ImportError:
    pass
