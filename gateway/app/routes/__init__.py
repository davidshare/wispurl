"""Proxy route modules.

Each module exposes an ``APIRouter`` that forwards a family of paths to one
internal service. Registration order in :mod:`app.main` is significant: the bare
``GET /{short_code}`` catch-all in :mod:`app.routes.redirect` MUST be included last.
"""
