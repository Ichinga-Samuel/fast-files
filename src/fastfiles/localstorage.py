from .main import FileUpload, FileData
from pprint import pp


class Local(FileUpload):
    async def upload(self) -> FileData:
        file = await self.file.read()
        g = open(f'{self.file.filename}', 'wb')
        g.write(file)
        g.close()
        print(type(file))
        return FileData(size=self.file.size, filename=self.file.filename, content_type=self.file.content_type)
