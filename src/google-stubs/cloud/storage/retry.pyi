from collections.abc import Callable

from google.api_core.retry import Retry

class ConditionalRetryPolicy:
    retry_policy: Retry
    conditional_predicate: Callable[..., bool]
    required_kwargs: list[str]
    def __init__(
        self, retry_policy: Retry, conditional_predicate: Callable[..., bool], required_kwargs: list[str]
    ) -> None: ...

DEFAULT_RETRY: Retry
DEFAULT_RETRY_IF_GENERATION_SPECIFIED: ConditionalRetryPolicy
DEFAULT_RETRY_IF_METAGENERATION_SPECIFIED: ConditionalRetryPolicy
DEFAULT_RETRY_IF_ETAG_IN_JSON: ConditionalRetryPolicy
