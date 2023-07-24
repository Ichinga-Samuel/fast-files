from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from dotenv import load_dotenv
from src.faststore.localstorage import LocalStorage
from src.faststore.s3 import S3

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory='.')
local = LocalStorage(name='book', config={'background': True})

s3 = S3(fields=[{'name': 'author'}], config={'background': True})
# local = LocalStorage(name='book')

@app.get('/')
async def home(req: Request):
    return templates.TemplateResponse('home.html', {'request': req})


@app.post('/upload')
async def upload(author: S3 = Depends(s3), book: LocalStorage = Depends(local)):
    print(author.result.files, book.result.file)
    return RedirectResponse('/', status_code=302)


if __name__ == "__main__":
    uvicorn.run("app:app", port=5000, log_level="info")
