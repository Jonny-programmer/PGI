from dash import Dash, dcc, html, Input, Output
import plotly.express as px
from h5py import File
import numpy as np


app = Dash(__name__)


file = File('/Users/eremin/Documents/GitHub/PGI/static/mat/2021-10-02-d3.mat')

light_curve = file['lightcurvesum_global']
unix_time = file['unixtime_global']

last = np.add(unix_time[-1], 5)
unix_time = np.append(unix_time, last)
unix_time = [np.linspace(unix_time[i], unix_time[i + 1], 128) for i in range(len(unix_time) - 1)]

x1 = np.concatenate(unix_time)
y2 = np.concatenate(light_curve)


colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app.layout = html.Div(style={}, children=[
    html.H2(children='Light curve PGI',
            style={'text-align': 'center',
                   'color': colors['text']
            }),
    dcc.Graph(id="graph"),
    html.P(children="Choose your favourite programmers:",
           style={'text-align': 'center',
                  'color': colors['text']
            }),
    dcc.Checklist(
        id='progers',
        options=["Emil", "Jonny", "Anne"],
        value=["Emil"],
        style={'text-align': 'center',
               'color': colors['text']
        }
    ),
    html.P(y2[:100])
])


@app.callback(
    Output("graph", "figure"), 
    Input("progers", "value"))
def load_frame(cols):
    fig = px.line(x=x1, y=y2)
    return fig


app.run_server(debug=True)