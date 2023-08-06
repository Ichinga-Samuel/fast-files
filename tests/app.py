"""
This module contains the FastAPI application and the endpoints.
"""
import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from .utils import single_local, multiple_local, single_s3, multiple_s3, single_mem, multiple_mem, Result

load_dotenv()

app = FastAPI()

templates = Jinja2Templates(directory='.')


@app.get('/')
async def home(req: Request):
    """
    Home page. Renders the home.html template.
    """
    return templates.TemplateResponse('home.html', {'request': req})


@app.post('/local_single')
async def local_single(model=Depends(single_local.model), sl=Depends(single_local)) -> Result:
    """
    Local storage single file upload endpoint.

    Args:
        model (FormModel): The form model dynamically built from the form file fields.
            This only useful to swagger UI to show the form fields.
        sl (LocalStorage): The LocalStorage instance.

    Returns:
        Result: The result of the storage operation.
    """
    return sl.result


@app.post('/local_multiple', name='upload', openapi_extra={'form': {'multiple': True}})
async def local_multiple(model=Depends(multiple_local.model), loc=Depends(multiple_local)) -> Result:
    """
    Local storage multiple file upload endpoint.

    Args:
        model (FormModel): The form model dynamically built from the form file fields.
            This only useful to swagger UI to show the form fields.
        loc (LocalStorage): The LocalStorage instance.

    Returns:
        Result: The result of the storage operation.
    """
    return loc.result


@app.post('/s3_multiple', openapi_extra={'form': {'multiple': True}})
async def s3_multiple(model=Depends(multiple_s3.model), s3=Depends(multiple_s3)) -> Result:
    """
    S3 storage multiple file upload endpoint.

    Args:
        model (FormModel): The form model dynamically built from the form file fields.
            This only useful to swagger UI to show the form fields.
        s3 (S3Storage): The S3Storage instance.

    Returns:
        Result: The result of the storage operation.
    """
    return s3.result


@app.post('/s3_single')
async def s3_single(model=Depends(single_s3.model), s3=Depends(single_s3)) -> Result:
    return s3.result


@app.post('/mem_single')
async def mem_single(model=Depends(single_mem.model), mem=Depends(single_mem)) -> Result:
    """
    Memory storage single file upload endpoint.

    Args:
        model (FormModel): The form model dynamically built from the form file fields.
            This only useful to swagger UI to show the form fields.
        mem (MemoryStorage): The MemoryStorage instance.

    Returns:
        Result: The result of the storage operation.
    """
    return mem.result


@app.post('/mem_multiple', openapi_extra={'form': {'multiple': True}})
async def mem_multiple(model=Depends(multiple_mem.model), mem=Depends(multiple_mem)) -> Result:
    """
    Memory storage multiple file upload endpoint.

    Args:
        model (FormModel): The form model dynamically built from the form file fields.
            This only useful to swagger UI to show the form fields.
       mem (MemoryStorage): The MemoryStorage instance.

    Returns:
        Result: The result of the storage operation.
    """
    return mem.result


if __name__ == "__main__":
    uvicorn.run("app:app", port=5000, log_level="info")
