"""Test."""
import pandas as pd
import pystore
import yfinance as yf
from yahoo_fin.stock_info import tickers_dow
from typing import Tuple
import itertools

PYSTORE = pystore.store("timeseries")
BOE_COLLECTION = PYSTORE.collection("BOE")
MORTAGE_INSTRUMENTS_ITEM = "mortage_instruments"
DEFAULT_SYMBOL = "AAPL"
INCONSISTENT_SERIES = ["DOW"]


def get_symbols_down_jones():
    """Retrieves Dow Jones Symbols"""
    return tickers_dow()


def load_dow_jones() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load BOE Mortage Instruments from cache or the network."""
    mi_item = BOE_COLLECTION.item(MORTAGE_INSTRUMENTS_ITEM)
    mi = pd.read_json(mi_item.metadata["instruments"])
    return mi, mi_item.to_pandas


def store_dow_jones():
    """Store BOE load_mortage_instruments into cache."""
    mortage_instruments = boe.mortage_instruments()
    series = boe.getFullSeries(mortage_instruments.SERIES)

    metadata = {
        "source": "Bank of England",
        "source_code": "BOE",
        "instruments": mortage_instruments.to_json(),
    }

    BOE_COLLECTION.write(MORTAGE_INSTRUMENTS_ITEM, series, metadata)


def timeseries_collection(interval="1d", source="yahoo", columns=[]):
    """Return local PyStore cache database."""
    return PYSTORE.collection(f"timeseries-{source}-{interval}")


def timeseries(
    tickers, period="10y", interval="1d", source="yahoo", columns=[], autoClean=True
):
    """Load or download timeseries data."""
    if isinstance(tickers, str):
        tickers = [tickers]

    tickers = set(tickers)
    collection = PYSTORE.collection(f"timeseries-{source}-{interval}")
    not_stored = tickers - collection.list_items()
    download_timeseries(not_stored, period="max", interval=interval, source=source)

    if len(columns) < 1:
        tdfs = list(
            map(lambda x: collection.item(x).data.last(period).compute(), tickers,)
        )
    else:
        tdfs = list(
            map(
                lambda x: collection.item(x).data.last(period)[columns].compute(),
                tickers,
            )
        )

    series = pd.concat(tdfs, axis=1, keys=tickers, join="outer")

    if len(tickers) == 1:
        series.columns = series.columns.droplevel(0)
    else:
        if len(columns) == 1:
            series.columns = series.columns.droplevel(1)

    return check_timeseries_data(series, autoClean)


def check_timeseries_data(series, autoClean=True):
    """Check data for necessary analisys treatements."""
    log = pd.DataFrame()
    errors = ""
    first_index_in_series = series.first_valid_index()
    log["First Index"] = [first_index_in_series]
    log["Last Index"] = [series.last_valid_index()]
    log["Series shape"] = [series.shape]

    report = pd.DataFrame()
    report["Consecutive NaN"] = series.apply(max_consecutive_na)

    zeros = series.where(series == 0).count()
    max_zeros = zeros.max()
    report["Total Zeros"] = zeros
    if max_zeros > 1:
        errors += "Error: maximum number of consecutive NaN is greater than 1"

        # try:  # Remove inconsistent series
        #     series.drop(INCONSISTENT_SERIES, axis=1)
        # except Exception:
        #     pass

    if autoClean:
        # drop = series.columns.intersection(INCONSISTENT_SERIES)
        for c in INCONSISTENT_SERIES:
            if c in series.columns:
                log["Inconsistent Symbol Dropped"] = c
                del series[c]

        trim_from = series[series.notna().all(axis=1)].first_valid_index()

        if trim_from > first_index_in_series:
            series = series[trim_from:]

            consecutive = series.apply(max_consecutive_na)
            max_consecutive = consecutive.max()
            report["AutoClean: Consecutive NaN"] = consecutive
            if max_consecutive > 4:
                errors += "Error: maximum number of consecutive NaN is greater than 4"

            log["AutoClean: First Index"] = [series.first_valid_index()]
            log["AutoClean: Last Index"] = [series.last_valid_index()]
            log["AutoClean: Series shape"] = [series.shape]

        series.dropna(inplace=True)
        report["AutoClean: Final NaN"] = series.isna().sum()

    return series, report.transpose(), log.transpose(), errors


def max_consecutive_na(a):
    """Return the maximum number of consecutive NaN."""
    return pd.Series([len(list(g)) for k, g in itertools.groupby(a.isna()) if k]).max()


def download_timeseries(tickers: list, period="max", interval="1d", source="yahoo"):
    """Download and store timeseries data into local cache."""
    t = tickers if isinstance(tickers, str) else " ".join(set(tickers))

    if len(t) < 2:
        return

    series = yf.download(
        t,
        period=period,
        interval=interval,
        auto_adjust=True,
        prepost=False,
        group_by="ticker",
    )

    if isinstance(series.columns, pd.MultiIndex):
        series.columns.levels[0].map(
            lambda x: store_timeseries(x, series[x], interval, source)
        )
    else:
        store_timeseries(t, series, interval, source)


def store_timeseries(symbol, series, interval, source):
    """Store timeseries data into local cache."""
    metadata = {
        "symbol": symbol,
        "interval": interval,
        "source": source,
    }
    collection = PYSTORE.collection(f"timeseries-{source}-{interval}")
    collection.write(symbol, series, metadata, overwrite=True)


SYMBOLS_DOW_JONES = [
    "AAPL",
    "AXP",
    "BA",
    "CAT",
    "CSCO",
    "CVX",
    "DIS",
    "DOW",
    "GS",
    "HD",
    "IBM",
    "INTC",
    "JNJ",
    "JPM",
    "KO",
    "MCD",
    "MMM",
    "MRK",
    "MSFT",
    "NKE",
    "PFE",
    "PG",
    "TRV",
    "UNH",
    "UTX",
    "V",
    "VZ",
    "WBA",
    "WMT",
    "XOM",
]
