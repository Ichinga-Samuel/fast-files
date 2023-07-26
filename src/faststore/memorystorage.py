import asyncio
from logging import getLogger

from .main import FastStore, FileData
from fastapi import UploadFile

logger = getLogger()


class MemoryStorage(FastStore):
    # noinspection PyTypeChecker
    async def upload(self, *, field_file: tuple[str, UploadFile]):
        field_name, file = field_file
        try:
            file_object = await file.read()
            self.result = FileData(size=file.size, filename=file.filename, content_type=file.content_type,
                                   field_name=field_name, file=file_object, message='{file.filename} saved successfully')
        except Exception as e:
            logger.error(f'Error uploading file: {e} in {self.__class__.__name__}')
            self.result = FileData(status=False, error=str(e), field_name=field_name, message='Unable to save {file.filename}')

    async def multi_upload(self, *, field_files: list[tuple[str, UploadFile]]):
        await asyncio.gather(*[self.upload(field_file=field_file) for field_file in field_files])
