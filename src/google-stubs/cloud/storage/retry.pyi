from collections.abc import Callable, Mapping
from warnings import deprecated

from google.api_core.retry import Retry

class ConditionalRetryPolicy:
    retry_policy: Retry
    conditional_predicate: Callable[..., bool]
    required_kwargs: list[str]
    def __init__(
        self, retry_policy: Retry, conditional_predicate: Callable[..., bool], required_kwargs: list[str]
    ) -> None: ...
    # `retry_policy` if `conditional_predicate` holds for the `required_kwargs` of the request, else `None`
    def get_retry_policy_if_conditions_met(self, **kwargs: object) -> Retry | None: ...

DEFAULT_RETRY: Retry

# the `conditional_predicate`s of the `DEFAULT_RETRY_IF_*` policies: `query_params` are the request's query parameters
# (`{"ifGenerationMatch": 1}`), `data` its JSON body
def is_generation_specified(query_params: Mapping[str, object]) -> bool: ...
def is_metageneration_specified(query_params: Mapping[str, object]) -> bool: ...
def is_etag_in_data(data: Mapping[str, object] | None) -> bool: ...
@deprecated("Use is_etag_in_data() instead.")
def is_etag_in_json(data: Mapping[str, object] | None) -> bool: ...

DEFAULT_RETRY_IF_GENERATION_SPECIFIED: ConditionalRetryPolicy
DEFAULT_RETRY_IF_METAGENERATION_SPECIFIED: ConditionalRetryPolicy
DEFAULT_RETRY_IF_ETAG_IN_JSON: ConditionalRetryPolicy
