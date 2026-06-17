"""Cleanup service application package (schedule-driven, not an API).

Periodically sweeps ``short_db`` for expired links, deactivates them in batches, and
publishes a ``link.expired`` event per deactivated link. See :mod:`app.main`.
"""
