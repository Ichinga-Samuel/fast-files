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

from .main import FastStore, FileData, FileField
from fastapi import UploadFile

logger = getLogger()


class LocalStorage(FastStore):
    """
    Local storage for FastAPI.
    """
    def get_path(self, file_field) -> Path:
        """
        Get the path to save the file to.
        Args:
            field_name (str): The name of the field the file is being uploaded to.
            filename (str): The name of the file to save.

        Returns:
            Path: The path to save the file to.
        """

        dest = file_field.get('config', {}).get('dest', None) or self.config.get('dest', 'uploads')
        if isinstance(dest, Path):
            return dest / file_field['file'].filename

        folder = Path.cwd() / dest
        Path(folder).mkdir(parents=True, exist_ok=True)
        return folder / file_field['file'].filename

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
    async def upload(self, *, file_field: FileField):
        """
        Upload a file to the destination.
        This method is called by the multi_upload method for multiple files storage.
        Sets the result of the storage operation to the result attribute of the class.
        If the background config is set to True, the upload operation is run in the background.

        Args:
            file_field (tuple[str, UploadFile]): A tuple containing the field name and the file to upload.

        Returns:
            None: Nothing is returned.
        """
        field_name, file = file_field['name'], file_field['file']
        try:
            dest = file_field.get('config', {}).get('destination') or self.config.get('destination', None)
            dest = dest(self.request, self.form, field_name, file) if dest else self.get_path(file_field)

            if file_field.get('config', {}).get('background') or self.config.get('background', False):
                self.background_tasks.add_task(self._upload, file, dest)
            else:
                await self._upload(file, dest)

            self.result = FileData(size=file.size, filename=file.filename, content_type=file.content_type,
                                   path=str(dest), field_name=field_name,
                                   message=f'{file.filename} storage was successful')
        except (AttributeError, KeyError, NameError, FileNotFoundError, TypeError) as err:
            logger.error(f'Error uploading file: {err} in {self.__class__.__name__}')
            self.result = FileData(status=False, error=str(err), field_name=field_name, message=f'Unable to save'
                                                                                              f' {file.filename}')

    async def multi_upload(self, *, file_fields: list[FileField]):
        """
        Upload multiple files to the destination.

        Args:
            file_fields (list[tuple[str, UploadFile]]): A list of tuples of field name and the file to upload.

        Returns:
            None: Nothing is returned.
        """
        await asyncio.gather(*[self.upload(file_field=file_field) for file_field in file_fields])
