from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime

df = pd.read_excel("../data.xlsx")
app = Dash(__name__)
server = app.server

possible_ports = df['portName'].drop_duplicates().sort_values()

app.layout = html.Div([
    html.Hr(),
    dcc.Dropdown([i for i in possible_ports], id='input', multi=True),
    html.Hr(),
    dcc.Graph(figure={}, id="output", style={'width': '100hh', 'height': '90vh'})
])

@callback(
    Output(component_id='output', component_property='figure'),
    Input(component_id='input', component_property='value')
)
def countryFilter(ports):
    fig = px.timeline(df, x_start='ARR', x_end='DEP', y='vesselName',text = df["portName"] + ", " + df["countryName"])
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(
                visible=True  # Set to True to make the rangeslider visible
            ),
            type="date",  # Specify the x-axis type as "date"
            tickangle=45,  # Rotate the tick labels by 90 degrees
            dtick="D1",  # Set the interval between ticks to one day
            rangebreaks=[
                dict(bounds=[6.5, 7.5], pattern='hour'),  # Skip hours 6-7 (Saturday)
                dict(bounds=[13.5, 14.5], pattern='hour')  # Skip hours 13-14 (Sunday)
            ]
        ),
        yaxis=dict(title=None),
        uirevision='graph'
    )
    fig.update_traces(
        textposition="inside",
        insidetextanchor="middle")

     # Calculate the range of dates
    t_df = df
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
    fig.update_traces(
        textposition="inside",
        insidetextanchor="middle")

    # Color bars red for specified ports
    if ports:
        fig.update_traces(marker=dict(color=['red' if port in ports else 'blue' for port in fig.data[0].text]))

    # Add vertical lines
    for i in range(len(df["vesselName"].drop_duplicates())):
        if i % 2 == 0:
            fig.add_hrect(y0= i + (-0.5), y1= i + 0.5, fillcolor="gray", opacity = 0.2, line_width=0)

    return fig
    
if __name__ == '__main__':
    app.run_server(debug=True)