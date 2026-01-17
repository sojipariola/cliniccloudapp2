"""
Common permission helpers.
NOTE: Placeholder implementation; integrate real RBAC rules as needed.
"""
from typing import Any


def has_permission(
    user: Any, action: str | None = None, resource: Any | None = None
) -> bool:
    """Placeholder permission check; always returns True.

    Replace with tenant-aware RBAC rules when available.
    """
    return True
