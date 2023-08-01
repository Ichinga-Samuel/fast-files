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

# local storage instance for multiple file upload with a maximum of 2 files from the same field
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

