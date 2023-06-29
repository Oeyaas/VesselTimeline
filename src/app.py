from dash import Dash, html, dcc, callback, Output, Input, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import dash_auth
import ast
import dash_bootstrap_components as dbc

##### INITIALIZATION #####
# Load list of usernames/passwords
with open("../pass.txt", "r") as f:
    auth_dict = ast.literal_eval(f.read())

# Setup data and global variables
df = pd.read_excel("../data.xlsx", index_col=0).sort_values(by="vessel_name")
df["country_and_port"] = df["country_name"] + ", " + df["port_name"]
df['vessel_name'] = df['vessel_name'].str.strip()

now = datetime.now().strftime("%Y-%m-%d")

# Start server
app = Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server
auth = dash_auth.BasicAuth(
    app,
    auth_dict
)


##### DEFINE FUNCTIONS #####
# Function for creating dropdowns
def create_dropdown_list(project, category):
    if project is None:
        return []
    else:
        filtered = df.groupby("project").get_group(project) # Create a DataFrame corresponding to selected project
        item_list = filtered[category].unique().tolist() # Create a list of all unique items
        options = [item for item in item_list]
        options.sort()
        return options
    
# Filter dict
def create_filter_dict(country_value, port_value, vessel_value, class_value):
    filter_dict = {"country_name" : [], "country_and_port" : [], "vessel_name" : []}
    filter_dict["country_name"] = country_value
    filter_dict["country_and_port"] = port_value
    filter_dict["vessel_name"] = vessel_value
    filter_dict["class"] = class_value
    return filter_dict

# Creating figure
def create_timeline_figure(df):
    fig = px.timeline(df,
                      x_start="ARR", x_end="DEP",
                      y="vessel_name",
                      text = "port_name",
                      hover_data = "country_name",
                      color = "country_name",
                      )

    fig.update_traces(
        textposition="inside",
        insidetextanchor="middle",
        )

    fig.update_layout(
        xaxis = {
            'rangeslider': {'visible': True},
            'type': "date",  # Specify the x-axis type as "date"
            'tickangle': 45,  # Rotate the tick labels by 90 degrees
            'dtick': "D1",  # Set the interval between ticks to one day
        },
        yaxis={"title" : None},
        uniformtext_minsize=10,
        uirevision='graph',  # Do not reset UI when updating graph
        # height=50*len(final_df["vessel_name"].drop_duplicates()),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
    )

    # # Add vertical lines
    for i in range(len(df["vessel_name"].drop_duplicates())):
        if i % 2 == 0:
            fig.add_hrect(y0= i + (-0.5), y1= i + 0.5, fillcolor="gray", opacity = 0.2, line_width=0)
    
    fig.update_yaxes(categoryorder='array', categoryarray=df['vessel_name'].unique()[::-1]) # Orders in alphabetical

    fig.update_layout()

    return fig

##### CALLBACKS #####
### UPDATE DROPDOWNS BASED ON SELECTED PROJECT ###
# Country whitelist
@app.callback(
    Output("country-whitelist-select", "options"),
    Input("project-selection", "value")
)
def update_country_filter_dropdown(project):
    return create_dropdown_list(project, "country_name")

# Port whitelist
@app.callback(
    Output("port-whitelist-select", "options"),
    Input("project-selection", "value")
)
def update_port_filter_dropdown(project):
    return create_dropdown_list(project, "country_and_port")

# Vessel whitelist
@app.callback(
    Output("vessel-whitelist-select", "options"),
    Input("project-selection", "value")
)
def update_country_filter_dropdown(project):
    return create_dropdown_list(project, "vessel_name")

# Class whitelist
@app.callback(
    Output("class-whitelist-select", "options"),
    Input("project-selection", "value")
)
def update_country_filter_dropdown(project):
    return create_dropdown_list(project, "class")

### UPDATE FILTER DICTS ###
@app.callback(
    Output("whitelist-dict", "data"),
    [Input("country-whitelist-select", "value"),
     Input("port-whitelist-select", "value"),
     Input("vessel-whitelist-select", "value"),
     Input("class-whitelist-select", "value")]
)
def create_highlight_dict(country_value, port_value, vessel_value, class_value):
    return create_filter_dict(country_value, port_value, vessel_value, class_value)

### CALLBACK TO RESET DROPDOWNS WHEN PROJECT SELECTION CHANGES ###
@app.callback(
    Output("country-whitelist-select", "value"),
    Output("port-whitelist-select", "value"),
    Output("vessel-whitelist-select", "value"),
    Output("class-whitelist-select", "value"),
    [Input("project-selection", "value")]
)
def clear_filter_selections(project):
    return [], [], [], []

##### GRAPH #####
@app.callback(
    Output("figure", "figure"),
    [Input("project-selection", "value"),
    Input("whitelist-dict", "data"),]
)
def vesselTimeline(project, whitelist):
    if project and ((whitelist["vessel_name"]) or
                   (whitelist["country_name"]) or
                   (whitelist["country_and_port"]) or
                   (whitelist["class"])):

        project_df = df.groupby("project").get_group(project)
        project_df = project_df.reset_index(drop=True)

        whitelist_mask = pd.Series([True]*len(project_df))
        
        if whitelist["vessel_name"]:
            whitelist_mask = (whitelist_mask &  project_df["vessel_name"].isin(whitelist["vessel_name"]))
        if whitelist["country_name"]:
            whitelist_mask = (whitelist_mask &  project_df["country_name"].isin(whitelist["country_name"]))
        if whitelist["country_and_port"]:
            whitelist_mask = (whitelist_mask &  project_df["country_and_port"].isin(whitelist["country_and_port"]))
        if whitelist["class"]:
            whitelist_mask = (whitelist_mask &  project_df["class"].isin(whitelist["class"]))
    
        final_df = project_df[whitelist_mask]
        final_df = final_df.sort_values(by=['vessel_name'])

        if not final_df.empty:
            fig = create_timeline_figure(final_df)
        else:
            fig = go.Figure()
        return fig
    else:
        fig = go.Figure()
        return fig
    
##### DOWNLOAD #####
@callback(
    Output("download-dataframe-xlsx", "data"),
    State("project-selection", "value"),
    Input("btn_xlsx", "n_clicks"),
    prevent_initial_call=True,
)
def func(project, n_clicks):
    project_df = df.groupby("project").get_group(project)
    return dcc.send_data_frame(project_df.to_excel, "VesselTimeline_{}_{}.xlsx".format(project, now), sheet_name="Sheet_name_1")

##### LAYOUT #####
app.layout = html.Div([
    html.Div(
        className = "header-menu",
        children = [
            dbc.Row([
                # Using "_" as place holder in list comprehension
                dbc.Col(dcc.Dropdown([name for name, _ in df.groupby("project")], placeholder="Select project",
                                    searchable = False, id="project-selection", multi=False, persistence=True, persistence_type="session"),
                        class_name="small-dropdown"),
                dbc.Col(dcc.Dropdown(placeholder="Country",
                                    id="country-whitelist-select", multi=True, persistence=True, persistence_type="session")),
            ], class_name="top-buffer"),
            dbc.Row([
                dbc.Col(children = 
                            [dbc.Button("Download", id="btn_xlsx", size = "sm"),
                            dcc.Download(id="download-dataframe-xlsx")],
                        className="d-grid gap-2 small-dropdown"),
                dbc.Col(dcc.Dropdown(placeholder="Port",
                                    id="port-whitelist-select", multi=True, persistence=True, persistence_type="session")),
            ], class_name="top-buffer"),
            dbc.Row([
                dbc.Col(className="d-grid gap-2 small-dropdown"),
                dbc.Col(dcc.Dropdown(placeholder="Class",
                                    id="class-whitelist-select", multi=True, persistence=True, persistence_type="session"))
            ], class_name="top-buffer"),
            dbc.Row([
                dbc.Col(className="d-grid gap-2 small-dropdown"),
                dbc.Col(dcc.Dropdown(placeholder="Vessel",
                                    id="vessel-whitelist-select", multi=True, persistence=True, persistence_type="session"))
            ], class_name="top-buffer"),
        ]
    ),
    html.Div(
        dcc.Graph(figure={}, id="figure",
                  style={'width': '100hh', 'height': '80vh'})
    ),
    dcc.Store(id="whitelist-dict"),
])

if __name__ == "__main__":
    app.run_server(debug=True)