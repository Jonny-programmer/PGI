from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html
from h5py import File
import numpy as np
from bokeh.embed import components
from flask import Flask, render_template, url_for

app = Flask(__name__)

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

plot = figure(title='example', x_axis_label='x', y_axis_label='y')

plot.line(x, y, legend_label='example_legend', line_width=2)

script, div = components(plot)


@app.route('/')
def index():
    return render_template('new.html', script=script, div=div)


if __name__ == '__main__':
    app.run(port=8087, host='127.0.0.1')
