# At runtime `InvalidResponse` and `DataCorruption` subclass the `google.resumable_media` classes of the same name
# when that package is installed, and `Exception` otherwise.
class InvalidPathError(Exception): ...

class InvalidResponse(Exception):
    response: object  # the HTTP response that caused the failure, a `requests.Response`
    def __init__(self, response: object, *args: object) -> None: ...

class DataCorruption(Exception):
    response: object  # the HTTP response that caused the failure, a `requests.Response`
    def __init__(self, response: object, *args: object) -> None: ...
