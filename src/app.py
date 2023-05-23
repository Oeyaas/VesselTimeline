from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime

df = pd.read_excel("../data.xlsx")
app = Dash(__name__)
server = app.server

df["countryAndPort"] = df["countryName"] + ", " + df["portName"] # Temporary, move to DataGet!

possible_ports = df['countryAndPort'].drop_duplicates().sort_values()
possible_vessels = df['vesselName'].drop_duplicates().sort_values()

app.layout = html.Div([
    html.Div(dcc.Dropdown([i for i in possible_ports], id='port-input', multi=True)),
    html.Div(dcc.Dropdown([i for i in possible_vessels], id='vessel-input', multi=True)),
    html.Hr(),
    html.Hr(),
    html.Hr(),
    dcc.Graph(figure={}, id="output", style={'width': '100hh', 'height': '90vh'})
])

@callback(
    Output(component_id='output', component_property='figure'),
    Input(component_id='port-input', component_property='value'),
    Input(component_id='vessel-input', component_property='value')
)
def countryFilter(ports, vessels):
    if vessels:
        mask = df["vesselName"].isin(vessels)
        f_df = df[mask]
    else:
        f_df = df
        
    fig = px.timeline(f_df, x_start='ARR', x_end='DEP', y='vesselName',text = "countryAndPort")
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(
                visible=True  # Set to True to make the rangeslider visible
            ),
            type="date",  # Specify the x-axis type as "date"
            tickangle=45,  # Rotate the tick labels by 90 degrees
            dtick="D1",  # Set the interval between ticks to one day
        ),
        yaxis=dict(title=None),
        uirevision='graph' # Do not reset UI when updating graph
    )

    fig.update_traces(
        textposition="inside",
        insidetextanchor="middle")

     # Calculate the range of dates
    t_df = f_df
    min_date = pd.to_datetime(t_df['ARR']).min().date()
    max_date = pd.to_datetime(t_df['DEP']).max().date()
    
    # Add rectangles for weekends
    weekends = pd.date_range(start=min_date, end=max_date, freq='W-SAT')
    shapes = []
    for weekend in weekends:
        weekend_start = weekend - datetime.timedelta(days=1)
        weekend_end = weekend + datetime.timedelta(days=1)
        shapes.append({
            'type': 'rect',
            'x0': weekend_start,
            'x1': weekend_end,
            'y0': 0,
            'y1': 1,
            'xref': 'x',
            'yref': 'paper',
            'fillcolor': 'rgba(100, 100, 100, 0.4)',  # Dark gray fill color
            'line': {'width': 0},
            "layer":"below"
        })
    fig.update_layout(shapes=shapes)

    # Color bars red for specified ports
    if ports:
        fig.update_traces(marker=dict(color=['red' if port in ports else 'blue' for port in fig.data[0].text]))

    # Add vertical lines
    for i in range(len(f_df["vesselName"].drop_duplicates())):
        if i % 2 == 0:
            fig.add_hrect(y0= i + (-0.5), y1= i + 0.5, fillcolor="gray", opacity = 0.2, line_width=0)
    return fig
    
if __name__ == '__main__':
    app.run_server(debug=True)