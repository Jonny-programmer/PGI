from bokeh.plotting import figure
from h5py import File
import numpy as np
from bokeh.embed import components
from flask import Flask, render_template, url_for

app = Flask(__name__)

file = File('static/mat/2021-10-02-d3.mat')

light_curve = file['lightcurvesum_global']
unix_time = file['unixtime_global']
last = np.add(unix_time[-1], 5)
unix_time = np.append(unix_time, last)
unix_time = [np.linspace(unix_time[i], unix_time[i + 1], 128) for i in range(len(unix_time) - 1)]

x = np.concatenate(unix_time)
y = np.concatenate(light_curve)


plot = figure(title='Light curve', x_axis_label='Intensity', y_axis_label='Time, 10^5', width=1000)

plot.line(x, y, legend_label='', line_width=2)

script, div = components(plot)


@app.route('/')
def index():
    return render_template('index.html', script=script, div=div)


if __name__ == '__main__':
    app.run(port=8065, host='127.0.0.1')

