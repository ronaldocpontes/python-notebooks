#!/usr/bin/python
# For issues concerning forward rate interpolation, which might be worth of
# knowing when working with ForwardCurve this video by Quantlib creator Luigi Ballabio
# https://www.youtube.com/watch?v=96pNeuU5ZKY

import QuantLib as ql

import matplotlib.pyplot as plt
import pandas

DAY_COUNTERS = {
    "Actual360": ql.Actual360(),
    "Actual365Fixed": ql.Actual365Fixed(),
    "ActualActual": ql.ActualActual,
    "Actual365NoLeap": ql.Actual365NoLeap(),
    "Business252": ql.Business252(),
    "Thirty360": ql.Thirty360(),
}

CALENDARS = {
    "NullCalendar": ql.NullCalendar(),
    "BespokeCalendar": ql.BespokeCalendar("CALENDAR_NAME"),
    "JointCalendar": ql.JointCalendar,
}

INTERPOLATION_METHODS = {
    "BackwardFlat": ql.BackwardFlat(),
    "ForwardFlat": ql.ForwardFlat(),
    "MonotonicLogCubic": ql.MonotonicLogCubic(),
    "Linear": ql.Linear(),
    "LogLinear": ql.LogLinear(),
    "Cubic": ql.Cubic(),
    "MonotonicCubic": ql.MonotonicCubic(),
    "DefaultLogCubic": ql.DefaultLogCubic(),
    "SplineCubic": ql.SplineCubic(),
    "Kruger": ql.Kruger(),
    "KrugerLog": ql.KrugerLog(),
    "KrugerCubic": ql.KrugerCubic,
    "FritschButlandCubic": ql.FritschButlandCubic,
    "ConvexMonotone": ql.ConvexMonotone(),
    "CubicNaturalSpline": ql.CubicNaturalSpline,
    "LogCubicNaturalSpline": ql.LogCubicNaturalSpline,
    "MonotonicCubicNaturalSpline": ql.MonotonicCubicNaturalSpline,
    "Parabolic": ql.Parabolic,
    "LogParabolic": ql.LogParabolic,
    "MonotonicParabolic": ql.MonotonicParabolic,
    "MonotonicLogParabolic": ql.MonotonicLogParabolic,
}


class YieldCurve:

    # Python constructor
    def __init__(
        self,
        terms,
        continuousCompoundedRates,
        day_counter=ql.Actual360(),
        calendar=ql.NullCalendar(),
        interpolation=ql.BackwardFlat(),
    ):
        today = ql.Settings.getEvaluationDate(ql.Settings.instance())
        self.terms = terms
        self.dates = [
            ql.WeekendsOnly().advance(today, ql.Period(term), ql.ModifiedFollowing)
            for term in ["0d"] + terms
        ]
        self.rates = [continuousCompoundedRates[0]] + continuousCompoundedRates
        self.yts = ql.ForwardCurve(
            self.dates, self.rates, day_counter, calendar, interpolation
        )

    # Calculate continously compounded rates from simple rates array
    def simpleToContinuousRates(self, simpleRates, dates, day_counter=ql.Actual360()):
        continousRates = simpleRates.copy()
        for i in range(len(simpleRates) - 1):
            r_simple = ql.InterestRate(
                simpleRates[i + 1], ql.Actual360(), ql.Simple, ql.Once
            )
            t = day_counter.yearFraction(dates[i], dates[i + 1])
            r_continuous = r_simple.equivalentRate(ql.Continuous, ql.NoFrequency, t)
            continousRates[i + 1] = r_continuous.rate()
        return continousRates

    # zero coupon bond
    def discount(self, dateOrTime):
        return self.yts.discount(dateOrTime, True)

    def forwardRate(self, time):
        return self.yts.forwardRate(time, time, ql.Continuous, ql.Annual, True).rate()

    # plot zero rates and forward rate
    def plot(self, stepsize=0.1):
        times = [k * stepsize for k in range(int(round(30.0 / stepsize, 0)) + 1)]
        continuousForwd = [
            self.yts.forwardRate(time, time, ql.Continuous, ql.Annual, True).rate()
            for time in times
        ]
        continuousZeros = [
            self.yts.zeroRate(time, ql.Continuous, ql.Annual, True).rate()
            for time in times
        ]
        annualZeros = [
            self.yts.zeroRate(time, ql.Compounded, ql.Annual, True).rate()
            for time in times
        ]
        # print(times, continuousForwd, continuousZeros, annualZeros)
        plt.plot(times, continuousForwd, label="Cont. forward rate")
        plt.plot(times, continuousZeros, label="Cont. zero rate")
        plt.plot(times, annualZeros, label="Annually comp. zero rate")
        plt.legend()
        plt.xlabel("Maturity")
        plt.ylabel("Interest rate")
        plt.show()

    # return a table with curve data
    def table(self):
        table = pandas.DataFrame([self.terms, self.dates, self.rates]).T
        table.columns = ["Terms", "Dates", "Rates"]
        return table

    def referenceDate(self):
        return self.referenceDate()
