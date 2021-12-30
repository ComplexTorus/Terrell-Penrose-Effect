import matplotlib.pyplot as plt
import csv
import sys

X = []
Y = []

file_name = str(sys.argv[1])
file = open(file_name, 'r')
reader = csv.reader(file, delimiter=',')

for data in reader:
    if len(data) == 3:
        pass
    else:
        X.append(float(data[0]))
        Y.append(float(data[-1]))

plt.plot(X,Y, label="Distance of the Centre Point")
plt.ylabel('Distance Travelled (m)')
plt.xlabel('Time (ns)')
plt.title("Distance v/s Time Graph for Apparent Image of Object", fontsize=20)
plt.grid()
plt.legend()
plt.xlim(0, X[-1])
plt.ylim(0, Y[-1])
plt.show()
