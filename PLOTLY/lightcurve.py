from h5py import File
import numpy as np
import plotly.express as px
from scipy import signal

file = File('/Users/eremin/Documents/GitHub/PGI/static/mat/2022-01-26-d3-nz.mat')

light_curve = file['lightcurvesum_global']
unix_time = file['unixtime_global']

last = np.add(unix_time[-1], 5)
unix_time = np.append(unix_time, last)
unix_time = [np.linspace(unix_time[i], unix_time[i + 1], 128) for i in range(len(unix_time) - 1)]
UNIX_TIME = np.concatenate(unix_time)
print("Length of UNIX_TIME:", len(UNIX_TIME))


y2 = np.concatenate(light_curve)
# Downsampling
q = 320
UNIX_TIME_2 = UNIX_TIME.reshape(-1, q)[:, 0]
light_curve_2 = signal.decimate(y2, q=q, ftype='fir', n=8)

light_curve = px.line(x=UNIX_TIME_2, y=light_curve_2)
light_curve.update_layout(legend_orientation="h",
                  legend=dict(x=.5, xanchor="center"),
                  title="Light Curve",
                  xaxis_title="Time",
                  yaxis_title="Intensity",)
light_curve.show()
