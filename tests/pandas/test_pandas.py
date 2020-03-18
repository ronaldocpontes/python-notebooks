"""."""
import pandas as pd
from ron.pandas import extend_pandas

extend_pandas()

r = pd.Series(range(1, 11)).iloc[::-1]
DF = pd.DataFrame({"10": r, "100": r * 10, "0.": r / 10})


def testPandasExtensions():
    """."""
    df = DF.copy()
    print(df.head())
    print(df.gmean())
