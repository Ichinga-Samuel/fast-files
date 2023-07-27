from fastapi import FastAPI, Request, Depends, UploadFile, Form
import uvicorn
from dotenv import load_dotenv
from ..src.faststore import LocalStorage, S3Storage, MemoryStorage, Result


load_dotenv()

app = FastAPI()

single_local = LocalStorage(name='book')
multiple_local = LocalStorage(fields=[{'name': 'author', 'max_count': 3}, {'name': 'book', 'max_count': 2}])


multiple_s3 = S3Storage(fields=[{'name': 'author', 'max_count': 2}, {'name': 'book', 'max_count': 2}])
single_s3 = S3Storage(name='author')

single_mem = MemoryStorage(name='cover')
multiple_mem = MemoryStorage(fields=[{'name': 'author', 'max_count': 2}, {'name': 'book', 'max_count': 2}])


@app.post('/local_single', response_model=Result)
async def local_single(sl_form=Depends(single_local.model), sl=Depends(single_local)) -> Result:
    return sl.result


# @app.post('/upload_book', response_model=Result)
# async def upload_book(form=Depends(local.model), boo: LocalStorage = Depends(local)) -> Result:
#     return boo.result
#
#
# @app.post('/upload_cover')
# async def upload_cover(cover: MemoryStorage = Depends(mem)) -> Result:
#     return cover.result

# if __name__ == "__main__":
#     uvicorn.run("app:app", port=5000, log_level="info")
