from pathlib import Path
import asyncio
from logging import getLogger

from .main import FastStore, FileData
from fastapi import UploadFile

logger = getLogger()


class LocalStorage(FastStore):
    def get_path(self, filename) -> Path:
        folder = Path.cwd() / self.config.get('dest', 'uploads')
        Path(folder).mkdir(parents=True, exist_ok=True)
        return folder / filename

    @staticmethod
    async def _upload(file: UploadFile, dest: Path):
        try:
            file_object = await file.read()
            with open(f'{dest}', 'wb') as fh:
                fh.write(file_object)
            await file.close()
        except Exception as e:
            logger.error(f'Error uploading file: {e} in {LocalStorage.__name__}')

    # noinspection PyTypeChecker
    async def upload(self, *, field_file: tuple[str, UploadFile]):
        field_name, file = field_file
        try:
            dest = self.config.get('destination', None)
            dest = dest(self.request, self.form, field_name, file) if dest else self.get_path(file.filename)

            if self.config.get('background', False):
                self.background_tasks.add_task(self._upload, file, dest)
            else:
                await self._upload(file, dest)

            self.result = FileData(size=file.size, filename=file.filename, content_type=file.content_type,
                                   path=str(dest), field_name=field_name)
        except Exception as e:
            logger.error(f'Error uploading file: {e} in {self.__class__.__name__}')
            self.result = FileData(status=False, error_msg=str(e), field_name=field_name)

    async def multi_upload(self, *, field_files: list[tuple[str, UploadFile]]):
        await asyncio.gather(*[self.upload(field_file=field_file) for field_file in field_files])
