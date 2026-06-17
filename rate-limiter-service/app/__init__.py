"""Rate limiter service application package.

A tiny, Redis-backed service with no database. It exposes a single internal
``POST /check`` endpoint that the Shortener calls before creating a link, applying a
per-user, per-action fixed-window limit backed by atomic Redis counters. See
:mod:`app.main` for the application factory.
"""
