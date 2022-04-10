import plotly
from flask import *
import plotly.express as px
import numpy as np
from h5py import File
from scipy import signal
import os

file = File('./static/mat/2022-01-26-d3-nz.mat')

unix_time = file['unixtime_global']

last = np.add(unix_time[-1], 5)
unix_time = np.append(unix_time, last)
unix_time = [np.linspace(unix_time[i], unix_time[i + 1], 128) for i in range(len(unix_time) - 1)]
UNIX_TIME = np.concatenate(unix_time)

q = 12400  # То, во сколько раз вы прорежаете массив (берете каждый q-й элемент)
a = np.zeros(q - UNIX_TIME.shape[0] + ((UNIX_TIME.shape[0] + 1) // q) * q)
UNIX_TIME_2 = np.concatenate((UNIX_TIME, a)).reshape(-1, q)[:, 0]


def Heatmap(frame: int, max_min_values: list):
    print(frame)
    data = file['pdm_2d_rot_global']
    array = data[frame]
    fig = px.imshow(array, zmax=max(max_min_values), zmin=min(max_min_values), aspect='equal', origin='upper')

    fig.update_layout(legend_orientation="h",
                      legend=dict(
                          title=f"This is frame number {frame} out of {len(data)} <br> timestamp is {UNIX_TIME[frame]:.3f} seconds",
                          x=.5, xanchor='center', bordercolor='red', borderwidth=3, ),
                      showlegend=True,
                      xaxis_title="",
                      yaxis_title="",
                      )

    return fig


def Keogram(max_min_values: list):
    diag_global = file["diag_global"]
    diag_global = np.rot90(diag_global)
    print("Size of diag_global:", len(diag_global), len(diag_global[0]), "\nsize of UNIX_TIME:", len(UNIX_TIME), 1)

    diag_global_2 = signal.decimate(diag_global, q=q, ftype='fir')

    fig = px.imshow(diag_global_2, x=UNIX_TIME_2, zmax=max(max_min_values), zmin=min(max_min_values), aspect='auto')

    fig.update_layout()
    return fig


def Light_curve():
    light_curve = file['lightcurvesum_global']
    y2 = np.concatenate(light_curve)
    light_curve_2 = signal.decimate(y2, q=q, ftype='fir', n=8)
    fig = px.line(x=UNIX_TIME_2, y=light_curve_2)
    fig.update_layout(legend_orientation="h",
                              legend=dict(x=.5, xanchor="center"),
                              xaxis_title="Time",
                              yaxis_title="Intensity", )
    return fig

app = Flask(__name__, template_folder='templates')


@app.route("/", methods=["GET", "POST"])
def main():
    if request.method == 'POST':
        if request.values.get('type') == 'first_event':
            fig1 = Heatmap(1, [20000, 200000])
            fig2 = Keogram([20000, 200000])
            fig3 = Light_curve()
            heatmap_graph = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
            keogram_graph = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
            lightcurve_graph = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
            result = {'heatmap': heatmap_graph, 'keogram': keogram_graph, 'lightcurve': lightcurve_graph}
            return result
        elif request.values.get('type') == 'heatmap_button_event':
            current = int(request.values.get('current'))
            changes = {'next': 1, 'next2': 10, 'next3': 1000, 'last': -1, 'last2': -10, 'last3': -1000}
            current += changes[request.values.get('pos')]
            values = [int(request.values.get('value0')), int(request.values.get('value1'))]
            fig = Heatmap(current, values)
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            result = {'heatmap': graphJSON, 'current': current}
            return result
        elif request.values.get('type') == 'heatmap_slider_event':
            current = int(request.values.get('current'))
            values = [int(request.values.get('value0')), int(request.values.get('value1'))]
            fig = Heatmap(current, values)
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            result = {'heatmap': graphJSON, 'current': int(current)}
            return result
        elif request.values.get('type') == 'keogram_slider_event':
            values = [int(request.values.get('value0')), int(request.values.get('value1'))]
            fig = Keogram(values)
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return graphJSON
        elif request.values.get('type') == 'lightcurve_click_event':
            x = float(request.values.get('x'))
            current = np.where(UNIX_TIME_2 == x)[0][0] * q
            values = [int(request.values.get('value0')), int(request.values.get('value1'))]
            fig = Heatmap(current, values)
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            result = {'heatmap': graphJSON, 'current': int(current)}
            return result

    else:
        files_list = []
        for elem in os.listdir('static/mat/'):
            if not elem.startswith('.'):
                files_list.append(elem)
        return render_template('main.html', files_list=files_list)


if __name__ == "__main__":
    app.run(port=8408, debug=True)
