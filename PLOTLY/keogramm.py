import plotly.express as px
import numpy as np
from h5py import File
from scipy import signal

file = File('../static/mat/2022-01-26-d3-nz.mat')

unix_time = file['unixtime_global']
last = np.add(unix_time[-1], 5)
unix_time = np.append(unix_time, last)
unix_time = [np.linspace(unix_time[i], unix_time[i + 1], 128) for i in range(len(unix_time) - 1)]
UNIX_TIME = np.concatenate(unix_time)

diag_global = file["diag_global"]
diag_global = np.rot90(diag_global)
print("Size of diag_global:", len(diag_global), len(diag_global[0]), "\nsize of UNIX_TIME:", len(UNIX_TIME), 1)

q = 320  # То, во сколько раз вы прорежаете массив (берете каждый q-й элемент)
UNIX_TIME_2 = UNIX_TIME.reshape(-1, q)[:, 0]
diag_global_2 = signal.decimate(diag_global, q=q, ftype='fir')

graph2 = px.imshow(diag_global_2, x=UNIX_TIME_2, contrast_rescaling='minmax',
                  title="Keogramm", aspect='auto')
graph2.show()
