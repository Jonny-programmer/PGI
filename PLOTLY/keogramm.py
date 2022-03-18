import plotly.express as px
import numpy as np
from h5py import File
from scipy import signal

file = File('/Users/eremin/Documents/GitHub/PGI/static/mat/2022-02-04-d3.mat')

unix_time = file['unixtime_global']
last = np.add(unix_time[-1], 5)
unix_time = np.append(unix_time, last)
unix_time = [np.linspace(unix_time[i], unix_time[i + 1], 128) for i in range(len(unix_time) - 1)]
UNIX_TIME = np.concatenate(unix_time)

diag_global = file["diag_global"]
diag_global = np.rot90(diag_global)
# print("Size of diag_global:", len(diag_global), len(diag_global[0]), "\nsize of UNIX_TIME:", len(UNIX_TIME), 1)

q = 4642  # То, во сколько раз вы прорежаете массив (берете каждый q-й элемент)
UNIX_TIME_2 = signal.decimate(UNIX_TIME, ftype='fir', q=q, n=8)
diag_global_2 = signal.decimate(diag_global, q=q, ftype='fir', n=8)
# print("Size of diag_global 2:", len(diag_global_2), len(diag_global_2[0]), "UNIX_TIME_2:", len(UNIX_TIME_2), "\n\n")

testu_array = np.array(range(len(diag_global_2[0])))
graph2 = px.imshow(diag_global_2, x=testu_array, contrast_rescaling='minmax',
                  title="Keogramm", aspect='auto') # Если нет проблем с .mat файлами, то можно установить x=UNIX_TIME_2
graph2.show()
