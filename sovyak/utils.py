async def anext(aiterator):
    return await aiterator.__anext__()
