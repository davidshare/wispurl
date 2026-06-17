"""Notification service application package (queue-driven, no API).

Consumes ``notifications.all`` and emits a notification per event. Default channel is
a structured stdout log; an optional SMTP/Mailtrap path sits behind NOTIFY_CHANNEL.
See :mod:`app.main`.
"""
