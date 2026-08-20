"""Interfaces package (DDD): HTTP / CLI / messaging adapters live here.

This package provides adapter entry-points that re-export existing
Flask blueprints and other interface-level components so we can
organize the project along DDD boundaries without breaking existing
imports immediately.
"""

__all__ = ["http"]
