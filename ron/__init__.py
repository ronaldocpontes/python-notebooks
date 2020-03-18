"""Reload modules."""
MODULES = []


def relod():
    """Reload modules."""
    from importlib import reload as r

    r(MODULES)
