import matplotlib.pyplot as plt
import csv
import sys

X = []
Y = []

c = 299792458

file_name = str(sys.argv[1])
file = open(file_name, 'r')
reader = csv.reader(file, delimiter=',')

for data in reader:
    if len(data) == 3:
        pass
    else:
        X.append(float(data[0]))
        Y.append(float(data[-1]))

V = [0]

for i in range(0,len(Y)-1):
    dr = Y[i+1] - Y[i]
    dt = X[i+1] - X[i]
    V.append(dr/dt*(10**9))

V[0] = V[1]

plt.plot(X, V, label="Speed of the Centre Point")
plt.ylabel('Speed (m/s)')
plt.xlabel('Time (ns)')
plt.title("Speed v/s Time Graph for Apprent Image of Object", fontsize = 20)
plt.grid()
plt.legend()
plt.xlim(0, X[-1])
plt.show()


    
