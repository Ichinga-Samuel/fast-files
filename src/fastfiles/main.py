from abc import ABC, abstractmethod
from typing import Annotated

from fastapi import Depends, File, UploadFile
from pydantic import BaseModel


class FileData(BaseModel):
    public_url: str = ''
    status: bool = True
    content_type: str
    filename: str
    size: float
    meta: dict = {}


class FileUpload:
    file: UploadFile
    files: list[UploadFile]
    config: dict

    async def __call__(self, file: UploadFile | None = None, files: list[UploadFile] | None = None) -> FileData:
        if file:
            self.file = file
            return await self.upload()

        # elif files:
        #     self.files = files
        #     return await self.multi_upload()
        # # return

    @abstractmethod
    async def upload(self, *args, **kwargs) -> FileData:
        """"""

    # @abstractmethod
    # async def multi_upload(self, *args, **kwargs) -> list[FileData]:
    #     """"""
