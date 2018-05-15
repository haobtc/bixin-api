from functools import wraps


DEFAULT_CODE = -1


class APIError(ValueError):
    def __init__(self, msg, code=DEFAULT_CODE):
        self.code = code
        super(APIError, self).__init__(msg)


class APIErrorCallFailed(APIError):
    """
    Http read timeout will cause this failure.
    In case of read-timeout, we can not know the status of our api-call.
    """
    pass


class APIErrorCallStatusUnknown(APIError):
    """
    Http read timeout will cause this failure.
    In case of read-timeout, we can not know the status of our api-call.
    """
    pass


def normalize_network_error(func):
    from requests import exceptions as exc

    call_failures = (
        exc.HTTPError,
        exc.ConnectTimeout,
    )
    call_status_unknown = (
        exc.ReadTimeout,
    )

    @wraps(func)
    def decorated(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except exc.RequestException as e:
            if isinstance(e, call_failures):
                raise APIErrorCallFailed(
                    msg=str(e),
                )
            elif isinstance(e, call_status_unknown):
                raise APIErrorCallStatusUnknown(
                    msg=str(e)
                )
            else:
                raise

    return decorated
