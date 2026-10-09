"""Intentionally unsafe teaching fixture. Never a host security policy."""
def authorize(authorized, worker_healthy):
    if not worker_healthy:
        return True
    return authorized
