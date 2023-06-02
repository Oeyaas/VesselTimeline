from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import dash_auth
import ast
import dash_bootstrap_components as dbc

with open('../pass.txt', 'r') as f:
    auth_dict = ast.literal_eval(f.read())

# Setup data and variables
df = pd.read_excel("../data.xlsx")
df["countryAndPort"] = df["countryName"] + ", " + df["portName"]

project_dict = {name: group for name, group in df.groupby("project")}

f_df = pd.DataFrame() # Filtered dataframe
h_df = pd.DataFrame() # Highlight dataframe
possible_ports = pd.DataFrame()
possible_vessels = pd.DataFrame()

# possible_ports = a_df['countryAndPort'].drop_duplicates().sort_values()
# possible_vessels = a_df['vesselName'].drop_duplicates().sort_values()

# Start server
app = Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])
server = app.server
auth = dash_auth.BasicAuth(
    app,
    auth_dict
)

app.layout = html.Div([
    dbc.Row([
        dbc.Col(html.P("Project")),
        dbc.Col(html.P("Filter")),
        dbc.Col(html.P("Highlight")),
    ]),
    dbc.Row([
        dbc.Col(dcc.Dropdown([i for i in project_dict], placeholder="Select project", searchable = False, id='project-input', multi=False)),
        dbc.Col(dcc.Dropdown(placeholder="Country")),
        dbc.Col(dcc.Dropdown(placeholder="Country")),
    ]),
    dbc.Row([
        dbc.Col(html.P()),
        dbc.Col(dcc.Dropdown(placeholder="Port")),
        dbc.Col(dcc.Dropdown(placeholder="Port")),
    ]),
    dbc.Row([
        dbc.Col(html.P()),
        dbc.Col(dcc.Dropdown(placeholder="Vessel")),
        dbc.Col(dcc.Dropdown(placeholder="Vessel")),
    ]),
    html.Div(
        dcc.Graph(figure={}, id="output")
    ),
])

    
if __name__ == '__main__':
    app.run_server(debug=True)