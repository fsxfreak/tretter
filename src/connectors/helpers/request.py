import logging
from typing import Callable, Awaitable, Optional

import niquests

logger = logging.getLogger(__name__)


async def safe_request(
    request_func: Callable[..., Awaitable[niquests.Response]], *args, **kwargs
) -> Optional[niquests.Response]:
    kwargs.setdefault("timeout", 10)

    response = None
    try:
        response = await request_func(*args, **kwargs)
        response.raise_for_status()
        return response
    except niquests.exceptions.HTTPError as e:
        if response:
            logger.error(f"HTTP Error: {e} - Response Body: {response.text}")
    except niquests.exceptions.RequestException as e:
        logger.error(f"Network error during request: {e}")

    return None
