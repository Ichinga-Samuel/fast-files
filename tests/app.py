from fastapi import FastAPI, Request, Depends, UploadFile, Form
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from dotenv import load_dotenv
from src.faststore import LocalStorage, S3Storage, MemoryStorage, Result


load_dotenv()

class Test(BaseModel):
    file: UploadFile = Form(...)
    name: str = Form(...)


app = FastAPI()
# templates = Jinja2Templates(directory='.')
local = LocalStorage(name='book', count=3)
s3 = S3Storage(fields=[{'name': 'author', 'max_count': 3}])
mem = MemoryStorage(name='cover')


@app.post('/upload_author')
async def upload_author(author: S3Storage = Depends(s3)) -> Result:
    return author.result


@app.post('/upload_book', response_model=Result)
async def upload_book(form=Depends(local.model), boo: LocalStorage = Depends(local)) -> Result:
    return boo.result


@app.post('/upload_cover')
async def upload_cover(cover: MemoryStorage = Depends(mem)) -> Result:
    return cover.result

@app.post('/test')
async def test(test: Test = Depends(Test)):
    return {'file': test.file, 'name': test.name}

@app.get('/')
async def index(request: Request):
    return RedirectResponse(url='/docs')

if __name__ == "__main__":
    uvicorn.run("app:app", port=5000, log_level="info")
