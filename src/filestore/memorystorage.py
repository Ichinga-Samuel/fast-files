"""
Memory storage for FastStore. This storage is used to store files in memory.
"""
import asyncio
from logging import getLogger

from .main import FastStore, FileData
from fastapi import UploadFile

logger = getLogger()


class MemoryStorage(FastStore):
    """
    Memory storage for FastAPI.
    This storage is used to store files in memory and returned as bytes.
    """
    # noinspection PyTypeChecker
    async def upload(self, *, field_file: tuple[str, UploadFile]):
        field_name, file = field_file
        try:
            file_object = await file.read()
            self.result = FileData(size=file.size, filename=file.filename, content_type=file.content_type,
                                   field_name=field_name, file=file_object,
                                   message=f'{file.filename} saved successfully')
        except Exception as err:
            logger.error(f'Error uploading file: {err} in {self.__class__.__name__}')
            self.result = FileData(status=False, error=str(err), field_name=field_name,
                                   message=f'Unable to save {file.filename}')

    async def multi_upload(self, *, field_files: list[tuple[str, UploadFile]]):
        await asyncio.gather(*[self.upload(field_file=field_file) for field_file in field_files])
