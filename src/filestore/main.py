"""
This module contains the main classes and methods for the filestore package.
"""
from typing import Any, Type, cast, TypeVar, Callable, Union, List, Dict
from abc import abstractmethod
from pathlib import Path
from logging import getLogger
from random import randint
from collections import defaultdict

from starlette.datastructures import UploadFile as StarletteUploadFile, FormData
from fastapi import Request, UploadFile as UF, Form, BackgroundTasks
from pydantic import BaseModel, create_model, Field

from .util import FormModel

try:
    td = True
    from typing import TypedDict
except ImportError:
    td = False
    Config = TypeVar('Config', bound=dict)
    FileField = TypeVar('FileField', bound=dict)

try:
    from functools import cache
except ImportError as err:
    from functools import lru_cache

    cache = lru_cache(maxsize=None)

logger = getLogger(__name__)
NoneType = type(None)


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


if td:
    class Config(TypedDict, total=False):
        """
        The configuration for the FastStore class.
        """
        dest: str
        destination: Callable[[Request, Form, str, UploadFile], Union[str, Path]]
        filter: Callable[[Request, Form, str, UploadFile], bool]
        max_files: int
        max_fields: int
        filename: Callable[[Request, Form, str, UploadFile], UploadFile]
        background: bool
        extra_args: dict
        bucket: str
        region: str


    class FileField(TypedDict, total=False):
        """
        The fields of the FileField class.
        """
        name: str
        max_count: int
        required: bool
        file: UploadFile
        config: Config

Self = TypeVar('Self', bound='FastStore')


def _file_filter(file):
    return isinstance(file, StarletteUploadFile)


def config_filter(req: Request, form: FormData, field: str, file: UploadFile) -> bool:
    """
    The default config filter function for the FastStore class. This filter applies to all fields.
    Args:
        req (Request): The request object.
        form (FormData): The form data object.
        field (Field): The name of the field.
        file (UploadFile): The file object.

    Returns (bool): True if the file is valid, False otherwise.
    """
    return True


def filename(req: Request, form: FormData, field: str, file: UploadFile) -> UploadFile:
    """
    Update the filename of the file object.

    Args:
        req (Request): The request object.
        form (FormData): The form data object.
        field (Field): The name of the field.
        file (UploadFile): The file object.

    Returns (UploadFile): The file object with the updated filename.
    """
    return file


class FileData(BaseModel):
    """
    The Store of a file storage operation.

    Attributes:
        path (str): The path to the file for local storage.
        url (str): The url to the file for cloud storage.
        status (bool): The status of the file storage operation.
        content_type (str): The content type of the file.
        filename (str | bytes): The name of the file or the file object for memory storage.
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
    file: Union[bytes, str] = None
    field_name: str = ''
    metadata: dict = {}
    error: str = ''
    message: str = ''


class Store(BaseModel):
    """
    The response model for the FastStore class.

    Attributes:
        file (FileData | None): The Store of a single file upload or storage operation.
        files (Dict[str, List[FileData]]): The response of the file storage operations(s) as a dictionary of field name and
            FileData arranged by field name and filename
        failed (Dict[str, List[FileData]]): The result of a failed file upload or storage operation as a dictionary of
            FileData arranged by field name and filename.
        error (str): The error message if the file storage operation failed.
        message (str): Success message if the file storage operation was successful.
    """
    file: Union[FileData, NoneType] = None
    files: Dict[str, List[FileData]] = defaultdict(list)
    failed: Dict[str, List[FileData]] = defaultdict(list)
    error: str = ''
    message: str = ''
    status: bool = True

    def __len__(self) -> int:
        total = 0
        for field in self.files.values():
            total += len(field)
        return total


class FastStore:
    """
    The base class for the FastStore package. It is an abstract class and must be inherited from for custom file
    storage services. The upload and multi_upload methods must be implemented in a child class.

    Attributes:
        fields (list[FileField]): The fields to expect from the form.
        request (Request): The request object.
        form (FormData): The form data object.
        config (dict): The configuration for the storage service.
        _store (Store): The Store of the file storage operation.
        store (Store): Property to access and set the result of the file storage operation.
        file_count (int): The Total number of files in the request.
        background_tasks (BackgroundTasks): The background tasks object for running tasks in the background.

    Methods:
        upload (Callable[[FileField]]): The method to upload a single file.

        multi_upload (Callable[List[FileField]]): The method to upload multiple files.

    Config:
        max_files (int): The maximum number of files to accept in a single request. Defaults to 1000.

        max_fields (int): The maximum number of fields to accept in a single request. Defaults to 1000.

        dest (str | Path): Destination to save the file to in the storage service defaults to 'uploads'.

        filename (Callable[[Request, FormData, str, UploadFile], UploadFile): A function that takes in the request,
            form and file, filename modifies the filename attribute of the file and returns the file.

        destination (Callable[[Request, FormData, str, UploadFile], str | Path]): A function that takes in the request,
            form and file and returns a path to save the file to in the storage service.

        filter (Callable[[Request, FormData, str, UploadFile], bool]): A function that takes in the request,
            form and file and returns a boolean.

        background (bool): A boolean to indicate if the file storage operation should be run in the background.

        extra_args (dict): Extra arguments to pass to the storage service.

        bucket (str): The name of the bucket to upload the file to in the cloud storage service.
    """
    fields: List[FileField]
    config: Config
    form: FormData
    request: Request
    background_tasks: BackgroundTasks
    file_count: int
    _store: Store
    store: Store

    def __init__(self, name: str = '', count: int = 1, required=False, fields: List[FileField] = None,
                 config: Config = None):
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
        self.config = {'filter': config_filter, 'max_files': 1000, 'max_fields': 1000, 'filename': filename,
                       **(config or {})}

    @property
    @cache
    def model(self) -> Type[FormModel]:
        """
        Returns a pydantic model for the form fields.
        Returns (FormModel):
        """
        body = {}
        for field in self.fields:
            if field.get('max_count', 1) > 1:
                body[field['name']] = (List[UploadFile], ...) if field.get('required', False) \
                    else (List[UploadFile], Field([], validate_default=False))
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
        self._store = Store()
        self.request = req
        self.background_tasks = bgt
        try:
            f_filter = self.config['filter']
            _filename = self.config['filename']
            max_files, max_fields = self.config['max_files'], self.config['max_fields']
            form = await req.form(max_files=max_files, max_fields=max_fields)
            self.form = form

            # this is terrible, but it works
            file_fields: List[FileField] = \
                [{'file': field.get('config', {}).get('filename', _filename)(req, form, field['name'], file), **field}
                 for field in self.fields for file in form.getlist((field['name']))[0:field.get('max_count', None)]
                 if (_file_filter(file) and
                     field.get('config', {}).get('filter', f_filter)(req, form, field['name'], file))]

            self.file_count = len(file_fields)
            if not file_fields:
                self._store = Store(message='No files were uploaded')

            elif len(file_fields) == 1:
                file_field = file_fields[0]
                await self.upload(file_field=file_field)

            else:
                await self.multi_upload(file_fields=file_fields)
        except (KeyError, AttributeError, ValueError, TypeError, NameError, MemoryError, BufferError) as err:
            logger.error(f'Error uploading files: {err} in {self.__class__.__name__}')
            self._store = Store(error=str(err), status=False)
        return self

    @abstractmethod
    async def upload(self, *, file_field: FileField):
        """
        Upload a single file to a storage service.

        Args:
            file_field (FileField): A FileField dictionary instance.
        """

    @abstractmethod
    async def multi_upload(self, *, file_fields: List[FileField]):
        """
        Upload multiple files to a storage service.

        Args:
            file_fields (list[FileField]): A list of FileFields to upload.
        """

    @property
    def store(self) -> Store:
        """
        Returns the Store of the file storage.

        Returns:
            Store: The Store of the file storage operation.
        """
        return self._store

    @store.setter
    def store(self, value: FileData):
        """
        Sets the Store of the file storage operation.

        Args:
            value: A FileData instance.
        """
        try:
            if not isinstance(value, FileData):
                logger.error(f'Expected FileData instance, got {type(value)} in {self.__class__.__name__}')
                return

            if self.file_count == 1:
                self._store.file = value if value.status else None
                self._store.message = f'{value.filename} stored' if value.status else \
                    f'{value.filename} not stored due to {value.error}'
                if value.status:
                    self._store.files[f'{value.field_name}'].append(value)
                else:
                    self._store.failed[f'{value.field_name}'].append(value)
                    self._store.error = f'{value.filename} not stored due to {value.error}'
            else:
                if value.status:
                    self._store.files[f'{value.field_name}'].append(value)
                    self._store.message += f'{value.filename} stored\n'
                else:
                    self._store.failed[f'{value.field_name}'].append(value)
                    self._store.error += f'{value.filename} not stored due to {value.error}\n'
        except Exception as err:
            logger.error(f'Error setting Store in {self.__class__.__name__}: {err}')
            self._store.error += f'{err}\n'
