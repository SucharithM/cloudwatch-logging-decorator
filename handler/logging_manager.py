import functools
from configs.configs import (
    DEFAULT_ERROR_LOG_STREAM,
    DEFAULT_INFO_LOG_STREAM,
    DEFAULT_LOG_GROUP,
)
from configs.logging_configurations import CloudWatchHandler


def log_this(
    log_group: str = DEFAULT_LOG_GROUP,
    info_log_stream: str = DEFAULT_INFO_LOG_STREAM,
    error_log_stream: str = DEFAULT_ERROR_LOG_STREAM,
    graceful_exit: bool = True,
):
    """Logs the exceptions of the function. If the exceptions are not raised then the event goes into the INFO stream.

    Args:
        log_group (str, optional): The name of the log group containing the stream / Creates the Log Group if non existent. Defaults to DEFAULT_LOG_GROUP.
        Custom Log Group Names should maintain uniformity.
        info_log_stream (str, optional): The name of the log stream to write the info event to / Creates the Log Stream if non existent. Defaults to DEFAULT_INFO_LOG_STREAM.
        error_log_stream (str, optional): The name of the log stream to write the error event to / Creates the Log Stream if non existent. Defaults to DEFAULT_ERROR_LOG_STREAM.
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                cloudwatch = CloudWatchHandler()

                def put_custom_log_event(
                    message: str, log_stream: str = DEFAULT_INFO_LOG_STREAM
                ):
                    """Adds a Custom Log Event to the Log Group and Log Stream specified in the log_this decorator.

                    Args:
                        message (str): Custom Message to be added in the log stream.
                    """
                    cloudwatch.put_log_event(
                        log_group_name=log_group,
                        log_stream_name=log_stream,
                        message=message,
                    )

                if log_group != DEFAULT_LOG_GROUP:
                    cloudwatch.create_log_group(log_group_name=log_group)
                    cloudwatch.create_log_stream(
                        log_group_name=log_group, log_stream_name=info_log_stream
                    )

                kwargs["put_custom_log_event"] = put_custom_log_event
                result = await func(*args, **kwargs)

                cloudwatch.put_log_event(
                    log_group_name=log_group,
                    log_stream_name=info_log_stream,
                    message=result,
                )

                return result
            except Exception as exc:
                if log_group != DEFAULT_LOG_GROUP:
                    cloudwatch.create_log_stream(
                        log_group_name=log_group, log_stream_name=error_log_stream
                    )

                cloudwatch.put_log_event(
                    log_group_name=log_group,
                    log_stream_name=error_log_stream,
                    message=exc,
                )
                if graceful_exit:
                    return None  # Fail Safely, Exit Gracefully, Live Happily, Die Peacefully.
                else:
                    raise exc
                # Return the exception to give power to the developer to decide what they want to do with it. Will they join the DARKSIDE?

        return wrapper

    return decorator
