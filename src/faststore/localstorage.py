"""
Local storage for FastAPI.
This module contains the LocalStorage class, which is a subclass of FastStore. It is used to store files locally in
the server. It is the default storage class for FastAPI.

Classes:
    LocalStorage: A subclass of FastStore. It is used to store files locally in the server. It is the default storage.
"""

import asyncio
from pathlib import Path
from logging import getLogger

from .main import FastStore, FileData
from fastapi import UploadFile

logger = getLogger()


class LocalStorage(FastStore):
    """
    Local storage for FastAPI.
    """
    def get_path(self, filename: str) -> Path:
        """
        Get the path to save the file to.
        Args:
            filename (str): The name of the file to save.

        Returns:
            Path: The path to save the file to.
        """
        folder = Path.cwd() / self.config.get('dest', 'uploads')
        Path(folder).mkdir(parents=True, exist_ok=True)
        return folder / filename

    @staticmethod
    async def _upload(file: UploadFile, dest: Path):
        """
        Private method to upload the file to the destination. This method is called by the upload method.

        Args:
            file (UploadFile): The file to upload.
            dest (Path): The destination to upload the file to.

        Returns:
            None: Nothing is returned.
        """
        file_object = await file.read()
        with open(f'{dest}', 'wb') as fh:
            fh.write(file_object)
        await file.close()

    # noinspection PyTypeChecker
    async def upload(self, *, field_file: tuple[str, UploadFile]):
        """
        Upload a file to the destination.
        This method is called by the multi_upload method for multiple files storage.
        Sets the result of the storage operation to the result attribute of the class.
        If the background config is set to True, the upload operation is run in the background.

        Args:
            field_file (tuple[str, UploadFile]): A tuple containing the field name and the file to upload.

        Returns:
            None: Nothing is returned.
        """
        field_name, file = field_file
        try:
            dest = self.config.get('destination', None)
            dest = dest(self.request, self.form, field_name, file) if dest else self.get_path(file.filename)

            if self.config.get('background', False):
                self.background_tasks.add_task(self._upload, file, dest)
            else:
                await self._upload(file, dest)

            self.result = FileData(size=file.size, filename=file.filename, content_type=file.content_type,
                                   path=str(dest), field_name=field_name,
                                   message=f'{file.filename} storage was successful')
        except (AttributeError, KeyError, NameError, FileNotFoundError) as err:
            logger.error(f'Error uploading file: {err} in {self.__class__.__name__}')
            self.result = FileData(status=False, error=str(err), field_name=field_name, message=f'Unable to save'
                                                                                              f' {file.filename}')

    async def multi_upload(self, *, field_files: list[tuple[str, UploadFile]]):
        """
        Upload multiple files to the destination.

        Args:
            field_files (list[tuple[str, UploadFile]]): A list of tuples of field name and the file to upload.

        Returns:
            None: Nothing is returned.
        """
        await asyncio.gather(*[self.upload(field_file=field_file) for field_file in field_files])
