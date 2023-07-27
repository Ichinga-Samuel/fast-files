from abc import abstractmethod
from typing import TypedDict, TypeVar, NotRequired, Callable
from functools import cache
from pathlib import Path

from starlette.datastructures import UploadFile as StarletteUploadFile
from fastapi import UploadFile, Request, Form, BackgroundTasks, File
from pydantic import BaseModel, create_model, Field

Fields = TypedDict('Fields', {'name': str, 'max_count': NotRequired[int], 'required': NotRequired[bool]})
Self = TypeVar('Self', bound='FastStore')


def file_filter(req: Request, form: Form, field: str, file: UploadFile) -> bool:
    return True if (isinstance(file, StarletteUploadFile) and file.filename) else False


def filename(req: Request, form: Form, field: str, file: UploadFile) -> UploadFile:
    return file


class Config(TypedDict, total=False):
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
    file: FileData | None = None
    files: list[FileData] = []
    failed: FileData | list[FileData] = []
    error: str = ''
    message: str = ''
    status: bool = True

    def reset(self):
        self.file = None
        self.files = []
        self.failed = []
        self.error = ''
        self.message = ''
        self.status = True
        return self


class FastStore:
    name: str
    count: int
    fields: list[Fields]
    config: Config = {'filter': file_filter, 'max_files': 1000, 'max_fields': 1000, 'filename': filename}
    form: Form
    request: Request
    result: Result
    background_tasks: BackgroundTasks
    """
    This class is used to upload files to a storage service.
    It is an abstract class and must be inherited from.
    The upload and multi_upload methods must be implemented in a child class.
    
    Attributes:
        name(str): The name of the form field to expect the file from. defaults to file.
        count(int): The number of files to expect when using the name argument to represent a single field
        this defaults to one
        fields(list[Fields]): The fields to expect from the form.
        request(Request): The request object.
        form(Form): The form object.
        config(dict): The configuration for the storage service.
        result(Result): The result of the file storage operation.
        background_tasks(BackgroundTasks): The background tasks object for running tasks in the background.
    
    Config:
        filter(Callable[]): A function that takes in the request, form and file and returns a boolean.
        max_files: The maximum number of files to accept in a single request. Defaults to 1000.
        max_fields: The maximum number of fields to accept in a single request. Defaults to 1000.
        filename: A function that takes in the request, form and file, 
                  filename modifies the filename attribute of the file and returns the file.
        dest: Destination to save the file to in the storage service defaults to 'uploads'.
        destination: A function that takes in the request, form and file and returns a path to save the file to in the storage service.
    """

    def __init__(self, name: str = '', count: int = 1, required=False, fields: list[Fields] | None = None,
                 config: dict | None = None):
        """
        Args:
            name (str): The name of the file field to expect from the form for a single field upload.
            count (int): The maximum number of files to accept for single field upload.
            required (bool): required for single field upload. Defaults to false.
            fields: The fields to expect from the form. Usually for multiple file uploads from different fields.

            Note:
                If fields is specified, name and count are ignored.
        """
        self.name = name
        self.fields = fields
        self.fields = self.fields or [{'name': self.name, 'max_count': count, 'required': required}]
        self.config |= (config or {})
        self._result = Result()

    @property
    @cache
    def model(self):
        body = {}
        for field in self.fields:
            body[field['name']] = (UploadFile, ...) if field.get('required') else (UploadFile, Field(default=UploadFile(File(...))))
        return create_model('Form', **body)

    async def __call__(self, req: Request, bgt: BackgroundTasks) -> Self:
        self.result.reset()
        try:
            _filter = self.config['filter']
            _filename = self.config['filename']
            max_files, max_fields = self.config['max_files'], self.config['max_fields']
            form = await req.form(max_files=max_files, max_fields=max_fields)
            self.request = req
            self.form = form
            self.background_tasks = bgt
            file_fields = [(field['name'], _filename(req, form, field['name'], file)) for field in self.fields for file in
                           form.getlist((field['name']))[0:field.get('max_count', None)] if
                           _filter(req, form, field['name'], file)]
            self.max_count = len(file_fields)

            if not file_fields:
                self._result = Result(message='No files were uploaded')
                
            elif len(file_fields) == 1:
                file_field = file_fields[0]
                await self.upload(field_file=file_field)
                
            else:
                await self.multi_upload(field_files=file_fields)
        except Exception as e:
            self._result = Result(error=str(e), status=False)
        return self

    @abstractmethod
    async def upload(self, *, field_file: tuple[str, UploadFile]) -> FileData:
        """"""

    @abstractmethod
    async def multi_upload(self, *, field_files: list[tuple[str, UploadFile]]) -> list[FileData]:
        """"""

    @property
    def result(self):
        """"""
        return self._result

    @result.setter
    def result(self, value: FileData):
        try:
            if self.max_count == 1:
                self._result.file = value if value.status else None
                self._result.message = f'{value.filename} stored'
                self._result.files.append(value) if value.status else self.result.failed.append(value)
            else:
                self._result.files.append(value) if value.status else self.result.failed.append(value)
                self._result.message = f'{len(self._result.files)} files stored'
        except Exception as e:
            self._result.error = str(e)
            self._result.status = False
