"""QR code service application package.

A stateless service with no database and no auth state of its own: it turns a short
code into a PNG QR image encoding the full short URL. Being a pure input->output
transformation, it is the platform's horizontal-scaling showcase — any replica can
serve any request identically. See :mod:`app.main` for the application factory.
"""
