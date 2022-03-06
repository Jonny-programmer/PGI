from h5py import *
import h5py
import numpy as np

file = File('static/mat/2021-10-02-d3.mat', mode='r')

pdm = (file.__getitem__('pdm_2d_rot_global'))

for elem in pdm:
    if number == 1000:
        break
    number += 1
    y.append(np.array(elem).mean())

x = list(range(0, 1000))

plot = figure(title='example', x_axis_label='x', y_axis_label='y')

plot.line(x, y, legend_label='example_legend', line_width=2)

