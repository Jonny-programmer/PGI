import plotly.express as px
import numpy as np
from h5py import File

file = File('/Users/eremin/Documents/GitHub/PGI/static/mat/2022-02-04-d3.mat')

unix_time = file['unixtime_global']

last = np.add(unix_time[-1], 5)
unix_time = np.append(unix_time, last)
unix_time = [np.linspace(unix_time[i], unix_time[i + 1], 128) for i in range(len(unix_time) - 1)]
UNIX_TIME = np.concatenate(unix_time)

data = np.concatenate(file['cwt_global'])

wave = px.imshow(data, x=UNIX_TIME, contrast_rescaling='minmax',
                  title="Wavelett", aspect='auto')
wave.show()