import os
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import iexfinance as iex
from dotenv import load_dotenv
from iexfinance.stocks import Stock
from iexfinance.refdata import get_symbols
import pystore

SYMBOL = "AAPL"
START_DATE = datetime(2020, 1, 1)
END_DATE = datetime.now()

IEX_TOKEN = os.environ.get("IEX_TOKEN")
IEX_API_VERSION = os.environ.get("IEX_API_VERSION")
IEX_OUTPUT_FORMAT = os.environ.get("IEX_OUTPUT_FORMAT")

PYSTORE = pystore.store("timeseries")
IEX_COLLECTION = PYSTORE.collection("IEX_CLOUD")
_SYMBOLS = "SYMBOLS"


def get_iex_cloud_config():
    """Read IEX Config from environment variables."""
    return (IEX_API_VERSION, IEX_TOKEN, IEX_OUTPUT_FORMAT)


def load_symbols():
    """Load or download IEX symbols from PyStore cache."""
    try:
        return IEX_COLLECTION.item(_SYMBOLS).to_pandas()
    except ValueError:
        store_symbols()
        return IEX_COLLECTION.item(_SYMBOLS).to_pandas()


def store_symbols():
    """Store IEX symbols to PyStore cache."""
    s = get_symbols()

    metadata = {
        "source": PYSTORE.datastore.name,
        "api": "refdata.get_symbols",
    }

    IEX_COLLECTION.write(_SYMBOLS, s, metadata, overwrite=True)

