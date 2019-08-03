'''Returns a response hook function which sleeps for `timeout` seconds if
    response is not cached

the first exempt calls exempted from throttling

'''
import logging
from time import sleep
from random import random

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


def make_throttle_hook(timeout=0.67, exempt=1000):
    """
    Returns a response hook function which sleeps for `timeout` seconds if
    response is not cached

    the first exempt calls exempted from throttling

    time.sleep(max(0, timeout - 0.5) + random())
        average delay: timeout

    s = requests_cache.CachedSession()
    s.hooks = {'response': make_throttle_hook(0.1)}
    s.get('http://httpbin.org/delay/get')
    s.get('http://httpbin.org/delay/get')
    """

    try:
        timeout = float(timeout)
    except Exception as _:
        timeout = .67

    try:
        exempt = int(exempt)
    except Exception as _:
        exempt = 100

    def hook(response, *args, **kwargs):  # pylint: disable=unused-argument
        if not getattr(response, 'from_cache', False):
            timeout_ = timeout + random() - 0.5
            timeout_ = max(0, timeout_)

            try:
                hook.flag
            except AttributeError:
                hook.flag = -1
            finally:
                hook.flag += 1
                quo, _ = divmod(hook.flag, exempt)
            # quo is 0 only for the first exempt calls

            LOGGER.debug('avg delay: %s, sleeping %s s, flag: %s', timeout, timeout_, bool(quo))

            # will not sleep (timeout_ * bool(quo)=0) for the first exempt calls
            sleep(timeout_ * bool(quo))

        return response
    return hook
