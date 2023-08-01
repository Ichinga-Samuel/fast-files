# FastStore

Simple file storage dependency for FastAPI. Makes use of FastAPI's dependency injection system to provide a simple way
to store files. Inspired by Multer it allows both single and multiple file uploads through different fields with a 
simple interface. Comes with a default implementation for local file storage, simple in-memory storage and AWS S3
storage but can be easily extended to support other storage systems.

## Installation

```bash 
pip install faststore
```
## Usage

```python
from fastapi import FastAPI, File, UploadFile, Depends
from faststore import LocalStorage, Result

app = FastAPI()

# local storage instance for single file upload
loc = LocalStorage(name='book', required=True)

# local storage instance for multiple file upload with a maximum of 2 files from a single field
loc2 = LocalStorage(name='book', required=True, count=2)

# local storage instance for multiple file uploads from different fields
multiple_local = LocalStorage(fields=[{'name': 'author', 'max_count': 2}, {'name': 'book', 'max_count': 1}])


@app.post('/upload_book')
async def upload_book(book=Depends(loc), model=Depends(loc.model)):
    return book.result


@app.post('/local_multiple', name='upload', openapi_extra={'form': {'multiple': True}})
async def local_multiple(model=Depends(multiple_local.model), loc=Depends(multiple_local)) -> Result:
    return loc.result
```

## API
FastStore Instantiation. All arguments are keyword arguments.
**Keyword Arguments**:
- `name str`: The name of the file field to expect from the form for a single field upload.
- `count int`: The maximum number of files to accept for a single field upload.
- `required bool`: Required for single field upload. Defaults to false.
- `fields list[Fields]`: A list of fields to expect from the form. Usually for multiple file uploads from different fields.
- `config Config`: The Config dictionary

**Note**:
If you provide both name and fields arguments the two are merged together with the name argument taking precedence if there is a name clash.\
**Fields**
A dictionary representing form fields. 
- `name str`: The name of the field
- `max_count int`: The maximum number of files to expect
- `required bool`: Optional flag to indicate if field is required. Defaults to false if not specified.

**Config**
The config dictionary to be passed to faststore. Config is a TypeDict and can be extended for customization.
|Key|Description|Note|
|---|---|---|
|`dest (str\|Path)`|The path to save the file relative to the current working directory. Defaults to uploads. Specifying destination will overide dest |LocalStorage and S3Storage
|`destination Callable[[Request, Form, str, UploadFile], str \| Path]`|A destination function saving the file|Local and Cloud Storage|
|`filter Callable[[Request, Form, str, UploadFile], bool]`|Remove unwanted files|
|`max_files int`|The maximum number of files to expect. Defaults to 1000|
|`max_fields int`|The maximum number of file fields to expect. Defaults to 1000|
|`filename Callable[[Request, Form, str, UploadFile], UploadFile]`|A function for customizing the filename|Local and Cloud Storage|
|`background bool`|If true run the storage operation as a background task|Local and Cloud Storage|
|`extra_args dict`|Extra arguments for AWS S3 Storage| S3Storage|
|`bucket str`|Name of storage bucket for cloud storage|Cloud Storage|
|`region str`|Name of region for cloud storage|Cloud Storage|

### FileData
This pydantic model represents the result of an individual file storage operation.
- `path str`: The path to the file for local storage.
- `url str`: The url to the file for cloud storage.
- `status bool`: The status of the file storage operation.
- `content_type bool`: The content type of the file.
- `filename str`: The name of the file.
- `size int`: The size of the file.
- `file bytes`: The file object for memory storage.
- `field_name str`: The name of the form field.
- `metadata dict`: Extra metadata of the file.
- `error str`: The error message if the file storage operation failed.
- `message str`: Success message if the file storage operation was successful.

## StoreResult Class
The response model for the FastStore class. A pydantic model.
- `file FileData | None`: The result of a single file upload or storage operation.
- `files list[FileData]`: The result of multiple file uploads or storage operations.
- `failed list[FileData]`: The result of a failed file upload or storage operation.
- `error str`: The error message if the file storage operation failed.
- `message str`: Success message if the file storage operation was successful.

### Filename and Destination Function. 
You can specify a filename and destination function for customizing a filename and specifying a storage location for the saved file.
The filename function should modify the filename attribute of the file and return the modified file while the destination function should return a path or string object.

#### A destination function
```python
def local_destination(req: Request, form: Form, field: str, file: UploadFile) -> Path:
    """
    Local storage destination function.
    Pass this function to the LocalStorage config parameter 'destination' to create a destination for the file.
    Creates a directory named after the field inside the test_data/uploads folder if it doesn't exist.

    Returns:
        Path: Path to the stored file.
    """
    path = Path.cwd() / f'test_data/uploads/{field}'
    path.mkdir(parents=True, exist_ok=True) if not path.exists() else ...
    return path / f'{file.filename}'
```
#### A filename function
```python
def local_filename(req: Request, form: Form, field: str, file: UploadFile) -> UploadFile:
    """
    Local storage filename function. Appends 'local_' to the filename.

    Returns:
        UploadFile: The file with the new filename.
    """
    file.filename = f'local_{file.filename}'
    return file
```
### Filtering
Set this to a function to control which files should be uploaded and which should be skipped. The function should look like this:
```python
def local_filter(req: Request, form: Form, field: str, file: UploadFile) -> bool:
    """
    Local storage filter function.
    Returns:
        bool: True if the file is a text file, False otherwise.
    """
    return file.filename and file.filename.endswith('.txt')
```








