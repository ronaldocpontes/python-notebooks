import sys, os

sys.path.append("../../")

import QuantLib as ql
import ron.QuantLib.YieldCurve as yc
import ron.QuantLib.Swap as sw

today = ql.Date(3, 9, 2018)
ql.Settings.setEvaluationDate(ql.Settings.instance(), today)

terms = [
    "1y",
    "2y",
    "3y",
    "4y",
    "5y",
    "6y",
    "7y",
    "8y",
    "9y",
    "10y",
    "12y",
    "15y",
    "20y",
    "25y",
    "30y",
]

rates = [
    2.70e-2,
    2.75e-2,
    2.80e-2,
    3.00e-2,
    3.36e-2,
    3.68e-2,
    3.97e-2,
    4.24e-2,
    4.50e-2,
    4.75e-2,
    4.75e-2,
    4.70e-2,
    4.50e-2,
    4.30e-2,
    4.30e-2,
]

rates2 = [r + 0.005 for r in rates]

discCurve = yc.YieldCurve(terms, rates)
projCurve = yc.YieldCurve(terms, rates2)

startDate = ql.Date(30, 10, 2018)
endDate = ql.Date(30, 10, 2038)

swap = sw.Swap(startDate, endDate, 0.05, discCurve, projCurve)

print("NPV:      %11.2f" % (swap.npv()))
print("FairRate: %11.6f" % (swap.fairRate()))
print("Annuity:  %11.2f" % (swap.annuity()))

print(swap.fixedCashFlows())
print(swap.floatCashFlows())
