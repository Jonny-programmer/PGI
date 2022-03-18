from dash import Dash, dcc, html

app = Dash(__name__)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app.layout = html.Div(style={}, children=[
    html.H2(children='PGI GRAPHS!!',
            style={'textAlign': 'center',
                   'color': colors['text']
            }),
    # dcc.Graph(figure=fig),
])

app.run_server(debug=True, port=8060)
