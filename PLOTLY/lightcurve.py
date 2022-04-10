from h5py import File
import numpy as np
import plotly.express as px
from scipy import signal
import os


file = File('../static/mat/2022-01-26-d3-nz.mat')

light_curve = file['lightcurvesum_global']
unix_time = file['unixtime_global']

last = np.add(unix_time[-1], 5)
unix_time = np.append(unix_time, last)
unix_time = [np.linspace(unix_time[i], unix_time[i + 1], 128) for i in range(len(unix_time) - 1)]
UNIX_TIME = np.concatenate(unix_time)
print("Length of UNIX_TIME:", len(UNIX_TIME))


y2 = np.concatenate(light_curve)
# Downsampling
q = 12400
a = np.zeros(q - UNIX_TIME.shape[0] + ((UNIX_TIME.shape[0] + 1) // q) * q)
UNIX_TIME_2 = np.concatenate((UNIX_TIME, a)).reshape(-1, q)[:, 0]
light_curve_2 = signal.decimate(y2, q=q, ftype='fir', n=8)

light_curve = px.line(x=UNIX_TIME_2, y=light_curve_2)
light_curve.update_layout(legend_orientation="h",
                          legend=dict(x=.5, xanchor="center"),
                          xaxis_title="Time",
                          yaxis_title="Intensity",)
# light_curve.show()
if not os.path.exists('../static/img/graphs_tmp_images'):
    os.mkdir('../static/img/graphs_tmp_images')
    os.chdir('../static/img/graphs_tmp_images')
    light_curve.write_image("Lightcurve.png") # Here the .jpeg, .webp, .svg, .pdf are also possible.

else:
    os.chdir('../static/img/graphs_tmp_images')
    try:
        light_curve.write_image("Lightcurve.png")
    except FileExistsError:
        os.remove('Lightcurve.png')
        light_curve.write_image("Lightcurve.png")
