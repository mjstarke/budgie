from bill import Bill
from datetime import date, timedelta
import matplotlib.pyplot as plt
import numpy as np
from settings import *
from typing import List, Tuple


def running_average(x: np.ndarray, n: int):
    cumsum = np.cumsum(x)
    return [(cumsum[i] - cumsum[i - n]) / n if i >= n else (cumsum[i] / (i + 1)) for i in range(len(x))]


with open("sample_bills.csv", "r") as f:
    bills = [Bill.from_csv(line) for line in f if (len(line.strip()) > 0) and (line[0] != "#")]

for bill in bills:
    if bill.irrelevant and not bill.actual:
        print("/!\\ NOTICE: Bill '{}' is irrelevant, as all of its dates are in the past.".format(bill.name))

living = [0]
emergency = [0]
discretionary = [0]
time = [SIMULATION_START - timedelta(days=1)]
present_balance = 0
while time[-1] < SIMULATION_END:
    time.append(time[-1] + timedelta(days=1))
    living.append(living[-1])
    emergency.append(emergency[-1])
    discretionary.append(discretionary[-1])
    for bill in bills:
        if time[-1] in bill:
            if bill.actual or (time[-1] >= PRESENT_DATE):
                living[-1] += bill.living
                emergency[-1] += bill.emergency
                discretionary[-1] += bill.discretionary

                if LIVING_DEPLETES_DISCRETIONARY and living[-1] < 0:
                    discretionary[-1] += living[-1]
                    living[-1] = 0

                if EMERGENCY_DEPLETES_DISCRETIONARY and emergency[-1] < 0:
                    discretionary[-1] += emergency[-1]
                    emergency[-1] = 0

        if time[-1] == PRESENT_DATE:
            present_balance = discretionary[-1] + emergency[-1] + living[-1]

living = np.array(living)
discretionary = np.array(discretionary)
emergency = np.array(emergency)

fig = plt.figure(figsize=(10, 5))
ax = fig.add_subplot(111)
line_1, = ax.plot(time, living, label="Living Balance", color="green")
line_2, = ax.plot(time, emergency, label="Emergency Balance", color="orange")
line_3, = ax.plot(time, discretionary, label="Discretionary Balance", color="purple")
line_4, = ax.plot(time, -discretionary, label="Negative Discretionary Balance", color="purple", linestyle="dashed")

legend_handles = [line_1, line_2, line_3, line_4]
legend_labels = ["Living Balance",
                 "Emergency Balance",
                 "Discretionary Balance",
                 "Negative Discretionary Balance"]

if PLOT_TOTAL:
    line_5, = ax.plot(time, living + emergency + discretionary, label="Total Balance", color="black")
    legend_handles.append(line_5)
    legend_labels.append("Total Balance")

for d in range(discretionary.shape[0] - 1):
    if time[d] >= PRESENT_DATE:
        if living[d] <= 0:
            q = ax.axvspan(time[d], time[d + 1], facecolor="orange", alpha=0.5)
            if "Living Balanced Depleted" not in legend_labels:
                legend_handles.append(q)
                legend_labels.append("Living Balanced Depleted")
        if discretionary[d] <= 0:
            q = ax.axvspan(time[d], time[d + 1], facecolor="red", alpha=0.5)
            if "Discretionary Balanced Depleted" not in legend_labels:
                legend_handles.append(q)
                legend_labels.append("Discretionary Balanced Depleted")

q = ax.axvspan(SIMULATION_START, PRESENT_DATE, facecolor="cyan", alpha=0.5)
legend_handles.append(q)
legend_labels.append("Actual Budget")

ax.set_xlim(time[1], time[-1])
ax.set_ylim(0)
ax.grid(axis="both")
ax.legend(legend_handles, legend_labels, loc="best")

ax.set_xticklabels([["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                    [date.fromordinal(int(i)).month - 1] for i in ax.get_xticks()])

ax.set_yticklabels(["${:.0f}".format(i) for i in ax.get_yticks()])

plt.title("Projected budget from {} to {}\n"
          "Current balance ${:.2f} as of {}".format(SIMULATION_START.strftime("%Y %B %d"),
                                                    time[-1].strftime("%Y %B %d"),
                                                    present_balance,
                                                    PRESENT_DATE.strftime("%Y %B %d"))
          )

plt.tight_layout()
plt.show()
