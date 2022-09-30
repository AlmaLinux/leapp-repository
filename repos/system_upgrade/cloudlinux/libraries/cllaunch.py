import functools
from leapp.libraries.common.config import version


def run_on_cloudlinux(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if (version.current_version()[0] != "cloudlinux"):
            return
        return func(*args, **kwargs)
    return wrapper
