# budgie

A simple budget projection tool.

**The project as a whole, including this readme, is still very much a work in progress!**

## Usage

### Bills

*budgie* uses its own `Bill` class to organize its data.
Each `Bill` represents an adjustment to current balance, whether recurring or not.
`Bill`s are specified in `bills.csv`, one per line.
Attributes and rules of each `Bill` are separated by commas.
The first three attributes must always be present, and must always be in the right order:
1. Name.
This can be anything, and doesn't even have to be unique.
A `Bill`'s name is only for your own reference.
2. Value.
How much of an adjustment to make.
Should be negative for a debit and positive for a credit.
Positive values can be, but do have to be, preceded by a `+`.
Negative values have to be preceded by a `-`.
*budgie* is currency-agnostic, and assumes you specify every `Bill` in the same currency.
Currency symbols or designators should not be supplied.
3. Date.
The date that the `Bill` is first valid.
Must be specified as `YYYY-MM-DD`, where month and day are always two digits (`09`, not `9`).

There are several optional rules which may be specified, and their order does not matter:
* `every N days`:
Specifies that the `Bill` should be repeated every `N` days after the first occurrence specified above.
* `every N months`:
Specifies that the `Bill` should be repeated every `N` months after the first occurrence specified above.
Note that this does take month length into account; a `Bill` with this attribute will always repeat on the same day of each `N`th month.
*The behavior of a* `Bill` *with this attribute with a day 29, 30, or 31 is currently undefined.*
* `occurs N times`:
Specifies that the `Bill` should occur at most `N` times.
Without this specification, the `Bill` repeats indefinitely (assuming that an `every` attribute is specified).
* `repeat N times`:
Specifies that the `Bill` should repeat at most `N` times.
Similar to the `occurs` rule, but specifies number of *repeats* after the first application - so `repeat 3 times` causes the bill to be applied 4 times total.
* `until YYYY-MM-DD`:
Specifies that the `Bill` should not be repeated past the given date.
This does not guarantee that the `Bill` is applied on the given date.
* `distribution X Y Z`:
Specifies that the `Bill` should be distributed across the discretionary, emergency, and living balances as given by `X`, `Y`, and `Z`, respectively.
If unspecified, the default is `distribution 0 0 100` - the `Bill` is applied entirely to the living balance.
The three numbers should add to 100.
* `actual`:
Specifies that the `Bill` represents an actual transaction, as opposed to a projected transaction.
Actual `Bill`s are applied regardless of what date they occur on.
* `projected`:
Specifies that the `Bill` represents one or more projected transactions.
Projected `Bill`s are not applied at dates that are in the past.
`Bill`s are projected by default (but see `PROJECTED_BY_DEFAULT` in `settings.py`).

#### Balance and Distribution

*budgie* splits balance into three categories: discretionary, emergency, and living.
By default, all `Bill`s are applied entirely to the living balance.
If the `distribution` rule is never set for any `Bill`, the living balance is the only balance that will change under normal circumstances.

If discretionary balance goes negative, nothing special happens.
If living or emergency balances go negative, the deficit is instead withdrawn from the discretionary balance.
For instance, if the living balance is 200 and discretionary is 20, and a `Bill` is applied which subtracts 300 from living,
then living is set to 0 while discretionary goes to -80.

#### Examples

* `Initial balance, 2000, 2019-07-22, distribution 20 30 50`

This `Bill` is applied only once.
Because its value is positive, it is a credit.
Its `distribution` splits it into 20% discretionary, 50% emergency, and 30% living.
An initial balance should always be supplied, or *budgie* assumes that the initial balance is zero.
Initial balance should be an `actual` `Bill`, so that it is applied even if it is in the past.

* `Paycheck, +450, 2019-07-28, every 14 days, distribution 20 10 70`

This `Bill` is a credit applied biweekly.

* `Paycheck, 453,22, 2019-07-28, actual, distribution 20 10 70`
* `Paycheck, 437.29, 2019-08-11, actual, distribution 20 10 70`

These `Bill`s are the `actual` instances of the above Paycheck `Bill`.
Since the recurring `Bill` is not `actual`, it will not be applied at dates in the past.
These two `actual` `Bill`s will be applied instead, and they also contain exact values whereas the recurring `Bill` only provides an estimated value.

* `Rent, -725, 2019-06-13, every 1 month`

This `Bill` is applied on the 13th of every month, starting with June 2019.
Because neither `until` nor `occurs` is specified, it will repeat indefinitely.

* `Rent paid, -723.57, 2019-06-13, actual`

This `Bill` is applied only once.
If both this `Bill` and the previous are in the same file, and the current date is past `2019-06-13`, then the first `Bill` is not applied at `2019-06-13`, because it is only a projection.
This latter `Bill`, on the other hand, is applied regardless.

* `Cell data plan for old phone (cancelling in September), -50.00, 2019-06-30, every 1 month, until 2019-09-25`

This `Bill` is applied monthly, but will not be applied after `2019-09-25`.
This means the last valid date for this `Bill` is actually `2019-08-30`.

* `Weekly installments, -12.50, 2019-07-25, every 7 days, repeat 10 times`

This `Bill` is applied weekly, and expires after repeating 10 times.
This means that the `Bill` is applied a total of 11 times.

* `Video streaming service, -15.00, 2019-08-01, every 30 days, distribution 100 0 0`

This `Bill` is applied every 30 days, which means it will not necessarily be on the first of each month.
The `distribution` is specified, which in this case indicates that it is entirely discretionary.

* `Lorem ipsum, -30, 2019-07-15, every 1 day, until 2019-07-31, occurs 10 times`

This `Bill` is applied daily, and expires after 10 applications.
If both `until` and `occurs` are specified, the `Bill` expires after either limit is reached - in this case, the number of repeats. 

