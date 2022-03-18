import plotly.express as px
import numpy as np
from h5py import File

file = File('/Users/eremin/Documents/GitHub/PGI/static/mat/2022-02-04-d3.mat')

unix_time = file['unixtime_global']

last = np.add(unix_time[-1], 5)
unix_time = np.append(unix_time, last)
unix_time = [np.linspace(unix_time[i], unix_time[i + 1], 128) for i in range(len(unix_time) - 1)]
UNIX_TIME = np.concatenate(unix_time)

data = file['pdm_2d_rot_global']

def Heatmap(frame: int):
    array = data[frame]
    fig = px.imshow(array, contrast_rescaling='minmax', aspect='equal', origin='upper',)
    fig.update_layout(legend_orientation="h",
                      legend=dict(title=f"This is frame number {frame} out of {len(data)} <br> timestamp is {UNIX_TIME[frame]:.3f} seconds",
                                  x=.5, xanchor='center', bordercolor='red', borderwidth=3,

                                  ),
                      showlegend=True,
                      xaxis_title="",
                      yaxis_title="",)
    return fig

figure = Heatmap(1331)
figure.show()