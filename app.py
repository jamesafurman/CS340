# Setup the Jupyter version of Dash
from jupyter_dash import JupyterDash

# Configure the necessary Python module imports
import dash_leaflet as dl
from dash import dcc, html, dash_table, ctx
import plotly.express as px
from dash.dependencies import Input, Output

# Configure the plotting routines
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# import AnimalShelter collection with CRUD module
from AnimalShelter import AnimalShelter


###########################
# Data Manipulation / Model
###########################

db = AnimalShelter()

# class read method must support return of list object and accept projection json input
# sending the read method an empty document requests all documents be returned
# note db.crud.read() does not return the '_id' column
df = pd.DataFrame.from_records(db.crud.read({"animal_type": "Dog"}))

## Debug
# print(len(df.to_dict(orient='records')))
# print(df.columns)

#########################
# Dashboard Layout / View
#########################
app = JupyterDash("SimpleExample")

app.layout = html.Div(
    [
        html.Div(id="hidden-div", style={"display": "none"}),
        html.Center(
            html.A(
                html.Img(
                    src="assets/logo.png", style={"height": "10%", "width": "10%"}
                ),
                href="https://www.snhu.edu",
            )
        ),
        html.Center(html.B(html.H1("Grazioso Salvare Search Dog Dashboard"))),
        html.Hr(),
        html.Div(
            children=[
                html.Label("Filter Data Table"),
                filter_menu := dcc.Dropdown(
                    [
                        # these strings must exactly match values in filter_db()
                        "Water Rescue",
                        "Mountain and Wilderness Rescue",
                        "Disaster Rescue and Individual Tracking",
                        "Reset",
                    ],
                    value="Reset",
                    id="filter-menu",
                    style={"width": "50%"},
                ),
            ],
            style={
                "padding": 10,
                "flex": 1,
                "display": "flex",
                "flex-direction": "horizontal",
            },
        ),
        html.Hr(),
        animal_table := dash_table.DataTable(
            id="datatable-id",
            columns=[
                # 'if not' statement omits several columns from datatable; to make them togglable, remove
                # and add hidden_columns=[] data table attribute assigned to the array of column names
                {
                    "name": i.replace("_", " ").title(),
                    "id": i,
                    "deletable": False,
                    "selectable": False,
                }
                for i in df.columns
                if not i
                in [
                    "animal_id",
                    "animal_type",
                    "rec_num",
                    "datetime",
                    "monthyear",
                    "location_lat",
                    "location_long",
                    "age_upon_outcome",
                    # "age_upon_outcome_in_weeks",
                ]
            ],
            data=df.to_dict("records"),
            row_selectable="single",
            selected_rows=[],
            sort_action="native",
            page_action="native",
            page_current=0,
            page_size=20,
            filter_action="native",
            filter_options={"case": "insensitive"},
            style_cell={"font-family": "sans-serif"},
            style_header={
                "whiteSpace": "normal",
                "height": "auto",
                "text-align": "center",
            },
            style_data={
                "maxWidth": 0,
                "overflow": "hidden",
                "textOverflow": "ellipsis",
            },
            tooltip_data=[
                {column: {"value": str(value)} for column, value in row.items()}
                for row in df.to_dict("records")
            ],
        ),
        html.Br(),
        html.Hr(),
        html.Div(
            id="datavis-container",
            children=[
                animal_map := dl.Map(
                    id="map-id",
                    style={"width": "1000px", "height": "500px"},
                    center=[30.75, -97.48],
                    zoom=10,
                    children=[dl.TileLayer(id="base-layer-id")],
                    className="col s12 m6",
                ),
                html.Br(),
                html.Hr(),
                html.Div(
                    id="graph-container",
                    children=[
                        html.Div(
                            children=[
                                html.Label("Filter Pie Chart"),
                                graph_menu := dcc.Dropdown(
                                    [
                                        # these strings must exactly match values in update_graph()
                                        "Breed",
                                        "Sex",
                                    ],
                                    value="Sex",
                                    style={"width": "50%"},
                                ),
                            ],
                            style={"display": "flex", "flex-direction": "row"},
                        ),
                        animal_graph := dcc.Graph(id="graph-id"),
                    ],
                ),
            ],
            style={"width": "100%", "display": "flex", "flex-direction": "column"},
        ),
        html.H2("jamesafurman"),
    ]
)

#############################################
# Interaction Between Components / Controller
#############################################


# Create a dictionary to filter the database, given an input string value
# If filter_val does not match a predefined string, return an empty dictionary
# filter_val values are received from the filter_menu dropdown in app.layout
def filter_db(filter_val):
    filter_dict = {"animal_type": "Dog"}

    # Water Rescue
    # comparison string value must exactly match app.layout.filter_menu values
    if filter_val == "Water Rescue":
        filter_dict["breed"] = {
            "$in": [
                "Labrador Retriever Mix",
                "Chesapeake Bay Retriever",
                "Newfoundland",
            ]
        }
        filter_dict["sex_upon_outcome"] = "Intact Female"
        filter_dict["age_upon_outcome_in_weeks"] = {"$gte": 26}
        filter_dict["age_upon_outcome_in_weeks"] = {"$lte": 156}

    # Mountain or Wilderness rescue
    # comparison string value must exactly match app.layout.filter_menu values
    elif filter_val == "Mountain and Wilderness Rescue":
        filter_dict["breed"] = {
            "$in": [
                "German Shepherd",
                "Alaskan Malamute",
                "Old English Sheepdog",
                "Siberian Husky",
                "Rottweiler",
            ]
        }
        filter_dict["sex_upon_outcome"] = "Intact Male"
        filter_dict["age_upon_outcome_in_weeks"] = {"$gte": 26}
        filter_dict["age_upon_outcome_in_weeks"] = {"$lte": 156}

    # Disaster rescue or Individual Tracking
    # comparison string value must exactly match app.layout.filter_menu values
    elif filter_val == "Disaster Rescue and Individual Tracking":
        filter_dict["breed"] = {
            "$in": [
                "Doberman Pinscher",
                "German Shepherd",
                "Golden Retriever",
                "Bloodhound",
                "Rottweiler",
            ]
        }
        filter_dict["sex_upon_outcome"] = "Intact Male"
        filter_dict["age_upon_outcome_in_weeks"] = {"$gte": 20}
        filter_dict["age_upon_outcome_in_weeks"] = {"$lte": 300}

    # No filter
    elif filter_val == "Reset":
        pass

    return filter_dict


# Update pie chart to display animals in the result by proportions of the selected attribute
# graph_selection value is received from the graph_menu dropdown in app.layout
@app.callback(
    Output(animal_graph, "figure"),
    [Input(graph_menu, "value"), Input(animal_table, "derived_virtual_data")],
)
def update_graph(graph_selection, table_data):
    # Read db with selected filter and return results as a dataframe
    df = table_data

    # these comparison string values must exactly match app.layout.graph_menu values
    if graph_selection == "Breed":
        name = "breed"
    elif graph_selection == "Sex":
        name = "sex_upon_outcome"

    fig = px.pie(df, names=name)
    return fig


# This callback will highlight a row on the data table when the user selects it
@app.callback(
    Output(animal_table, "style_data_conditional"),
    [Input(animal_table, "derived_virtual_selected_rows")],
)
def update_styles(selected_rows):
    return [
        {"if": {"row_index": i}, "background_color": "#D2F3FF"} for i in selected_rows
    ]


# This callback will filter data to only include species selected in a checklist
@app.callback(Output(animal_table, "data"), [Input(filter_menu, "value")])
def filter_results(in_rescue):
    filter_dict = filter_db(in_rescue)

    # Read db with selected filter and return results as a dataframe
    df = pd.DataFrame.from_records(db.crud.read(filter_dict))
    return df.to_dict("records")


# This callback will update the geo-location chart for the selected data entry
# derived_virtual_data will be the set of data available from the datatable in the form of
# a dictionary.
# derived_virtual_selected_rows will be the selected row(s) in the table in the form of
# a list. For this application, we are only permitting single row selection so there is only
# one value in the list.
# The iloc method allows for a row, column notation to pull data from the datatable
@app.callback(
    Output(animal_map, "children"),
    [
        Input(animal_table, "derived_virtual_data"),
        Input(animal_table, "derived_virtual_selected_rows"),
    ],
)
def update_map(viewData, index):
    dff = pd.DataFrame.from_dict(viewData)
    # Because we only allow single row selection, the list can
    # be converted to a row index here
    if index is None:
        row = 0
    else:
        row = index[0]

    return [
        dl.TileLayer(id="base-layer-id"),
        # Marker with tool tip and popup
        # Columns 13 and 14 define the grid coordinates for the map
        # Column 4 defines the breed for the animal
        # Column 9 defines the name of the animal
        dl.Marker(
            position=[dff.iloc[row, 13], dff.iloc[row, 14]],
            children=[
                dl.Tooltip(dff.iloc[row, 4]),
                dl.Popup(
                    [
                        html.H1("Name: " + dff.iloc[row, 9]),
                        # html.H2("Species: " + dff.iloc[row, 3]),
                        html.H2("Breed: " + dff.iloc[row, 4]),
                    ]
                ),
            ],
        ),
    ]


# Centers the map on the selected animal
@app.callback(
    Output(animal_map, "center"),
    [
        Input(animal_table, "derived_virtual_data"),
        Input(animal_table, "derived_virtual_selected_rows"),
    ],
)
def update_map(viewData, index):
    dff = pd.DataFrame.from_dict(viewData)
    # Because we only allow single row selection, the list can
    # be converted to a row index here
    if index is None:
        row = 0
    else:
        row = index[0]

    # Columns 13 and 14 define the grid coordinates for the map
    return [dff.iloc[row, 13], dff.iloc[row, 14]]


app.run_server(debug=False)
