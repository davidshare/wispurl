"""IP-address anonymization.

PRIVACY: the analytics service never stores a raw client IP. Each address is
truncated to its network prefix before storage — the last octet of an IPv4 address
is zeroed (``/24``) and the last 80 bits of an IPv6 address are zeroed (``/48``).
This is a standard GDPR-friendly anonymization that preserves coarse geographic
signal for aggregation while no longer identifying an individual visitor.

TODO(retention): even anonymized rows should not be kept forever — add a scheduled
purge of click_events older than a configured retention window (e.g. 90 days),
likely alongside the Cleanup service (Prompt 7/8).
"""

from __future__ import annotations

import ipaddress

# How many leading bits to keep per address family before zeroing the remainder.
_IPV4_PREFIX = 24
_IPV6_PREFIX = 48


def anonymize_ip(raw_ip: str | None) -> str | None:
    """Return the anonymized network prefix of ``raw_ip``.

    Args:
        raw_ip: A client IP string, or ``None``.

    Returns:
        The truncated network address (e.g. ``"203.0.113.0"`` for an IPv4 input),
        or ``None`` if the input was empty or not a parseable IP address. Unparseable
        input is dropped rather than stored verbatim.
    """
    if not raw_ip:
        return None
    try:
        address = ipaddress.ip_address(raw_ip.strip())
    except ValueError:
        return None

    prefix = _IPV4_PREFIX if address.version == 4 else _IPV6_PREFIX
    network = ipaddress.ip_network(f"{address}/{prefix}", strict=False)
    return str(network.network_address)
