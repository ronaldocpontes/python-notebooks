# Based on:
# SOFR
# https://github.com/lballabio/QuantLib/blob/4f529451059642c586f8a0546cfdef4effbbd033/ql/experimental/futures/overnightindexfutureratehelper.hpp
# https://github.com/lballabio/QuantLib/blob/68bbbe90efc2f5a8362d35e1abd0cec4f6a3f45b/ql/experimental/futures/overnightindexfutureratehelper.cpp
# https://github.com/lballabio/QuantLib-SWIG/blob/master/Python/test/ratehelpers.py
# https://github.com/lballabio/QuantLib/blob/master/test-suite/sofrfutures.cpp
#


import matplotlib.pyplot as plt
import numpy as np
import QuantLib as ql
import types
import datetime


# utility class for different QuantLib type conversions
class Convert:

    # convert date string ('yyyy-mm-dd') to QuantLib Date object
    @staticmethod
    def to_date(s):
        monthDictionary = {
            "01": ql.January,
            "02": ql.February,
            "03": ql.March,
            "04": ql.April,
            "05": ql.May,
            "06": ql.June,
            "07": ql.July,
            "08": ql.August,
            "09": ql.September,
            "10": ql.October,
            "11": ql.November,
            "12": ql.December,
        }
        s = s.split("-")
        return ql.Date(int(s[2]), monthDictionary[s[1]], int(s[0]))

    # convert QuantLib Date object to Python Datetime
    @staticmethod
    def to_datetime(s):
        return datetime.date(s.year(), s.month(), s.dayOfMonth())

    # convert string to QuantLib businessdayconvention enumerator
    @staticmethod
    def to_businessDayConvention(s):
        if s.upper() == "FOLLOWING":
            return ql.Following
        if s.upper() == "MODIFIEDFOLLOWING":
            return ql.ModifiedFollowing
        if s.upper() == "PRECEDING":
            return ql.Preceding
        if s.upper() == "MODIFIEDPRECEDING":
            return ql.ModifiedPreceding
        if s.upper() == "UNADJUSTED":
            return ql.Unadjusted

    # convert string to QuantLib calendar object
    @staticmethod
    def to_calendar(s):
        if s.upper() == "TARGET":
            return ql.TARGET()
        if s.upper() == "UNITEDSTATES":
            return ql.UnitedStates()
        if s.upper() == "UNITEDKINGDOM":
            return ql.UnitedKingdom()
        # TODO: add new calendar here

    # convert string to QuantLib swap type enumerator
    @staticmethod
    def to_swapType(s):
        if s.upper() == "PAYER":
            return ql.VanillaSwap.Payer
        if s.upper() == "RECEIVER":
            return ql.VanillaSwap.Receiver

    # convert string to QuantLib frequency enumerator
    @staticmethod
    def to_frequency(s):
        if s.upper() == "DAILY":
            return ql.Daily
        if s.upper() == "WEEKLY":
            return ql.Weekly
        if s.upper() == "MONTHLY":
            return ql.Monthly
        if s.upper() == "QUARTERLY":
            return ql.Quarterly
        if s.upper() == "SEMIANNUAL":
            return ql.Semiannual
        if s.upper() == "ANNUAL":
            return ql.Annual

    # convert string to QuantLib date generation rule enumerator
    @staticmethod
    def to_dateGenerationRule(s):
        if s.upper() == "BACKWARD":
            return ql.DateGeneration.Backward
        if s.upper() == "FORWARD":
            return ql.DateGeneration.Forward
        # TODO: add new date generation rule here

    # convert string to QuantLib day counter object
    @staticmethod
    def to_dayCounter(s):
        if s.upper() == "ACTUAL360":
            return ql.Actual360()
        if s.upper() == "ACTUAL365FIXED":
            return ql.Actual365Fixed()
        if s.upper() == "ACTUALACTUAL":
            return ql.ActualActual()
        if s.upper() == "ACTUAL365NOLEAP":
            return ql.Actual365NoLeap()
        if s.upper() == "BUSINESS252":
            return ql.Business252()
        if s.upper() == "ONEDAYCOUNTER":
            return ql.OneDayCounter()
        if s.upper() == "SIMPLEDAYCOUNTER":
            return ql.SimpleDayCounter()
        if s.upper() == "THIRTY360":
            return ql.Thirty360()

    # convert string (ex.'USD.3M') to QuantLib ibor index object
    @staticmethod
    def to_iborIndex(s):
        s = s.split(".")
        if s[0].upper() == "USD":
            return ql.USDLibor(ql.Period(s[1]))
        if s[0].upper() == "EUR":
            return ql.Euribor(ql.Period(s[1]))


# create piecewise yield term structure
class PiecewiseCurveBuilder(object):

    FREQUENCIES = {"Monthly": ql.Monthly, "Quarterly": ql.Quarterly}
    NESTINGS = {
        "Averaging": ql.OvernightIndexFuture.Averaging,
        "Compounding": ql.OvernightIndexFuture.Compounding,
    }

    # in constructor, we store all possible instrument conventions and market data
    def __init__(self, evaluationDate, conventions, marketData):
        self.instruments = []  # bootstrap instruments and helpers for reporting
        self.helpers = []  # bootstrap helpers for PiecewiseCurveBuilder
        self.evaluationDate = evaluationDate
        self.conventions = conventions
        self.market = marketData
        self.curves = {}
        self.overnightIndexes = {}
        self.curveData = {}

    # for a given curve, first assemble bootstrap helpers,
    # then construct yield term structure handle
    def Build(self, curve, enableExtrapolation=True):

        # clear all existing bootstrap helpers from list
        self.helpers.clear()
        self.instruments.clear()
        # filter out correct market data set for a given curve
        data = self.market.loc[self.market["Ticker"].str.startswith(f"""{curve}."""), :]
        self.curveData[curve] = data

        discounting_yts_handle = ql.RelinkableYieldTermStructureHandle()

        if curve == "SOFR":
            self.overnightIndexes[curve] = ql.Sofr(discounting_yts_handle)
        elif curve == "SONIA":
            self.overnightIndexes[curve] = ql.Sonia(discounting_yts_handle)
        elif curve == "EONIA":
            self.overnightIndexes[curve] = ql.Eonia(discounting_yts_handle)

        # loop through market data set
        for i in range(data.shape[0]):
            # extract ticker and value
            ticker = data.iloc[i]["Ticker"]
            instrument = ticker.split(".")[1]
            value = data.iloc[i]["Value"]
            helper = None

            # add deposit rate helper
            # ticker prototype: 'CCY.OISFIXING.0D' = evaluation date
            if instrument == "FIXINGD":
                self.overnightIndexes[curve].addFixing(
                    Convert.to_date(ticker.split(".")[2]), value
                )

            elif instrument == "FIXING":
                self.overnightIndexes[curve].addFixing(
                    self.evaluationDate + ql.Period(ticker.split(".")[2]), value,
                )

            # add deposit rate helper
            # ticker prototype: 'CCY.DEPOSIT.3M'
            elif instrument == "DEPOSIT":
                # extract correct instrument convention
                convention = self.conventions[curve]["DEPOSIT"]
                rate = ql.QuoteHandle(ql.SimpleQuote(value))
                period = ql.Period(ticker.split(".")[2])
                # extract parameters from instrument convention
                fixingDays = convention["FIXINGDAYS"]
                calendar = Convert.to_calendar(convention["CALENDAR"])
                businessDayConvention = Convert.to_businessDayConvention(
                    convention["BUSINESSDAYCONVENTION"]
                )
                endOfMonth = convention["ENDOFMONTH"]
                dayCounter = Convert.to_dayCounter(convention["DAYCOUNTER"])
                # create and append deposit helper into helper list
                helper = ql.DepositRateHelper(
                    rate,
                    period,
                    fixingDays,
                    calendar,
                    businessDayConvention,
                    endOfMonth,
                    dayCounter,
                )

            # add ois rate helper
            # ticker prototype: 'CCY.OIS.3M'
            # https://www.cmegroup.com/trading/interest-rates/stir/one-month-sofr_contract_specifications.html
            # https://www.cmegroup.com/trading/interest-rates/stir/three-month-sofr_contract_specifications.html
            # https://www.cmegroup.com/education/courses/introduction-to-eurodollars/understanding-imm-price-and-date.html
            elif instrument == "SOFRFUTURE":
                # extract correct instrument convention
                price = ql.QuoteHandle(ql.SimpleQuote(value))
                month = int(ticker.split(".")[2])
                year = int(ticker.split(".")[3])
                frequency = self.FREQUENCIES[ticker.split(".")[4]]
                netting = self.NESTINGS[ticker.split(".")[5]]
                convexityAdjustment = 0
                convexityAdjustmentQuote = ql.QuoteHandle(
                    ql.SimpleQuote(convexityAdjustment)
                )

                # print(value, month, year, ticker.split(".")[4], ticker.split(".")[5])
                # extract parameters from instrument convention
                # create and append SofrFutureRate helper into helper list
                helper = ql.SofrFutureRateHelper(
                    price,
                    month,
                    year,
                    frequency,
                    self.overnightIndexes[curve],
                    convexityAdjustmentQuote,
                    netting,
                )

                def rate(helper):
                    return round(100 - helper.quote().value(), 10)

                helper.rate = types.MethodType(rate, helper)

            # add ois rate helper
            # ticker prototype: 'CCY.OIS.3M'
            elif instrument == "OIS":
                # extract correct instrument convention
                convention = self.conventions[curve]["OIS"]
                rate = ql.QuoteHandle(ql.SimpleQuote(value))
                period = ql.Period(ticker.split(".")[2])
                # extract parameters from instrument convention
                settlementDays = convention["SETTLEMENTDAYS"]
                # create and append ois helper into helper list
                helper = ql.OISRateHelper(
                    settlementDays,
                    period,
                    rate,
                    self.overnightIndexes[curve],
                    discounting_yts_handle,
                )

            # add futures rate helper
            # ticker prototype: 'CCY.FUTURE.10M'
            # note: third ticker field ('10M') is defining starting date
            # for future to be 10 months after defined settlement date
            elif instrument == "FUTURE":
                # extract correct instrument convention
                convention = self.conventions[curve]["FUTURE"]
                price = value
                iborStartDate = ql.IMM.nextDate(
                    self.evaluationDate + ql.Period(ticker.split(".")[2])
                )
                # extract parameters from instrument convention
                lengthInMonths = convention["LENGTHINMONTHS"]
                calendar = Convert.to_calendar(convention["CALENDAR"])
                businessDayConvention = Convert.to_businessDayConvention(
                    convention["BUSINESSDAYCONVENTION"]
                )
                endOfMonth = convention["ENDOFMONTH"]
                dayCounter = Convert.to_dayCounter(convention["DAYCOUNTER"])
                # create and append futures helper into helper list
                helper = ql.FuturesRateHelper(
                    price,
                    iborStartDate,
                    lengthInMonths,
                    calendar,
                    businessDayConvention,
                    endOfMonth,
                    dayCounter,
                )

            # add swap rate helper
            # ticker prototype: 'CCY.SWAP.2Y'
            elif instrument == "SWAP":
                # extract correct instrument convention
                convention = self.conventions[curve]["SWAP"]
                rate = value
                periodLength = ql.Period(ticker.split(".")[2])
                # extract parameters from instrument convention
                fixedCalendar = Convert.to_calendar(convention["FIXEDCALENDAR"])
                fixedFrequency = Convert.to_frequency(convention["FIXEDFREQUENCY"])
                fixedConvention = Convert.to_businessDayConvention(
                    convention["FIXEDCONVENTION"]
                )
                fixedDayCount = Convert.to_dayCounter(convention["FIXEDDAYCOUNTER"])
                floatIndex = Convert.to_iborIndex(convention["FLOATINDEX"])
                # create and append swap helper into helper list
                helper = ql.SwapRateHelper(
                    rate,
                    periodLength,
                    fixedCalendar,
                    fixedFrequency,
                    fixedConvention,
                    fixedDayCount,
                    floatIndex,
                )

            if helper is not None:
                self.instruments.append(helper)
                self.helpers.append(helper)
            else:
                self.instruments.append(None)

        # extract day counter for curve from configurations
        dayCounter = Convert.to_dayCounter(
            self.conventions[curve]["CONFIGURATIONS"]["DAYCOUNTER"]
        )
        # construct yield term structure handle
        yieldTermStructure = ql.PiecewiseLinearZero(
            self.evaluationDate, self.helpers, dayCounter
        )
        if enableExtrapolation is True:
            yieldTermStructure.enableExtrapolation()

        discounting_yts_handle.linkTo(yieldTermStructure)
        self.curves[curve] = discounting_yts_handle

        self.__buildDataReport(
            curve, data, self.instruments, discounting_yts_handle, dayCounter
        )

        return self.curves[curve]

    # builc curve construction report
    def __buildDataReport(self, curve, data, instruments, yts, dayCounter):

        yts.discount(1.0)  # Initialize lazy bootstrap
        # errorTolerance = 1.0e-9

        data["Quote"] = list(
            map(lambda x: x.quote().value() if "quote" in dir(x) else "", instruments,)
        )

        data["Curve Implied Quote"] = list(
            map(
                lambda x: x.impliedQuote() if "impliedQuote" in dir(x) else "",
                instruments,
            )
        )

        # data["Error"] = data["CurveQuote"] - data["Quote"]
        # data["In Tolerance"] = data["Error"] < errorTolerance

        data["Rate"] = list(
            map(lambda x: str(x.rate() if "rate" in dir(x) else ""), instruments,)
        )

        data["Discount Factor"] = list(
            map(
                lambda x: yts.discount(
                    dayCounter.yearFraction(self.evaluationDate, x.pillarDate()),
                )
                if "pillarDate" in dir(x)
                else "",
                instruments,
            )
        )

        data["Forward Rate"] = list(
            map(
                lambda x: yts.forwardRate(
                    dayCounter.yearFraction(self.evaluationDate, x.pillarDate()),
                    dayCounter.yearFraction(self.evaluationDate, x.pillarDate()),
                    ql.Continuous,
                    ql.Annual,
                    True,
                ).rate()
                if "pillarDate" in dir(x)
                else "",
                instruments,
            )
        )

        data["Annual ZeroRate"] = list(
            map(
                lambda x: yts.zeroRate(
                    dayCounter.yearFraction(self.evaluationDate, x.pillarDate()),
                    ql.Compounded,
                    ql.Annual,
                    True,
                ).rate()
                if "pillarDate" in dir(x)
                else "",
                instruments,
            )
        )

        data["Continuous ZeroRate"] = list(
            map(
                lambda x: yts.zeroRate(
                    dayCounter.yearFraction(self.evaluationDate, x.pillarDate()),
                    ql.Continuous,
                    ql.Annual,
                    True,
                ).rate()
                if "pillarDate" in dir(x)
                else "",
                instruments,
            )
        )

        data["Maturity"] = list(
            map(
                lambda x: Convert.to_datetime(x.maturityDate())
                if "maturityDate" in dir(x)
                else "",
                instruments,
            )
        )

        data["Pillar"] = list(
            map(
                lambda x: Convert.to_datetime(x.pillarDate())
                if "pillarDate" in dir(x)
                else "",
                instruments,
            )
        )

        data["Fraction"] = list(
            map(
                lambda x: dayCounter.yearFraction(self.evaluationDate, x.pillarDate())
                if "pillarDate" in dir(x)
                else "",
                instruments,
            )
        )

        self.curveData[curve] = data

    # plot zero rates and forward rate
    def data(self, curve):
        return self.curveData[curve]

    # plot zero rates and forward rate
    def plot(self, curve="USD", years=30.0, stepsize=0.1):
        yts_curve = self.curves[curve]
        times = [k * stepsize for k in range(int(round(years / stepsize, 0)) + 1)]
        continuousForwd = [
            yts_curve.forwardRate(time, time, ql.Continuous, ql.Annual, True).rate()
            for time in times
        ]
        continuousZeros = [
            yts_curve.zeroRate(time, ql.Continuous, ql.Annual, True).rate()
            for time in times
        ]
        annualZeros = [
            yts_curve.zeroRate(time, ql.Compounded, ql.Annual, True).rate()
            for time in times
        ]
        # print(times, continuousForwd, continuousZeros, annualZeros)
        plt.plot(times, continuousForwd, label="Cont. forward rate")
        plt.plot(times, continuousZeros, label="Cont. zero rate")
        plt.plot(times, annualZeros, label="Annually comp. zero rate")
        plt.legend()
        plt.title(f"""{curve} Term Structure""")
        plt.xlabel("Maturity")
        plt.ylabel("Interest rate")
        plt.grid()
        plt.show()
