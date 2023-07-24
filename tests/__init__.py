from fastapi import Request, UploadFile, Form


def file_filter(req: Request, form: Form, file: UploadFile) -> bool:
    return True if file.filename.startswith('test') else False


def filename(req: Request, form: Form, file: UploadFile) -> UploadFile:
    file.filename = 'test'+file.filename
    return file
