from datetime import date

# The bounds of the simulation.  Bills occurring outside of this date range are ignored.
SIMULATION_START =                 date(2019, 7, 22)
SIMULATION_END =                   date(2020, 7, 22)

# The date to use as the present date.  Projected Bills before this date are not applied.
PRESENT_DATE =                     date.today()

# Whether to plot the total balance in addition to the constituent balances.
PLOT_TOTAL =                       True

# Whether emergency or living balances can deplete from discretionary.
EMERGENCY_DEPLETES_DISCRETIONARY = True
LIVING_DEPLETES_DISCRETIONARY =    True
