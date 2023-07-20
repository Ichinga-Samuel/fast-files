from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import uvicorn

from src.fastfiles.localstorage import Local, FileData

app = FastAPI()
templates = Jinja2Templates(directory='.')
local = Local()


@app.get('/')
async def home(req: Request):
    return templates.TemplateResponse('home.html', {'request': req})


@app.post('/upload')
async def upload(file: FileData = Depends(local)):
    # print()
    return RedirectResponse('/', status_code=302)


if __name__ == "__main__":
    uvicorn.run("app:app", port=5000, log_level="info")
