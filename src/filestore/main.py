"""
This module contains the FastStore class which is used to upload files to a storage service such as local, cloud,
or memory. It also contains the FileData class which is used to return the result of a file storage operation.
The Result class is used to return the result of a file storage operation. It also contains helper functions for the
FastStore class configuration.

Functions:
    file_filter (Callable[[Request, Form, str, UploadFile], bool]): The default filter function for the FastStore class.
    filename Callable[[Request, Form, str, UploadFile], UploadFile]: Update the filename of the file object.

Classes:
    Config: The configuration for the FastStore class. This is a TypedDict not a Pydantic model.
    FileData: The result of a file storage operation. A Pydantic model.
    Result: The result of a file storage operation. A Pydantic model.
    FastStore: The base class for all storage services. An abstract class.
"""
import os
from typing import Any, Type, cast, TypedDict, TypeVar, NotRequired, Callable
from abc import abstractmethod
from pathlib import Path
from logging import getLogger
from functools import cache
from random import randint

from starlette.datastructures import UploadFile as StarletteUploadFile
from fastapi import Request, UploadFile as UF, Form, BackgroundTasks
from pydantic import BaseModel, create_model, Field

from .util import FormModel

Fields = TypedDict('Fields', {'name': str, 'max_count': NotRequired[int], 'required': NotRequired[bool]})

Self = TypeVar('Self', bound='FastStore')

logger = getLogger(__name__)


class UploadFile(UF):
    @classmethod
    def validate(cls: Type["UploadFile"], v: Any) -> Any:
        if not isinstance(v, (StarletteUploadFile, str, type(None))):
            raise ValueError(f"Expected UploadFile, received: {type(v)}")
        return v

    @classmethod
    def _validate(cls, __input_value: Any, _: Any) -> "UploadFile":
        if not isinstance(__input_value, (StarletteUploadFile, str, type(None))):
            raise ValueError(f"Expected UploadFile, received: {type(__input_value)}")
        return cast(UploadFile, __input_value)


def _file_filter(file):
    return isinstance(file, StarletteUploadFile)


def file_filter(req: Request, form: Form, field: str, file: UploadFile) -> bool:
    """
    The default filter function for the FastStore class.
    Args:
        req (Request): The request object.
        form (Form): The form object.
        field (Field): The name of the field.
        file (UploadFile): The file object.

    Returns (bool): True if the file is valid, False otherwise.
    """
    return isinstance(file, StarletteUploadFile) and file.filename


def filename(req: Request, form: Form, field: str, file: UploadFile) -> UploadFile:
    """
    Update the filename of the file object.

    Args:
        req (Request): The request object.
        form (Form): The form object.
        field (Field): The name of the field.
        file (UploadFile): The file object.

    Returns (UploadFile): The file object with the updated filename.
    """
    return file


class Config(TypedDict, total=False):
    """
    The configuration for the FastStore class.
    """
    dest: str | Path
    destination: Callable[[Request, Form, str, UploadFile], str | Path]
    filter: Callable[[Request, Form, str, UploadFile], bool]
    max_files: int
    max_fields: int
    filename: Callable[[Request, Form, str, UploadFile], UploadFile]
    background: bool
    extra_args: dict
    bucket: str
    region: str


class FileData(BaseModel):
    """
    The result of a file storage operation.

    Attributes:
        path (str): The path to the file for local storage.
        url (str): The url to the file for cloud storage.
        status (bool): The status of the file storage operation.
        content_type (str): The content type of the file.
        filename (str): The name of the file.
        size (int): The size of the file.
        file (bytes | None): The file object for memory storage.
        field_name (str): The name of the form field.
        metadata (dict): Extra metadata of the file.
        error (str): The error message if the file storage operation failed.
        message (str): Success message if the file storage operation was successful.
    """
    path: str = ''
    url: str = ''
    status: bool = True
    content_type: str = ''
    filename: str = ''
    size: int = 0
    file: bytes | None = None
    field_name: str = ''
    metadata: dict = {}
    error: str = ''
    message: str = ''


class Result(BaseModel):
    """
    The response model for the FastStore class.

    Attributes:
        file (FileData | None): The result of a single file upload or storage operation.
        files (list[FileData]): The result of multiple file uploads or storage operations.
        failed (FileData | list[FileData]): The result of a failed file upload or storage operation.
        error (str): The error message if the file storage operation failed.
        message (str): Success message if the file storage operation was successful.
    """
    file: FileData | None = None
    files: list[FileData] = []
    failed: FileData | list[FileData] = []
    error: str = ''
    message: str = ''
    status: bool = True


def validator(cls, v):
    print(v)
    assert True is True
    return v


class FastStore:
    """
    This class is used to upload files to a storage service.
    It is an abstract class and must be inherited from.
    The upload and multi_upload methods must be implemented in a child class.

    Attributes:
        fields (list[Fields]): The fields to expect from the form.
        request (Request): The request object.
        form (Form): The form object.
        config (dict): The configuration for the storage service.
        _result (Result): The result of the file storage operation.
        result (Result): Property to access and set the result of the file storage operation.
        max_count (int): The maximum number of files to accept for all fields.
        background_tasks (BackgroundTasks): The background tasks object for running tasks in the background.

    Methods:
        upload (Callable[[tuple(str, UploadFile)]]): The method to upload a single file.

        multi_upload (Callable[[Request, Form, str, UploadFile]]): The method to upload multiple files.

    Config:
        max_files (int): The maximum number of files to accept in a single request. Defaults to 1000.

        max_fields (int): The maximum number of fields to accept in a single request. Defaults to 1000.

        dest (str | Path): Destination to save the file to in the storage service defaults to 'uploads'.

        filename (Callable[[Request, Form, str, UploadFile], UploadFile): A function that takes in the request,
            form and file, filename modifies the filename attribute of the file and returns the file.

        destination (Callable[[Request, Form, str, UploadFile], str | Path]): A function that takes in the request,
            form and file and returns a path to save the file to in the storage service.

        filter (Callable[[Request, Form, str, UploadFile], bool]): A function that takes in the request, form and file
            and returns a boolean.

        background (bool): A boolean to indicate if the file storage operation should be run in the background.

        extra_args (dict): Extra arguments to pass to the storage service.

        bucket (str): The name of the bucket to upload the file to in the cloud storage service.
    """
    fields: list[Fields]
    config: Config
    form: Form
    request: Request
    result: Result
    background_tasks: BackgroundTasks
    max_count: int
    _result: Result

    def __init__(self, name: str = '', count: int = 1, required=False, fields: list[Fields] | None = None,
                 config: Config | None = None):
        """
        Initialize the FastStore class. For single file upload, specify the name of the file field and the expected
        number of files. If the field is required, set required to True.
        For multiple file uploads, specify the fields to expect from the form and the expected number
        of files for each field. If the field is required, set required to True.
        Use the config parameter to specify the configuration for the storage service.

        Keyword Args:
            name (str): The name of the file field to expect from the form for a single field upload.
            count (int): The maximum number of files to accept for single field upload.
            required (bool): required for single field upload. Defaults to false.
            fields: The fields to expect from the form. Usually for multiple file uploads from different fields.

        Note:
            If fields and name are specified then the name field is added to the fields list.
        """
        field = {'name': name, 'max_count': count, 'required': required} if name else {}
        self.fields = fields or []
        self.fields.append(field) if field else ...
        self.config = ({'filter': file_filter, 'max_files': 1000, 'max_fields': 1000, 'filename': filename}
                       | (config or {}))

    @property
    @cache
    def model(self):
        """
        Returns a pydantic model for the form fields.

        Returns (FormModel):
        """
        body = {}
        for field in self.fields:
            if field.get('max_count', 1) > 1:
                body[field['name']] = (list[UploadFile], ...) if field.get('required', False) \
                    else (list[UploadFile], Field([], validate_default=False))
            else:
                body[field['name']] = (UploadFile, ...) if field.get('required', False) \
                    else (UploadFile, Field(None, validate_default=False))
        model_name = f"FormModel{randint(100, 1000)}"
        model = create_model(model_name, **body, __base__=FormModel)
        return model

    async def __call__(self, req: Request, bgt: BackgroundTasks) -> Self:
        """
        Upload files to a storage service. This enables the FastStore class instance to be used as a dependency.

        Args:
            req (Request): The request object.
            bgt (BackgroundTasks): The background tasks object for running tasks in the background.

        Returns:
            FastStore: An instance of the FastStore class.
        """
        self._result = Result()
        self.request = req
        self.background_tasks = bgt
        try:
            _filter = self.config['filter']
            _filename = self.config['filename']
            max_files, max_fields = self.config['max_files'], self.config['max_fields']
            form = await req.form(max_files=max_files, max_fields=max_fields)
            self.form = form
            file_fields = [(field['name'], _filename(req, form, field['name'], file)) for field in self.fields for
                           file in form.getlist((field['name']))[0:field.get('max_count', None)]
                           if (_file_filter(file) and _filter(req, form, field['name'], file))]

            self.max_count = len(file_fields)
            if not file_fields:
                self._result = Result(message='No files were uploaded')

            elif len(file_fields) == 1:
                file_field = file_fields[0]
                await self.upload(field_file=file_field)

            else:
                await self.multi_upload(field_files=file_fields)
        except (KeyError, AttributeError, ValueError, TypeError, NameError, MemoryError, BufferError) as err:
            man = os.environ.get('man')
            key_id = os.environ.get('AWS_ACCESS_KEY_ID')
            access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
            region_name = os.environ.get('AWS_DEFAULT_REGION') or self.config.get('region')
            print('env-keys', man, key_id, access_key, region_name)
            logger.error(f'Error uploading files: {err} in {self.__class__.__name__} {man=} {key_id=} {region_name=}')
            self._result = Result(error=str(err), status=False)
        return self

    @abstractmethod
    async def upload(self, *, field_file: tuple[str, UploadFile]):
        """
        Upload a single file to a storage service.

        Args:
            field_file (tuple[str, UploadFile]): A tuple containing the name of the file field and the file to upload.
        """

    @abstractmethod
    async def multi_upload(self, *, field_files: list[tuple[str, UploadFile]]):
        """
        Upload multiple files to a storage service.

        Args:
            field_files (list[tuple[str, UploadFile]]): A list of tuples containing the name of the file field and the
        """

    @property
    def result(self) -> Result:
        """
        Returns the result of the file storage.

        Returns:
            Result: The result of the file storage operation.
        """
        return self._result

    @result.setter
    def result(self, value: FileData):
        """
        Sets the result of the file storage operation.

        Args:
            value: A FileData instance.
        """
        try:
            if not isinstance(value, FileData):
                logger.error(f'Expected FileData instance, got {type(value)} in {self.__class__.__name__}')
                return

            if self.max_count == 1:
                self._result.file = value if value.status else None
                self._result.message = f'{value.filename} stored' if value.status else f'{value.filename} not stored'
                self._result.files.append(value) if value.status else self.result.failed.append(value)
            else:
                self._result.files.append(value) if value.status else self.result.failed.append(value)
                self._result.message = (f'{len(self._result.files)} files stored\n{len(self._result.failed)} files not'
                                        f' stored')
        except Exception as err:
            logger.error(f'Error setting result in {self.__class__.__name__}: {err}')
            self._result.error += f'{err}\n'
