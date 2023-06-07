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

### UPDATE HIGHLIGHT DROPDOWNS BASED ON SELECTED FILTERS ###
# Country highlight
@app.callback(
    Output("country-highlight-select", "options"),
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

# Port highlight
@app.callback(
    Output("port-highlight-select", "options"),
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
    
# Vessel highlight
@app.callback(
    Output("vessel-highlight-select", "options"),
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


### CREATE FILTER AND HIGHLIGHT DICTS ###
# Filter dict
@app.callback(
    Output("filter-dict", "data"),
    [Input("country-filter-select", "value"),
     Input("port-filter-select", "value"),
     Input("vessel-filter-select", "value")]
)
def create_filter_dict(country_value, port_value, vessel_value):
    filter_dict = {}
    filter_dict["country"] = country_value
    filter_dict["port"] = port_value
    filter_dict["vessel"] = vessel_value
    return filter_dict

# Highlight dict
@app.callback(
    Output("highlight-dict", "data"),
    [Input("country-highlight-select", "value"),
    Input("port-highlight-select", "value"),
    Input("vessel-highlight-select", "value"),]
)
def create_highlight_dict(country_value, port_value, vessel_value):
    highligt_dict = {"country" : [], "port" : [], "vessel" : []}
    highligt_dict["country"] = country_value
    highligt_dict["port"] = port_value
    highligt_dict["vessel"] = vessel_value
    return highligt_dict

### GRAPH ###
@app.callback(
    Output("final-figure", "figure"),
    [Input("project-selection", "value"),
    Input("filter-dict", "data"),
    Input("highlight-dict", "data")]
)
def vesselTimeline(project, filter, highlight):
    filtered = df.groupby("project").get_group(project)
    
    filter_mask = pd.DataFrame()
    filter_mask = filtered["vesselName"].isin(filter["vessel"]) + filtered["countryName"].isin(filter["country"]) + filtered["countryAndPort"].isin(filter["port"])
    
    highlight_mask = pd.DataFrame()
    highlight_mask = filtered["vesselName"].isin(highlight["vessel"]) + filtered["countryName"].isin(highlight["country"]) + filtered["countryAndPort"].isin(highlight["port"])

    filtered["highlighted"] = highlight_mask
    filter_df = filtered[filter_mask]
    filter_df = filter_df.sort_values(by=['vesselName'])
    
    fig = px.timeline(filter_df,
                      x_start="ARR", x_end="DEP",
                      y="vesselName",
                      text = "portName",
                      hover_data = "countryName",
                      color = "highlighted",
                      category_orders={"vesselName": filter_df['vesselName'].unique().tolist()},
                      color_discrete_map = {True: 'red', False: 'blue'}
                      )

    fig.update_traces(
        textposition="inside",
        insidetextanchor="middle")

    #  # Calculate the range of dates
    # t_df = filter_df
    # min_date = pd.to_datetime(t_df['ARR']).min().date()
    # max_date = pd.to_datetime(t_df['DEP']).max().date()
    
    # # Add rectangles for weekends
    # weekends = pd.date_range(start=min_date, end=max_date, freq='W-SAT')
    # shapes = []
    # for weekend in weekends:
    #     weekend_start = weekend - datetime.timedelta(days=1)
    #     weekend_end = weekend + datetime.timedelta(days=1)
    #     shapes.append({
    #         'type': 'rect',
    #         'x0': weekend_start,
    #         'x1': weekend_end,
    #         'y0': 0,
    #         'y1': 1,
    #         'xref': 'x',
    #         'yref': 'paper',
    #         'fillcolor': 'rgba(100, 100, 100, 0.4)',  # Dark gray fill color
    #         'line': {'width': 0},
    #         "layer":"below"
    #     })

    fig.update_layout(
        xaxis = {
            'rangeslider': {'visible': True},
            'type': "date",  # Specify the x-axis type as "date"
            'tickangle': 45,  # Rotate the tick labels by 90 degrees
            'dtick': "D1",  # Set the interval between ticks to one day
        },
        yaxis={"title" : None},
        uirevision='graph',  # Do not reset UI when updating graph
        # shapes = shapes,
        # height=50*len(filter_df["vesselName"].drop_duplicates()),
        showlegend=False
    )

    # # Add vertical lines
    # for i in range(len(filter_df["vesselName"].drop_duplicates())):
    #     if i % 2 == 0:
    #         fig.add_hrect(y0= i + (-0.5), y1= i + 0.5, fillcolor="gray", opacity = 0.2, line_width=0)

    fig.update_layout()

    return fig


### LAYOUT ###
app.layout = html.Div([

    dbc.Row([
        dbc.Col(html.P("Project")),
        dbc.Col(html.P("Filter")),
        dbc.Col(html.P("Highlight")),
    ]),
    dbc.Row([
        # Using "_" as place holder in list comprehension
        dbc.Col(dcc.Dropdown([name for name, _ in df.groupby("project")], placeholder="Select project",
                             searchable = False, id="project-selection", multi=False, persistence=True, persistence_type="session")),
        dbc.Col(dcc.Dropdown(placeholder="Country",
                             id="country-filter-select", multi=True, persistence=True, persistence_type="session")),
        dbc.Col(dcc.Dropdown(placeholder="Country",
                             id="country-highlight-select", multi=True, persistence=True, persistence_type="session")),
    ]),
    dbc.Row([
        dbc.Col(html.P()),
        dbc.Col(dcc.Dropdown(placeholder="Port",
                             id="port-filter-select", multi=True, persistence=True, persistence_type="session")),
        dbc.Col(dcc.Dropdown(placeholder="Port",
                             id="port-highlight-select", multi=True, persistence=True, persistence_type="session")),
    ]),
    dbc.Row([
        dbc.Col(html.P()),
        dbc.Col(dcc.Dropdown(placeholder="Vessel",
                             id="vessel-filter-select", multi=True, persistence=True, persistence_type="session")),
        dbc.Col(dcc.Dropdown(placeholder="Vessel",
                             id="vessel-highlight-select", multi=True, persistence=True, persistence_type="session")),
    ]),
    dcc.Store(id="filter-dict"),
    dcc.Store(id="highlight-dict"),
    html.Div(
        dcc.Graph(figure={}, id="final-figure",
                  style={'width': '100hh', 'height': '80vh'})
    ),
])


if __name__ == "__main__":
    app.run_server(debug=True)