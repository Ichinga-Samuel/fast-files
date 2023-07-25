from pydantic import BaseModel, create_model, Field
from typing import Optional


def make_model(name: str, **kwargs):
    return create_model(name, **kwargs)


file = 'tom'

v = make_model('Test', file=(Optional[int], ...), nam=(str, ...))

v(nam='4')
print(v.file)