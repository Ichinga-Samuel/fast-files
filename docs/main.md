<a id="faststore.main"></a>

This module contains the FastStore class which uploads files to a storage service such as local, cloud, or memory.\
It also contains the FileData and Result data classes which contains the result of the file storage operation.\
Helper functions for configurations are also defined here.

<a id="faststore.main.file_filter"></a>

### file_filter Function

```python
def file_filter(req: Request, form: Form, field: str, file: UploadFile) -> bool:
```
The default filter function.

**Arguments**:

- `req` _Request_ - The request object.
- `form` _Form_ - The form object.
- `field` _Field_ - The name of the field.
- `file` _UploadFile_ - The file object.
  
- `Returns` _bool_ - True if the file is valid, False otherwise.

<a id="faststore.main.filename"></a>

***
## filename Function
```python
def filename(req: Request, form: Form, field: str,
             file: UploadFile) -> UploadFile
```

Update the filename of the file object.

**Arguments**:

- `req` _Request_ - The request object.
- `form` _Form_ - The form object.
- `field` _Field_ - The name of the field.
- `file` _UploadFile_ - The file object.
  
- `Returns` _UploadFile_ - The file object with the updated filename.

<a id="faststore.main.Config"></a>
***
## Config

```python
class Config(TypedDict):
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
```

The configuration dictionary for the FastStore class.

<a id="faststore.main.FileData"></a>
***
## FileData Class

```python
class FileData(BaseModel):
```

The result of a file storage operation.

**Attributes**:

- `path (str)`: The path to the file for local storage.
- `url` _str_ - The url to the file for cloud storage.
- `status` _bool_ - The status of the file storage operation.
- `content_type` _str_ - The content type of the file.
- `filename` _str_ - The name of the file.
- `size` _int_ - The size of the file.
- `file` _bytes | None_ - The file object for memory storage.
- `field_name` _str_ - The name of the form field.
- `metadata` _dict_ - Extra metadata of the file.
- `error` _str_ - The error message if the file storage operation failed.
- `message` _str_ - Success message if the file storage operation was successful.

<a id="faststore.main.Result"></a>
***
## Result Class

```python
class Result(BaseModel):
```

The response model for the FastStore class.

**Attributes**:

- `file` _FileData | None_ - The result of a single file upload or storage operation.
- `files` _list[FileData]_ - The result of multiple file uploads or storage operations.
- `failed` _FileData | list[FileData]_ - The result of a failed file upload or storage operation.
- `error` _str_ - The error message if the file storage operation failed.
- `message` _str_ - Success message if the file storage operation was successful.

<a id="faststore.main.FastStore"></a>
***
## FastStore Class

```python
class FastStore:
```

This class is used to upload files to a storage service.
It is an abstract class and must be inherited from.
The upload and multi_upload methods must be implemented in a child class.

**Attributes**:

- `fields` _list[Fields]_ - The fields to expect from the form.
- `request` _Request_ - The request object.
- `form` _Form_ - The form object.
- `config` _dict_ - The configuration for the storage service.
- `_result` _Result_ - The result of the file storage operation.
- `result` _Result_ - Property to access and set the result of the file storage operation.
- `max_count` _int_ - The maximum number of files to accept for all fields.
- `background_tasks` _BackgroundTasks_ - The background tasks object for running tasks in the background.
  

**Methods**:

  upload (Callable[[tuple(str, UploadFile)]]): The method to upload a single file.
  
- `multi_upload` _Callable[[Request, Form, str, UploadFile]]_ - The method to upload multiple files.
  
  Config:
- `max_files` _int_ - The maximum number of files to accept in a single request. Defaults to 1000.
  
- `max_fields` _int_ - The maximum number of fields to accept in a single request. Defaults to 1000.
  
- `dest` _str | Path_ - Destination to save the file to in the storage service defaults to 'uploads'.
  
- `filename` _Callable[[Request, Form, str, UploadFile], UploadFile_ - A function that takes in the request,
  form and file, filename modifies the filename attribute of the file and returns the file.
  
- `destination` _Callable[[Request, Form, str, UploadFile], str | Path]_ - A function that takes in the request,
  form and file and returns a path to save the file to in the storage service.
  
- `filter` _Callable[[Request, Form, str, UploadFile], bool]_ - A function that takes in the request, form and file
  and returns a boolean.
  
- `background` _bool_ - A boolean to indicate if the file storage operation should be run in the background.
  
- `extra_args` _dict_ - Extra arguments to pass to the storage service.
  
- `bucket` _str_ - The name of the bucket to upload the file to in the cloud storage service.

<a id="faststore.main.FastStore.__init__"></a>

#### \_\_init\_\_

```python
def __init__(name: str = '',
             count: int = 1,
             required=False,
             fields: list[Fields] | None = None,
             config: Config | None = None)
```

Initialize the FastStore class. For single file upload, specify the name of the file field and the expected
number of files. If the field is required, set required to True.
For multiple file uploads, specify the fields to expect from the form and the expected number
of files for each field. If the field is required, set required to True.
Use the config parameter to specify the configuration for the storage service.

**Arguments**:

- `name` _str_ - The name of the file field to expect from the form for a single field upload.
- `count` _int_ - The maximum number of files to accept for single field upload.
- `required` _bool_ - required for single field upload. Defaults to false.
- `fields` - The fields to expect from the form. Usually for multiple file uploads from different fields.
  

**Notes**:

  If fields is specified, name and count are ignored.

<a id="faststore.main.FastStore.model"></a>

#### model

```python
@property
@cache
def model()
```

Returns a pydantic model for the form fields.

Returns (FormModel):

<a id="faststore.main.FastStore.__call__"></a>

#### \_\_call\_\_

```python
async def __call__(req: Request, bgt: BackgroundTasks) -> Self
```

Upload files to a storage service. This enables the FastStore class instance to be used as a dependency.

**Arguments**:

- `req` _Request_ - The request object.
- `bgt` _BackgroundTasks_ - The background tasks object for running tasks in the background.
  

**Returns**:

- `FastStore` - An instance of the FastStore class.

<a id="faststore.main.FastStore.upload"></a>

#### upload

```python
@abstractmethod
async def upload(*, field_file: tuple[str, UploadFile])
```

Upload a single file to a storage service.

**Arguments**:

- `field_file` _tuple[str, UploadFile]_ - A tuple containing the name of the file field and the file to upload.

<a id="faststore.main.FastStore.multi_upload"></a>

#### multi\_upload

```python
@abstractmethod
async def multi_upload(*, field_files: list[tuple[str, UploadFile]])
```

Upload multiple files to a storage service.

**Arguments**:

- `field_files` _list[tuple[str, UploadFile]]_ - A list of tuples containing the name of the file field and the

<a id="faststore.main.FastStore.result"></a>

#### result

```python
@property
def result() -> Result
```

Returns the result of the file storage.

**Returns**:

- `Result` - The result of the file storage operation.

<a id="faststore.main.FastStore.result"></a>

#### result

```python
@result.setter
def result(value: FileData)
```

Sets the result of the file storage operation.

**Arguments**:

- `value` - A FileData instance.
