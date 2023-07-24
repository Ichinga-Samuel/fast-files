from pathlib import Path
import asyncio


async def err(n):
    if n == 5:
        raise ValueError('This is not allowed')
    return n

def check(n):
    return n

async def main():
    task = await asyncio.gather(*[err(n) for n in range(10)], return_exceptions=True)
    # print(v:=type(task[5]))
    # print(isinstance(task[5], Exception))
    print(str(task[5]))
asyncio.run(main())
