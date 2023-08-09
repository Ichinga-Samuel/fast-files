"""
Memory storage for FastStore. This storage is used to store files in memory.
"""
import asyncio
from logging import getLogger

from .main import FastStore, FileData, FileField
from fastapi import UploadFile

logger = getLogger()


class MemoryStorage(FastStore):
    """
    Memory storage for FastAPI.
    This storage is used to store files in memory and returned as bytes.
    """
    # noinspection PyTypeChecker
    async def upload(self, *, file_field: FileField):
        field_name, file = file_field['name'], file_field['file']
        try:
            file_object = await file.read()
            self.result = FileData(size=file.size, filename=file.filename, content_type=file.content_type,
                                   field_name=field_name, file=file_object,
                                   message=f'{file.filename} saved successfully')
        except Exception as err:
            logger.error(f'Error uploading file: {err} in {self.__class__.__name__}')
            self.result = FileData(status=False, error=str(err), field_name=field_name,
                                   message=f'Unable to save {file.filename}')

    async def multi_upload(self, *, file_fields: list[FileField]):
        await asyncio.gather(*[self.upload(file_field=file_field) for file_field in file_fields])
