import os
import asyncio
import logging
from functools import cache
from urllib.parse import quote as urlencode

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from .main import FastStore, FileData, UploadFile

logger = logging.getLogger(__name__)


class S3Storage(FastStore):
    @property
    @cache
    def client(self):
        key_id = os.environ.get('AWS_ACCESS_KEY_ID')
        access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        region_name = os.environ.get('AWS_DEFAULT_REGION') or self.config.get('region')
        return boto3.client('s3', region_name=region_name, aws_access_key_id=key_id, aws_secret_access_key=access_key)

    async def _upload(self, *, file_obj, bucket, obj_name, extra_args):
        try:
            await asyncio.to_thread(self.client.upload_fileobj, file_obj, bucket, obj_name, ExtraArgs=extra_args)
        except Exception as e:
            logger.error(f'Error uploading file: {e} in {self.__class__.__name__}')

    # noinspection PyTypeChecker
    async def upload(self, *, field_file: tuple[str, UploadFile]):
        field_name, file = field_file
        try:
            dest = self.config.get('destination', None)
            object_name = dest(self.request, self.form, field_name, file) if dest else file.filename
            bucket = self.config.get('bucket') or os.environ.get('AWS_BUCKET_NAME')
            region = self.config.get('region') or os.environ.get('AWS_DEFAULT_REGION')
            extra_args = self.config.get('extra_args', {})

            if self.config.get('background', False):
                self.background_tasks.add_task(self._upload, file_obj=file.file, bucket=bucket, obj_name=object_name,
                                               extra_args=extra_args)
            else:
                await asyncio.to_thread(self._upload, file_obj=file.file, bucket=bucket, obj_name=object_name,
                                        extra_args=extra_args)

            url = f"https://{bucket}.s3.{region}.amazonaws.com/{urlencode(object_name.encode('utf8'))}"
            self.result = FileData(filename=file.filename, content_type=file.content_type, field_name=field_name,
                                   url=url)
        except (NoCredentialsError, ClientError, Exception) as err:
            logger.error(f'Error uploading file: {err} in {self.__class__.__name__}')
            self.result = FileData(status=False, error_msg=str(err), field_name=field_name, filename=file.filename)

    async def multi_upload(self, *, field_files: list[tuple[str, UploadFile]]):
        await asyncio.gather(*[self.upload(field_file=field_file) for field_file in field_files])
