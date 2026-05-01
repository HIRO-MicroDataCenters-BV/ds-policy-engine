"""
Request context — the carrier object threaded through every use-case call.

Keeps auth, audit, and per-request metadata out of service constructors so
implementations don't need to be rebuilt per request. Matches the
ds-catalog convention.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Context:
    """Per-call context for use cases.

    Attributes:
        user: Identifier of the caller (username, service account, etc.).
            ``"system"`` for internal flows (startup deploy, migrations).
        request_id: Correlation id for tracing a single request across logs.
            ``None`` outside an HTTP request.
        node_name: Site tag (``ki``, ``hus``, ``uva``, ``local``) — used as
            the default ``institute`` when rules don't specify one.
    """

    user: str = "system"
    request_id: str | None = None
    node_name: str = "local"
