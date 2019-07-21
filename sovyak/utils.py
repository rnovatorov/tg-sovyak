async def aiter(aiterable):
    return await aiterable.__aiter__()
