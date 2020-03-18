"""Enhances pandas objects."""
from . import stats


def extend_pandas():
    """Enhances pandas objects."""
    import quantstats as qs
    from pandas.core.base import PandasObject as _po

    qs.extend_pandas()

    _po.gmean = stats.gmean
