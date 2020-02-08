import trio


async def after(duration, task_status=trio.TASK_STATUS_IGNORED):
    timeout = trio.Event()
    task_status.started(timeout)
    await trio.sleep(duration)
    timeout.set()
