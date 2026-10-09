"""Pinned fail-closed teaching fixture."""
def authorize(authorized, worker_healthy):
    return authorized and worker_healthy
