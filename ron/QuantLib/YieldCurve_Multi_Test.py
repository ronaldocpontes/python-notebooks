import sys

sys.path.append("../../")

import QuantLib as ql
import pandas as pd
import numpy as np
from io import StringIO

from ron.QuantLib.YieldCurve_Multi import PiecewiseCurveBuilder, Convert


def getQuantlibSoftrTestData():
    """
    Replicates tests from Quantlib C++ Test Class:
    https://github.com/lballabio/QuantLib/blob/master/test-suite/sofrfutures.cpp

    Recent SOFR Fixings quotes on:
    https://apps.newyorkfed.org/markets/autorates/sofr

    Recent SOFR Futures quotes on:
    https://www.cmegroup.com/trading/interest-rates/stir/one-month-sofr.html
    https://www.cmegroup.com/trading/interest-rates/stir/three-month-sofr.html

    CME SOFR Curve
    https://www.cmegroup.com/trading/interest-rates/sofr-strip-rates.html
    """
    evaluationDate = Convert.to_date("2018-10-26")

    market_data = StringIO(
        """
        Ticker,Value
        SOFR.FIXINGD.2018-10-17,0.0217
        SOFR.FIXINGD.2018-10-18,0.0219
        SOFR.FIXINGD.2018-10-19,0.0219
        SOFR.FIXINGD.2018-10-22,0.0218
        SOFR.FIXINGD.2018-10-23,0.0217
        SOFR.FIXINGD.2018-10-24,0.0218
        SOFR.FIXINGD.2018-10-25,0.0219
        SOFR.SOFRFUTURE.10.2018.Monthly.Averaging, 97.8175
        SOFR.SOFRFUTURE.11.2018.Monthly.Averaging, 97.770
        SOFR.SOFRFUTURE.12.2018.Monthly.Averaging, 97.685
        SOFR.SOFRFUTURE.01.2019.Monthly.Averaging, 97.595
        SOFR.SOFRFUTURE.02.2019.Monthly.Averaging, 97.590
        SOFR.SOFRFUTURE.03.2019.Monthly.Averaging, 97.525
        SOFR.SOFRFUTURE.03.2019.Quarterly.Compounding, 97.440
        SOFR.SOFRFUTURE.06.2019.Quarterly.Compounding, 97.295
        SOFR.SOFRFUTURE.09.2019.Quarterly.Compounding, 97.220
        SOFR.SOFRFUTURE.12.2019.Quarterly.Compounding, 97.170
        SOFR.SOFRFUTURE.03.2020.Quarterly.Compounding, 97.160
        SOFR.SOFRFUTURE.06.2020.Quarterly.Compounding, 97.165
        SOFR.SOFRFUTURE.09.2020.Quarterly.Compounding, 97.175
        """
    )
    return evaluationDate, pd.read_csv(market_data, sep=",", skipinitialspace=True)


def getQuantlibEoniaTestData():
    """
    """
    evaluationDate = Convert.to_date("2016-08-26")

    market_data = StringIO(
        """
        Ticker,Value
        EONIA.FIXING.1D,-0.00341
        EONIA.DEPOSIT.1D,-0.00341
        EONIA.OIS.1W,-0.342
        EONIA.OIS.1M,-0.344
        EONIA.OIS.3M,-0.349
        EONIA.OIS.6M,-0.363
        EONIA.OIS.1Y,-0.00389
        """
    )
    return evaluationDate, pd.read_csv(market_data, sep=",", skipinitialspace=True)


def testSoftr():

    evaluationDate, marketData = getQuantlibSoftrTestData()

    conventions = {
        "SOFR": {
            "CONFIGURATIONS": {"DAYCOUNTER": "Actual365Fixed"},
            "DEPOSIT": {
                "FIXINGDAYS": 0,
                "CALENDAR": "TARGET",
                "BUSINESSDAYCONVENTION": "MODIFIEDFOLLOWING",
                "ENDOFMONTH": True,
                "DAYCOUNTER": "ACTUAL360",
            },
            "OIS": {"SETTLEMENTDAYS": 2},
        }
    }

    ql.Settings.instance().evaluationDate = evaluationDate
    builder = PiecewiseCurveBuilder(evaluationDate, conventions, marketData)

    curveType = "SOFR"
    discountCurve = builder.Build(curveType)
    # print discount factors semiannually up to 30 years
    times = np.linspace(0.0, 30.0, 61)
    df = [round(discountCurve.discount(t), 4) for t in times]
    print("discount factors for", curveType)
    print(df)
    builder.plot(curveType)

    # overnightIndex = builder.overnightIndexes[curveType]
    # payoff = ql.VanillaForwardPayoff(ql.Position.Long, 97.440)
    # valueDate = Convert.to_date("2019-03-20")
    # maturityDate = Convert.to_date("2019-06-19")

    # Not yet exposed to Python bindinds
    # https://github.com/lballabio/QuantLib/blob/master/test-suite/sofrfutures.cpp
    # sf = ql.OvernightIndexFuture(overnightIndex,
    #                         payoff,
    #                         valueDate,
    #                         maturityDate,
    #                         curve)

    # expected_price = 97.44
    # expected_npv = 0.0
    # tolerance = 1.0e-9

    # error = sf.spotValue() - expected_price
    # if error > tolerance:
    #     raise Exception("spot value outside expected tolerance")

    # error = sf.NPV() - expected_npv
    # if error > tolerance:
    #     raise Exception("NPV outside expected tolerance")


testSoftr()
