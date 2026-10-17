"""Gunicorn server hooks for Prometheus multiprocess mode.

Load with: gunicorn -c python:wispurl_metrics.gunicorn_hooks ...
"""

from typing import Any

from prometheus_client import multiprocess


def child_exit(server: Any, worker: Any) -> None:
    """Drop a dead worker's live gauge values so they stop counting toward livesum."""
    multiprocess.mark_process_dead(worker.pid)
