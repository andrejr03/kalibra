"""Prototype UI projection helpers.

These helpers sit outside Kalibra's domain engines. They prepare static,
inspection-only view data for the workbench prototype.
"""

from .local_provider_projection import (
    DEFAULT_DEMO_OUTPUT_PATH,
    DEFAULT_FIXTURE_PATH,
    build_local_provider_demo_projection,
    render_demo_data_javascript,
    write_local_provider_demo_data,
)

__all__ = [
    "DEFAULT_DEMO_OUTPUT_PATH",
    "DEFAULT_FIXTURE_PATH",
    "build_local_provider_demo_projection",
    "render_demo_data_javascript",
    "write_local_provider_demo_data",
]
