from pydantic import BaseModel, ConfigDict


class PortFixedIP(BaseModel):
    """Fixed IP assignment for a port.

    Either `subnet_id` or `ip_address` may be provided; both can be provided.
    """

    subnet_id: str | None = None
    ip_address: str | None = None


class AllowedAddressPair(BaseModel):
    """Allowed address pair entry for a port."""

    ip_address: str
    mac_address: str | None = None


class AllocationPool(BaseModel):
    """Allocation pool for a subnet."""

    start: str
    end: str


class HostRoute(BaseModel):
    """Static host route for a subnet."""

    destination: str
    nexthop: str


class Route(BaseModel):
    """Static route for a router."""

    destination: str
    nexthop: str


class ExternalFixedIP(BaseModel):
    """External fixed IP assignment for router gateway."""

    subnet_id: str | None = None
    ip_address: str | None = None


class ExternalGatewayInfo(BaseModel):
    """External gateway information for a router.

    At minimum include `network_id`. Optionally include `enable_snat` and
    `external_fixed_ips`.
    """

    network_id: str
    enable_snat: bool | None = None
    external_fixed_ips: list[ExternalFixedIP] | None = None


class PortBindingProfile(BaseModel):
    """Binding profile for a port (driver-specific extra keys allowed)."""

    model_config = ConfigDict(extra="allow")
