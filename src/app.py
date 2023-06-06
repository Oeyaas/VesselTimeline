from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import dash_auth
import ast
import dash_bootstrap_components as dbc

with open("../pass.txt", "r") as f:
    auth_dict = ast.literal_eval(f.read())


# Setup data and variables
df = pd.read_excel("../data.xlsx")
df["countryAndPort"] = df["countryName"] + ", " + df["portName"]

# Start server
app = Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server
auth = dash_auth.BasicAuth(
    app,
    auth_dict
)

### CALLBACKS ###
### UPDATE DROPDOWNS BASED ON SELECTED PROJECT ###
# Country filter
@app.callback(
    Output("country-filter-select", "options"),
    Input("project-selection", "value")
)
def update_country_filter_dropdown(project):
    if project is None:
        return []
    else:
        filtered = df.groupby("project").get_group(project)
        country_list = filtered["countryName"].unique().tolist()
        options = [country for country in country_list]
        options.sort()
        return options

# Port filter
@app.callback(
    Output("port-filter-select", "options"),
    Input("project-selection", "value")
)
def update_port_filter_dropdown(project):
    if project is None:
        return []
    else:
        filtered = df.groupby("project").get_group(project)
        port_list = filtered["countryAndPort"].unique().tolist()
        options = [port for port in port_list]
        options.sort()
        return options

# Vessel filter
@app.callback(
    Output("vessel-filter-select", "options"),
    Input("project-selection", "value")
)
def update_country_filter_dropdown(project):
    if project is None:
        return []
    else:
        filtered = df.groupby("project").get_group(project)
        vessel_list = filtered["vesselName"].unique().tolist()
        options = [vessel for vessel in vessel_list]
        options.sort()
        return options

### CREATE FILTER DICT ###
# Filter dict
@app.callback(
    Output("filter-dict", "data"),
    [Input("country-filter-select", "value"),
     Input("port-filter-select", "value"),
     Input("vessel-filter-select", "value")]
)
def create_filter_dict(country_value, port_value, vessel_value):
    filter_dict = {"country" : [0], "port" : [0], "vessel" : [0]}
    filter_dict["country"] = country_value
    filter_dict["port"] = port_value
    filter_dict["vessel"] = vessel_value
    return filter_dict

### GRAPH ###
@app.callback(
    Output("final-figure", "figure"),
    [Input("project-selection", "value"),
    Input("filter-dict", "data")]
)
def vesselTimeline(project, filter):
    if project is None or filter is None:
        return go.Figure()
    elif project and filter:
        filtered = df.groupby("project").get_group(project)
        
        filter_mask = pd.DataFrame()
        filter_mask = filtered["vesselName"].isin(filter["vessel"]) + filtered["countryName"].isin(filter["country"]) + filtered["countryAndPort"].isin(filter["port"])

        filter_df = filtered[filter_mask]
        filter_df = filter_df.sort_values(by=['vesselName'])
        
        fig = px.timeline(filter_df,
                        x_start="ARR", x_end="DEP",
                        y="vesselName",
                        text = "portName",
                        hover_data = "countryName",
                        )

        fig.update_traces(
            textposition="inside",
            insidetextanchor="middle")


        fig.update_layout(
            xaxis = {
                'rangeslider': {'visible': True},
                'type': "date",  # Specify the x-axis type as "date"
                'tickangle': 45,  # Rotate the tick labels by 90 degrees
                'dtick': "D1",  # Set the interval between ticks to one day
            },
            yaxis={"title" : None},
            uirevision='graph',  # Do not reset UI when updating graph
            showlegend=False
        )

        fig.update_layout()

        return fig


### LAYOUT ###
app.layout = html.Div([

    dbc.Row([
        dbc.Col(html.P("Project")),
        dbc.Col(html.P("Filter")),
    ]),
    dbc.Row([
        # Using "_" as place holder in list comprehension
        dbc.Col(dcc.Dropdown([name for name, _ in df.groupby("project")], placeholder="Select project",
                             searchable = False, id="project-selection", multi=False, persistence=True, persistence_type="session")),
        dbc.Col(dcc.Dropdown(placeholder="Country",
                             id="country-filter-select", multi=True, persistence=True, persistence_type="session")),
    ]),
    dbc.Row([
        dbc.Col(html.P()),
        dbc.Col(dcc.Dropdown(placeholder="Port",
                             id="port-filter-select", multi=True, persistence=True, persistence_type="session")),
    ]),
    dbc.Row([
        dbc.Col(html.P()),
        dbc.Col(dcc.Dropdown(placeholder="Vessel",
                             id="vessel-filter-select", multi=True, persistence=True, persistence_type="session")),
    ]),
    dcc.Store(id="filter-dict"),
    html.Div(
        dcc.Graph(figure={}, id="final-figure")
    ),
])


if __name__ == "__main__":
    app.run_server(debug=True)