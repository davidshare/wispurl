"""API Gateway application package.

The gateway is the single externally reachable entry point for the URL-shortener
platform. It owns no business logic: it authenticates protected routes locally,
routes each request to the correct internal service, and faithfully forwards the
request and response. See :mod:`app.main` for the application factory.
"""
