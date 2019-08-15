from datetime import date, datetime, timedelta
from settings import *
from typing import Tuple, Optional


class Bill:
    def __init__(self, name: str, amount: float, on: date,
                 every: Optional[str] = None, at_most: int = 1e9, until: Optional[date] = None,
                 dist: Tuple[float, float, float] = (0.0, 0.0, 1.0), actual: bool = False):
        """
        Bill objects represent adjustments to balance.

        :param name: str.  The name of the bill.
        :param amount: float.  The value of the bill; negative for debit and positive for credit.
        :param on: date.  The date the bill will first be paid.
        :param every: optional str.  How often the bill recurs: either 'x months' or 'x days', or None if the bill
        should not recur.  Default None.
        :param at_most: int.  How many times the bill will occur (not recur) at most.  Default 1e9.
        :param until: optional date.  The last day the bill could recur on, assuming that 'every' is set and 'number'
        allows it.  Note the bill may not actually recur on the given date; importantly, the bill will never recur after
        the given date.  None causes the value to default to five years after the initial 'on' date.  Default None.
        :param category: str.  If the bill is a debit, the category of balance that it will deduct from.  If it is a
        credit, no effect.  Default 'living'.
        """
        assert at_most > 0, "at_most must be at least 1."
        self.name = name
        self.total = amount
        self.dates = [on]
        self.discretionary = amount * dist[0]
        self.emergency = amount * dist[1]
        self.living = amount * dist[2]
        self.actual = actual

        if until is None:
            until = date(on.year + 5, on.month, on.day)

        if every is not None:
            period_number, period_unit = every.split()
            period_number = int(period_number)
            assert period_number > 0, "Recurrence period must be positive."
            if "day" in period_unit:
                while len(self.dates) < at_most:
                    newdate = self.dates[-1] + timedelta(days=period_number)

                    if newdate > until:
                        break
                    else:
                        self.dates.append(newdate)

            elif "month" in period_unit:
                while len(self.dates) < at_most:
                    year = self.dates[-1].year
                    month = self.dates[-1].month + period_number
                    day = self.dates[-1].day

                    while month > 12:
                        month -= 12
                        year += 1

                    newdate = date(year, month, day)

                    if newdate > until:
                        break
                    else:
                        self.dates.append(newdate)
            else:
                raise ValueError("Recurrence period must be specified either in days or months.")

    def __contains__(self, item):
        return item in self.dates

    @property
    def irrelevant(self) -> bool:
        """
        :return: bool.  True if this Bill is irrelevant because all of its dates are in the past; False otherwise.
        """
        return self.dates[-1] < date.today()

    @staticmethod
    def from_csv(text: str) -> "Bill":
        """
        Creates a Bill from the given text.  The text should be a line from a CSV file containing Bill specifications.
        See README.md for details.
        :param text: The Bill specification.
        :return: A Bill instance.
        """
        s = text.split(",")
        if len(s) < 3:
            raise ValueError("Invalid Bill '{}':\nAt least name, value, and date must be given.".format(text))

        bill_name = s[0].strip()

        try:
            bill_value = float(s[1].strip())
        except ValueError:
            raise ValueError("Invalid Bill '{}':\nValue is not a number.".format(text))

        try:
            bill_date = datetime.strptime(s[2].strip(), "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Invalid Bill '{}':\nDate is not valid.".format(text))

        bill_every = None
        bill_until = None
        bill_repeat = 1e9
        bill_distribution = (0.0, 0.0, 1.0)
        bill_actual = not PROJECTED_BY_DEFAULT

        for rule in s[3:]:
            ss = rule.strip().split()
            if ss[0] == "every":
                try:
                    bill_every = ss[1] + " " + ss[2]
                    _ = int(ss[1])
                    if ss[2] not in ["month", "months", "day", "days"]:
                        raise ValueError("Invalid Bill '{}':\nInvalid repetition period unit in '{}'.".format(text, rule))
                except ValueError:
                    raise ValueError("Invalid Bill '{}':\nInvalid repetition period number in '{}'.".format(text, rule))
                except IndexError:
                    raise ValueError("Invalid Bill '{}':\nInvalid repetition period in '{}'.".format(text, rule))

            elif ss[0] == "until":
                try:
                    bill_until = datetime.strptime(ss[1], "%Y-%m-%d").date()
                except ValueError:
                    raise ValueError("Invalid Bill '{}':\nInvalid date in '{}'.".format(text, rule))

            elif ss[0] in ["occurs", "repeat", "repeats"]:
                try:
                    bill_repeat = int(ss[1]) + (1 if "repeat" in ss[0] else 0)
                except ValueError:
                    raise ValueError("Invalid Bill '{}':\nInvalid number in '{}'.".format(text, rule))

            elif ss[0] == "distribution":
                try:
                    bill_distribution = tuple(float(a) / 100 for a in ss[1:4])
                    _ = ss[3]
                except ValueError:
                    raise ValueError("Invalid Bill '{}':\nInvalid number in '{}'.".format(text, rule))
                except IndexError:
                    raise ValueError("Invalid Bill '{}':\nDistribution must have three values in '{}'.".format(text, rule))

            elif ss[0] == "actual":
                bill_actual = True

            elif ss[0] == "projected":
                bill_actual = False

            else:
                raise ValueError("Invalid Bill '{}':\nInvalid rule type in '{}'.".format(text, rule))

        return Bill(bill_name, bill_value, bill_date,
                    bill_every, bill_repeat, bill_until, bill_distribution, bill_actual)

