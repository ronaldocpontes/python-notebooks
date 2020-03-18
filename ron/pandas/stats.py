"""."""
import numpy as _np
import quantstats.utils as _utils


def gmean(returns, aggregate=None, compounded=True):
    """
    returns the expected return for a given period
    by calculating the geometric holding period return
    """
    returns = _utils._prepare_returns(returns)
    returns = _utils.aggregate_returns(returns, aggregate, compounded)
    return _np.product(1 + returns) ** (1 / len(returns)) - 1
