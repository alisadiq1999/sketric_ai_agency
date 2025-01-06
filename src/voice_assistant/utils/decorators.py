import asyncio
import functools
import time

from voice_assistant.utils.log_utils import log_runtime


def timeit_decorator(func):
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = await func(*args, **kwargs)
        duration = round(time.perf_counter() - start_time, 4)
        if args and hasattr(args[0], "__class__"):
            class_name = args[0].__class__.__name__
            log_runtime(f"{class_name}.{func.__name__}", duration)
        else:
            log_runtime(func.__name__, duration)
        return result

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        duration = round(time.perf_counter() - start_time, 4)
        if args and hasattr(args[0], "__class__"):
            class_name = args[0].__class__.__name__
            log_runtime(f"{class_name}.{func.__name__}", duration)
        else:
            log_runtime(func.__name__, duration)
        return result

    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
