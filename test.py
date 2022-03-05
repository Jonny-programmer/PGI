from h5py import File
import numpy as np
from bokeh.plotting import figure, show
# from bokeh.models import ColumnDataSource
# from bokeh.plotting import figure, output_file, show


number = 0
y = []
file = File('static/mat/2021-09-29-d1.mat')

pdm = (file.__getitem__('pdm_2d_rot_global'))

for elem in pdm:
    if number == 1000:
        break
    number += 1
    y.append(np.array(elem).mean())

x = list(range(0, 1000))

p = figure(title='example', x_axis_label='x', y_axis_label='y')

p.line(x, y, legend_label='example_legend', line_width=2)

show(p)