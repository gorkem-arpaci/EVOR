"""Application layer: use-cases and orchestration logic.

Keep this module minimal so importing `application` doesn't pull in
heavy dependencies. Specific services live in submodules and can be
imported directly (e.g. `from application.profile_service import ProfileService`).
"""

__all__ = []
