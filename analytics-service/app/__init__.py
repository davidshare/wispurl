"""Analytics service application package.

Owns ``stats_db``. Ingests click events from the Shortener over an internal,
key-protected endpoint and serves aggregated per-short-code statistics. See
:mod:`app.main` for the application factory.
"""
