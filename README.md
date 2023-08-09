# FileStore
![GitHub](https://img.shields.io/github/license/ichinga-samuel/faststore?style=plastic)
![GitHub issues](https://img.shields.io/github/issues/ichinga-samuel/faststore?style=plastic)
![PyPI](https://img.shields.io/pypi/v/filestore)

## Introduction
Simple file storage dependency for FastAPI. Makes use of FastAPI's dependency injection system to provide a simple way
to store files. Inspired by Multer it allows both single and multiple file uploads through different fields with a 
simple interface. Comes with a default implementation for local file storage, simple in-memory storage and AWS S3
storage but can be easily extended to support other storage systems.

## Installation

```bash 
# Python 3.10+
pip install filestore

# to use aws s3 storage
pip install filestore[s3]
```
## Usage

```python
from fastapi import FastAPI, File, UploadFile, Depends
from filestore import LocalStorage, Result

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
FastStore Instantiation. All arguments are keyword arguments.\
**Keyword Arguments:**
- `name str`: The name of the file field to expect from the form for a single field upload.
- `count int`: The maximum number of files to accept for a single field upload.
- `required bool`: Required for single field upload. Defaults to false.
- `fields list[FileField]`: A list of fields to expect from the form. Usually for multiple file uploads from different fields.
- `config Config`: The Config dictionary

**Note:**\
If you provide both name and fields arguments the two are merged together with the name argument taking precedence if there is a name clash.\
**FileField**
A dictionary representing form fields. 
- `name str`: The name of the field
- `max_count int`: The maximum number of files to expect. Defaults to one
- `required bool`: Optional flag to indicate if field is required. Defaults to false if not specified.
- `config Config`: A config dict for individual field: This is optional.

**Config**\
The config dictionary is to be passed to faststore class during instantiation or added to individual file field dict
|Key|Description|Note|
|---|---|---|
|`dest (str\|Path)`|The path to save the file relative to the current working directory. Defaults to uploads. Specifying destination will override dest |LocalStorage and S3Storage
|`destination Callable[[Request, Form, str, UploadFile], str \| Path]`|A destination function saving the file|Local and Cloud Storage|
|`filter Callable[[Request, Form, str, UploadFile], bool]`|Remove unwanted files|
|`max_files int`|The maximum number of files to expect. Defaults to 1000| Not applicable to filefield config dict|
|`max_fields int`|The maximum number of file fields to expect. Defaults to 1000| Not applicable in filefield config dict|
|`filename Callable[[Request, Form, str, UploadFile], UploadFile]`|A function for customizing the filename|Local and Cloud Storage|
|`background bool`|If true run the storage operation as a background task|Local and Cloud Storage|
|`extra_args dict`|Extra arguments for AWS S3 Storage| S3Storage|
|`bucket str`|Name of storage bucket for cloud storage|Cloud Storage|
|`region str`|Name of region for cloud storage|Cloud Storage| Not available in filefield config dict|

**\_\_call\_\_**\
This method allows you to use the FastStore instance as a dependency for your route function. It sets the result
of the file storage operation and returns an instance of the class. It accepts the request object and the background
task object. The background task object is only used if the background config parameter is set to true.

**model**\
The model property dynamically generates a pydantic model for the FastStore instance. This model can be used as a
dependency for your path function. It is generated based on the fields attribute. It is useful for validating the form
fields and for API documentation. Using this property in your path function will enable openapi generate the
appropriate form fields.

**result**\
The result property returns the result of the file storage operation. The setter method accepts
a FileData object while the getter method returns a Result object.

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

## Result Class
The response model for the FastStore class. A pydantic model.
- `file FileData | None`: The result of a single file upload or storage operation.
- `files list[FileData]`: The result of multiple file uploads or storage operations.
- `failed list[FileData]`: The results of a failed file upload or storage operation.
- `error str`: The error message if the file storage operation failed.
- `message str`: Success message if the file storage operation was successful.

### Filename and Destination Function. 
You can specify a filename and destination function for customizing a filename and specifying a storage location for the saved file.
The filename function should modify the filename attribute of the file and return the modified file while the destination function should return a path or string object. These functions have access to the request object, the form, the form field and the file objects.

#### A destination function
```python
def local_destination(req: Request, form: FormData, field: str, file: UploadFile) -> Path:
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
def local_filename(req: Request, form: FormData, field: str, file: UploadFile) -> UploadFile:
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
def local_filter(req: Request, form: FormData, field: str, file: UploadFile) -> bool:
    """
    Local storage filter function.
    Returns:
        bool: True if the file is a text file, False otherwise.
    """
    return file.filename and file.filename.endswith('.txt')
```
### Example
```python
# initiate a local storage instance with a destination function, a filename function and a filter function.

loc = LocalStorage(
    fields = [{'name': 'book', 'max_count': 2, 'required': True}, {'name': 'image', 'max_count': 2}],
    config={
        'destination': local_destination,
        'filename': local_filename,
        'filter': local_filter
    }
)
@app.post('/upload')
async def upload(form: Form = Depends(loc)):
    return loc.result
```
### Swagger UI and OpenAPI 
Adding the model property of the faststore instance as a dependency to the route function will add a pydantic model
generated from the form fields to the swagger ui and openapi docs.

### Error Handling.
Any error that occurs is caught and passed to the error attribute of the FileData class and the status is set to false
indicating a failed operation then the FileData object is added to the failed list of the result object.

## Storage Classes
To all storage class inherit from the base FastStore class. This class implements a callable instance that can be used
as a dependency in a fastapi route. The instance is called with the request and the background task object. It returns
itself and updates the _result attribute with the result of the file storage operation. The _result attribute accessed
and updated via the result property. The result property returns a Result object.

### LocalStorage
This class handles local file storage to the disk.

### S3Storage
This class handles cloud storage to AWS S3. When using this class ensure that the following environment variables
are set. Any extra parameters is passed to the extra_args dict of the config dict.
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION`: This is optional as you can specify the region in the config.
- `AWS_BUCKET_NAME`: This is optional as you can specify the bucket name in the config.

```python   
from filestore import S3Storage
s3 = S3Storage(fields=[{'name': 'book', 'max_count': 2, 'required': True}, {'name': 'image', 'max_count': 2}],
               config={'region': 'us-east-1', 'bucket': 'my-bucket', extra_args={'ACL': 'public-read'}})
```

### MemoryStorage
This class handles memory storage. It stores the file in memory and returns the file object in the result object as 
a bytes object.

### Background Tasks
You can run the file storage operation as a background task by setting the background config parameter to True.

### Build your own storage class
You can build your own storage class by inheriting from the FastStore class and implementing the **upload** and 
**multiple_upload** methods. Just make sure you properly set the private **_result** attribute with the result of the file 
storage operation.
