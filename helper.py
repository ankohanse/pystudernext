
import asyncio
import inspect


class RunHelper():
    """Helper class to run the example code after converting from async to sync"""
    @staticmethod
    def run(func, *args, **kwargs):
        if inspect.iscoroutinefunction(func):
            asyncio.run(func(*args, **kwargs))
        else:
            func(*args, **kwargs)
            