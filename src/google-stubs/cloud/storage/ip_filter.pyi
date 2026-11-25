class PublicNetworkSource:
    allowed_ip_cidr_ranges: list[str]
    def __init__(self, allowed_ip_cidr_ranges: list[str] | None = None) -> None: ...

class VpcNetworkSource:
    # the resource name of the VPC network, e.g. `projects/<project>/global/networks/<network>`
    network: str
    allowed_ip_cidr_ranges: list[str]
    def __init__(self, network: str, allowed_ip_cidr_ranges: list[str] | None = None) -> None: ...

# Built empty and filled in through the attributes; assign it to `Bucket.ip_filter`, then `patch()` the bucket.
class IPFilter:
    # "Enabled" or "Disabled"
    mode: str | None
    public_network_source: PublicNetworkSource | None
    vpc_network_sources: list[VpcNetworkSource]
    allow_all_service_agent_access: bool | None
    allow_cross_org_vpcs: bool | None
    def __init__(self) -> None: ...
