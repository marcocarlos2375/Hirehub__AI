"""
Timeout and retry logic for external API calls
Prevents indefinite hangs and provides retry mechanism
"""

import time
import asyncio
from typing import Callable, Any, Optional
from functools import wraps
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from app.config import get_settings

settings = get_settings()

# Thread pool for running synchronous functions with timeout
_executor = ThreadPoolExecutor(max_workers=10)


class TimeoutError(Exception):
    """Custom timeout exception"""
    pass


class RetryExhaustedError(Exception):
    """Raised when all retry attempts have been exhausted"""
    pass


def with_timeout(timeout_seconds: Optional[int] = None):
    """
    Decorator to add timeout protection to synchronous functions

    Usage:
        @with_timeout(30)
        def slow_function():
            # Long-running operation
            pass
    """
    timeout = timeout_seconds or settings.GEMINI_TIMEOUT

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            future = _executor.submit(func, *args, **kwargs)
            try:
                result = future.result(timeout=timeout)
                return result
            except FuturesTimeoutError:
                raise TimeoutError(
                    f"{func.__name__} exceeded timeout of {timeout} seconds"
                )
            except Exception as e:
                # Re-raise original exception
                raise e

        return wrapper
    return decorator


def with_retry(
    max_retries: Optional[int] = None,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator to add retry logic with exponential backoff

    Usage:
        @with_retry(max_retries=3, backoff_factor=2.0)
        def unreliable_function():
            # Function that might fail
            pass
    """
    retries = max_retries or settings.GEMINI_MAX_RETRIES

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(retries + 1):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 0:
                        print(f"✅ {func.__name__} succeeded on retry #{attempt}")
                    return result
                except exceptions as e:
                    last_exception = e
                    if attempt < retries:
                        wait_time = backoff_factor ** attempt
                        print(
                            f"⚠️  {func.__name__} failed (attempt {attempt + 1}/{retries + 1}): {e}"
                        )
                        print(f"   Retrying in {wait_time:.1f}s...")
                        time.sleep(wait_time)
                    else:
                        print(
                            f"❌ {func.__name__} failed after {retries + 1} attempts"
                        )

            raise RetryExhaustedError(
                f"{func.__name__} failed after {retries + 1} attempts. "
                f"Last error: {last_exception}"
            )

        return wrapper
    return decorator


def with_timeout_and_retry(
    timeout_seconds: Optional[int] = None,
    max_retries: Optional[int] = None,
    backoff_factor: float = 2.0
):
    """
    Combined decorator for timeout + retry logic

    Usage:
        @with_timeout_and_retry(timeout_seconds=30, max_retries=2)
        def api_call():
            # External API call
            pass
    """
    def decorator(func: Callable) -> Callable:
        # First apply timeout, then retry
        func_with_timeout = with_timeout(timeout_seconds)(func)
        func_with_retry = with_retry(
            max_retries=max_retries,
            backoff_factor=backoff_factor,
            exceptions=(TimeoutError, Exception)
        )(func_with_timeout)
        return func_with_retry

    return decorator


async def run_with_timeout_async(
    coro,
    timeout_seconds: Optional[int] = None
) -> Any:
    """
    Run an async coroutine with timeout

    Usage:
        result = await run_with_timeout_async(my_async_func(), 30)
    """
    timeout = timeout_seconds or settings.GEMINI_TIMEOUT
    try:
        result = await asyncio.wait_for(coro, timeout=timeout)
        return result
    except asyncio.TimeoutError:
        raise TimeoutError(f"Operation exceeded timeout of {timeout} seconds")


async def run_in_parallel(*tasks, timeout_seconds: Optional[int] = None):
    """
    Run multiple tasks in parallel with optional timeout

    Usage:
        results = await run_in_parallel(
            task1(),
            task2(),
            task3(),
            timeout_seconds=60
        )
    """
    timeout = timeout_seconds or settings.GEMINI_TIMEOUT * 2  # Double timeout for parallel

    try:
        results = await asyncio.gather(*tasks)
        return results
    except Exception as e:
        print(f"❌ Parallel execution failed: {e}")
        raise
