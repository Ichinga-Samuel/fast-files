from abc import abstractmethod
from typing import TypedDict, TypeVar, NotRequired, Callable
from pathlib import Path

from fastapi import UploadFile, Request, Form, BackgroundTasks
from pydantic import BaseModel

Fields = TypedDict('Fields', {'name': str, 'max_count': NotRequired[int]})
Self = TypeVar('Self', bound='FastStore')


def file_filter(req: Request, form: Form, field: str, file: UploadFile) -> bool:
    return True if file else False


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
    error_msg: str = ''


class Result(BaseModel):
    file: FileData | None = None
    files: list[FileData] = []
    failed: FileData | list[FileData] = []
    error_message: str = ''


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
        count(int): The maximum number of files to accept when using the name argument to represent a single field
        this defaults to one
        fields(list[Fields]): The fields to expect from the form.
        request(Request): The request object.
        form(Form): The form object.
        config(dict): The configuration for the storage service.
        result(Result): The result of the filestorage operation.
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

    def __init__(self, name: str = '', count: int = 1, fields: list[Fields] | None = None,
                 config: dict | None = None):
        """
        Args:
            name: The name of the file field to expect from the form for a single field upload.
            count: The maximum number of files to accept for single field upload.
            fields: The fields to expect from the form. Usually for multiple file uploads from different fields.

            Note:
                If fields is specified, name and count are ignored.
        """
        self.name = name
        self.fields = fields
        self.fields = self.fields or [{'name': self.name, 'max_count': count}]
        self.max_count = sum([field.get('max_count', 1) for field in self.fields])
        self.config |= (config or {})
        self._result = Result()

    async def __call__(self, req: Request, bgt: BackgroundTasks) -> Self:
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

            if not file_fields:
                self.result = Result(error_message='No files were uploaded')

            elif len(file_fields) == 1:
                file_field = file_fields[0]
                await self.upload(field_file=file_field)

            else:
                await self.multi_upload(field_files=file_fields)
        except Exception as e:
            self.result = Result(error_message=str(e))

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

            self._result.files.append(value) if value.status else self.result.failed.append(value)
        except Exception as e:
            self._result.error_message = str(e)
