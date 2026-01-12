def slugify(text: str) -> str:
    return text.replace(' ', '_').replace('(', '').replace(')', '').replace('/', 'OR').replace('&', ' ').replace(':', '').replace('.', '').lower()

import logging
from typing import Any
logger = logging.getLogger(__name__)

def with_retries(fun, *args, max_tries=3, exception=Exception, msg=f"Exception. Retrying") -> Any:
    """Call fun() max_tries number of times, until it executes without an exception. 
    
    If max_tries is exceeded, the exception raised on the last call is raised. 

    Args:
        fun (_type_): Callable
        *args: Arguments passed to fun
        exception (_type_, optional): Exception to catch. Defaults to Exception.
        msg (_type_, optional): Error message logged between retries. Defaults to f"Exception. Retrying".
        max_tries (int, optional): Number of times to attempt executing fun(). Defaults to 3.

    Raises:
        exception: If max_tries is exceeded. The exception raised on the last call.

    Returns:
        Any: value returned by fun()
    """
       
    msg += f" {fun}."
    val: Any

    for i in range(max_tries):
        try:
            val = fun(*args)
            break
        except exception as e:
            logger.error(msg)
            if i == max_tries-1: 
                raise e
            continue

    return val
